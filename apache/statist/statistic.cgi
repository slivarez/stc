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

#$user=$ENV{'REMOTE_USER'};
#print "Content-type: text/html; charset=windows-1251\n\n";
#print "<TITLE>Blocked user!</TITLE>";
$scode="ok";
require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("Your statistic");
&init_stc;

print "<p align=center>$msg[111] <b>$user</b>!</p>";

#Let's get out traffic info
get_traffic($user);

open(LOG1,"$conf_stc_path/traffic.users") || print "$msg[2] $conf_stc_path/traffic.users: $!<br>";
while(<LOG1>){
    @F1= split(' ');
    $user1=$F1[0];
    if($user1 ne $user){next;}
    $maxtraffic{$user1} = $F1[1];
}#while LOG1
close(LOG1);
if ($maxtraffic{$user} eq "NL"){
    $maxtraffic{$user}="nolimit";
}
else{
        $maxtraffic{$user}=$maxtraffic{$user}/$conf_mega_byte;
}

if ($maxtraffic{$user} eq "nolimit"){
    $left="nolimit";
}
else {
    $left=$maxtraffic{$user}*$conf_mega_byte-$traffic{$user};
    $left=$left/$conf_mega_byte;
}
$traffic{$user}=$traffic{$user}/$conf_mega_byte;


    $tm=localtime;

print "<p align=center>";

    print "$msg[116]: ";
    print ("$tm");
    print "<br><br>";

print "<table align=center width=50%>";
printf ("<tr><td>$msg[119]</td><td style=\"text-align:right;\">%.06f</td><td>Mb</td></tr>", $traffic{$user});

if ($maxtraffic{$user} eq "nolimit"){
    print "<tr><td>$msg[120]</td><td colspan=2 style=\"text-align:right;\"><font color=$web_green_font>UNLIMITED</font></td></tr>";
}
else{
    printf ("<tr><td>$msg[120]</td><td style=\"text-align:right;\">%.06f</td><td>Mb</td></tr>", $maxtraffic{$user});
}
if ($maxtraffic{$user} eq "nolimit"){
    print "<tr><td>$msg[121]</td><td colspan=2 style=\"text-align:right;\"><font color=$web_green_font>UNLIMITED</font></td></tr>";
}
else{
    printf ("<tr><td>$msg[121]</td><td style=\"text-align:right;\">%.06f</td><td>Mb</td></tr>", $left);
}
print "</table>";

#Web Messages
if (($conf_web_messages eq 'admin') or ($conf_web_messages eq 'all')){
    open lastfil, "<$conf_stc_path/messages/users/$user/lastmess.dat";
    while(<lastfil>){
	@F=split (' ');
	if ($F[0] ne '') {$last_mess=$F[0];}
    }
    close (lastfil);

    open messfil, "<$conf_stc_path/messages/users/$user/messages.dat";
    while(<messfil>){
	@F=split ('#');
	if ($F[0] eq "ID"){
	    $real_last_mess=$F[1];
	}
    }
    close (messfil);

    if ($last_mess < $real_last_mess){
	print "<center><font color=$web_red_font><b>$msg[127]</b></font></center><br>";
    }

    print "<form action=\"mess_view.cgi\" method=\"POST\">";
    print "<center><input type=submit value=\"$msg[128]\"></center>";
    print "</form>";
}
#endof Web messages

#INS#
# do not remove INS!

#Admin block
if($admin{$user} eq 'yep'){
    print "<hr><center>";

#    print "<br><a href='admin.cgi'>$msg[124]</a><br><br>";

    print "<BR><a href='total.cgi'>$msg[125]</a><BR>";
    print "<BR><a href='st.cgi'>$msg[126]</a><BR><BR></center>";
#INS#
# do not remove INS!
}#if
#EO Admin block
print "</p>";


#Boss block
print "<p align=center>";
    if(($user_boss{$user} eq "yep") or ($admin{$user} eq 'yep'))
    {
#print "You are boss - $user_boss{$user}<br>";
#INS#
# do not remove INS!
	print "<table border=1 align=center>";
	foreach $otdel (@otdels) {
    	    if ($otdel_prn{$otdel} ne ''){
		$protd="$otdel_prn{$otdel}";
	    }
	    else{
		$protd="$msg[16] $otdel";
	    }
	    $ref="<br><a href='total.cgi?otdel=$otdel'>";
	    $ref=$ref."$msg[129]</a><br>";

	    print "<tr>";

	    print "<td style=\"text-align:center;vertical-align:middle\">";
	    print "$protd";
	    print "</td>";

	    print "<td>";
	    print "$ref";
	    print "</td>";

	    $ref="<a href='view.cgi?page=daily/o$otdel/index.html'>$msg[130] $msg[131]</a>";

	    print "<td>";
	    print "$ref";
	    $ref="<br><a href='view.cgi?page=weekly/o$otdel/index.html'>$msg[130] $msg[132]</a>";
	    print "$ref";
	    $ref="<br><a href='view.cgi?page=monthly/o$otdel/index.html'>$msg[130] $msg[133]</a>";
	    print "$ref";

	    print "</td>";

	    print "</tr>";
        }#for otdel
	print "</table>";
    }
print "</p>";
#EO Boss block

&load_footer;
