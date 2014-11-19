#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

$ucount=0;
$ducount=0;
$alowedcount=0;

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


open(LOG, "<$stc_path/password") or logmsg (__FILE__." line ".__LINE__." :[ERROR] Can't open read file: $stc_path/password");
while(<LOG>)
{
  @F = split(':');
  
  $user_name{$ucount} = $F[0];
  &get_profile($user_name{$ucount});
  $ucount=$ucount+1;
}
close(LOG);

open blockfil, "<$stc_path/blocked.users" or logmsg (__FILE__." line ".__LINE__." :[ERROR] Can't open read file: $stc_path/blocked.users");
while (<blockfil>){
    @F=split(' ');
    if ($F[0] eq '') {next;}
    $blocked{$F[0]}="TRUE";
}
close (blockfil);


open(LOG1, "<$stc_path/deny.users") or logmsg (__FILE__." line ".__LINE__." :[ERROR] Can't open read file: $stc_path/deny.users");
while(<LOG1>)
{
  @F = split(' ');
  
  $deny_user{$ducount} = $F[0];
  $ducount=$ducount+1;
}
close(LOG1);

open A1, ">$stc_path/allow.users" or logmsg (__FILE__." line ".__LINE__." :[ERROR] Can't open write file: $stc_path/allow.users");
open A2, ">$stc_path/blocked.users" or logmsg (__FILE__." line ".__LINE__." :[ERROR] Can't open write file: $stc_path/blocked.users");
printf A2 "loooser\n";
for($i=0; $i<$ucount; ++$i){
    if ($user_name{$i} eq ""){next;}
    $write=1;
    for($k=0; $k<$ducount; ++$k){
	if($user_name{$i} eq $deny_user{$k}){
	    $write=0;
	    break;
	}
    }#for k
    if ($write==1){
	if ($blocked{$user_name{$i}} eq "TRUE"){
	    printf A2 "$user_name{$i}\n";
	    if ($domain{$user_name{$i}}){printf A2 "$logu{$user_name{$i}}\n";}
	}
	else{
	    $allowedcount=$allowedcount+1;
	    printf A1 "$user_name{$i}\n";
	    if ($domain{$user_name{$i}}){printf A1 "$logu{$user_name{$i}}\n";}
	}
    }#if
}#for i
if($allowedcount==0){
    printf A1 "looser";
    printf A1 "\n";
}
close (A1);
close (A2);
system("chown $squid_user:$apache_group $stc_path/allow.users >> /var/log/error.log 2>&1");
system("chown $squid_user:$apache_group $stc_path/blocked.users >> /var/log/error.log 2>&1");

### added by snAke 26.04.2010 BEGIN
if ($allow_deny_files_by_otdels eq 'true') {
    open(AOTD, "<$stc_path/allign.otdel") or logmsg (__FILE__." line ".__LINE__." :[ERROR] Can't open read file: $stc_path/allign.allow");
    while(<AOTD>)
        {
           ($otdel,$foo) = split(':');
           open TEMP_OTD, "< $stc_path/o$otdel.users" or logmsg (__FILE__." line ".__LINE__." :[ERROR] Can't open file: $stc_path/o$otdel.users");
           open A1, ">$stc_path/o$otdel.allow" or logmsg (__FILE__." line ".__LINE__." :[ERROR] Can't open write file: $stc_path/o$otdel.allow");
           open A2, ">$stc_path/o$otdel.deny" or logmsg (__FILE__." line ".__LINE__." :[ERROR] Can't open write file: $stc_path/o$otdel.deny");
           $allowed_user_exists = $denied_user_exists = 0;
           while (<TEMP_OTD>){
                ($line,$foo)=split(' ');
                if ($line eq ''){next;}
                $is_write=0;
                for($k=0; $k<$ducount; $k++){
                    if($line eq $deny_user{$k}){
                        $is_write++;
                        $denied_user_exists++;
                        printf A2 "$line\n";
                        break;
                        }#if
                    }#for k
                if (!$is_write && $blocked{$line} ne "TRUE"){
                        printf A1 "$line\n";
                        $allowed_user_exists++;
                    }#if
                } # while
           close TEMP_OTD;
           if (!$allowed_user_exists) {printf A1 "lucky\n";}
           if (!$denied_user_exists) {printf A2 "lucky\n";}
           close (A1);
           close (A2);
           system("chown $squid_user:$apache_group $stc_path/o$otdel.allow >> /var/log/error.log 2>&1");
           system("chown $squid_user:$apache_group $stc_path/o$otdel.deny >> /var/log/error.log 2>&1");
        }#while(<AOTD)>;
close (AOTD);
}#if $allow_deny_files_by_otdels
#### added by snAke 26.04.2010 END
