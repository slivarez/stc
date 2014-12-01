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

require "./init_stc.pl";

&get_conf;
$coren = $conf_reports_dir;

$query = new CGI;
$picfile = $query->param(pic);

$type="image/png"; # type of returning content
$picfile =~ s/\.\.//ig;
$file = $coren."/".$picfile;

open(IMGF, $file) or die "cannot open file: ".$file."\n"; # if open fails, it will be logged by apache
binmode(IMGF); # work with file in binary mode
$size = ( -s $file);
print "Content-type: $type\n"; 
print "Content-length: $size\n\n"; 
while(read(IMGF,$data,1024)){ print $data; } # put image to stdout as binary stream
close (IMGF);
