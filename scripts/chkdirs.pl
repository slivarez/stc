#!/usr/bin/perl
#STC chkdirs.pl script - version 0.1
print "\nReading /etc/stc.conf file ... ";

open cf, "</etc/stc.conf" or die "Can't open /etc/stc.conf: $! \n";
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

@dirs=undef;
push @dirs, "$stc_path<>$apache_user<>493<>0755";
push @dirs, "$stc_path/dpools<>$apache_user<>493<>0755";
push @dirs, "$stc_path/profiles<>$apache_user<>493<>0755";
push @dirs, "$stc_path/lang<>$apache_user<>493<>0755";
push @dirs, "$stc_path/includes<>$apache_user<>493<>0755";
push @dirs, "$www_data_path/stat<>$apache_user<>493<>0755";
push @dirs, "$www_data_path/stat/statist<>$apache_user<>493<>0755";
push @dirs, "$www_data_path/stat/themes<>$apache_user<>493<>0755";
push @dirs, "$www_data_path/stat/messages<>$apache_user<>493<>0755";
push @dirs, "$stc_path/messages/users<>$apache_user<>493<>0755";
push @dirs, "$stc_path/messages<>$apache_user<>493<>0755";
push @dirs, "$limit_path<>root<>493<>0755";
push @dirs, "$SC_path<>root<>493<>0755";
push @dirs, "$repots_dir<>root<>493<>0755";

print "Checking dirs...\n";
foreach (@dirs){
   ($dir, $owner, $bperms, $perms) = split ('<>');
   $ERR=undef;
   opendir (DIR, $dir) or $ERR='gluck';
   closedir DIR;
   if ($ERR){
      print "\tError: $dir not found! Creating it... ";
      mkdir ("$dir", oct($perms));
      system ("chown $owner $dir");
      print "done\n";
   }#if
   else {
	($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($dir);
	$realowner = getpwuid ($uid);
	$mod=$mode & 0b111111111;
	chomp ($realowner); chomp ($owner);
	if ($realowner ne $owner){
	   print "\tWrong owner($realowner) for dir ($dir). Will set to $owner ... ";
	   system ("chown $owner $dir");
	   print "done\n";
	}
	if ($mod ne $bperms){
	   print "\tWrong perms for dir ($dir). Will set to $perms ... ";
	   chmod oct($perms), $dir;
	   print "done\n";
	}
   }#else
}
print "done\n";

