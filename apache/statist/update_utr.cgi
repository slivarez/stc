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

$bigsp=6;
$smallsp=3;
$language="rus-1251";
$scode="ok";

require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("User's limit control");
&init_stc;

$query=new CGI;

$back_url=$query->param(back_url);

if($admin{$user} eq 'yep'){

    print "<center>";
    print "<b>$msg{ulimit_control}</b><br><br>";

    #Security check
    if (safe_url($back_url, 'update_utr.cgi')) {

	print "<hr>";
	print "<u>$msg[147]</u><br>";
        print "<form method=\"POST\">";
	print "<input type=hidden name=back_url value=$back_url>";
        print "<table width=50%>";
        print "<table cellspacing=$bigsp>";
        print "<tr>";
        print "<td>$msg[12]:</td>";
        print "<td><input type=text name=form_user size=20 value=$start_usver></td>";
        print "</tr>";
        print "<table cellspacing=$bigsp>";
        print "<tr>";
        print "<td>$msg[17]:</td>";
        print "<td><input type=text name=lim size=20></td>";
        print "</tr>";

        print "<tr>";
        print "<td><input type=checkbox name=\"NL\"></td><td>$msg[18]</td>";
        print "</tr>";

        print "<tr align=center>";
        print "<td align=center><input type=submit name=save value=\"$msg[148]\"></td>";
        print "<td style=text-align:right><input type=reset value=\"$msg[77]\"></td>";
        print "</tr>";
        print "</table>";
        print "</form>";

        print "<hr>";
        print "<u>$msg[149]</u><br>";
        print "<form method=\"POST\">";
	print "<input type=hidden name=back_url value=$back_url>";
        print "<table width=50%>";
        print "<table cellspacing=$bigsp>";
        print "<tr>";
        print "<td>$msg[12]:</td>";
        print "<td><input type=text name=form_user size=20 value=$start_usver></td>";
        print "</tr>";
        print "<table cellspacing=$bigsp>";
        print "<tr>";
        print "<td>$msg[150]:</td>";
        print "<td><input type=text name=lim size=20></td>";
        print "</tr>";
        print "<tr align=center>";
        print "<td align=center><input type=submit name=add value=\"$msg[151]\"></td>";
        print "<td style=text-align:right><input type=reset value=\"$msg[77]\"></td>";
        print "</tr>";
        print "</table>";
        print "</form>";

        print "<hr>";

        $save=$query->param(save);
        $add=$query->param(add);

	if (($save) or ($add)) {
	    $usver=$query->param(form_user);
	    $limit=$query->param(lim) * $conf_mega_byte;
	    $NL=$query->param(NL);
	    if ($NL eq 'on'){$limit="NL";}
	    if ($u_exist{"$usver"}) {
	        my $logfile="$conf_stc_path/traffic.users";
	        my @thisarray;
	        open(LR,"$logfile") or print "$msg[2] $logfile: $!<br>";
	        flock(LR,1) or print "$msg[3] $logfile: $!<br>";
	        @thisarray = <LR>;
	        close(LR) or print "$msg[4] $logfile: $!<br>";
	        my @tmp;
	        foreach (@thisarray) {
	            @tmp = split(/ /);
	            if ($tmp[0] eq $usver) {
	        	if ($add) {
			    $limit=$limit+$tmp[1];
			}
			$tmp[1] = "$limit\n";
			$_ = join(' ', @tmp);
	            }
    		}#foreach thisarray
    		open(LR,"> $logfile") or print "$msg[2] $logfile: $!<br>";
    		flock(LR,1) or print "$msg[3] $logfile: $!<br>";
	        print LR @thisarray;
	        close(LR) or print "$msg[4] $logfile: $!<br>";

		$tm=localtime;
		
		open log_f, ">>$conf_stc_path/users.log";
		printf log_f "CT $tm $usver $otdel $user NewTr $limit\n";
		close(log_f);
	
		if ($limit eq "NL") {
		    $limit="$msg{'nolimit'}";
		} else {
		    $limit=$limit/$conf_mega_byte;
		    $limit="$limit Mb";
		}
		print "$msg[146] <b>$usver</b>: $limit<br><br>";
	
	    } else { #if not exist user
    		printf "<b>$msg[7]<br>$msg[12] $msg{'not_exist'}</b><br>";
	    }

	}#if save or add

	print "<form action=\"$back_url\" method=\"POST\">";
	print "<input type=submit value=\"$msg[53]\">";
	print "</form>";

    }#if safe_url
}#if admin
else{
    print "<font size=5>$msg[5]</font><br>";
}
print "</center>";

&load_footer;
