#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
# chktraf.pl, version 2.1
#created by Didenko A.V. e-Mail:slivarez@list.ru

use Time::localtime;
#$nodeny = 0;
#$denied_users = 0;
$ucount = 0;
#$access_log = "fs.log";
$mode="full";
$m1=$ARGV[0];
$tm=localtime;
$day=$tm->mday;
$mon=$tm->mon + 1;
$year=$tm->year + 1900;

$m1 = 0+$m1;
if (($m1 < 1) or ($m > 12) or ($ARGV[0] eq '-h') or ($ARGV[0] eq '--help')){
    print "USAGE: \t./chktraf.pl MONTH\nSAMPLE:\t./chktraf.pl 8\n";
    exit 0;
}
open fil1, "</etc/stc.conf" or die "Can't open /etc/stc.conf: $!\n";
#open LOG2, ">cur_tr.result";
#printf LOG2 "Squid access.log Report\n";
while($line=<fil1>){
    chomp($line);
    $line=~ s/#.*//;
    $line=~ s/[\s\t]{1,}/ /;
    $line=~ s/^[\s\t]{0,}//;
    if (!$line){next;}
    @parts=split(" ", $line);
    $var=shift(@parts);
    @$var=@parts;
    $$var=$parts[0];
}

$access_log .= '.m'.$m1;

require "$stc_path/includes/limit.inc";

open(LOG9, "$stc_path/password") || die "Can't open log";
while(<LOG9>)
{
  @F = split(':');
  if (!$F[0]){next;}
  $user{$ucount} = $F[0];
  &get_profile($user{$ucount});
  $ucount=$ucount+1;
}
close (LOG9);

if (!get_all_traffic("$access_log")){
    print "[ERROR] Can't open $access_log\n";
}

open cur_tr, ">cur_tr.m";
for ($i=0; $i<$ucount; ++$i)
{
    printf cur_tr $user{$i};
    printf cur_tr " ";
    printf cur_tr $traffic{$user{$i}};
    printf cur_tr "\n";
}
close (cur_tr);
