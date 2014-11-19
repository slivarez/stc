#!/usr/bin/perl

$a=`locale |grep LANG`;
$a=~s/^.+\.([a-zA-Z0-9\-]{0,})$/$1/i;
$a=~s/\s//i;
print "Current locale:".$a."\n";
if ($a eq 'UTF-8') {print "WARNING! Codepage no converted.\n";}
@f_name=("adduser.cgi","admin.cgi","dpools.cgi","init_stc.pl","serverstat.cgi");
foreach $f (@f_name) {print $f; system("iconv -futf8 -t$a $f >$a\_$f"); print " - ok \n";}



