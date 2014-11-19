#!/usr/bin/perl
#
# (C) 2004 STC Developers Team
#    slivarez            Didenko A.V.    slivarez@list.ru
#    alexenin            Enin Alexander  alexenin@yandex.ru
#    Demimurych          Demimuruch      demimurych@mail.ru
#    Orkan               Sirota S.S.     brahma@ua.fm
#
# Great thanks to:
#    adm -               Kostin Ilya
#    yolka_palka                         yolka@ydk.com.ua
#
# STC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# STC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with STC; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

#List of profile fields allowed for user to modify
@allowed=undef;
$allowed{"iface"}="ok";

use Apache::Htpasswd;
$scode="ok";
require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("$user: $msg{'page_change_pass'}");
&init_stc;

$query=new CGI;
$oldpass=$query->param(oldpasswd);
$newpass=$query->param(newpasswd);
$repass=$query->param(repasswd);
$mod_user=$query->param(mod_user);
$chpasswd=$query->param(chpasswd);

if ($chpasswd){
  if(($newpass ne '') and ($newpass eq $repass)){

    if ($conf_htpasswd_usemd5 eq 'true') {
        $pas = new Apache::Htpasswd({
            passwdFile => "$conf_stc_path/password",
            UseMD5     => 1,
        });
    } else {
        $pas = new Apache::Htpasswd("$conf_stc_path/password");
    }

    $check_pass=$pas->htCheckPassword($user, $oldpass);
    if ($check_pass == 1){
       $check_pass=$pas->htpasswd($user, $newpass, $oldpass);
       &del_from_file ("${conf_stc_path}/password.digest", $user);
       open dpf, ">>$conf_stc_path/password.digest";
       printf dpf "$user:$newpass\n";
       close (dpf);

	print "<center><b class=ok>$msg[43]</b></center><br>";
    logmsg (__FILE__." line ".__LINE__.":[INFO] User '$user' has changed his own password.");
goto the_end;
    }
    else{
    logmsg (__FILE__." line ".__LINE__.":[WARNING] user '$user' failed to change own password because of old password verification failure.");
	print "<b class=error>$msg{'error'}</b> ";
	print "$msg[45]<br><br>";
    }
  }
  if($newpass ne $repass){
    print "<b class=error>$msg{'error'}</b> $msg{'pass_mismatch'}<br>";
  }
}#if chpasswd

if ($mod_user){
#Updating user profile
    open prof, "<$conf_stc_path/profiles/${user}.profile" or print "$msg{\"no_profile_makedef\"}<br>$conf_stc_path/profiles/${user}.profile: $!";
    my @tmpprof=undef;
    while ($stin=<prof>){
	chomp ($stin);
	my @tt=split(':', $stin);
	my $tkey=$tt[0];
	if (($tt[1] ne $query->param("$tt[0]")) and !($tkey =~ s/o\d+/$1/) and $allowed{"$tt[0]"}){
	    $tt[1] = $query->param("$tt[0]");
	}
	$stin = join (':', $tt[0], $tt[1]);
	if ($stin) {push @tmpprof, $stin;}
    }
    close prof;
    $gluk=undef; open prof, ">$conf_stc_path/profiles/$user.profile" or $gluk='sux';
    foreach (@tmpprof){
	my $tt=$_;
	if (!$tt){next;}
	printf prof "$tt\n";
    }#foreach
    close (prof);

    if ($gluk eq 'sux'){
        print "$msg{'cannot_open'} $conf_stc_path/profiles/$user.profile: $!";
        logmsg (__FILE__." line ".__LINE__.":[ERROR] Cannot create user profile for $user in '$conf_stc_path/profiles/$user.profile': $!");
    }
    logmsg (__FILE__." line ".__LINE__.":[INFO] User $user modified his info");
}#if mod_user

print "<center><b>$msg[39] $user</b><br><br>";

if($admin{$user} eq 'yep'){
    print "<a href='supasswd.cgi?back_url=chpasswd.cgi'>$msg[29]</a><br><br>";
}

print start_form(-action=>'chpasswd.cgi', -method=>"POST");
print table(
      {-align=>"center"},
      Tr (
      [
         td (["$msg[40]:", password_field(-name=>'oldpasswd', -size=>'20')]),
         td (["$msg[19]:", password_field(-name=>'newpasswd', -size=>'20')]),
         td (["$msg[20]:", password_field(-name=>'repasswd', -size=>'20')]),
         td ({-colspan=>2, -align=>"center"}, [submit(-name=>'chpasswd', -value=>"$msg{change_pw}")]),
      ]
     )
 );
print end_form();

print "<hr><br>";
print "<center><b>$msg{\"iface_change\"}</b><br>";
print "<form method=POST>
     <table>
     <tr>
        <td style=\"text-align:right;\">$msg[153]:</td>
        ", td(popup_menu(-name=>'iface', -values=>\@theme, -default=>$user_profile{"${user}_iface"})),"
     </tr>
     <tr>
        <td colspan=2 style=\"text-align:center;\">
        <input type=submit value=\"$msg[26]\" name=\"mod_user\">
        &nbsp; &nbsp; &nbsp;
        <input type=reset value=\"$msg[27]\">
        </td>
     </tr>
     </table>
     </form>
";
print "</center>";
print "<hr><br>";
print "<b>$msg{\"profile_info\"}</b>";

print "<table width=50%>";
print "<tr><td>$msg{user}:</td><td>$user</td></tr>";
print "<tr><td>$msg[13]:</td><td>",$user_profile{"${user}_lname"},"</td></tr>";
print "<tr><td>$msg[14]:</td><td>",$user_profile{"${user}_fname"},"</td></tr>";
print "<tr><td>$msg[15]:</td><td>",$user_profile{"${user}_mname"},"</td></tr>";
print "<tr><td>$msg{otdel}:</td><td>",$otdel_prn{$user_profile{"${user}_otdel"}},"</td></tr>";
print "</table>";
print "<hr>";

the_end:
&load_footer;

sub del_from_file
    {
    my ($filename, $delu) = @_;
          $err='ok';
    my $out="";
          open f1, "<${filename}" or $err="gluk";
           if ($err eq "gluk")
                {
                print "<b class=error>$msg{'error'}</b> $msg{'cannot_open'} ${filename} ($msg{'read'})";
                logmsg (__FILE__." line ".__LINE__.":[ERROR] cannot open file '${filename}' for reading: $!");
                }
           while (<f1>)
              {
              $tmpu=$_;
              $tmpu=~s/:.*$//;
              $tmpu=(split(" ", $tmpu))[0];
              if ($tmpu eq $delu) {next;}
              $out.=$_;
              }
          close (f1);
          open f1, ">${filename}" or $err="gluk";
           if ($err eq "gluk")
                {
                print "<b class=error>$msg{'error'}</b> $msg{'cannot_open'} ${filename} ($msg{'write'})";
                logmsg (__FILE__." line ".__LINE__.":[ERROR] cannot open file '${filename}' for writing: $!");
                }
          print f1 $out;
          close (f1);
    }
