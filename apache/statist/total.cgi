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

$ucount=0;
$fs=1;
$scode="ok";
require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("Total statistic");
&init_stc;
print $set_pointer;

$query=new CGI;
$param_otdel=undef;
$totalstat=undef;
$param_otdel=$query->param("otdel");

#Checking if such otdel exists
if ($param_otdel and !$o_exist{$param_otdel}){
    print "<center><br>$msg[501]<br></center>";
    goto the_end;
}

#Checking user's access for this otdel
$cko=chk_boss_otdel($param_otdel);
#print "U=$user O=$param_otdel BOSS=$cko<br>";
if(chk_boss_otdel($param_otdel) ne 'ok'){
    print "<p align=center>$msg[5]</p><br>";
    goto the_end;
}

open blockfil, "$conf_stc_path/blocked.users" or print "$msg[2] $conf_stc_path/blocked.users";
while (<blockfil>){
    @F=split(' ');
    if ($F[0] eq '') {next;}
    $blocked{$F[0]}="TRUE";
}
close (blockfil);

if ($query->param("otdel") ne '') {@otdels=($query->param("otdel"));}

foreach (@otdels) {

    $f="$conf_stc_path/o$_.users";
    if (-r $f)
	{
	open fil, "<$f" or die "$!";
	while (<fil>)
	    {
	    @F=split ' ';
	    if ($F[0] ne '')
		{
		$user{$ucount}=$F[0];
		$traffic{$user{$ucount}} = 0;
#	        $tmp=$user{$ucount};
		&get_profile($user{$ucount});
		$ucount++;
		}
	    }#while ff
	close (fil);
	}
  }#foreach

print "<p align=center>$msg[111] <b>$user</b>!</p>";

#Let's get everybody's traffic
if (!get_all_traffic()){goto the_end;}

$err="ok";
    if (!-r "$conf_stc_path/traffic.users")
	{
	logmsg (__FILE__." line ".__LINE__.":[ERROR] Cannot open '$conf_stc_path/traffic.users': $!");
	print "$msg{'cannot_open'} '$conf_stc_path/traffic.users': $!";
        goto the_end;
	}
    open(LOG1,"<$conf_stc_path/traffic.users")  or die "$!";
    while(<LOG1>){
        my ($cur_user, $cur_limit)=split(' ');
        $maxtraffic{$cur_user} = $cur_limit;
    }#while LOG1
    close(LOG1);

    $tm=localtime;
    print "<p align=center>";
    $tu=$ucount;
    print "$msg[41]: $tu<br>";

#print "TT=$totaltraffic<br>";

#    $tpr=$totaltraffic/$conf_mega_byte;
#    printf ("<b>$msg[42]:</b> %.06f $msg[94]<br>", $tpr);
    if ($param_otdel){
        $prq=get_otdel_reserv($param_otdel)/$conf_mega_byte;
	printf ("$msg[87]: %.06f $msg[94]<br>",$prq);
    }

    print "$msg[116] ";
    print ("$tm");
    print "<br><br>";

if ($query->param("otdel") ne '')
    {print "${msg{'otdel_traffic'}}: <b>", $otdel_prn{$query->param("otdel")}, "</b><br><br>";}


    print "<table border=1 cellspacing=0 width=100%>";
    print "<tr align=center>";

    print "<tr><th>$msg[21]</th><th>$msg[134]</th>";
    if (!$param_otdel){
	print "<th>$msg[16]</th>";
    }

    print "<th>$msg[119]</th>
           <th>$msg[120]</th>
           <th>$msg[121]</th>
           <th>$msg[88]</th></tr>";
$TOTAL_traffic=$TOTAL_left=$TOTAL_limit=0;
    foreach $cur_user (sort {$traffic{$b}<=>$traffic{$a}} keys %traffic)
    {
	if ($user_profile{"${user}_otdel"} eq ''){next;}
	if (($user_profile{"${cur_user}_otdel"} != $param_otdel) and $param_otdel){next;}
        $left=$maxtraffic{$cur_user}-$traffic{$cur_user};
        $traffic{$cur_user}=$traffic{$cur_user}/$conf_mega_byte;
	if ($maxtraffic{$cur_user} eq "NL"){
	    $maxtraffic{$cur_user}="nolimit";
	}
	else{
            $maxtraffic{$cur_user}=$maxtraffic{$cur_user}/$conf_mega_byte;
	}
	if ($maxtraffic{$cur_user} eq "nolimit"){
	    $left="nolimit";
	}
        $left=$left/$conf_mega_byte;
	print "<tr>";
	print "<tr align=center $apply_pointer>";
        print "<td><font size=$fs><a href=\"user_mod.cgi?user=$cur_user&back_url=total.cgi&otdel=$param_otdel\"><b>$cur_user</b></a><br>";
	if ($admin{$user}){
	if ($blocked{$cur_user} eq "TRUE"){
	    print "<font size=$fs><a href=\"access_u.cgi?user=$cur_user&action=unblock&back_url=total.cgi&otdel=$param_otdel\">$msg[135]</a></td>";
	}
	else {
	    print "<a href=\"access_u.cgi?user=$cur_user&action=block&back_url=total.cgi&otdel=$param_otdel\">$msg[136]</a></td>";
	}
	}#if admin
        print "<td>&nbsp;<font size=$fs>".$user_profile{"${cur_user}_lname"}." ".$user_profile{"${cur_user}_fname"}." ".$user_profile{"${cur_user}_mname"}."</td>";

        if (!$param_otdel){
	    print "<td><font size=$fs>".$otdel_prn{$user_profile{"${cur_user}_otdel"}}."</td>";
	}
        printf ("<td align=right><font size=$fs>%.06f</td>", $traffic{$cur_user});
        if ($maxtraffic{$cur_user} eq "nolimit"){
	    printf ("<td align=right><font color=$web_green_font size=$fs>nolimit</font></td>");
	    printf ("<td align=right><font color=$web_green_font size=$fs>nolimit</font></td>");
	}
	else{
	    printf ("<td align=right><font size=$fs>%.03f", $maxtraffic{$cur_user});
	    if ($param_otdel){
		$ref="otd_ctrl.cgi?user=$cur_user&otd=$param_otdel";
		print "<br><font size=$fs><a href=$ref>$msg[142]</a>";
	    }
	    print "</td>";
	    printf ("<td align=right><font size=$fs>%.06f</td>", $left);
	}
	print "<td>";
	if($left<=0){
	    if ($maxtraffic{$cur_user} eq "nolimit"){
		print "<font color=$web_green_font size=$fs>$msg[137]</font>";
	    }
	    else{
		print "<b><font color=$web_red_font size=$fs>$msg[138]</font></b>";
	    }
	}
	else{
	    print "<font color=$web_green_font size=$fs>$msg[137]</font>";
    	}
	if ($blocked{$cur_user} eq "TRUE"){
	    print "<br><font color=$web_red_font size=$fs>$msg[139]</font>";
	}
	print "</td></tr>";
    $TOTAL_traffic+=$traffic{$cur_user};
    $TOTAL_left+=$left;
    }#foreach

    print "<tr><td align=right>
           <font size=$fs><b>$msg{'total'}:</b></td>";
    if (!$param_otdel){print "<td>&nbsp;</td>";}
    printf ("<td>&nbsp;</td>
           <td align=right><b>%.02f</b></td>
           <td>&nbsp;</td>
           <td align=right><b>%.02f</b></td>
           <td>&nbsp;</td></tr>", $TOTAL_traffic, $TOTAL_left);
    print "</table></p>";

    if (adv_boss_chk($user, $param_otdel, 'user_add')){
        print "<table width=50%>";
        print "<form action=\"adduser.cgi\" method=\"POST\">";
        print "<input type=hidden name=start_otd value=$param_otdel>";
        print "<input type=hidden name=back_url value=\"total.cgi\">";
        print "<input type=hidden name=back_url1 value=\"$back_url\">";
        print "<tr>";
        print "<td align=center><input type=submit value=\"$msg[28]\"></td>";
        print "</tr>";
	print "</form>";
	print "</table>";
    }

the_end:
&load_footer;
