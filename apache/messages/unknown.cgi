#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

$use_init=undef;
$language="rus-1251";
$scode="ok";

if (-e "../statist/init_stc.pl"){require "../statist/init_stc.pl"; $use_init="yes"; &get_conf;}
else{
    if (-e "../cgi/init_stc.pl"){require "../cgi/init_stc.pl"; $use_init="yes"; &get_conf;}
    else {print "Content-type: text/html; charset=$msg[600]\n\n";}
}

if ($use_init and $user){
#&get_conf;&get_profile("$user");&load_header("Limit page");&init_stc;
    eval '&get_conf; &get_profile("$user"); &load_header("Unknown user","fullpaths"); &init_stc;';
}
else {
   print "Content-type: text/html; charset=$msg[600]\n\n";
}

print "<p align=center><font size=5 color=red>";
print "$msg[505]</font><BR>";
print "<font size=4 color=black>$msg{'unknown_user'}</font><BR>";
print "<font size=4 color=black>$msg[500]</font></p><BR>";

if ($use_init){eval '&load_footer("shortinfo","fullpaths");'};

