#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

$conf_mega_byte=1000000;
$language="rus-1251";
$scode="ok";
require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("Users control");
&init_stc;

$query = new CGI;

my $q = new CGI;
my $ot = $q->param("otd");

my $usver = $q->param("user");

$boss="looser";

#if(chk_boss_otdel($ot) eq 'ok'){
if (adv_boss_chk ($user, $ot, "manage_traff")){
    $state='OK';
    &get_profile($usver);

    $tru="$conf_stc_path/cur_tr.users";
    open fil, "<$tru" or $state="gluk";
    if ($state eq 'gluk'){
        print "$msg[7] $msg[503] $usver $msg[83]<br>";
        goto l1;
    }
    while (<fil>){
    @F=split (' ');
    if ($F[0] eq $usver){
        $trusv= $F[1];
    }
    }#while fil
    close (fil);

    $tra="$conf_access_log";
    open fil, "<$tra" or $state="gluk";
    if ($state eq 'gluk'){
	print "$msg[7] $msg[503] $usver $msg[83]<br>";
	goto l1;
    }
    while (<fil>){
    @F=split (' ');
#MOD# do not remove this!!!
    if ($F[7] eq $logu{$usver}){
        $trusv= $trusv+$F[4];
    }
    }#while fil
    close (fil);

    $trm="$conf_stc_path/traffic.users";
    open fil, "<$trm" or $state="gluk";
    if ($state eq 'gluk'){
	print "$msg[7] $msg[503] $usver $msg[83]<br>";
	goto l1;
    }
    while (<fil>){
    @F=split (' ');
    if ($F[0] eq $usver){
        $maxusv= $F[1];
    }
    }#while fil
    close (fil);
    if ($maxusv eq "NL"){
	print "<center><b>UNLIMIT USER!</b><br><br>";
	print "$msg[504]<br></center>";
	goto l1;
    }
    $leftusv=$maxusv-$trusv;

    #Get current otdel reserv
    $oquota=get_otdel_reserv($ot);

    if ($oquota eq "DENIED"){
	print "<center>$msg[85] \"$ot\"<br>";
	print "<br>$msg[500]<br><br></center>";
	goto l1;
    }
    
    $prq=$oquota/$conf_mega_byte;
    
    print "<form>";
    print "<p align=center>";
    print "$msg[86] <b>$usver</b><br><br>";
    print "<table size=70%>";
    printf ("<tr><td>$msg[87]:</td><td>%.06f $msg[94]</td></tr>",$prq);
    printf ("<tr><td>$msg[120] <b> $usver</b>:</td><td>%.03f $msg[94]</td></tr>", $maxusv/$conf_mega_byte);
    printf ("<tr><td>$msg[33] <b> $usver</b>:</td><td>%.06f</td></tr><tr><td>$msg[89] <b>$usver</b>:</td><td>%.06f</td></tr>", $trusv/$conf_mega_byte, $leftusv/$conf_mega_byte);
    print "</table>";

    print "<input type=hidden name=user value=$usver>";
    print "<input type=hidden name=otd value=$ot>";
    print "<input type=hidden name=action value=\"change\">";

    print "<br><br>";
    print "<table width=50%>";
    print "<table cellspacing=$bigsp>";

    print "<tr>";
    print "<td>$msg[90]:</td>";
    print "<td><input type=text name=lim size=20></td>";
    print "</tr>";

    
    print "<tr>";
    print "<td align=center><input type=submit value=\"$msg[26]\"></td>";
    print "<td style=text-align:right><input type=reset value=\"$msg[27]\"></td>";
    print "</tr>";
    print "</table>";
    
    print "</p>";

    $limit=$query->param(lim) * $conf_mega_byte;
    $action=$query->param(action);

    if($action ne "change"){goto l1;}
    #Checking input values	
    if (($usver ne '') and ($limit ne '')){
      if($limit>=0){
        $t=$oquota-$limit;
        $m=0;
      }
      else{
        $m=$leftusv-abs($limit);
        $t=0;
      }

      if(($t >= 0) and ($m >= 0)){
	 open ff, "$conf_stc_path/o$ot.users";
	 $us_ctrl="obaba";
	 while (<ff>){
	   @F = split (' ');
	   if ($usver ne $F[0]){next;}
	   else{
	     $us_ctrl="OK";
	   }
	 }#while ff
	 close (ff);
	 if ($us_ctrl eq "OK"){
            my $logfile="$conf_stc_path/traffic.users";
            my @thisarray;
            open(LR,"$logfile") or print "$msg[2] $logfile: $!<br>";
            flock(LR,1) or print "$msg[3] $logfile: $!<br>";
            @thisarray = <LR>;
            close(LR) or print "$msg[4] $logfile: $!<br>";
            my @tmp;
            foreach (@thisarray) {
                @tmp = split(/ /);
                if ($tmp[0] eq $usver) {
            $addlim1=$tmp[1]+$limit;
                    $tmp[1] = "$addlim1\n";
                    $_ = join(' ', @tmp);
                }
            }#foreach thisarray
            open(LR,"> $logfile") or print "$msg[2] $logfile: $!<br>";
            flock(LR,1) or print "$msg[3] $logfile: $!<br>";
            print LR @thisarray;
            close(LR) or print "$msg[4] $logfile: $!<br>";
    
            my $logfile="$trotd";
	    my @thisarray;
            open(LR,"$logfile") or print "$msg[2] $logfile: $!<br>";
            flock(LR,1) or print "$msg[3] $logfile: $!<br>";
	    @thisarray = <LR>;
            close(LR) or print "$msg[4] $logfile: $!<br>";
            my @tmp;
            foreach (@thisarray) {
                @tmp = split(/ /);
                if ($tmp[0] eq $ot) {
        	    $addlim=$tmp[1]-$limit;
                    $tmp[1] = "$addlim\n";
                    $_ = join(' ', @tmp);
                }
            }#foreach thisarray
            open(LR,"> $logfile") or print "$msg[2] $logfile: $!<br>";
            flock(LR,1) or print "$msg[3] $logfile: $!<br>";
            print LR @thisarray;
            close(LR) or print "$msg[4] $logfile: $!<br>";

	    print "<p align=center>";
	    $prq=$addlim/$conf_mega_byte;
	    print "$msg[92]:<br><br>";

	    print "<table size=70%>";
	    printf ("<tr><td>$msg[87]:</td><td>%.06f $msg[94]</td></tr>",$prq);
	    printf ("<tr><td>$msg[120] <b> $usver</b>:</td><td>%.03f $msg[94]</td></tr>", ($maxusv+$limit)/$conf_mega_byte);
	    printf ("<tr><td>$msg[33] <b> $usver</b>:</td><td>%.06f</td></tr><tr><td>$msg[89] <b>$usver</b>:</td><td>%.06f</td></tr>", $trusv/$conf_mega_byte, ($leftusv+$limit)/$conf_mega_byte);
	    print "</table>";

#    	    printf ("$msg[93]: %.06f $msg[94]<br>",$prq);
#	    printf ("$msg[120] <b>$usver</b>: %.03f $msg[94]<br>", ($maxusv+$limit)/$conf_mega_byte);
#    	    printf ("$msg[33] <b> $usver</b>: %.06f <br>$msg[95] <b>$usver</b>: %.06f", $trusv/$conf_mega_byte, ($leftusv+$limit)/$conf_mega_byte);
	    print "</p>";

    }#if us_ctrl
    else{
        print "<b>$msg[7]</b> $msg[96] $usver $msg[97] $ot!!!<br>";
    }
      }#if $oquota
      else{
        print "$msg[98]<br>";
      }
    }#if limit ne ''
    else{
	print "$msg[7]<br>";
    }
l1:
}#if not looser
else{
    print "<center><b>$msg[5]<b></center><br>";
}
print "</form>";

print "<form action=\"total.cgi\" method=\"POST\">";
print "<input type=hidden name=otdel value=$ot>";
print "<center><input type=submit value=\"$msg[53]\"></td>";
print "</form>";

&load_footer;

