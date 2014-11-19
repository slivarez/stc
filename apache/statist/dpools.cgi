#!/usr/bin/perl
#
# (C) 2004 STC Developers Team
#    slivarez            Didenko A.V.    slivarez@list.ru
#    alexenin            Enin Alexander  alexenin@yandex.ru
#    Demimurych          Demimuruch      demimurych@mail.ru
#    Orkan               Sirota S.S.     brahma@ua.fm
#
# Great thanks to:
#    adm -               Kostin Ilya
#    yolka_palka                         yolka@ydk.com.ua
#
# STC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# STC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. �See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with STC; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA �02111-1307 �USA
#

$stat="OK";
$scode="ok";
require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("Delay pool control");
&init_stc;

$query=new CGI;
$squid_reconf = $query->param('squid_reconf');

if( $admin{$user} eq 'yep') { # ���� ������ ����� - �������. ����� - ���
    print "<center>";
    print "<big>$msg[2000]</big><br><br>";

    #Checking for dpools
    $squidv=`$conf_squid_path/squid -v`; # ������� ������ ����� � �������� ��� ������������� ������

    if ( $squidv =~ /--enable-delay-pools/ ) {
	$status = "enable";
    } else {
	$status = "disable";
    }

    if ($status ne "enable"){ # ���� �� �������� ���� - ��� ������� :)
    print "<font color=$web_red_font><b>$msg[2001]:</b></font> $msg[2002].<br><br>"; # ���������� ������ � ����������
    print "<font>$msg[2003]<br></font>"; # �������� :)
    $stat="GLUCK: no --enable-delay-pools!"; # ��������� ����� ��� ���� :\
    goto the_end; # ���� � ���... :) ������ �� ����� ������ �����.
    }

    #If service_to_reconf not equal 'squid' then we will add squid reconf button
    if ($conf_service_to_reconf ne 'squid'){

	if ($squid_reconf and !(-e "$conf_stc_path/squid_reconf.lock")){
	    open tmpf, ">$conf_stc_path/squid_reconf.lock" or $ERR=$!;
	    close tmpf;
	}
	print "<hr>";
	print "<font size=1>$msg{'dpools_header'}</font><br>";
	print "<form method=POST>";
	my $ERR = undef;
	if (!(-e "$conf_stc_path/squid_reconf.lock")){
	    print "<input type=submit name=\"squid_reconf\" value=\"$msg{squid_reconf}\">";
	}
	else {
	    print "$msg{squid_reconf_queued}<br>";
	}
	print "</form>";
	print "<hr>";
    }#if

    if ($ERR){
	print "$msg{error}Can't create $conf_stc_path/squid_reconf.lock: $ERR<br>";
	logmsg(__FILE__." line ".__LINE__.":[ERROR] $user dpools.cgi can't create $conf_stc_path/squid_reconf.lock: $ERR");
    }


# ������ �������� ����� ������ � ��������

  @delay_users=(); # ��� ������������ - ���������� �� 0
  @otdel_acls=();
  $broken_otdels = ' ';
    foreach (@otdels)
        { # ������������� ����� stc/etc/
	     $o=$_;
	     my $usercount=0;
             open(USERLIST, "$conf_stc_path/o$_.users"); # ��������� ���� ����
	     open DPOOLOTDEL, ">$conf_stc_path/dpools/o$o.users" or $broken_otdels .= "$o ";
             while ($delay_cuser=<USERLIST>) # ������ ������ ������ �������
                     {
                      $delay_cuser=~ s/[\s\t]{0,}#.*$//; # �������� ��� ������ � �������
		      $delay_cuser =~ s/\s+//;
                      chomp($delay_cuser); # ������� �����
                      if ($delay_cuser){
		        push @delay_users, $delay_cuser; # ��������� ����� � ������
                        $delay_user_otdel{$delay_cuser}=$_; # �� �����... :(
		        printf DPOOLOTDEL "\^$delay_cuser\$\n";
			++$usercount;
		      }
                     }
             close (USERLIST); # ��������� ������ �������
	     close DPOOLOTDEL;
	     if ($usercount < 1){
	        $broken_otdels .= "$o ";
	     }
	     else {
	        push (@otdel_acls, "$o:otdel_$o");
	        $otdel_acls_name[$o]=$parts[1];
	        $otdel_acls_id[$parts[1]]=$o;
	     }
        }
# ��������� �������, �������� ������, �������� ��������� � �.�.

$dpools_num=0; # ������������� ���������� ���-�� �����

system ("cp -f $conf_squid_conf_path/squid.conf ./squid.conf.old"); # �������� squid.conf � ������� ����������. �� ���� ����� ������.
$err=0;
open SCF, "./squid.conf.old" or $err=1;
   if ($err eq 1)
   {print "<font color=#BB0000>$msg[2000]</font> $msg[2007] ./squid.conf.old: $!\n"; # ��������� ������������� ���� �� ������
    goto the_end;
   }
$err=0;
open NEWCONF, ">$conf_squid_conf_path/squid.conf" or $err=1;
   if ($err eq 1)
   {
   print "<font color=#BB0000>$msg[2000]</font> $msg[2007] $conf_squid_conf_path/squid.conf: $!\n"; # ��������� ������������ ������ �� ������
   goto the_end;
   }
$stc=0; # ������� � ������ ������ STC

while ($beg_line=<SCF>) # ������ ���� �������
    {
    $mod=0; # ������� � ��������� ����������� ������
    $line=$beg_line; # ������������ ������ ������� - ������ :)
    if ($line =~ /^#DO NOT REMOVE OR MODIFY THIS LINE!!!/) # ���� ��������� �������� �������...
    {$stc=1;} # ������ ������� ��� �� ��������� � ������ STC. ��� �������� ��� �� ������ �� ����� ���������� ��������� ����� ����, � ������ ������� ��. ������� �����.
    chomp($line); # ������� �����
#    $line=~ s/#.*//; # ������� ���������� ��-����� ��� ������... ��� ���������� ������ � ������ ������ ����� ������.
    $line=~ s/[\s\t]{1,}/ /; # ��� ������� � ���� - �������� �� ����
    $line=~ s/^[\s\t]{1,}//; # ������� ��� ������� � ���� � ������ ������
    if (!$line && $stc eq 0) # ���� ���������� ������ ������ (����� ���������� ��� ������ �����) � �� ��������� � ����� ������
            {print NEWCONF "$beg_line"; next;} # ������� ������ � ���������� ����
    @parts=split(" ", $line); # ��������� ������ � ������������ ������
#    if ($parts[0] eq "acl") # ���� �� ��������� �������� acl
#    {
#    }
    if ($parts[0] eq "delay_pools") # ���� �� ��������� �������� delay_pools
    {
    $mod=1;  # ����� � ���, ��� ���� �������������� ������ (� ������ ��������� �� � �����, ���� �� ��������� �� � ������ STC)
    $dpools_num=$parts[1]; # ���������� ���-�� �����
    } # ���� �� ��������� �������� delay_pools
    if ($parts[0] eq "delay_class" ) # ���� �� ��������� �������� delay_class
    {
    $mod=1; # ����� � ���, ��� ���� �������������� ������ (� ������ ��������� �� � �����, ���� �� ��������� �� � ������ STC)
    $delay_class[$parts[1]]=$parts[2]; # � ��������� �������� ����� ������� ����
    } # ���� �� ��������� �������� delay_class
    elsif ($parts[0] eq "delay_access")  # ���� �� ��������� �������� delay_access
    {
    $mod=1; # ����� � ���, ��� ���� �������������� ������ (� ������ ��������� �� � �����, ���� �� ��������� �� � ������ STC)
    $clients=$line; # �������� �������� ������ ��������. �� ����� ���� ��������� ����� ������
    $clients=~ s/^delay_access[\s]{1,}[0-9]{1,}[\s]{1,}(allow|deny)[\s]{1,}//; # ������� ����� � ���������� "delay_access"
    if ($parts[2] eq "allow" | $parts[2] eq "deny") # ���� allow ��� deny - ������� �� �� ��������. ���� ������ - �������� ������ ������ ������ ;)
        {
        if ($parts[2] eq "allow"){
	    $delay_access{"$parts[2]_$parts[1]"}.="DELAYACCESS ".$clients."\n"; # ���������� �� 2 ������� �� ��� allow_$i, deny_$i, � ������� ������ �������
	}
	else{
	    $delay_access{"$parts[2]_$parts[1]"}.=" ".$clients;
	}
        # ����� ����� ���� ��������� ����� � ������� ������ � ������ ���� ���������. ��� ���� �������������� ;)
	} # ���� allow ��� deny - ������� �� �� ��������.
    } # ���� �� ��������� �������� delay_access
    elsif ($parts[0] eq "delay_parameters")  # ���� �� ��������� �������� delay_parameters
    {
    $mod=1; # ����� � ���, ��� ���� �������������� ������ (� ������ ��������� �� � �����, ���� �� ��������� �� � ������ STC)
    $param=$line; # ���������� ��������� � ��������� ����������
    $param=~s/^delay_parameters\s[0-9]{1,}[\s]{1,}//; # ������� ����� � "delay_parameters"
    $delay_parameters{"$parts[1]"}=$param; # ���������� ��������� � ������.
    }  # ���� �� ��������� �������� delay_parameters

    if ($mod eq 1 && $stc eq 0) # ���� ����� �����������, � �� �� � ������ STC
    {
    print NEWCONF "\n#MOVED TO THE BOTTOM\n#$beg_line"; # �������� � ������� ��� ��������� ��� ������ � ������ STC
    } # ���� ����� �����������, � �� �� � ������ STC
    elsif ($stc eq 0) # ���� �� �� � ������ STC
    {print NEWCONF "$beg_line";} # ������ �������� ������ � ��������� ����.
    } # ��������� ������ ���� �������
close (SCF); # ��������� ���

if ($ENV{'REQUEST_METHOD'} eq "POST") # ���� ����� ������� - POST - ������ ���-�� ����� ���-�� ���������� :)
    {
    $query=new CGI;

    if ($query->param('addnew')) # �������� ����� ���
           {
        $ADD_pool_q=1; # ����� ��� ����� ��������� ���
            $ADD_pool=$query->param('insert_order'); # �����������, ����� ����� ����� ����� �������� �������.
print "INSERT: $ADD_pool<br>";
            $ADD_pool_class=$query->param('pool_class'); # ���� ����
            $ADD_delay_parameters=$query->param('param1')."/".$query->param('param2'); # ��������� 1
            if ($ADD_pool_class eq "2") # ���� ���� - 2 - �������� ������ ���� ����������
                 {$ADD_delay_parameters.=" ".$query->param('param3')."/".$query->param('param4');} # ���������� ������ ���� ����������
        if (!($query->param('param1') =~ /[\-0-9]{1,}/ && $query->param('param2') =~ /[\-0-9]{1,}/)) # ���� �����-�� �������� �� ������ ���� ��������, ��� �� �����
            {
            $ADD_pool="";
            $ADD_pool_q=""; # ������� ����� ����������
            print ("<font color=#BB0000>$msg[2001]!</font> $msg[2004]!<br>"); # ������ ������
            } # ������ ���� �� �������
        if ($ADD_pool_class eq 2 && !($query->param('param3') =~ /[\-0-9]{1,}/ && $query->param('param4') =~ /[\-0-9]{1,}/)) # ���� ���� ���� - 2 � �� ������� ������ ���� ��� ��� ������
            {
            $ADD_pool="";
            $ADD_pool_q=""; # ������� ����� ����������
            print ("<font color=#BB0000>$msg[2001]!</font> $msg[2005]!"); # ������� ��������� �� ������
            } # ���� �����=2 � ������ �� ������ ����
            $ADD_pool_access=""; # �������������� ���������� ������� ����.

	my $pervyjnah = undef;
        foreach ($query->param('users')) # ������ ���������� � ������� multiple select - �������
            {
	    if ($_ =~ /otdel_/s){
		my $otd = $_;
		$otd =~ s/otdel_//g;
		$otd = 0 + $otd;
		$ADD_pool_access .="DELAYACCESS otdel_$otd\n";
	    }#if
	    else {
		$ADD_pool_access.="DELAYACCESS $_\n";
            }
	}#foreach
        if (!($ADD_pool_access =~ /[^\s\t]/)) # ���� � ������� ���� - ����
            {
            $ADD_pool="";
            $ADD_pool_q=""; # ������� ����� ����������
            print ("<font color=#BB0000>$msg[2001]!</font> $msg[2006]!"); # ������� ���������
            } # ���� � ������� ���� - ����
        if (!match_users($ADD_pool_access)) # ���� $user �� ����� ������ ��� ��������, ������� ����� �������� � ���
            {
            $ADD_pool="";
            $ADD_pool_q=""; # ������� ����� ����������
            print ("<font color=#BB0000>$msg[2001]!</font> $msg[2027]!"); # ������� ���������
            } # ���� $user �� ����� ������ ��� ��������, ������� ����� �������� � ���
           } # �������� ����� ���
    elsif ($query->param('refresh')) # �������� ������������ ���
    {
        $MOD_pool=$query->param('pool_id'); # �������� ����� ����, ������� ����� ���������������
        $MOD_pool_class=$query->param('pool_class'); # �������� ����� ���� ����
        $MOD_parameters[1]=$query->param('param1'); # ���������
        $MOD_parameters[2]=$query->param('param2'); # ���������
        $MOD_parameters[3]=$query->param('param3'); # ���������
        $MOD_parameters[4]=$query->param('param4'); # ���������
        # ������ ��� ���������� ����������, ���� ���������� �� $ADD_... � $MOD_...
    if (!($MOD_parameters[1] =~ /[\-0-9]{1,}/ && $MOD_parameters[2] =~ /[\-0-9]{1,}/))
        {
        $MOD_pool="";
        print ("<font color=#CC0000>$msg[2001]!</font> $msg[2004]!<br>");
        }
    if ($MOD_pool_class eq 2 && !($MOD_parameters[3] =~ /[\-0-9]{1,}/ && $MOD_parameters[4] =~ /[\-0-9]{1,}/))
        {
        $MOD_pool="";
        print ("<font color=#CC0000>$msg[2001]!</font> $msg[2005]!");
        }
        $MOD_pool_access="";
    foreach ($query->param('users'))
        {
        $MOD_pool_access.="DELAYACCESS $_\n";
        }
    if (!($MOD_pool_access =~ /[^\s\t]/))
        {
        $MOD_pool="";
        print ("<font color=#CC0000>$msg[2001]!</font> $msg[2006]!");
        }
        if (!match_users($MOD_pool_access))
            {
            $MOD_pool="";
            print ("<font color=#BB0000>$msg[2001]!</font> $msg[2027]!");
            }
    } # �������� ������������ ���

    elsif ($query->param('delete')) # ������� ���
           {
           $DEL_pool=$query->param('pool_id'); # ������� ����� ����, ���������� ��������. �������� ���� - ����� ������ �������
           } # ������� ���
    } # ����� ��������� POST �������


# �������� ������ ������ STC � ������

 print NEWCONF "#DO NOT REMOVE OR MODIFY THIS LINE!!!\n#\n"; # ���������� �����������

# User and otdel ACL's...

#        print NEWCONF "\n#########################################\n# STC otdel acls\n#\n";
#   foreach (@otdels) # ���������� ��� ������, ������� ����� � stc/etc/
#       {
#        print NEWCONF "acl STC_otdel_$_ proxy_auth \"$conf_stc_path/o$_.users\"\n";
#       }

        print NEWCONF "\n#########################################\n# STC users acls\n#\n";
   foreach (@delay_users) # ���������� ���� �������, ������� ����� � �������
    {
        print NEWCONF "acl STC_user_$_ proxy_auth_regex ^$_\$\n";
    }
    print NEWCONF "\n#########################################\n# STC otdel acls\n#\n";
    foreach (@otdel_acls){
	($totd, $foo) = split (':');
	if ($broken_otdels =~ /\ $totd\ /s){print "!!!!!!<br>";next;}
	print NEWCONF "acl otdel_$totd proxy_auth_regex \"$conf_stc_path/dpools/o$totd.users\"\n";
    }
# End User and Otdel ACL's

if ($DEL_pool) # ���� ��� ������� ��� �� ��������
    {
        if (!match_users($delay_access{"allow_$DEL_pool"})) # ���� ��� ���� � ������� ����� ��� ������ - �� ������
            {
            $DEL_pool=""; # ������� ������� �� ��������
            print ("<font color=#BB0000>$msg[2001]!</font> $msg[2028]!"); # ������ ��������� �� ������
            $dpools_num_new=$dpools_num; # ���������� ����� ���-�� ����� ������ ������� ���-��...
            }
        else # ���� ���� ����� � ������� ����� ��� ������ - ������
       {$dpools_num_new=$dpools_num-1;} # ���������� ����� ���-�� ����� �� 1 ������ ��� ������, ����� �������� ������...
    }
elsif ($ADD_pool_q) # ���� ����� ������� � ���������� ����
    {$dpools_num_new=$dpools_num+1;} # ���������� ����� ���-�� ����� ������ �� ���� ������
else {$dpools_num_new=$dpools_num;} # ���� ��� ��������� - ���������� ����� ���-�� ����� ������ ������� ���-��...

if ($dpools_num_new) # ���� � ��� ���� �����-�� ����
    {print NEWCONF "\n\n#########################################\n# STC delay pools configuration\n#\ndelay_pools $dpools_num_new\n\n";} # ���������� � ������ ���-�� �����

$deleted=0; # ������� �� �������������� ��������
$added=0; # ������� �� �������������� ����������
for ($i=1; $i<=$dpools_num; ++$i){ # ���� ���������� �����. ��������� ���� ��� ���� :)
    if ($ADD_pool eq $i) # ���� ���� �������� ��� ����� �������
    {
print "ADD_pool = $ADD_pool<br>";
        $added=1; # ��������� � ������ ������� �� �������������� ����������
        # ���������� ������
        print NEWCONF "#########################################\n# pool number $i\n#\n";
        print NEWCONF "delay_class $i $ADD_pool_class\n";
	$ADD_pool_access =~ s/DELAYACCESS/delay_access\ $i\ allow/ig;
        print NEWCONF $ADD_pool_access."\n";
        print NEWCONF "delay_access $i deny all\n";
        print NEWCONF "delay_parameters $i ".$ADD_delay_parameters."\n\n";
    }
    elsif ($DEL_pool eq $i) # ���� ���������� ������� ������� ���
    {$deleted=1; next;} # ������� � ������ �������
    elsif ($MOD_pool eq $i) # ���� ���������� �������������� ������� ���
    { # ���������� ����� ���������
        $delay_parameters{"$i"}="$MOD_parameters[1]/$MOD_parameters[2]"; # ������ ���� ��������
        if ($MOD_pool_class eq 2) # ���� ����� = 2
        {
	    $delay_parameters{"$i"}.=" $MOD_parameters[3]/$MOD_parameters[4]"; # ������ ���� �������
	}
        $delay_class[$i]=$MOD_pool_class; # ����� �����
	$MOD_pool_access =~ s/DELAYACCESS/delay_access\ $i\ allow/ig;
        $delay_access{"allow_$i"}=$MOD_pool_access; # ����� ������
        $modified=1; # ������ ������� �� �������������� �����������
    } # ���� ���������� �������������� ������� ���

    if ($deleted) # ���� ��� ������ �����-�� ���
    {
	$num=$i-1; # ������������ ����� �� 1. ����� ������ ����� ����� �� 1 ������, � ��������� � ��� - �������� �� ������� ������. ��������
        $delay_class[$num]=$delay_class[$i];
        $delay_access{"allow_$num"}=$delay_access{"allow_$i"};
        $delay_access{"deny_$num"}=$delay_access{"deny_$i"};
        $delay_parameters{"$num"}=$delay_parameters{"$i"};
    }
    elsif ($added)
    { # ���� ����� ��� ��������, �� ����� � ��������������� �������
        $num=$i+1;
#print "DEBUG: I=$i ($delay_class[$i] $delay_access{\"allow_$i\"}) NUM=$num ($delay_class[$num] $delay_access{\"allow_$num\"})<br>";
        $new_delay_class[$num]=$delay_class[$i];
        $new_delay_access{"allow_$num"}=$delay_access{"allow_$i"};
        $new_delay_access{"deny_$num"}=$delay_access{"deny_$i"};
        $new_delay_parameters{"$num"}=$delay_parameters{"$i"};
    }
    else {$num=$i;} # ���� ��� ������ - ����� ��� ��������� �������� ��� ������� �������
    if (!$delay_access{"deny_$i"}){$delay_access{"deny_$i"}=" all";}
    # ���������� ��� � ������-����
    print NEWCONF "#########################################\n# pool number $num\n#\n";
    print NEWCONF "delay_class $num $delay_class[$i]\n";
    my $tmp_access = $delay_access{"allow_$i"};
    $tmp_access =~ s/DELAYACCESS/delay_access\ $num\ allow/ig;
    print NEWCONF $tmp_access;
    print NEWCONF "delay_access $num deny ".$delay_access{"deny_$i"}."\n";
    print NEWCONF "delay_parameters $num ".$delay_parameters{"$i"}."\n\n";
}#for

if ($added){
for ($i=1; $i<=$dpools_num_new; ++$i){
    if ($i <= $ADD_pool){next;}
    else{
        $delay_class[$i]=$new_delay_class[$i];
        $delay_access{"allow_$i"}=$new_delay_access{"allow_$i"};
        $delay_access{"deny_$i"}=$new_delay_access{"deny_$i"};
        $delay_parameters{"$i"}=$new_delay_parameters{"$i"};
    }
}#for
}#if
    if ($ADD_pool eq 0 && $ADD_pool_q) # ���� ���� ����������� �������� ��� � ����� �������
        {
        # ���������� � ������-���� ����� ���
        print NEWCONF "#########################################\n# pool number $i\n#\n";
        print NEWCONF "delay_class $i $ADD_pool_class\n";
	$ADD_pool_access =~ s/DELAYACCESS/delay_access\ $i\ allow/ig;
        print NEWCONF $ADD_pool_access."\n";
        print NEWCONF "delay_access $i deny all\n";
        print NEWCONF "delay_parameters $i ".$ADD_delay_parameters."\n\n";
        # ������������� ��������� ��� ����������� � �������, ������� ����� ����.
        $delay_class[$i]=$ADD_pool_class;
        $delay_access{"allow_$i"}=$ADD_pool_access;
        $delay_access{"deny_$i"}="all";
        $delay_parameters{"$i"}=$ADD_delay_parameters;
        } # ���� ���� ����������� �������� ��� � ����� �������
    elsif ($added eq 1) # ���� ��������� �� � ����� ������� - ��������� ����� � � ���������� - ��� ���� � ����������� ����������� � ������ (� ������� ����� ;))
        { # ���� �� ��� �� ����������� ��� ����� ���
        $delay_class[$ADD_pool]=$ADD_pool_class;
        $delay_access{"allow_$ADD_pool"}=$ADD_pool_access;
        $delay_access{"deny_$ADD_pool"}="all";
        $delay_parameters{"$ADD_pool"}=$ADD_delay_parameters;
    }

close (NEWCONF); # ��������� ����� ������-����

system ("rm -f ./squid.conf.old"); # ������� ������ ��������� ������

$dpools_num=$dpools_num_new; # ���������� ���-�� ����� � ��������������� ����������
# ����� ��������� ����� �������

# ����� �� ����� ���� ���������� � ����...

print ("<table width=\"100%\" border=0 cellspacing=0 align=center>"); # ���������� �������

# �������� ����� ����� ��� �������
$dclass[1]=$msg[2009];
$dclass[2]=$msg[2010];

for ($i=1; $i<=$dpools_num; $i++)
    { # ������������ ��� ����
    print ("<tr><form action=dpools.cgi method=post><input type=hidden name=pool_id value=$i>\n"); # ������ ������ - ��������� �����
    print ("<td valign=top><br><b>$msg[2011]:</b> <select name=pool_class style=\"width:auto;\">
            <option value=1>$dclass[1]</option>
            <option value=2");
    if ($delay_class[$i] eq 2) {print (" selected");}
    print (">$dclass[2]</option>
            </select><br>\n");
    print ("<b>$msg[2012]:</b><br>\n<select multiple name=users style=\"width:100%; height:120;\">\n");

   foreach (@otdel_acls) # ������ �������
       {
       # ���� � ������� ���� ��������� ������������, ������� ����������� �������� ������ - ������� ������ ��� �������, ������� � ����������
       # ���� ��������� ������������ �� ������ ������� - ������� ���� �������������, �� ������� �������� ;)
        ($id, $acl) = split (':');
       if (match_users($delay_access{"allow_$i"}) eq 1 && match_users("$acl") eq 0)
           {
            next;
           }
        print ("<option value=\"$acl\"");
           if (($delay_access{"allow_$i"} =~ /^$acl[\s]/) || ($delay_access{"allow_$i"} =~ /[\s]$acl$/) || ($delay_access{"allow_$i"} =~ /[\s]$acl[\s]/))
           {print (" selected");}
        print (">$msg[2013]");
	if ($otdel_prn[$id]) {print $otdel_prn[$id];}
	else {print $id;}
	print ("</option>\n");

       }

   foreach (@delay_users)
       {
       if (match_users($delay_access{"allow_$i"}) eq 1 && match_users("STC_user_$_") eq 0)
           {
            next;
           }
        print ("<option value=\"STC_user_$_\"");
           if ($delay_access{"allow_$i"} =~ /STC_user_$_/)
           {print (" selected");}
        print (">$_</option>\n");
       }

    print ("</select></td>\n<td width=\"220\"><br><center><b>$msg[2014]:</b></center>");
    $delay_parameters{"$i"} =~ s/(^[\t\s]{1,}|[\t\s]{1,}$)//; # ��������� ��������
    @l1=split(" ", $delay_parameters{"$i"});
    @l2=split("/", $l1[0]);
    @l3=split("/", $l1[1]);
    print ("<b>$msg[2015]:</b><br>");
    print ("$msg[2016]: <input type=text name=param1 value=\"$l2[0]\" style=\"width:60;\"> $msg[2018]<br>\n");
    print (" &nbsp; &nbsp; $msg[2017]: <input type=text name=param2 value=\"$l2[1]\" style=\"width:60;\"> $msg[2019]<br>\n");
    print ("<br><b>$msg[2020]:</b><br>");
    print ("$msg[2016]: <input type=text name=param3 value=\"$l3[0]\" style=\"width:60;\"> $msg[2018]<br>\n");
    print (" &nbsp; &nbsp; $msg[2017]: <input type=text name=param4 value=\"$l3[1]\" style=\"width:60;\"> $msg[2019]<br><br>\n");
    print ("</td>");
    print ("<td valign=top align=center><br><br>$msg[2021]: <b>$i</b><br><br>");
    if (match_users($delay_access{"allow_$i"}) eq 1 )
        {
        print ("<input type=submit name=refresh value=\"$msg[2022]\" style=\"width:100;\"><br><br>\n");
        print ("<input type=submit name=delete value=\"$msg[2023]\" style=\"width:100;\">\n");
        }
    print ("</td></form></tr>\n<tr><td colspan=3><hr></td></tr>\n\n");
    }

## ����� ����������... ���������� ����������
if ($admin{$user}){
    print ("<tr><form action=dpools.cgi method=post>\n");
    print ("<td><br><b>$msg[2011]:</b> <select name=pool_class style=\"width:auto;\">
            <option value=1>$dclass[1]</option>
            <option value=2>$dclass[2]</option>
            </select><br>\n");
    print ("<b>$msg[2012]:</b><br>\n<select multiple name=users style=\"width:100%; height:120;\">\n");

   foreach (@otdel_acls)
       {
       ($id, $acl) = split(":");
       if (match_users("STC_otdel_$id") eq 1)
        {
	print ("<option value=\"".$acl."\">$msg[2013]");
	if ($otdel_prn[$id]) {print $otdel_prn[$id];}
	else {print $id;}
	print ("</option>\n");
	}
       }
#   foreach (@otdels)
#       {
#       if (match_users("STC_otdel_$_") eq 1)
#        {print ("<option value=\"STC_otdel_$_\">$msg[2013] $_</option>\n")};
#       }

   foreach (@delay_users)
       {
       if (match_users("STC_user_$_") eq 1 )
        {print ("<option value=\"STC_user_$_\">$_</option>\n")};
       }

    print ("</select></td>\n<td><br><center><b>$msg[2014]:</b></center>");
    print ("<b>$msg[2015]:</b><br>");
    print ("$msg[2016]: <input type=text name=param1 value=\"\" style=\"width:60;\"> $msg[2018]<br>\n");
    print (" &nbsp; &nbsp; $msg[2017]: <input type=text name=param2 value=\"\" style=\"width:60;\"> $msg[2019]<br>\n");
    print ("<br><b>$msg[2020]:</b><br>");
    print ("$msg[2016]: <input type=text name=param3 value=\"\" style=\"width:60;\"> $msg[2018]<br>\n");
    print (" &nbsp; &nbsp; $msg[2017]: <input type=text name=param4 value=\"\" style=\"width:60;\"> $msg[2019]<br><br>\n");
    print ("</td>");
    print ("<td><br><br>
            <select name=insert_order>
            <option value=0>$msg[2024]</option>");
       for ($i=1; $i<=$dpools_num; $i++) # ��� ����� ���� ���� ��� ���������. � ����� ��� ����� �����-��...
            {print "<option value=$i>$msg[2025] $i</option>\n";}
    print ("</select><br><br>
            <input type=submit name=addnew value=\"$msg[2026]\" style=\"width:100;\"><br><br>\n");
    print ("</form></tr>\n\n");
}#if admin

print ("</table>"); # ��������� �������

# ����� ������...


sub match_users # ������� �������� �������������� ������� � ������ �������� ����������, ��� �������� ������...
    {

    if ($admin{$user}) # ���� ���� - �����
      { return 1;} # ��� �����, �� ���� ����������� :)
    else {return 0;}
      my ($users)=@_; # �����, ���������� � �������� ���������
      @sub_users=split(" ", $users); # ����������� - ������

      foreach (@sub_users)
          { # ������� ���� �������
           if ($_ =~ /^STC_user_/) # ���� ������ - ��� �����
               {
               $_=~ s/^STC_user_//; # �������� �����
               $_=$delay_user_otdel{$_}; # ������� ����� ������ ��� ����� �����. ���������� ����������� ������.

               if (!( (" ".join(" ", @user_boss)." ") =~ /\s$_\s/)) # ���� �� �������� �������� ����
                      {return 0;} # � ���
               } # ���� ������ - ��� �����
           else # ���� ������ - ��� �����
               {
#               print $_;
               $_= $otdel_acls_id[$_]; # �������� ����� ������
#               print "-".$boss_users{$user}."- =~ -$_-";
               if (!( (" ".join(" ", @user_boss)." ") =~ /\s$_\s/)) # ���� ��� - �� ��� ����� ������
                      {return 0;} # � ���
               } # ���� ������ - ��� �����
          }
      return 1; # ���� �� ���� ����� - ������ ������ - ���� ��� ����� ���������� ��������
    }

}
else # � ���� ������ ������� �� ����� � �� ��� - �������� ��� ��� �� ��������� ������� :)
    {
     print "$msg[5]<br>"; # ��� ���!
    }

# �����!
the_end:

&load_footer; # ���� ������ ��� �������, ��� �����

# ������� �� ��������! :)))
# Blin! Orkan, gde ty takuju travu beresh?! 2 dnya razabiralsya/peredelyval script! /slivarez/
