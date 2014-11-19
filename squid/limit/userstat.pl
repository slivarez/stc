#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

$nodeny = 0;
$denied_users = 0;
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

open IN, "<$stc_path/deny.users" or logmsg (__FILE__." line ".__LINE__." :Can't open read $stc_path/deny.users");
while (<IN>){
    @F = split(" ");
    if ($F[0] eq '') {next;}
    $old_deny{$F[0]}="TRUE";
    $denied_users++;
}
close (IN);

open(LOG9, "<$stc_path/password") or logmsg (__FILE__." line ".__LINE__." :Can't open read $stc_path/password");
while(<LOG9>)
{
  @F = split(':');
  if ($F[0] eq '') {next;}
  $user{$ucount} = $F[0];
  &get_profile($user{$ucount});
  $ucount++;
}
close (LOG9);

if (!get_all_traffic("$access_log")){
    logmsg(__FILE__." line ".__LINE__." :[ERROR] get all traffics is failed.");
    exit;
}

open(LOG1,"<$stc_path/traffic.users") or logmsg (__FILE__." line ".__LINE__." :Can't open read $stc_path/traffic.users");
while(<LOG1>){
    @F1= split(' ');
    if ($F1[0] eq '') {next;}
    $user1=$F1[0];
    $maxtraffic{$user1} = $F1[1];
}#while LOG1
close(LOG1);

open LOG2, ">$stc_path/deny.users" or logmsg (__FILE__." line ".__LINE__." :Can't open write $stc_path/deny.users");
for ($i=0; $i<$ucount; ++$i)
{
#print "$user{$i}:$traffic{$user{$i}}\n";
    if ($maxtraffic{$user{$i}} eq "NL"){next;}
    if($traffic{$user{$i}}>=$maxtraffic{$user{$i}}){
	printf LOG2 $user{$i};
	printf LOG2 "\n";
	$new_deny[$nodeny]=$user{$i};
	$nodeny=$nodeny+1;
	if ($domain{$user{$i}}){printf LOG2 "$logu{$user{$i}}\n";}
    }
}
close (LOG2);

if ($nodeny==0){
    open LOG3, ">$stc_path/deny.users" or logmsg (__FILE__." line ".__LINE__." :Can't open write $stc_path/deny.users");
    printf LOG3 "looser";
    printf LOG3 "\n";
    close LOG3;
}#if
system("chown $squid_user:$apache_group $stc_path/deny.users");

$squid_restart="FALSE";

for ($i=0; $i<$nodeny; ++$i){
#    print "OLD for $new_deny[$i]=$old_deny{$new_deny[$i]}\n";
    if ($old_deny{$new_deny[$i]} ne "TRUE"){
	$squid_restart="TRUE";
    }
}#for i

if ($squid_restart eq "TRUE"){
    #There is new denied user, we need to drop all connections for him
}#if $squid_restart

