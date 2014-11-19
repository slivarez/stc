#!/usr/bin/perl
#
# (C) 2004 STC developers team
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

use Apache::Htpasswd;
$scode="ok";
require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("Users");
&init_stc;

$query=new CGI;
$param_otdel=$query->param(otdel);
$grant=$query->param(grant);
$grant_otd=$query->param(grant_otd);

print "<center>";
print "
<script language=\"JavaScript\">
<!--
function SubmitDelete(msg)
     {
     conf = confirm(msg);
     if (conf) return true;
     else return false;
     }
-->
</script>
";

$usver=clean($query->param('user'));
&get_profile($usver);

$actual_otdel=$user_profile{"${usver}_otdel"};
if(!adv_boss_chk($user, $actual_otdel, 'view_stat')){
    print "$msg{'access_denied'}<br>";
    logmsg (__FILE__." line ".__LINE__.":[WARNING] User $user - access denied to adduser.cgi");
    goto l1;
}

$back_url=$query->param('back_url');
if (!safe_url($back_url, 'user_mod.cgi')){goto l1;}

#DEBUG
#print "SU: $start_usver, BU: $back_url, BU1: $back_url1, O: $otdel<br>";

if ($query->param(mod_user))
    {
        $otdel=$query->param(otd);
        $otdel=0+$otdel;
        if (!adv_boss_chk($user, $otdel, 'user_add')){
	    print "$msg{'access_denied'}<br>";
            logmsg (__FILE__." line ".__LINE__.":[WARNING] user $user tried to move user into bad department #$otdel");
            goto l1;
        }

        if ($user_profile{"${usver}_otdel"} ne $otdel)
            {
            &del_from_file ("${conf_stc_path}/o".$user_profile{"${usver}_otdel"}.".users", $usver);

            $file_otd="$conf_stc_path/o$otdel.users";
            $err="ok";

            open f1, ">>$file_otd" or $err="gluk";
            printf f1 "$usver\n";
            close (f1);

            if ($err eq "gluk")
                {
                print "<b class=error>$msg{'error'}</b> $msg{'cannot_open'} $msg{'otdel_file'} ($msg{'write'})";
                logmsg (__FILE__." line ".__LINE__.":[ERROR] cannot open otdel file '$file_otd' for writing: $!");
                goto form_begin;
                }
            }

        $limit=$query->param(lim);
	$limit =~ s/\D+//ig;
	$limit = $limit * $conf_mega_byte;
        if ($query->param('NL') eq 'on'){$limit="NL";}
        $newpass=$query->param('newpasswd');
        $repass=$query->param('repasswd');

        if(($newpass ne '') && ($newpass ne $repass)){
            print "$msg[25]<br>";
            goto form_begin;
        }

        if ($newpass)
            {
            $pass_path="$conf_stc_path/password";
            $ap_htpass=new Apache::Htpasswd($pass_path);
            $ap_htpass->htpasswd($usver, $newpass, {'overwrite' => 1});

            &del_from_file ("${conf_stc_path}/password.digest", $usver);
            open dpf, ">>$conf_stc_path/password.digest";
            printf dpf "$usver:$newpass\n";
            close (dpf);
            }

            &del_from_file ("${conf_stc_path}/traffic.users", $usver);
            open t1, ">>$conf_stc_path/traffic.users";
                printf t1 $usver;
                printf t1 " ";
                printf t1 $limit;
                printf t1 "\n";
                close (t1);

#Updating user profile
	    open prof, "<$conf_stc_path/profiles/${usver}.profile" or print "$msg{\"no_profile_makedef\"}<br>$conf_stc_path/profiles/${usver}.profile: $!";
	    my @tmpprof=undef;
	    while ($stin=<prof>){
		chomp ($stin);
		my @tt=split(':', $stin);
		my $tkey=$tt[0];
		if (($tt[1] ne $query->param("$tt[0]")) and !($tkey =~ s/o\d+/$1/)){
		    $tt[1] = clean($query->param("$tt[0]"), '\ ');
		}
		$stin = join (':', $tt[0], $tt[1]);
		if ($stin) {push @tmpprof, $stin;}
	    }
	    close prof;

            $gluk=undef; open prof, ">$conf_stc_path/profiles/$usver.profile" or $gluk='sux';
	    foreach (@tmpprof){
		my $tt=$_;
		if (!$tt){next;}
		printf prof "$tt\n";
	    }#foreach
            close (prof);

            if ($gluk eq 'sux')
            {
                print "$msg{'cannot_open'} $conf_stc_path/profiles/$usver.profile: $!";
                logmsg (__FILE__." line ".__LINE__.":[ERROR] Cannot create user profile for $usver in '$conf_stc_path/profiles/$usver.profile': $!");
            }
#            printf prof "domain:".$query->param('domain')."\n"; #Domain Name ONLY for ntlm helpers
#            printf prof "iface:".$query->param('iface')."\n"; #Interface
#            printf prof "email:".$query->param('email')."\n"; #e-mail
#            printf prof "lname:".$query->param('lname1')."\n"; #last name
#            printf prof "fname:".$query->param('fname1')."\n"; #first name
#            printf prof "mname:".$query->param('mname1')."\n"; #middle name
#            close (prof);

            logmsg (__FILE__." line ".__LINE__.":[INFO] User $user modified user's $usver info");

            $user_ok="false";
            open pasf, "<$conf_stc_path/password" or print "$msg[502]: $!<br>";
            while (<pasf>){
            @F=split(':');
            if ($F[0] eq $usver){
                $user_ok="true";
                goto user_check_end;
            }
            }
            close (pasf);
user_check_end:
            if ($user_ok eq "true"){
            print "$msg{'user_info'} <b>$usver</b> $msg{'changed'}.<br>";
            goto form_begin;
            }
            else
            {
            print "<b class=error>$msg{'error'}</b> $msg{'error_mod_user'}";
            }

    goto l1;
}#if user_mod
# add actions end

#Grant otdel to user 
if ($grant and $admin{$user} and $grant_otd){
    my @tmpprof=undef;
    open upf, "<$conf_stc_path/profiles/${usver}.profile" or print "$msg{\"no_profile_makedef\"}<br>$conf_stc_path/profiles/${usver}.profile: $!";
    while ($stin=<upf>){
	my @tt=split(':', $stin);
	my $tkey=$tt[0];
	$tkey=~s/o//;
	$tkey=0+$tkey;
#	if (($tkey<=999) and ($tkey>=1)){next;}
	chomp ($stin);
	if ($stin) {push @tmpprof, $stin;}
#print "$stin<br>";
    }
    close upf;
    push @tmpprof, "o$grant_otd:";
    sleep 1;
    open upf, ">$conf_stc_path/profiles/${usver}.profile" or print "Can't open for writing<br>$conf_stc_path/profiles/${usver}.profile: $!";
    foreach (@tmpprof){
	my $tt=$_;
	if (!$tt){next;}
	printf upf "$tt\n";
    }#foreach
    close upf;
#print "O: $grant_otd granted!<br>";
}# if grant

form_begin:

&get_profile($usver);
&get_bosses;

print "<br>
<a href=user.cgi>$msg{'to_user_list'}</a>
<br><br>
<table width=300 align=center border=0>
   <form action=user_mod.cgi method=POST>
   <input type=hidden name=user value=\"$usver\">
   <input type=hidden name=otdel value=$param_otdel>
   <input type=hidden name=action value=\"add\">

     <tr>
        <td style=\"text-align:right;\">$msg[12]:</td>
        <td>".$usver."</td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[13]:</td>
        <td><input type=text name=lname size=20 value=\"".$user_profile{"${usver}_lname"}."\"></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[14]:</td>
        <td><input type=text name=fname size=20 value=\"".$user_profile{"${usver}_fname"}."\"></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[15]:</td>
        <td><input type=text name=mname size=20 value=\"".$user_profile{"${usver}_mname"}."\"></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[16]:</td>
        <td><select name=otd>";
foreach (@otdels)
          {
          $name="";
          $name=$otdel_prn{$_};
          if ($name eq "") {$name="# $_";}
          print "<option value=\"$_\"";
            if ($user_profile{"${usver}_otdel"} eq $_) {print " selected";}
          print ">$name</option>";
          }
print "</select></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[17]:</td>
        <td><input type=text name=lim size=20 value=\"".($user_profile{"${usver}_limit"}/$conf_mega_byte)."\"></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\"><input type=checkbox name=\"NL\" value='on'";
      if ($user_profile{"${usver}_limit"} eq 'NL') {print " checked";}
print "></td>
        <td>$msg[18]</td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[19]:</td>
        <td><input type=password name=newpasswd size=20></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[20]:</td>
        <td><input type=password name=repasswd size=20></td>
     </tr>

     <tr>
        <td  style=\"text-align:right;\">$msg[152]:</td>
        <td><input type=text name=domain size=20 value=\"".$user_profile{"${usver}_domain"}."\"></td>
     </tr>
     <tr><td></td><td><b class=error>* </b><font size=1>$msg{'msg_domain'}</font></td></tr>

     <tr>
        <td style=\"text-align:right;\">$msg[154]:</td>
        <td><input type=text name=email size=20 value=\"".$user_profile{"${usver}_email"}."\"></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[153]:</td>
        ", td(popup_menu(-name=>'iface', -values=>\@theme, -default=>$user_profile{"${usver}_iface"})),"
     </tr>

     <tr>
        <td colspan=2 style=\"text-align:center;\">
	<input type=hidden name=back_url value=$back_url>
        <input type=submit value=\"$msg[26]\" name=\"mod_user\">
        &nbsp; &nbsp; &nbsp;
        <input type=reset value=\"$msg[27]\">
        </td>
     </tr>

   </form>
</table>";

    print "<br><br>";

#<grant otdel>
if ($admin{$user}){
print "
    <form action=user_mod.cgi method=POST>
    <input type=hidden name=user value=\"$usver\">
    <input type=hidden name=otdel value=$param_otdel>
    <input type=hidden name=back_url value=$back_url>
";

    print "<table width=50%>";
    print "<tr><td style=\"text-align:left;\">";
    print "$msg{\"grant_otdel\"}:</td>";
    print "<td style=\"text-align:right;\">";
    print "<select name=grant_otd>";
    my $freeotdel=undef;
    foreach (@otdels){
	if ($bosshash{"${usver}_o$_"}){next;}
	$freeotdel='windows_must_die';
        $name="";
        $name=$otdel_prn{$_};
        if ($name eq "") {$name="# $_";}
        print "<option value=\"$_\"";
#       if ($user_profile{"${usver}_otdel"} eq $_) {print " selected";}
        print ">$name</option>";
    }#for
    if (!$freeotdel){print "<option value=\"\">$msg{empty_otdel}</option>"};
    print "</select></td></tr>";

    print "<tr><td colspan=2 style=\"text-align:center;\">";
    if ($freeotdel){print "<input type=submit name=\"grant\" value=\"$msg{\"grant_button\"}\">";}
    print "</td></tr>";
    print "</table>";
    print "</form>";
    print "<br><br>";
}
#</grant otdel>
    print "<table width=50%>";

#    print "<form action=\"update_utr.cgi\" method=\"POST\">";
#    print "<input type=hidden name=start_user value=$usver>";
#    print "<input type=hidden name=otdel value=$otdel>";
#    print "<input type=hidden name=back_url value=\"user_mod.cgi\">";
#    print "<input type=hidden name=back_url1 value=\"$back_url\">";
#    print "<tr>";
#    print "<td align=center><input type=submit value=\"$msg[105]\"></td>";
#    print "</tr>";
#    print "</form>";

#    print "<form action=\"supasswd.cgi\" method=\"POST\">";
#    print "<input type=hidden name=start_user value=$usver>";
#    print "<input type=hidden name=back_url value=\"user_mod.cgi\">";
#    print "<input type=hidden name=back_url1 value=\"$back_url\">";
#    print "<input type=hidden name=otdel value=\"$otdel\">";
#    print "<tr>";
#    print "<td align=center><input type=submit value=\"$msg[106]\"></td>";
#    print "</tr>";
#    print "</form>";

    print "<form action=\"st.cgi\" method=\"POST\">";
    print "<input type=hidden name=start_user value=$usver>";
    print "<input type=hidden name=otdel value=$param_otdel>";
    print "<input type=hidden name=back_url value=\"user_mod.cgi\">";
    print "<input type=hidden name=back_url1 value=\"$back_url\">";
#    print "<input type=hidden name=back_otd value=\"$otdel\">";
    print "<tr text_align=center>";
    print "<td align=center><input type=submit value=\"$msg[107]\"></td>";
    print "</tr>";
    print "</form>";

    print "<form action=\"mess_send.cgi\" method=\"POST\">";
    print "<input type=hidden name=start_user value=$usver>";
    print "<input type=hidden name=back_url value=\"user_mod.cgi\">";
    print "<input type=hidden name=back_url1 value=\"$back_url\">";
    print "<input type=hidden name=back_otd value=\"$otdel\">";
    print "<tr text_align=center>";
    print "<td align=center><input type=submit value=\"$msg[108]\"></td>";
    print "</tr>";
    print "</form>";
    print "</table>";

    print "<br><br>";


#    print "<table width=50%>";
#    print "<form action=\"user.cgi\" method=\"POST\">";
#    print "<input type=hidden name=del value=$usver>";
#    print "<input type=hidden name=back_url value=\"profile.cgi\">";
#    print "<input type=hidden name=back_url1 value=\"$back_url\">";
#    print "<input type=hidden name=back_otd value=\"$back_otd\">";
#    print "<tr tex_align=center>";
#    print "<td align=center><input type=submit value=\"$msg[109] $usver\"></td>";
#    print "</tr>";
#    print "</form>";

#    print "</table>";

print "<a href=\"user.cgi?del=$usver\" onClick=\"javascript:return SubmitDelete('$msg{'submit_delete'} $usver?');\"><u>$msg{'delete'} <b>$usver</b></u></a><br>";

#print "BU: $back_url, U: $user, O: $otdel<br>";

    print "<br><br>";

    print "<form action=\"$back_url\" method=\"POST\">";
    print "<input type=hidden name=otdel value=$param_otdel>";
    print "<input type=submit value=\"$msg[53]\">";
    print "</form>";
print "</center>";

l1:


&load_footer;
