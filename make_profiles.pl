#!/usr/bin/perl

open cf, "</etc/stc.conf" or die "$!";
while(<cf>){
    @F=split(/\s+/);
    if ($F[0] eq '#'){next;}
    if ($F[0] eq 'stc_path'){
	$stc_path=$F[1];
    }
    if ($F[0] eq 'apache_user'){
	$apache_user=$F[1];
    }
    if ($F[0] eq 'apache_group'){
	$apache_group=$F[1];
    }
}
close (cf);

print "Reading *.otdel files...\t\t";
for ($i=0;$i<999;++$i){
    $f="$stc_path/o$i.users";
    open fil, "<$f" or $E='gluk';
    if ($E ne 'gluk'){
	while (<fil>){
	    @F=split ' ';
	    if ($F[0] ne ''){
		$user1=$F[0];
		$otdel{$user1}=$i;
		$lname{$user1}=$F[2];
		$fname{$user1}=$F[3];
		$mname{$user1}=$F[4];
	    }
	}#while ff
    }
    close (fil);
    $E='q';
}#for
print "done\n";

print "Updating profiles...\t\t\t";
open pasfil, "<$stc_path/password" or print "$msg[2] $stc_path/password: $!";
while(<pasfil>){
    @F=split(':');
    if ($F[0] ne ""){
	if (!( -e "$stc_path/profiles/$F[0].profile")){
	    open tmpf, ">$stc_path/profiles/$F[0].profile";
	    printf tmpf "domain:\niface:standart\email:\n";
	    printf tmpf "lname:$lname{$F[0]}\nfname:$fname{$F[0]}\nmname:$mname{$F[0]}\n";
	    close (tmpf);
	}
	else{
	    my $logfile="$stc_path/profiles/$F[0].profile";
    	    my @thisarray;
    	    open(LR,"$logfile") or print "Can't open $logfile: $!\n";
	    flock(LR,1) or print "Can't flock $logfile: $!\n";
	    @thisarray = <LR>;
    	    close(LR) or print "Can't close $logfile: $!\n";
    	    my @tmp;
	    my $lname_found=undef;
	    my $fname_found=undef;
	    my $mname_found=undef;
    	    foreach (@thisarray) {
		$_ =~ s/1:/domain:/g;
		$_ =~ s/2:/iface:/g;
		$_ =~ s/3:/email:/g;
		$_ =~ s/\d:\n//g;
		($key, $foo) = split (':');
		if ($key eq 'lname'){$lname_found='yep';}
		if ($key eq 'fname'){$fname_found='yep';}
		if ($key eq 'mname'){$mname_found='yep';}
    	    }#foreach thisarray
    	    open(LR,"> $logfile") or print "Can't open $logfile: $!\n";
    	    flock(LR,1) or print "Can't flock $logfile: $!\n";
    	    print LR @thisarray;
    	    close(LR) or print "Can't close $logfile: $!\n";
	    open tmpf, ">>$stc_path/profiles/$F[0].profile";
	    if (!$lname_found){printf tmpf "lname:$lname{$F[0]}\n";}
	    if (!$fname_found){printf tmpf "fname:$fname{$F[0]}\n";}
	    if (!$mname_found){printf tmpf "mname:$mname{$F[0]}\n";}
	    close (tmpf);
	}
    }
}
close (pasfil);
print "done\n";

system ("chown -R $apache_user:$apache_group $stc_path/profiles");
