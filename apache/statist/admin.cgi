#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

$scode="ok";
require "./init_stc.pl";
$fs=1;


&get_conf;
&get_profile("$user");

$query=new CGI;

&load_header("Admin page");
&init_stc;
    if ($query->param('s_month') eq '')
    {
        $mm=(localtime)[4]+1;
    }
    else 
    {
	$mm =$query->param('s_month');
    }

print $set_pointer;

print "<center>";

if($admin{$user} eq 'yep'){

    print "<hr>";
    print "<a href='adduser.cgi?back_url=admin.cgi'>$msg[28]</a><br><br>";
    print "<a href='supasswd.cgi?back_url=admin.cgi'>$msg[29]</a><br><br>";
    print "<a href='update_utr.cgi?back_url=admin.cgi'>$msg[30]</a><br><br>";

    print "<br><table width=100% align=center>";
    print "<tr>";
#    print "<td align=center><a href=\"block.cgi?action=block\">$msg[122]</a></td>";
#    print "<td align=center><a href='block.cgi?action=unblock'>$msg[123]</a></td>";
    print "<form action=\"block.cgi\" method=\"POST\">";
    print "<input type=hidden name=\"action\" value=\"block\">";
    print "<td align=center><input type=submit value=\"$msg[122]\"></td>";
    print "</form>";
    print "<form action=\"block.cgi\" method=\"POST\">";
    print "<input type=hidden name=\"action\" value=\"unblock\">";
    print "<td align=center><input type=submit value=\"$msg[123]\"></td>";
    print "</form>";

    print "</tr>";
    print "</table><br>";

#    print "<a href='addotdel.cgi'>Добавить новый отдел</a><br><br>";
#    print "<a href='delotdel.cgi'>Удалить отдел</a><br><br>";    
    print "<hr>";
    print "<b>$msg[51]</b><br><br>";
    print "<form action=dpools.cgi>";
    print "<input type=hidden name=back_url value=\"admin.cgi\">";
    print "<input type=submit value=\"$msg[52]\">";
    print "</form>";
    print "<hr>";
    print "<b>$msg[31]</b><br><br>";
    print "<form method=\"POST\">";
    print "<table width=50%>";

    print "<tr>";
    print "<td>$msg[32]:</td>";
print "<td><select name=s_month>";

for ($i=1; $i<=12; $i++)
     {
      print "<option value=$i";
        if ($mm eq $i) {print " selected";}
      print ">".$msg[(400+$i)]."</option>\n";
     }
print "</select>";

    print "</td>";
    print "</tr>";

    print "<input type=hidden name=act value=\"getstat\">";
    print "<tr align=center>";
    print "<td><input type=submit value=\"$msg[26]\"></td>";
    print "<td style=text-align:right><input type=reset value=\"$msg[27]\"></td>";
    print "</tr>";
    print "</table>";
    print "</form>";

#    $mm=$query->param(s_month);

    $act=$query->param(act);
    if ($act eq "getstat"){
	$total=0;
        $mon=(localtime)[4]+1;
#	&get_profile_all;

#	get_adm_stat();
	if($mon == $mm){
	    open crtf, "<$conf_stc_path/cur_tr.users" or print "$msg[2] <b>cur_tr.m$mm</b>: $!<br><br>";
	}
	else{
	    open crtf, "<$conf_stc_path/cur_tr.m$mm" or print "$msg[2] <b>cur_tr.m$mm</b>: $!<br><br>";
	}
	while (<crtf>){
	    @F=split(' ');
	    if ($F[0] ne ""){
		$traffic1{$F[0]}=$F[1];
	    }
	}
	close (crtf);
	for ($i=0;$i<999;++$i){
	    $E='OK';
	    $f="$conf_stc_path/o$i.users";
	    open fil, "<$f" or $E='gluk';
	    if ($E ne 'gluk'){
		push(@otdnames,$i);
	    }
	    close (fil);
	}#for
	foreach (@otdnames){
	    $ot=$_;
	    if ($otdel_prn{$ot} ne ""){
		$otdel=$otdel_prn{$ot};
	    }
	    else{
		$otdel=$ot;
	    }
	    print "<br>$msg[33] $otdel (#$ot)<br>";
	    print "<table width=50% border=1>";
	    print "<tr><th>$msg[21]</th><th>$msg[34]</th><th>$msg[35]</th></tr>";
	    open ofil, "<$conf_stc_path/o$ot.users";
	    $total_otd=0;
	    while(<ofil>){
		@F=split(' ');
		&get_profile($F[0]);
		if ($F[0] ne ""){
		    my $cur_user=$F[0];
		    $traffic{$F[0]}=0+$traffic1{$F[0]};
		    $traffic{$F[0]}=$traffic{$F[0]}/$conf_mega_byte;
		    print "<tr $apply_pointer><td>";
		    print "<a href=user_mod.cgi?user=$F[0]&back_url=admin.cgi>$F[0]</a>";
		    print "<td>&nbsp;<font size=$fs>".$user_profile{"${cur_user}_lname"}." ".$user_profile{"${cur_user}_fname"}." ".$user_profile{"${cur_user}_mname"}."</td>";
#		    printf ("</td><td>$domain{$F[0]}</td><td>$F[2] $F[3] $F[4]</td>");
#		    if ($email{$F[0]} ne 'N/A'){
#			printf ("&nbsp;<td><a href=\"mailto:$email{$F[0]}\">$email{$F[0]}</a>");
#		    }
#		    else{
#			printf ("<td>&nbsp;$email{$F[0]}");
#		    }
		    printf ("</td><td>%.06f</td></tr>",$traffic{$F[0]});
		    $total_otd=$total_otd+$traffic{$F[0]};
		}
	    }
	    close (ofil);
	    $total=$total+$total_otd;
	    printf ("<tr><td><b>$msg[37]</b></td><td>&nbsp;</td><td>%.06f</td></tr>",$total_otd);
	    print "</table>";
	}#foreach otdnames
	printf ("<br><b>$msg[36]: %.06f</b><br><br>", $total);
    }#if $act
    print "<hr>";
}
else{
    print "<font color=$web_red_font><b>$msg[5]</b></font>";
}
print "</center>";

#open foot, "$www_data_path/stat/footer.htm" or print "</body>";
#while (<foot>){
#    print;    
#}#while foot
#close (foot);
&load_footer("fullinfo");
