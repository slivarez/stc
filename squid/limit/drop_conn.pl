#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

use Time::localtime;

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

if (!$drop_connections eq "yes"){exit 0;}

open dufile, "<$stc_path/deny.users" or die "Can't open $stc_path/deny.users: $!\n";
while (<dufile>){
    @F=split(' ');
    if ($F[0] ne ""){
	$baduser{$F[0]}='yep';
    }
}
close (dufile);

open dufile, "<$stc_path/blocked.users" or die "Can't open $stc_path/blocked.users: $!\n";
while (<dufile>){
    @F=split(' ');
    if ($F[0] ne ""){
	$baduser{$F[0]}='yep';
    }
}
close (dufile);

$last_time=0;

open runf, "<$stc_path/drop_conn.run";
while (<runf>){
    @F=split(/\s+/);
    if ($F[0] ne ""){$last_time=$F[0];}
}
close (runf);

open logfile, "<$access_log" or die "Can't open $access_log: $!\n";
while (<logfile>){
    @F=split(' ');
    $time=$F[0];
    $user_name=$F[7];
    $ip=$F[2];
    $port=$F[10];
    @code=split('/',$F[3]);
    if ($last_time < $time){$last_time=$time;}
    else{next;}
    
    if (($code[0] ne "TCP_DENIED") and $baduser{$user_name} and $port and $ip){
#print "!-> $time $user_name - $code[0]/$code[1] - $ip:$port\t";
	if ($done{$user_name}{"$ip-$port"} ne 'yep'){
	    system ("$limit_path/reset_conn.pl $ip $port $local_eth_device 5");
	    $done{$user_name}{"$ip-$port"}='yep';
#print "KILL";
	}#if done
#print "\n";
    }
}
close (logfile);

open runf, ">$stc_path/drop_conn.run";
printf runf "$last_time\n";
close (runf);
