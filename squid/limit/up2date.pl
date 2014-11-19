#!/usr/bin/perl
#
# STC up2date scipt, updates STC from STC-server to the latest release
# !!! For stc-2.0.1-beta and higher ONLY !!!

$stc_site="stc-update.nixdev.org";
$wget="/usr/bin/wget -N";
$version = '1.0';

use Time::localtime;
use File::Copy cp;
use FileHandle;
use IO::Socket;
use IO::Handle;
#use Apache::Htpasswd;

my $k = @ARGV;
my $options = undef;
for (my $i; $i<$k; ++$i){
   $options .= "$ARGV[$i] ";
}

if (($ARGV[0] eq '-h') or ($ARGV[0] eq '--help')){
    print "\nSTC up2date scipt (version $version), updates STC from STC-server to the latest release\n!!! For stc-2.0.1-beta and higher ONLY !!!\n";
    print "\nUSAGE:\n\tup2date.pl [option1] [option1] ... [optionN]\n\n";
    print "OPTIONS:\n\t--skip-attributes - to skip chmod and chown stage\n";
    print "\t--auto - up2date.pl runs in auto mode without output to STDOUT\n";
    print "\n";
    exit 0;
}

if (!($options =~ /--auto\ /s)){
print "\nYou are going to update STC from $stc_site. Continue? (y/n): ";
$answer=undef;
while (!($answer =~ /[yYnN]/))
{
$answer=<STDIN>;
}
chomp $answer;
if ($answer ne "Y" and $answer ne "y") { print "User break... \n"; sleep 1; exit; }
print "Continue...\n";
}

print "\nReading /etc/stc.conf file ... " if (!($options =~ /--auto\ /s));

$tm = localtime;
$m = $tm->mon + 1;
$d = $tm->mday;
$y = $tm->year + 1900;
$h=$tm->hour;
$mm=$tm->min;

open cf, "</etc/stc.conf" or die "Can't open /etc/stc.conf: $! : line 53\n";
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

open UNAME, "uname|" or print "Error detect name system or no run uname: line 67\n";
while (<UNAME>){ $UName=$_;}
  close (UNAME);
chop($UName);

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

print "done\n" if (!($options =~ /--auto\ /s));

print "Checking host $stc_site..." if (!($options =~ /--auto\ /s));
$error=undef;
my $sock = IO::Socket::INET->new(PeerAddr=>"$stc_site",PeerPort=>"80",Proto=>"tcp") or $error="yep";
if ($error){
    print "ERROR\n\tCan't connect to $stc_site:80\n\n";
    exit 0;
}
close ($sock);
print " host OK\n" if (!($options =~ /--auto\ /s));


$url = "$stc_site/up2date/version.txt";
$new_build = http_query($url);

$new_build =~ s/\n//ig;
$new_build =~ s/#END#.*$//ig;
$new_build =~ s/^.*#BEGIN#//ig;

$new_build = 0 + $new_build;

if ($new_build == 0){print "Can't find STC on that server... Exiting...\n\n";exit 0;}
print "Checking version on server... \t found build $new_build\n" if (!($options =~ /--auto\ /s));

print "Checking installed version...\t " if (!($options =~ /--auto\ /s));
require "$stc_path/includes/ver.inc" or die "Can't open $stc_path/includes/ver.inc\n";
($day, $mon, $year) = split (/\./, "$date");
$cur_build = "$year$mon$day";
$cur_build += 0;
print "found build $cur_build\n" if (!($options =~ /--auto\ /s));

if ($cur_build >= $new_build) {
   print "\nYour current version is up to date. Exiting...\n\n" if (!($options =~ /--auto\ /s));
   exit 0;
}

print "Fetching tarball... " if (!($options =~ /--auto\ /s));
system ("$wget $stc_site/up2date/new_stc.tgz  >> $log_file 2>&1");
sleep 2;
print "done\n" if (!($options =~ /--auto\ /s));

if (! ( -e "new_stc.tgz")){ print "Error: new_stc.tgz not found. Exiting...\n\n"; exit 0;}
print "Extracting... " if (!($options =~ /--auto\ /s));
system ("tar xzf new_stc.tgz >> $log_file 2>&1");
print "done\n" if (!($options =~ /--auto\ /s));

print "Deleting files... " if (!($options =~ /--auto\ /s));
open rmf, "<new_stc/rmlist";
while (<rmf>){
    ($type, $file) = split(':');
    $rfile=$file;
    chomp($file);
    chomp($rfile);

    $file =~ s/#.*//;
    if (!$file){next;}

    $file =~ s/\/$//g;
    $file =~ s/\*$//g;
    $file =~ s/\/$//g;

    $file =~ s/^@//ig;
    $tmp=undef;
    ($var, $ffile) = split ('@', $file);
    if ($$var){
	$tmp=$$var;
	$file = join ('', $tmp, $ffile);
    }

    $rfile =~ s/^@//ig;
    $tmp=undef;
    ($var, $ffile) = split ('@', $rfile);
    if ($$var){
	$tmp=$$var;
	$rfile = join ('', $tmp, $ffile);
    }

    if ($file eq "/"){next;}
    if ($file eq "/usr"){next;}
    if ($file eq "/var"){next;}
    if ($file eq "/usr/local"){next;}
    if ($file eq "/usr/local/etc"){next;}
    if ($file eq "/usr/local/bin"){next;}
    if ($file eq "/boot"){next;}
    if ($file eq "/usr/bin"){next;}
    if ($file eq "/usr/sbin"){next;}
    if ($file eq "/usr/include"){next;}
    if ($file eq "/dev"){next;}
    if ($file eq "/etc"){next;}
    if ($file eq "/src"){next;}
    if ($file eq "/man"){next;}
    if ($file eq "/share"){next;}

    if ($type eq 'FILE')	{system ("rm -f $rfile >> $log_file 2>&1");}
    if ($type eq 'DIR')		{system ("rmdir $rfile >> $log_file 2>&1");}
}
close (rmf);
print "done\n" if (!($options =~ /--auto\ /s));

print "Updating files... " if (!($options =~ /--auto\ /s));
if ( -e "new_stc/foretc/includes"){
	system ("cp -r new_stc/foretc/includes/* $stc_path/includes/ >> $log_file 2>&1");
}
if ( -e "new_stc/foretc/lang"){
	system ("cp -r new_stc/foretc/lang/* $stc_path/lang/ >> $log_file 2>&1");
}
if (( -e "new_stc/sarg") and ($SC_path ne '/')){
	system ("cp -r new_stc/sarg/* $SC_path/ >> $log_file 2>&1");
}
if (( -e "new_stc/squid/limit") and ($limit_path ne '/')){
	system ("cp -r new_stc/squid/limit/* $limit_path/ >> $log_file 2>&1");
}
if ( -e "new_stc/apache/themes"){
	system ("cp -r new_stc/apache/themes/* $www_data_path/stat/themes/ >> $log_file 2>&1");
}
if ( -e "new_stc/apache/statist"){
	system ("cp -r new_stc/apache/statist/* $www_data_path/stat/statist/ >> $log_file 2>&1");
}
if ( -e "new_stc/apache/messages"){
        system ("cp -r new_stc/apache/messages/* $www_data_path/stat/messages/ >> $log_file 2>&1");
}
if ( -e "new_stc/apache/stat"){
	system ("cp -r new_stc/apache/stat/* $www_data_path/stat/ >> $log_file 2>&1");
}
print "done\n" if (!($options =~ /--auto\ /s));


print "Changing file attributes... " if (!($options =~ /--auto\ /s));
if (!($options =~'--skip-attributes')){
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
    print "done\n" if (!($options =~ /--auto\ /s));
}
else {
    print "SKIPPED\n" if (!($options =~ /--auto\ /s));
}

if ( -e "new_stc/install.conf"){
    print "Updating /etc/stc.conf... " if (!($options =~ /--auto\ /s));
    system ("mv /etc/stc.conf /etc/stc.conf.backup >> $log_file 2>&1");
    system ("cp new_stc/install.conf /etc/stc.conf >> $log_file 2>&1");

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
    print "done\n" if (!($options =~ /--auto\ /s));
}#if

if ( -e "new_stc/up2date.pl"){
    print "Updating $limit_path/up2date.pl script... " if (!($options =~ /--auto\ /s));
    system("rm -f $limit_path/up2date.pl >> $log_file 2>&1");
    system("cp new_stc/up2date.pl $limit_path/up2date.pl >> $log_file 2>&1");
    system("chown root $limit_path/up2date.pl >> $log_file 2>&1");
    system("chmod 700 $limit_path/up2date.pl >> $log_file 2>&1");
    print "done\n" if (!($options =~ /--auto\ /s));
}
    system("rm -rf new_stc >> $log_file 2>&1");
    system("rm -f new_stc.tgz >> $log_file 2>&1");

    print "Update finished. Please check $log_file for details.\n\n" if (!($options =~ /--auto\ /s));



#######################
sub http_query($){
    my ($url) = @_;
    my $host=$url;
    my $query=$url;
    my $page="";
    $host =~ s/href=\"?http:\/\///;
    $host =~ s/([-a-zA-Z0-9\.]+)\/.*/$1/;
    $query =~s/$host//;
    if ($query eq "") {$query="/";};
    eval {
          local $SIG{ALRM} = sub { die "1";};
          alarm 10;
          my $sock = IO::Socket::INET->new(PeerAddr=>"$host",PeerPort=>"80",Proto=>"tcp") or return;
          print $sock "GET $query HTTP/1.0\nHost: $host\nAccept: */*\nUser-Agent: Mozilla/4.0\n\n ";
          my @r = <$sock>;
          $page="@r";
          alarm 0;
          close($sock);
    };
    return $page;
}
########################
