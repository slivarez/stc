#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

$scode="ok";
require "./init_stc.pl";
print "Content-type: text/html; charset=$msg[600]\n\n";
&get_conf;

#Let's get out traffic info
get_traffic($user);

open(LOG1,"$conf_stc_path/traffic.users") || print "$msg[2] $conf_stc_path/traffic.users: $!<br>";
while(<LOG1>){
    @F1= split(' ');
    $user1=$F1[0];
    if($user1 ne $user){next;}
    if ($F1[1] eq "NL"){
	$maxtraffic{$user1} = 1000000000000;
    }
    else{
	$maxtraffic{$user1} = $F1[1];
    }
}#while LOG1
close(LOG1);

$left=$maxtraffic{$user}-$traffic{$user};
$traffic{$user}=$traffic{$user}/$conf_mega_byte;
$maxtraffic{$user}=$maxtraffic{$user}/$conf_mega_byte;
$left=$left/$conf_mega_byte;


print "<pre>\n";
print "user= $user\n";
printf ("total= %.06f\n", $traffic{$user});
printf ("current= %.06f\n", $maxtraffic{$user});
printf ("left= %.06f\n", $left);
print "</pre>\n";