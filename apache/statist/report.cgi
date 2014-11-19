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
&load_header("Reports");
&init_stc;

print "<p align=center>$msg[111] <b>$user</b>!</p>";

print "<center>";

$user="\L$user";

print "<a href=view.cgi?page=daily/total/index.html>$msg[112]</a><br>";
print "<br>";
print "<a href=view.cgi?page=weekly/total/index.html>$msg[113]</a><br>";
print "<br>";
print "<a href=view.cgi?page=monthly/total/index.html>$msg[114]</a><br>";

print "</center>";
print "</p>";

&load_footer;
