#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

#use Time::localtime;

$ucount = 0;

open cf, "</etc/stc.conf" or die "$!";
while($line=<cf>){
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
close (cf);

my $fname="$stc_path/includes/limit.inc";
if (-r $fname)
    {
    require $fname;
    }
else
    {
    system("echo ".__FILE__." line ".__LINE__." :[ERROR] Cannot open '$fname' >> $log_file");
    die __FILE__." line ".__LINE__." $msg{'cannot_open'} '$fname'";
    }


#Checking for cycle records in logs
if (! -s "$access_log.0")
{
    logmsg (__FILE__." line ".__LINE__.":[INFO] $access_log.0 is empty");
    exit;
}

#$tm = localtime;
#$m = $tm->mon + 1;
$m = (localtime)[4] + 1;

$str=`tail -n 1 $access_log.m$m`;
@F=split(' ', $str);
$ltime=$F[0];

$str=`head -n 1 $access_log.0`;
$no_records=0;


@F=split(' ', $str);
$ftime=$F[0];

if (($ftime > $ltime) or $no_records)
{
    open(LOG9, "<$stc_path/password") or logmsg (__FILE__." line ".__LINE__." :[ERROR] Can't open read file: $stc_path/password");
    while(<LOG9>)
    {
	@F = split(':');
  
	$user{$ucount} = $F[0];
	&get_profile($user{$ucount});
	$ucount=$ucount+1;
    }
    close (LOG9);

    if (!get_all_traffic("${access_log}.0")){
	logmsg(__FILE__." line ".__LINE__." :[ERROR] get_all_traffic is failed.");
    }

    open cur_tr, ">$stc_path/cur_tr.users" or logmsg (__FILE__." line ".__LINE__." :[ERROR] Can't open write file:  $stc_path/cur_tr.users"); 
    foreach $tuser (sort keys %traffic)
    {
        if ($traffic{$tuser}>0) {printf cur_tr $tuser." ".$traffic{$tuser}."\n";}
    }
    close (cur_tr);
    system("chown $apache_user:$apache_group $stc_path/cur_tr.users");
#    logmsg (__FILE__." line ".__LINE__." :[DEBUG] calcul ok. no_records=$no_records. time: $ftime > $ltime");
}#if ftime > ltime
else
{
    logmsg (__FILE__." line ".__LINE__." :[WARNING] Time mismatch in $access_log.m$m and $access_log.0");
}
