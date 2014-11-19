#!/usr/bin/perl
#
# Script for updating STC from current distr
#created by Didenko A.V. e-Mail: slivarez@gmail.com


use Time::localtime;
use File::Copy cp;
use FileHandle;

print "\nYou are going to update STC. Continue? (y/n): ";
$answer=undef;
while (!($answer =~ /[yYnN]/))
{
$answer=<STDIN>;
}
chomp $answer;
if ($answer ne "Y" and $answer ne "y") { print "User break... \n"; sleep 1; exit; }
print "Continue...\n";


print "\n\n\n\nReading /etc/stc.conf...\t\t\t";
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
print "done\n";


if (( $site_ip eq "") or ($site_ip eq "auto"))                  { $site_ip="127.0.0.1"; }
if (( $stc_path eq "") or ($stc_path eq "auto"))                { $stc_path="/usr/local/stc/etc";}
if (( $limit_path eq "") or ($limit_path eq "auto"))            { $limit_path="/usr/local/stc/limit";}
if (( $SC_path eq "") or ($SC_path eq "auto"))                  { $SC_path="/usr/local/stc/sarg";}
if (( $squid_user eq "") or ($squid_user eq "auto"))            { $squid_user="squid";}
if (( $squid_group eq "") or ($squid_group eq "auto"))          { $squid_group="squid";}
if (( $apache_user eq "") or ($apache_user eq "auto"))          { $apache_user="nobody";}
if (( $apache_group eq "") or ($apache_group eq "auto"))        { $apache_group="nobody";}
#if (( $log_install eq "") or ($log_install eq "auto"))          { $log_install="/var/log/error.log";}
if (( $exclude_hosts eq "") or ($exclude_hosts eq "auto"))      { $exclude_hosts="$stc_path/exclude_hosts";}
if (( $language eq "") or ($language eq "auto"))                { $language="rus-koi8r";}
if (!$log_file)							{ $log_file="/var/log/stc_error.log";}


require "foretc/includes/ver.inc";
print "\nBegin Update to $version-$date ...\n";

$tm = localtime;
$m = $tm->mon + 1;
$d = $tm->mday;
$y = $tm->year + 1900;
$h=$tm->hour;
$mm=$tm->min;

open slog, ">>$log_file";
printf slog "\nUpdate to $version-$date on $d.$m.$y at $h:$mm [begin]\n";
close (slog);

print "STC data files directory: \t\t\t$stc_path\n";
print "STC limit scripts directory: \t\t\t$limit_path\n";
print "STC CGI-scripts directory: \t\t\t$www_data_path/stat\n";

print "Copying files...\t\t\t\t";

#system("cp uninstall $stc_path/ >> $log_file 2>&1");
if ($limit_path and ($limit_path ne '/')) {system ("rm -rf $limit_path/* >> $log_file 2>&1");}
system("cp squid/limit/* $limit_path/ >> $log_file 2>&1");
#system("cp foretc/squidGuard.* $stc_path/ >> $log_file 2>&1");
system("cp sarg/* $SC_path/ >> $log_file 2>&1");
system("cp apache/statist/* $www_data_path/stat/statist/ >> $log_file 2>&1");
system("cp -R apache/stat/* $www_data_path/stat/ >> $log_file 2>&1");
system("cp apache/messages/* $www_data_path/stat/messages/ >> $log_file 2>&1");
system("cp -R foretc/includes $stc_path/ >> $log_file 2>&1");
system("cp -R foretc/lang $stc_path/ >> $log_file 2>&1");
system("mkdir $stc_path/profiles >> $log_file 2>&1");
if ($www_data_path and ($www_data_path ne '/')) {system ("rm -rf $www_data_path/stat/themes");}
system("cp -R apache/themes $www_data_path/stat/ >> $log_file 2>&1");
print "done\n";

print "Changing file attributes...\t\t\t";
    system("chown -R $apache_user $stc_path >> $log_file 2>&1");
    system("chmod 755 $stc_path/profiles >> $log_file 2>&1");
    system("chown $apache_user $reports_dir >> $log_file 2>&1");
    system("chmod 755 $reports_dir >> $log_file 2>&1");
    system("chown root $stc_path/trusted_users >> $log_file 2>&1");
    system("chown root $stc_path/admin.users >> $log_file 2>&1");
    system("chown $apache_user:$apache_group $www_data_path/stat/* >> $log_file 2>&1");
    system("chown $apache_user:$apache_group $www_data_path/stat/statist/* >> $log_file 2>&1");
    system("chown $apache_user:$apache_group $www_data_path/stat/messages/* >> $log_file 2>&1");
    system("chown $apache_user:$apache_group $www_data_path/stat/themes >> $log_file 2>&1");
    system("chown $apache_user:$apache_group $stc_path/messages/users >> $log_file 2>&1");
    system("chown $apache_user:$apache_group $stc_path >> $log_file 2>&1");
    system("chmod -R 755 $limit_path >> $log_file 2>&1");
    system("chmod -R 755 $www_data_path/stat/statist/  >> $log_file 2>&1");
    system("chmod -R 755 $www_data_path/stat/messages/  >> $log_file 2>&1");
    system("chmod 755 $www_data_path/stat/themes/  >> $log_file 2>&1");
print "done\n";


print "Creating profiles....\t\t\t\t";
system ("./make_profiles.pl");
print "done\n";

print "Updating /etc/stc.conf... ";
system ("mv /etc/stc.conf /etc/stc.conf.backup >> $log_file 2>&1");
system ("cp install.conf /etc/stc.conf >> $log_file 2>&1");

my $logfile="/etc/stc.conf";
my @thisarray;
open(LR,"$logfile") or print "Can't open $logfile: $!\n";
flock(LR,1) or print "Can't flock $logfile: $!\n";
@thisarray = <LR>;
close(LR) or print "Can't close $logfile: $!\n";
my @tmp;
foreach (@thisarray) {
    $line = $_;
    chomp ($line);
    if (!$line){next;}
    $line=~ s/^[\s\t]{0,}//;
    $line=~ s/#.*//;
    if (!$line){next;}
    @parts=split(/\s+/, $line);
    $var=shift(@parts);
    @$var=@parts;
    if (!$$var){$$var=$parts[0];}
    $line = join (' ', $var, $$var);
    $_ = $line."\n";
}#foreach thisarray
open(LR,"> $logfile") or print "Can't open $logfile: $!\n";
flock(LR,1) or print "Can't flock $logfile: $!\n";
print LR @thisarray;
close(LR) or print "Can't close $logfile: $!\n";
print "done\n";

print "\nPlease read CHANGES and check out files:\n";
print "\t/etc/stc.conf\n";
print "\t/etc/crontab\n";
print "\n";

open slog, ">>$log_file";
printf slog "Update to $version-$date at $d.$m.$y [end]\n";
close (slog);

print "Update compleat!\n";
