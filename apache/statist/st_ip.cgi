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
require "./init_stc.pl";
&get_conf;
&get_profile("$user");
&load_header("Full statistic +IP");
&init_stc;

$query=new CGI;

$mon=(localtime)[4]+1;

if ($query->param('s_month') eq '') {
    $mm=(localtime)[4]+1;
}
else {
    $mm=$query->param('s_month');
}
$start_usver=$query->param(start_user);
$usver=$query->param(user1);
$selected_user=($usver ne ''?$usver:$start_usver);
$o=$query->param(otdel);
$back_url=$query->param('back_url');
$back_url1=$query->param('back_url1');
$back_url2=$query->param('back_url2');

if (!safe_url($back_url, 'st_ip.cgi')){goto l1;}

##################### Form selection User and Month  #####################
print "<form method=POST>";
print "<center>";

if($admin{$user} ne 'yep')
    {
    logmsg (__FILE__." line ".__LINE__.":[WARNING] user '$user' tried to access full statistic page.");
    print "$msg[5]<br>";
    goto l1;
    }

print "<b>$msg[115]</b><br><br>
        <table width=50%>";
    if ($selected_user ne '' and $user_pass_list{$selected_user} ne "TRUE") 
	{
	    print "</tr><th nowrap colspan=2 class=stat>WARNING!!! user <font color=yellow>$selected_user</font> is failed!</th></tr>";
	}
#print "<td><input type=text name=user1 size=20 value=\"".$start_usver."\"></td>";

    print "<tr>
            <td>$msg[12]:</td>
            <td><select name=user1>
                 <option value=''>[Selected user]</option>\n";
        foreach $us (sort keys %user_pass_list)
            {
            if ($user_pass_list{$us} ne "TRUE") {next;}
            print "<option value=$us";
            if ($us eq $selected_user) {print " selected";}
            print ">$us</option>\n";
            }
        print "</select></td>";


#print "<tr>";
#print "<td>$msg[16]:</td>";
#print "<td><input type=text name=otd size=20 value=\"$o\"></td>";
#print "</tr>";

    print "<tr>
	<td>$msg[32]:</td>
	<td><select name=s_month>";
	for ($i=1; $i<=12; $i++)
    	    {
    	    print "<option value=$i";
    	    if ($mm eq $i) {print " selected";}
    	    print ">".$msg[(400+$i)]."</option>\n";
    	    }
	    print "</select>
	</td>
    </tr>";

    print "<input type=hidden name=start_user value=\"$selected_user\">
           <input type=hidden name=otdel value=\"$o\">
           <input type=hidden name=back_url1 value=\"$back_url\">
           <input type=hidden name=back_url2 value=\"$back_url1\">
           <input type=hidden name=back_url2 value=\"$back_url2\">

    <tr align=center>
	    <td align=center><input type=submit value=\"$msg[26]\"></td>
	<td style=text-align:right><input type=reset value=\"$msg[27]\"></td>
	</tr>
    </table>
</form>";
##################### Form selection User and Month  #####################

#$usver=$query->param(user1);
#$mm=$query->param(s_month);

print "<br><br>
    <form action=\"$back_url\" method=\"POST\">
    <input type=hidden name=start_user value=\"$selected_user\">
    <input type=hidden name=otdel value=\"$o\">
    <input type=hidden name=back_url1 value=\"$back_url\">
    <input type=hidden name=back_url2 value=\"$back_url1\">
    <input type=submit value=\"$msg[53]\">
    </form>";

if ($usver ne ''){

    &get_profile($usver);

$ll_date=0;
open(LOG, "$conf_access_log.m$mm") || print "$msg[2] $conf_access_log.m$mm: $!<br>";
while(<LOG>)
    {
            ($user_name, $size,$user_ip,$skip_cache)=log_line($_);
            $traffic{$user_ip}{$skip_cache} += $size;
            $usage{$user_ip}{$site}{$skip_cache} += $size;
	    $totaltraffic{$skip_cache}+=$size;
	    if($udate>$ttm{$user_ip}) {$ttm{$user_ip}=$udate;}
    }
close(LOG);

if ($mm == $mon){
open(LOG, "$conf_access_log") || print "$msg[2] $conf_access_log: $!<br>";
while(<LOG>)
    {
            ($user_name, $size,$user_ip,$skip_cache)=log_line($_);
            $traffic{$user_ip}{$skip_cache} += $size;
            $usage{$user_ip}{$site}{$skip_cache} += $size;
	    $totaltraffic{$skip_cache}+=$size;
	    if($udate>$ttm{$user_ip}) {$ttm{$user_ip}=$udate;}
    }

close(LOG);
}

        $tm=localtime;
        print "<br>$msg[116] ";
	    print ($tm);
        print "<br>";




        foreach $SEC (sort keys (%sarg_exclude_codes)) {if ($SEC ne '') {$title_sarg.=$SEC."\n";}}
        $title_sarg=~s/\n$//;
        $conf_exclude_sites=~s/\n$//;
        if ($title_sarg ne ''){$title_sarg="&nbsp;<IMG src='/stat/warning.gif' title='$title_sarg'>";}
        if ($conf_exclude_sites ne ''){$conf_exclude_sites="&nbsp;<IMG src='/stat/warning.gif' title='$conf_exclude_sites'>";}

        $tr=$totaltraffic{"1"}/$conf_mega_byte;
        printf ("<br>$msg[33] $usver = <b>%.06f Mb</b>", $tr);


foreach $ip (sort { $traffic{$b} <=> $traffic{$a} } keys %usage)
{

        $tr=$traffic{$ip}{"1"}/$conf_mega_byte;
        $tr_0=$traffic{$ip}{"0"}/$conf_mega_byte;
        $tr_1=$traffic{$ip}{"-1"}/$conf_mega_byte;
        $tr_2=$traffic{$ip}{"-2"}/$conf_mega_byte;

        print ("<table width=280 border=0 CELLPADDING=3 CELLSPACING=2>");

        print ("<tr><td align=left colspan=5 style=\"font-size:10px;\"><br><br><b>IP:</b> $ip</td></tr>");
        print ("<tr>");
        print ("<th class=stat nowrap>E-HOST$conf_exclude_sites</th>");
        print ("<th class=stat nowrap>CACHE-HIT</th>");
        print ("<th class=stat nowrap>E-CODES$title_sarg</th>");
        print ("<th class=stat>Download</th><th class=stat nowrap>Compare vs sarg</th></tr>");
        printf("<tr><td class=row_stat>%.06f&nbsp;Mb</td><td class=row_stat>%.06f&nbsp;Mb</td><td class=row_stat>%.06f&nbsp;Mb</td><td class=row_stat><b>%.06f&nbsp;Mb</b></td><td class=row_stat>%.06f&nbsp;Mb</td></tr>",$tr_1,$tr_0,$tr_2,$tr,($tr+$tr_0));

        print ("<tr><td class=row_ip align=right colspan=5 style=\"font-size:10px;\"> <b>CACHE-HIT</b> + <b>Download</b> = <b>Compare vs sarg</b></td></tr></table><br>");

        print "<table border=0 CELLPADDING=3 CELLSPACING=2>";
        print ("<tr><td align=left colspan=2 style=\"font-size:10px;\"><b>IP:</b> $ip <b>Download:</b><br></td></tr>");
        print "<tr align=center><th class=stat>$msg[117]</th>";
        print "<th nowrap class=stat>EXCLUDE</th>";
        print "<th nowrap class=stat>CACHE</th>";
        print "<th nowrap class=stat>Download</th>";
        print "<th nowrap class=stat>vs Sarg</th></tr>";


	%ipusage = %{$usage{$ip}};
        $s_tr2=$s_tr1=$s_tr0=$s_tr=0;
        $sn_tr2=$sn_tr1=$sn_tr0=$sn_tr=0;
        $print=0;
	foreach $site (sort { $ipusage{$b}{"1"} <=> $ipusage{$a}{"1"} } keys %ipusage)
	{
            unless ($ipusage{$site}{"1"}>0)
                {
                unless ($print)
                {
                    $s_tr2/=$conf_mega_byte;
                    $s_tr1/=$conf_mega_byte;
                    $s_tr0/=$conf_mega_byte;
                    $s_tr/=$conf_mega_byte;
                    print "<tr>";
                    print "<td class=row_ip align=right>Total vs download:</td>";
                    ($s_tr1+$s_tr2)>0?printf ("<th class=stat>%.06f</th>", ($s_tr1+$s_tr2)):printf ("<th class=stat>&nbsp</th>");
                    $s_tr0>0?printf ("<th class=stat nowrap>%.06f</th>", $s_tr0):printf ("<th class=stat>&nbsp</th>");
                    $s_tr>0?printf ("<th class=stat nowrap>%.06f</th>", $s_tr):printf ("<th class=stat>&nbsp</th>");
                    printf ("<th class=stat nowrap>%.06f</th>", $s_tr+$s_tr0);
                    print "</tr>";
                    $print++;
                    print "<tr><td align=left colspan=2 style=\"font-size:10px;\"><b>IP:</b> $ip <b>No Download:</b><br></td></tr>";
                    print "<tr align=center><th class=stat>$msg[117]</th>";
                    print "<th nowrap class=stat>EXCLUDE</th>";
                    print "<th nowrap class=stat>CACHE</th>";
                    print "<th nowrap class=stat>Download</th>";
                    print "<th nowrap class=stat>vs Sarg</th></tr>";
                }
                $sn_tr2+=$ipusage{$site}{"-2"};
                $sn_tr1+=$ipusage{$site}{"-1"};
                $sn_tr0+=$ipusage{$site}{"0"};
                $sn_tr+=$ipusage{$site}{"1"};


                print "<tr>";
                print "<td class=row_ip><a href=\"http://$site\">$site</a></td>";
                $tr2=$ipusage{$site}{"-2"}/$conf_mega_byte;
                $tr1=$ipusage{$site}{"-1"}/$conf_mega_byte;
                $tr0=$ipusage{$site}{"0"}/$conf_mega_byte;
                $tr=$ipusage{$site}{"1"}/$conf_mega_byte;

                ($tr1+$tr2)>0?printf ("<td class=row_stat>%.06f</td>", ($tr1+$tr2)):printf ("<td class=row_stat>&nbsp</td>");
                $tr0>0?printf ("<td class=row_stat nowrap>%.06f</td>", $tr0):printf ("<td class=row_stat>&nbsp</td>");
                $tr>0?printf ("<td class=row_stat nowrap>%.06f</td>", $tr):printf ("<td class=row_stat>&nbsp</td>");
                $tr0>0?printf ("<td class=row_stat nowrap>%.06f</td>", $tr0):printf ("<td class=row_stat>&nbsp</td>");
                print "</tr>";
                next;
                }
            print "<tr>";
            print "<td class=row_ip><a href=\"http://$site\">$site</a></td>";
            $tr2=$ipusage{$site}{"-2"}/$conf_mega_byte;
            $tr1=$ipusage{$site}{"-1"}/$conf_mega_byte;
            $tr0=$ipusage{$site}{"0"}/$conf_mega_byte;
            $tr=$ipusage{$site}{"1"}/$conf_mega_byte;

            $s_tr2+=$ipusage{$site}{"-2"};
            $s_tr1+=$ipusage{$site}{"-1"};
            $s_tr0+=$ipusage{$site}{"0"};
            $s_tr+=$ipusage{$site}{"1"};

            ($tr1+$tr2)>0?printf ("<td class=row_stat>%.06f</td>", ($tr1+$tr2)):printf ("<td class=row_stat>&nbsp</td>");
            $tr0>0?printf ("<td class=row_stat nowrap>%.06f</td>", $tr0):printf ("<td class=row_stat>&nbsp</td>");
            $tr>0?printf ("<td class=row_stat nowrap>%.06f</td>", $tr):printf ("<td class=row_stat>&nbsp</td>");
            printf ("<td class=row_stat>%.06f</td>", $tr+$tr0);
            print "</tr>";
        }


            $sn_tr2/=$conf_mega_byte;
            $sn_tr1/=$conf_mega_byte;
            $sn_tr0/=$conf_mega_byte;
            $sn_tr/=$conf_mega_byte;


            print "<tr>";
            print "<td class=row_ip align=right>Total no download:</td>";
            ($sn_tr1+$sn_tr2)>0?printf ("<th class=stat>%.06f</th>", ($sn_tr1+$sn_tr2)):printf ("<th class=stat>&nbsp</th>");
            $sn_tr0>0?printf ("<th class=stat nowrap>%.06f</th>", $sn_tr0):printf ("<th class=stat>&nbsp</th>");
            $sn_tr>0?printf ("<th class=stat nowrap>%.06f</th>", $sn_tr):printf ("<th class=stat>&nbsp</th>");
            printf ("<th class=stat>%.06f</th>", $sn_tr+$sn_tr0);
            print "</tr>";

            print "<tr>";
            print "<td class=row_ip align=right>Total:</td>";
            ($s_tr1+$s_tr2+$sn_tr1+$sn_tr2)>0?printf ("<th class=stat>%.06f</th>", ($s_tr1+$s_tr2+$sn_tr1+$sn_tr2)):printf ("<th class=stat>&nbsp</th>");
            ($s_tr0+$sn_tr0)>0?printf ("<th class=stat nowrap>%.06f</th>", $s_tr0+$sn_tr0):printf ("<th class=stat>&nbsp</th>");
            ($s_tr+$sn_tr)>0?printf ("<th class=stat nowrap>%.06f</th>", $s_tr+$sn_tr):printf ("<th class=stat>&nbsp</th>");
            printf ("<th class=stat>%.06f</th>", $s_tr+$s_tr0+$sn_tr+$sn_tr0);
            print "</tr>";

        print "</table>";

}#foreach ip

}#if usver ne ''

l1:
print "</center>";

&load_footer;
