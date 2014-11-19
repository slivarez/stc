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

use Apache::Htpasswd;
$scode="ok";
require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("Change password for other user");
&init_stc;

print "<center>";

if($admin{$user} eq 'yep'){
$usver=undef;
$query=new CGI;
$usver=$query->param(user1);
$start_usver=$query->param(start_user);
if (!$usver){$usver = $start_usver;}
$newpass=$query->param(newpasswd);
$repass=$query->param(repasswd);
$param_otdel=$query->param(otdel);
$back_url1=$query->param('back_url1');

$back_url=$query->param('back_url');
if (!safe_url($back_url, 'supasswd.cgi')){goto l1;}

if(($newpass ne '') and ($newpass eq $repass)){
    $pas = new Apache::Htpasswd("$conf_stc_path/password");
    $pas->htpasswd($usver, $newpass, {'overwrite' => 1});

    my $logfile="$conf_stc_path/password.digest";
        my @thisarray;
        open(LR,"$logfile") or print "$msg[2] $logfile: $!<br>";
        flock(LR,1) or print "$msg[3] $logfile: $!<br>";
        @thisarray = <LR>;
        close(LR) or print "$msg[4] $logfile: $!<br>";
        my @tmp;
        foreach (@thisarray) {
            @tmp = split(':');
            if ($tmp[0] eq $usver) {
        $tmp[1] = "$newpass\n";
            $_ = join(':', @tmp);
            }
    }#foreach thisarray
    open(LR,"> $logfile") or print "$msg[2] $logfile: $!<br>";
    flock(LR,1) or print "$msg[3] $logfile: $!<br>";
    print LR @thisarray;
    close(LR) or print "$msg[4] $logfile: $!<br>";

    $tm=localtime;

    open log_f, ">>$stc_path/users.log";
    printf log_f "CP $tm $usver $user\n";
    close(log_f);

    print "$msg[43]<br><br>";
}
if($newpass ne $repass){
    print "$msg[46]<br>";
}

print "<form action=supasswd.cgi method=POST>";
    print "<input type=hidden name=start_user value=$start_usver>";
    print "<input type=hidden name=back_url value=\"$back_url\">";
    print "<input type=hidden name=back_url1 value=\"$back_url1\">";
    print "<input type=hidden name=otdel value=\"$param_otdel\">";

print "<b>$msg[39]</b><br><br>";
print "<table width=50%>";
print "<tr>";
print "<td>$msg[12]:</td>";
print "<td><input type=text name=user1 size=20 value=$usver></td>";
print "</tr>";
print "<tr>";
print "<td>$msg[19]:</td>";
print "<td><input type=password name=newpasswd size=20></td>";
print "</tr>";
print "<tr>";
print "<td>$msg[20]:</td>";
print "<td><input type=password name=repasswd size=20></td>";
print "</tr>";
print "<tr align=center>";
print "<td align=center><input type=submit value=\"$msg[26]\"></td>";
print "<td style=text-align:right><input type=reset value=\"$msg[27]\"></td>";
print "</tr>";
print "</form>";
print "</table>";

}
else{
    print "$msg[5]<br>";
}
l1:

    print "<br><br>";

    print "<form action=\"$back_url\" method=\"POST\">";
    print "<input type=hidden name=user value=$start_usver>";
    print "<input type=hidden name=otdel value=\"$param_otdel\">";
    print "<input type=hidden name=back_url value=\"$back_url1\">";
    print "<input type=submit value=\"$msg[53]\">";
    print "</form>";

print "</center>";

&load_footer;
