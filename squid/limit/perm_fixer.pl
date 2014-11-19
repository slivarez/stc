#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.

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

($login,$pass,$uid,$gid) = getpwnam($apache_user);

$file_uid = (stat '/tmp/stc')[4];
if ($file_uid ne $apache_user){
   chown $uid, $gid, '/tmp/stc';
}

$file_uid = (stat $log_file)[4];
if ($file_uid ne $apache_user){
   chown $uid, $gid, $log_file;
}

