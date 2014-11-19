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
    eval '&get_conf; &get_profile("$user"); &load_header("Limit page","fullpaths"); &init_stc;';
}
else {
   print "Content-type: text/html; charset=$msg[600]\n\n";
}

print "<p align=center><font size=5 color=red>$msg[505]</font><br>";
print "<font size=4>$msg[508]<br>";
print "Попробуйте в следующем месяце.<br></font></p>";

if ($use_init){eval '&load_footer("shortinfo","fullpaths");'};
