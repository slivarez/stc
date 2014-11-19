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
$scode="ok";
$font="<font size=1>";
$fonte="</font>";
require "./init_stc.pl";
&get_conf;
&get_profile("$user");
&load_header($msg{'page_user'});
&init_stc;
print "$jf_SubmitDelete";

    if ($user_boss{$user} ne 'yep' && $admin{$user} ne 'yep')
        {
         logmsg (__FILE__." line ".__LINE__.":[WARNING] user $user tried to access users page (user.cgi). Access denied!");
         print "<b class=error>$msg{'error'}</b> $msg{'access_denied'}";
         goto the_end;
        }

#begin userdel
$query=new CGI;
if ($query->param('del') ne '')
    {
    $tmp=$query->param('del');
    &get_profile($tmp);
$to=$user_profile{"${tmp}_otdel"};
#$ttt=adv_boss_chk($user, $to, 'user_rm');
#print "TTT=$ttt - $tmp - $to <br>";


#    if (chk_boss_otdel($user_profile{"${tmp}_otdel"}) ne 'ok')
    if (!adv_boss_chk($user, $user_profile{"${tmp}_otdel"}, 'user_rm'))
        {
         logmsg (__FILE__." line ".__LINE__.":[WARNING] user $user tried to delete user $tmp. Access denied!");
         print "<b class=error>$msg{'error'}</b> $msg{'access_denied'}";
         goto userlist;
        }
    if ($u_exist{"\L$tmp"} ne "TRUE")
        {
        logmsg (__FILE__." line ".__LINE__.":[WARNING] user $user tried to delete user $tmp that does not exists.");
        print "<b class=error>$msg{'error'}</b> $msg{'no_such_user'}<br>";
        goto userlist;
        }

    &del_from_file ("${conf_stc_path}/password", $tmp);
    &del_from_file ("${conf_stc_path}/password.digest", $tmp);
    &del_from_file ("${conf_stc_path}/o".$user_profile{"${tmp}_otdel"}.".users", $tmp);
    &del_from_file ("${conf_stc_path}/traffic.users", $tmp);

    unlink("$conf_stc_path/messages/users/$tmp/messages.dat");
    unlink("$conf_stc_path/messages/users/$tmp/lastmess.dat");
    unlink("$conf_stc_path/profiles/$tmp.profile");
    rmdir ("$conf_stc_path/messages/users/$tmp");

    logmsg (__FILE__." line ".__LINE__.":[INFO] User $tmp was deleted by '$user'");
    print "<center>$msg{'user'} <b>$tmp</b> $msg{'was_deleted'}</center><br>";

    }
#end userdel

#print "<a href='adduser'>$msg[28]</a><br><br>";
#print "<a href='supasswd'>$msg[29]</a><br><br>";
#print "<a href='update_utr'>$msg[30]</a><br><br>";
#print "<br><br>";

userlist:

print $set_pointer;

@otdels = sort (@otdels);
foreach (@otdels)
{
    $otdel=$_;
    if (!$otdel){next;}
    $otdel+=0;
    if (chk_boss_otdel($otdel) ne 'ok'){next;}
    $gluk='no';
    open OTDFILE, "<$conf_stc_path/o$otdel.users" or $gluk='yes';
    if ($gluk eq 'yes')
        {
         logmsg (__FILE__." line ".__LINE__.":[ERROR] Unable to read department users file '$conf_stc_path/o$otdel.users'");
         print "<b class=error>$msg[7]!</b> $msg[501] ($otdel)";
	 next;
         }
    print "<br><br><b><u>$msg[16]:</u></b> $otdel_prn{$otdel} <br><br>";
#$kkk=@user_boss;
#for ($ii=0; $ii<$kkk;++$ii){
#    print "UB $ii = $user_boss[$ii]<br>";
#}
    print "<table border=1 cellspacing=0 width=\"99%\">
           <tr>
             <th align=center>$msg{'login'}&nbsp;</th>
             <th align=center>$msg[13] $msg[14] $msg[15]</th>
             <th align=center>$msg[16]</th>
             <th align=center>$msg{'limit'}</th>
             <th align=center>&nbsp;</th>
             <th align=center>&nbsp;</th>
           </tr>
           ";
    while ($line1=<OTDFILE>)
         {
          chomp($line1);
	  @tmpline=split(' ', $line1);
	  $line=$tmpline[0];
          &get_profile($line);
          $tmp=$user_profile{"${line}_limit"};
          if ($tmp ne 'NL') {$tmp=($tmp/$conf_mega_byte)."M";}
          print "<tr $apply_pointer>
                  <td><a href=\"user_mod.cgi?user=$line&back_url=user.cgi\">$line</a></td>
                  <td><a href=\"user_mod.cgi?user=$line&back_url=user.cgi\">".$font.$user_profile{"${line}_lname"}." ".$user_profile{"${line}_fname"}." ".$user_profile{"${line}_mname"}."$fonte</a>&nbsp;</td>
                  <td>".$otdel_prn{$otdel}."&nbsp;</td>
                  <td>".$tmp."&nbsp;</td>
		";
            if ($user_profile{"${line}_email"}){
	        print "<td align=center><a href=mailto:".$user_profile{"${line}_email"}.">$msg{'mailto'}</a></td>";
	    }
	    else{
		print "<td align=center>$msg{'mailto'}</a></td>";
	    }            
	    print"<td align=center><a href=\"user.cgi?del=$line\" onClick=\"javascript:return SubmitDelete('$msg{'submit_delete'} $line?');\">$msg{'delete'}</a></td>
                 </tr>";
         }
    print "</table>";
    close (OTDFILE);
    if (adv_boss_chk($user, $otdel, 'user_add')){
#print "CO= $otdel<br>";
        print "<table width=50%>";
        print "<form action=\"adduser.cgi\" method=\"POST\">";
        print "<input type=hidden name=start_otd value=$otdel>";
        print "<input type=hidden name=back_url value=\"user.cgi\">";
        print "<input type=hidden name=back_otd value=\"$otdel\">";
        print "<tr>";
        print "<td align=center><input type=submit value=\"$msg[28]\"></td>";
        print "</tr>";
	print "</form>";
	print "</table>";
    }
}#foreach

$otdel=$line=undef;
@F=undef;

the_end:
&load_footer();



