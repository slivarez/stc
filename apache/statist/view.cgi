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

$script = "/cgi-bin/view?page";

$scode="ok";
require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("Your statistic");
&init_stc;

$query=new CGI;
$ips=$ENV{'REMOTE_ADDR'};
$url=$ENV{'REQUEST_URI'};
$coren=$conf_reports_dir;
$start_usver=$query->param(page);

($url, $foo) = split ('=', $url);

my @tmp = split("", $conf_sarg_version);
my $sarg_version = 0 + $tmp[0];
if ($sarg_version == 0){$sarg_version = 1;}

$user || logdanger();
$start_usver =~ s/\0|\.\.|\|//ig;
$start_usver =~ s/\0|\.\.|\|//ig;
$Otdel = "bes ego znaet";
$ZapUser= "bes ego znaet";
if ($start_usver =~ /^(daily|monthly|total|users|weekly)\/([a-z0-9]+)\/([a-z0-9\-\_\.]+)\/?([a-z0-9\_\.]*)\/?([a-z0-9\-\_\.]*)/i) {
            $Opred = $1;
            $Otdel = $2;
            $otdel = $2;
            $p3=$3;
            $p4=$4;
            $p5=$5;
            $ZapUser  = $4;
            $ZapUser =~ s/\.html$//ig;
            $otdel =~ s/o//g;
            $otdel = 0+$otdel;
}
#print "ZAP = $ZapUser<br>";

$view_allow = adv_boss_chk($user, $otdel, 'view_rep');
#print "ADV_BOSS_CHK (".$user.', '.$otdel.','."view_rep) = $view_allow<br>";

if ($sarg_version == 1){$userhref = "\L$user.html";}
if ($sarg_version == 2){$userhref = "\L$user/"."\L$user.html";}

## START alexenin 07.05.2009 add navigation

#goto skip_navigation;

$L_script="No page";
$U_script="index.html";

if ($Opred eq 'daily')      {$L_script=$msg[112];$N_script=$msg[131];}
elsif ($Opred eq 'weekly') {$L_script=$msg[113];$N_script=$msg[132];}
elsif ($Opred eq 'monthly')  {$L_script=$msg[114];$N_script=$msg[133];}

#Added by slivarez on 2009-10-23: fix for HTTP/HTTPS URLs
if (!$ENV{'HTTPS'}){$http = "http://";}
else {$http = "https://";}

print "<table><tr><td align=left width=80%><a href='".$http.$ENV{'HTTP_HOST'}."/stat/cgi/report.cgi'>$L_script</a>";

if (($admin{$user} eq 'yep') or $view_allow)
{
    if ($ZapUser!=$p4) {
	print " -> <a href='$url=$Opred/$Otdel/$U_script'>$p3</a>";
        print " -> <a href='$url=$Opred/$Otdel/$p3/$U_script'>$ZapUser</a>";
    }
    elsif ($p4 ne $U_script and $p3 ne $U_script) {
	print " -> <a href='$url=$Opred/$Otdel/$U_script'>$p3</a>";
        print " -> <a href='$url=$Opred/$Otdel/$p3/$U_script'>$ZapUser</a>";
    }
    elsif ($p4) {$URL_dop="$p3/";
	print " -> <a href='$url=$Opred/$Otdel/$U_script'>$p3</a>";
    }
}
else
{
    if ($p4 ne $U_script and $p3 ne $U_script) {
	print " -> <a href='$url=$Opred/$Otdel/$U_script'>$p3</a>";
    }
    elsif ($p4) {$URL_dop="$p3/";
	print " -> <a href='$url=$Opred/$Otdel/$U_script'>$p3</a>";
    }
    
}
print "</td></tr></table><br>";

#for debug
#print $msg[6].": $script=$Opred/$Otdel/$U_script<br>";
#print "<br>Opred=$Opred<br>Otdel=$Otdel<br>otdel=$otdel<br>p3=$p3<br>p4=$p4<br>p5=$p5<br>ZapUser=$ZapUser<br>";
#for debug

#skip_navigation:

## END alexenin 07.05.2009 add navigation

unless	($admin{$user} eq 'yep' or $p3 eq "index.html") {
	 if ($Otdel ne "total" and !$view_allow) {logdanger("$coren/$start_usver", "ACCESS DENIED");}
         if (($Otdel eq "total") and ("\Ltt$user" ne $ZapUser) and ("\Ld$user" ne $ZapUser) and ("\L$user" ne $ZapUser)) {
		print "user=$user<br>ZapUser=$ZapUser<br>"; 
		logdanger("$coren/$start_usver", "ACCESS DENIED");
	}
	 if ((($ZapUser eq $user) or ("tt$user" ne $ZapUser) or ("d$user" ne $ZapUser)) and ($p5 ne "")){ $userhref = "$ZapUser/$p5";}
	 else {$userhref = "$ZapUser.html";}
}
if ($start_usver =~ /\.png$/){ # link in SARG report may not refer to html-file
    print "<center><img src=sarg_graph.pl?pic=".$start_usver.">" # so, we supply special processing for images
}
else{
open bf1, "<$coren/$start_usver" or logdanger("$coren/$start_usver", $!);

    if ($start_usver =~ /index\.html/) {
    $sel="yes"};
    $start_usver=~ s/(\/)(\w*)(\.html|\.htm)$/$1/ig;
#    $start_usver=~ s/\.html|\.htm$//ig;

while (<bf1>){
    $reff = "$script=$start_usver";
    unless (($admin{$user} eq 'yep') or $view_allow) {
	if ($sel eq "yes") {
		    s/\>([0-9\.]+)\</*/g;
		    s/index\.html/$userhref/;
         }
    }#unless

#OLD
s/(href=)([\',\"]?)([a-z0-9\.\_\-\/]+)(?=[\'|\"| |\>])/$1$2$url=$start_usver$3$2/ig;

#NEW
#@t = split ('/', $start_usver);
#$k = @t;
#$base = '';
#for ($i=0; $i < $k-1; $i++){
#    $base .= $t[$i].'/';
#}
#print "SU = $start_usver<br>BA = $base<br>";
#s/(href=)([\',\"]?)([a-z0-9\.\_\-\/]+)(?=[\'|\"| |\>])/$1$2$url=$base$3$2/ig;

#Removing table headers from sarg report
# s/\<th/\<td/ig;
# s/\<\/th/\<\/td/ig;
# It isn't good idea, in my opinion

if ($sarg_version == 2){
  #Removing/replacing styles in sarg 2 report

  s/\<style\>//ig;  # Commenting sarg styles and head definitions
  s/\<\/style\>/\-\-\>/ig;
  s/\<head\>/\<\!\-\-/ig; 
  s/\<\/head\>//ig;
  
  s/\<html\>//ig; # Removing <html> tags
  s/\<\/html\>//ig;
  
  s/\<body style.*\>/\<body\>/ig; # Removing style from <body> tag
#  s/\<\/body\>//ig;  # We won't drop <body> tags, we only drop style from thise
# so, in the body will be used default theme style

# We must newly define styles used in sarg report, instead commented internal SARG 2 styles

# The basic concept is to define a new special standard styles in header.html files
# and use ones for replacing original SARG 2 styles
# In these case the new standard styles must be implemented in an all present themes and in a new ones
# It allows the finest tuning reports view to fit to featuires of each theme
# So, I have selected these way... All SARG-2-related styles will be with sarg2_ prefix

  s/class\=\"body\"//ig; # I think thise will be right because I have already drop style from <body>, but I don't sure...
  s/class\=\"/class\=\"sarg2\_/ig;

# Graph img link workaround
  $graph_find = "<img src=\"(graph_.*.png)\"";
  $graph_replace = '"<img src=sarg_graph.pl?pic='.$start_usver.'$1"';
  s/$graph_find/$graph_replace/eeig;
  
# At thise point I fix paths to <img src = ... It works only if all used by SARG 2 pictures
# placed to /stat/images directory

  s/\<img src\=\"[^"]+\/images\//\<img src\=\"\.\.\/images\//ig;
  s/\<img src="images\//\<img src="..\/images\//ig;

}

print;

}#while
close (bf1);
}; # else from if ($start_usver =~ /\.png$/)

the_end:
&load_footer;


    exit(0);


sub logdanger {
    my $file = $_[0];
    my $error = $_[1];

    print "<center>$msg{reports_na}</center>";
#    open futer,"<$www_data_path/stat/footer.htm";
#    while (<futer>) {
#    print;
#    }
    if (!$file){
	logmsg (__FILE__." line ".__LINE__.":[WARNING] $ips $user view.cgi $start_usver");
    }
    else{
	logmsg (__FILE__." line ".__LINE__.":[ERROR] $ips $user view.cgi $file: $error");
    }
    goto the_end;
}
