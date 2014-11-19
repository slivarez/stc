#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

#use Time::localtime;
use File::Copy cp;
use FileHandle;
$error_log="/var/log/stc_error.log";


my $fname="/etc/stc.conf";
if (!-r $fname)
    {
    my $time_now = sprintf "%02d.%02d.%04d %02d:%02d:%02d", (localtime)[3], (localtime)[4]+1, (localtime)[5]+1900, (localtime)[2,1,0];
    $pr=__FILE__." line ".__LINE__." :[ERROR] Cannot open '$fname'";
    system("echo ".$time_now." - $pr >> $error_log");    
    die "$pr\n";
    }
else
    {
    open cf, "<$fname" or die "$!";
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
}

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


$m = (localtime)[4]+1;


if (! -s "$access_log.0")
{
    logmsg (__FILE__." line ".__LINE__.":[INFO] $access_log.0 is empty");
    exit;
}

if (-e "$access_log.m$m"){
   $str=`tail -n 1 $access_log.m$m`;
   @F=split(' ', $str);
   $ltime=$F[0];
}
else{
   $ltime=0;
}


$str=`head -n 1 $access_log.0`;
@F=split(' ', $str);
$ftime=$F[0];

if ($ftime > $ltime){
    my $new = FileHandle->new("$access_log.m$m", "a");
    my $old = FileHandle->new("$access_log.0", "r");
    cp ($old, $new);
    system("chown $squid_user:$apache_group $access_log");
    system("chown $squid_user:$apache_group $access_log.m$m");
}
else{
    logmsg (__FILE__." line ".__LINE__.":[WARNING] Time mismatch in $access_log.m$m and $access_log.0");
}


