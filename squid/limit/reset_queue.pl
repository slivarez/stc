#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Sirota S.S. e-Mail:brahma@ua.fm

#$local_eth_device="eth0";
$sec_per_kill=20;

    open cf, "</etc/stc.conf" or die "$!";
    while($line=<cf>){
           chomp($line);
           $line=~ s/#.*//;
           $line=~ s/[\s\t]{1,}/ /;
       $line=~ s/^[\s\t]{0,}//;
           if (!$line)
                {next;}
           @parts=split(" ", $line);
           $var=shift(@parts);
           @$var=@parts;
           $$var=$parts[0];
    }
    close (cf);
#Create temp dir
if (!(-e '/tmp/stc')){mkdir("/tmp/stc", 0755);}

#Kill queue sequence
if (-e '/tmp/stc/kill.queue')
     {
     system ('touch /tmp/stc/kill.queue.lock');
     $i=0;
     open (KILLFILE, "/tmp/stc/kill.queue");
     while (<KILLFILE>)
             {
             chomp;
             ($ip, $port) = split (":");
             if ($ip ne '')
                 {
                 $$i{'ip'}=$ip;
                 $$i{'port'}=$port;
                 $i++;
                 }
             }
     close (KILLFILE);
     system ('rm /tmp/stc/kill.queue');
     system ('rm /tmp/stc/kill.queue.lock');

     $reset=0;
     for ($j=0; $j<$i; $j++)
          {system ("$limit_path/reset_conn.pl ".$$j{'ip'}." ".$$j{'port'}." $local_eth_device $sec_per_kill");}
     }

