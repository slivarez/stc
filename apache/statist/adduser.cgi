#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru
#mod by Sirota S.S. E-mail:brahma@ua.fm
$bigsp=6;
$smallsp=3;

$conf_mega_byte=1000000;
$language="rus-1251";

use Apache::Htpasswd;
$scode="ok";
require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("Add new user page");
&init_stc;

$otdel=undef;
$query=new CGI;

$start_otd=$query->param(start_otd);
$back_url=$query->param(back_url);
$back_otd=$query->param(back_otd);
if (!$back_otd){$back_otd=$start_otd;}
# add actions
$usver = clean($query->param(user1), '\ ');
$usver = "\L$usver";
$name = clean($query->param(name1), '\ ');
$lname = clean($query->param(lname1), '\ ');
$oname = clean($query->param(oname1), '\ ');
$action=$query->param(action);
$NL=$query->param(NL);
$domain = clean($query->param(domain));
$iface=$query->param(iface);
$email = $query->param(email);
$email =~ s/\<|\>|\:|\"|\'|\`|\ //ig;
$add_user=$query->param(add_user);
$otdel=$query->param(otd);
$otdel =~ s/\D+//ig;
$otdel=0+$otdel;
$start_otd=0+$start_otd;

#DEBUG OUTPUT
#print "!!! O=$otdel SO=$start_otd BO=$back_otd;<br>";
print "<center>";

#Security check
if (!safe_url($back_url, 'adduser.cgi')){goto l1;}
#end of security check

if($add_user and $otdel){$tmp_otd=$otdel;}
else {$tmp_otd=$start_otd;}

if (adv_boss_chk($user, $tmp_otd, 'user_add')){
  $err=0;
  opendir(STCETC, $conf_stc_path) or $err=1;
  if ($err eq 1)
  {
    print "<font color=#BB0000>$msg[2000]</font> $msg[2008] $conf_stc_path: $!"; # Открываем папку stc/etc/ и будем щас юзверей и отделы выдирать :)
    goto the_end;
  }

  @otdels=();
    foreach (readdir(STCETC))
        { # просматриваем папку stc/etc/
        if ($_ =~ /^o[0-9]{1,3}\.users$/) # Если увидели файл типа "o###.users" - который является списком юзверей отдела - парсим его
            {
            $otdel1=$_;
            $otdel1 =~ s/^o([0-9]{1,3})\.users$/$1/; # из названия файла получаем название отдела
             push @otdels, $otdel1; # вставляем в массив отделов текущий номер
#DEBUG
#print "oo=$otdel1<br>";
            }
        }
   closedir(STCETC); # закрываем папку stc/etc/

open oaf, "<$conf_stc_path/allign.otdel" or print "$msg[2] $conf_stc_path/allign.otdel: $!<br>";
while (<oaf>){
    @F=split('\n');
    $k=@F;
    @name= split(':',$F[0]);

    $otdel_prn{$name[0]}=$name[1];
}
close (oaf);

print "<b>$msg[11]</b><br><br>";

if ($add_user)
    {
        #Security check
	if (!safe_url($usver, 'adduser.cgi')){goto l1;}
        #end of security check

        if ($action ne "add"){goto l1;}
        
print "Adding user $usver to otdel $otdel<br>";
        if (($otdel<1) or ($otdel>999)){
            $tm=localtime;

            print "$msg[9]<br>";
            open log_f, ">>$conf_stc_path/users.log";
            printf log_f "!A $tm $user adduser.cgi OTD $o\n";
            close(log_f);
            goto l1;
        }

        $limit=$query->param(lim);
	$limit =~ s/\D+//ig;
	$limit = $limit * $conf_mega_byte;
        if ($NL eq 'on'){$limit="NL";}
        $newpass=$query->param(newpasswd);
        $repass=$query->param(repasswd);

        if ($u_exist{"\L$usver"} ne "TRUE"){
        if(($newpass ne '') and ($newpass eq $repass)){
            $file_otd="$conf_stc_path/o${otdel}.users";
            $err="ok";

            open ftest, "<$file_otd" or $err="gluk";
            close (ftest);
            if ($err ne "gluk"){
                open f1, ">>$file_otd" or $err="gluk";
                printf f1 $usver;
		printf f1 "\n";
                close (f1);
            }
            if ($err ne "gluk"){
            $pass_path="$conf_stc_path/password";
            $ap_htpass=new Apache::Htpasswd($pass_path);
            $ap_htpass->htpasswd($usver, $newpass);
#                system ("$conf_stc_path/htpasswd -b $conf_stc_path/password $usver $newpass");

            open dpf, ">>$conf_stc_path/password.digest";
            printf dpf "$usver:$newpass\n";
            close (dpf);

            open t1, ">>$conf_stc_path/traffic.users";
                printf t1 $usver;
                printf t1 " ";
                printf t1 $limit;
                printf t1 "\n";
                close (t1);

            open prof, ">$conf_stc_path/profiles/$usver.profile" or print "$msg[510] $conf_stc_path/profiles/$usver.profile: $!";
            printf prof "domain:$domain\n"; #Domain Name ONLY for ntlm helpers
            printf prof "iface:$iface\n"; #Interface
            printf prof "email:$email\n"; #e-mail
            printf prof "lname:$lname\n"; #last name
            printf prof "fname:$name\n"; #first name
            printf prof "mname:$oname\n"; #middle name
            close (prof);

            $tm=localtime;

            open log_f, ">>$conf_stc_path/users.log";
            printf log_f "AD $tm $usver $otdel $user\n";
            close(log_f);

            }#if err
            else {
             printf "$msg[501]<br>";
            }
            $user_ok="false";
            open pasf, "<$conf_stc_path/password" or print "$msg[502]<br>";
            while (<pasf>){
            @F=split(':');
            if ($F[0] eq $usver){
                $user_ok="true";
            }
            }
            close (pasf);
            if ($user_ok eq "true"){
            print "$msg[21] <b>$usver</b> $msg[22].";
            }
        }#if newpass and repass
#TODO: syuda vstavit' mesagu pro pustoj password
	else {print "PASSWORD EMPTY/MISSMATCH ERROR<br>"};
        }#if $u_exist
        else{
            print "$msg[23] <b>$usver</b> $msg[24]<br>";
        }
        if($newpass ne $repass){
            print "$msg[25]<br>";
        }
    goto l1;
    }
# add actions end


print "<table width=300 align=center border=0>
   <form action=adduser.cgi method=POST>
   <input type=hidden name=back_url value=$back_url>
   <input type=hidden name=back_otd value=$back_otd>
   <input type=hidden name=action value=\"add\">

     <tr>
        <td style=\"text-align:right;\">$msg[12]:</td>
        <td><input type=text name=user1 size=20></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[13]:</td>
        <td><input type=text name=lname1 size=20></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[14]:</td>
        <td><input type=text name=name1 size=20></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[15]:</td>
        <td><input type=text name=oname1 size=20></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[16]:</td>
        <td><select name=otd>";
if($admin{$user}){
    foreach (@otdels)
    {


          $name="";
          $name=$otdel_prn{$_};
          if ($name eq "") {$name="# $_";}
          print "<option value=\"$_\"";
            if ($start_otd eq $_) {print " selected";}
          print ">$name</option>";
    }

}#if admin
else{
    print "<option value=\"$start_otd\" selected>$otdel_prn{$start_otd}</option>";
}#else
print "</select></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[17]:</td>
        <td><input type=text name=lim size=20></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\"><input type=checkbox name=\"NL\"></td>
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
        <td><input type=text name=domain size=20></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[154]:</td>
        <td><input type=text name=email size=20></td>
     </tr>

     <tr>
        <td style=\"text-align:right;\">$msg[153]:</td>
        ", td(popup_menu(-name=>'iface', -values=>\@theme, -default=>$conf_default_interface)),"
     </tr>

     <tr>
        <td colspan=2 style=\"text-align:center;\">
        <input type=submit value=\"$msg[26]\" name=\"add_user\">
        &nbsp; &nbsp; &nbsp;
        <input type=reset value=\"$msg[27]\">
        </td>
     </tr>

   </form>
</table>";

}
else{
    print "$msg[5]<br>";
}
l1:

    print "<table>";
    print "<form action=\"$back_url\" method=\"POST\">";
    print "<input type=hidden name=otdel value=$back_otd>";
    print "<tr tex_align=center>";
    print "<td align=center><input type=submit value=\"$msg{back}\"></td>";
    print "</tr>";
    print "</form>";
    print "</table>";

print "</center>";

&load_footer;
