#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

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
if (-r $fname){
    require $fname;
}
else {
    system("echo ".__FILE__." line ".__LINE__." :[ERROR] Cannot open '$fname' >> $log_file");
    die __FILE__." line ".__LINE__." $msg{'cannot_open'} '$fname'";
}
require "$stc_path/includes/ver.inc" or die "Can't open $stc_path/includes/ver.inc\n";

my $err = undef;
my $cfile = "$stc_path/version.cache";
my $lver = get_latest_version($version);
unless ($lver =~ /^ERROR/i){
        open CF, "> $cfile" or $err=1;
        print CF "LATEST_VERSION:$lver" unless $err;
        close CF;
}

