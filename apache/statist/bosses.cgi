#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

$language="rus-1251";
$scode="ok";
require "./init_stc.pl";
$font="<font size=1>";
$fonte="</font>";
$fullstring="view_rep user_add user_rm manage_traff manage_res";

&get_conf;
&get_profile("$user");
&load_header("Bosses access control");

$submit=undef;
$query=new CGI;
$action=$query->param(action);
$cur_boss=$query->param(boss);
$usver=$cur_boss;
$submit=$query->param(submit);
$grant=$query->param(grant);
$grant_otd=$query->param(grant_otd);

&init_stc;


#Grant otdel to user 
if ($grant and $admin{$user} and $grant_otd and $u_exist{"\L$cur_boss"}){
    my @tmpprof=undef;
    open upf, "<$conf_stc_path/profiles/${usver}.profile" or print "$msg{\"no_profile_makedef\"}<br>$conf_stc_path/profiles/${usver}.profile: $!";
    while ($stin=<upf>){
	my @tt=split(':', $stin);
	my $tkey=$tt[0];
	$tkey=~s/o//;
	$tkey=0+$tkey;
#	if (($tkey<=999) and ($tkey>=1)){next;}
	chomp ($stin);
	if ($stin) {push @tmpprof, $stin;}
    }
    close upf;
    push @tmpprof, "o$grant_otd:";
    sleep 1;
    open upf, ">$conf_stc_path/profiles/${usver}.profile" or print "Can't open for writing<br>$conf_stc_path/profiles/${usver}.profile: $!";
    foreach (@tmpprof){
	my $tt=$_;
	if (!$tt){next;}
	printf upf "$tt\n";
    }#foreach
    close upf;
}# if grant


if ($submit and $u_exist{"\L$cur_boss"}){
    my @tmpprof=undef;
    open upf, "<$conf_stc_path/profiles/${cur_boss}.profile" or print "$msg{\"no_profile_makedef\"}<br>$conf_stc_path/profiles/${cur_boss}.profile: $!";
    while ($stin=<upf>){
	my @tt=split(':', $stin);
	my $tkey=$tt[0];
	$tkey=~s/o//;
	$tkey=0+$tkey;
	if (($tkey<=999) and ($tkey>=1)){next;}
	chomp ($stin);
	if ($stin) {push @tmpprof, $stin;}
#print "$stin<br>";
    }
    close upf;

  $ot=undef;$ot1=undef;
  foreach (@total_otd){
    my $ot=$_;
    $ot=0+$ot;
    if (!$ot){next;}
    if (!$bosshash{"${cur_boss}_o$ot"}){next;}
    my $ttmain=$query->param("${ot}_view_stat");
    if ($ttmain){
	$ostring{"o$ot"}="o$ot:";
    }#if

    my $tt=$query->param("${ot}_user_add");
    if ($tt and $ttmain){
	$ostring{"o$ot"}=$ostring{"o$ot"}." user_add";
    }#if

    my $tt=$query->param("${ot}_user_rm");
    if ($tt and $ttmain){
	$ostring{"o$ot"}=$ostring{"o$ot"}." user_rm";
    }#if

    my $tt=$query->param("${ot}_view_rep");
    if ($tt and $ttmain){
	$ostring{"o$ot"}=$ostring{"o$ot"}." view_rep";
    }#if

    my $tt=$query->param("${ot}_manage_traff");
    if ($tt and $ttmain){
	$ostring{"o$ot"}=$ostring{"o$ot"}." manage_traff";
    }#if

    my $tt=$query->param("${ot}_manage_res");
    if ($tt and $ttmain){
	$ostring{"o$ot"}=$ostring{"o$ot"}." manage_res";
    }#if

    my $tt=$query->param("${ot}_give_all");
    if ($tt and $ttmain){
	$ostring{"o$ot"}="o$ot:$fullstring";
    }    
#  print "$ostring{\"o$ot\"}<br>";
  push @tmpprof, $ostring{"o$ot"};
  }#foreach otdel
    sleep 1;
    open upf, ">$conf_stc_path/profiles/${cur_boss}.profile" or print "Can't open for writing<br>$conf_stc_path/profiles/${cur_boss}.profile: $!";
    foreach (@tmpprof){
	my $tt=$_;
	if (!$tt){next;}
	printf upf "$tt\n";
    }#foreach
    close upf;
}#if submit


if($admin{$user} eq 'yep'){
#    print "BOSSES:<br>";
    print "<center>";
    if ($u_exist{"\L$cur_boss"}){
    #Output info about required boss
#    $DEBUG=1;
    &get_bosses; #Updating bosses info
	print "<p align=right><a href=\"bosses.cgi\">$msg{'boss_list'}</a></p>";
	print "$msg{cur_boss_info} <b>$cur_boss</b><br><br>";
	print "<table width=80% border=1>";
	print "<th>$msg{otdel}</th><th>$msg{permissions}</th>";
	$ot=undef; $ot1=undef;
	foreach (@total_otd){
	    $ot=$_;
	    my $ot=$_;
	    if ($submit and !$query->param("${ot}_view_stat")){
		$bosshash{"${usver}_o$ot"}=undef;
		next;
	    }
	    if (adv_boss_chk($usver, $ot, 'view_stat')){
	        print "<tr><td style=\"text-align:center;vertical-align:middle\">$otdel_prn{$ot} $bosshash{\"${usver}_o$ot1\"}</td>";
		print "<td style=\"text-align:center;\">";
		#Here we should output some checkboxes
		print "<table border=0>";
		print "<form method=\"POST\">";
		print "<tr><td>$font <b>$msg{\"view_stat\"}</b> $fonte</td><td>&nbsp;</td>";
		print "<td>$font $msg{\"view_reports\"} $fonte</td><td>&nbsp;</td>";
		print "<td>$font $msg{\"add_users\"} $fonte</td><td>&nbsp;</td>";
		print "<td>$font $msg{\"del_users\"} $fonte</td><td>&nbsp;</td>";
		print "<td>$font $msg{\"manage_traffic\"} $fonte</td><td>&nbsp;</td>";
		print "<td>$font $msg{\"manage_reserv\"} $fonte</td><td>&nbsp;</td>";
		print "<td>$font $msg{\"give_all\"} $fonte</td>";
		print "</tr>";

		print "<tr>";
		if (adv_boss_chk($cur_boss, $ot, 'view_stat')){$chk='checked';}
		else {$chk=undef;}
		print "<td><input type=checkbox name=\"${ot}_view_stat\" $chk>";
		print "</td><td>&nbsp;</td>";
		if (adv_boss_chk($cur_boss, $ot, 'view_rep')){$chk='checked';}
		else {$chk=undef;}
		print "<td><input type=checkbox name=\"${ot}_view_rep\" $chk>";
		print "</td><td>&nbsp;</td>";
		if (adv_boss_chk($cur_boss, $ot, 'user_add')){$chk='checked';}
		else {$chk=undef;}
		print "<td><input type=checkbox name=\"${ot}_user_add\" $chk>";
		print "</td><td>&nbsp;</td>";
		if (adv_boss_chk($cur_boss, $ot, 'user_rm')){$chk='checked';}
		else {$chk=undef;}
		print "<td><input type=checkbox name=\"${ot}_user_rm\" $chk>";
		print "</td><td>&nbsp;</td>";
		if (adv_boss_chk($cur_boss, $ot, 'manage_traff')){$chk='checked';}
		else {$chk=undef;}
		print "<td><input type=checkbox name=\"${ot}_manage_traff\" $chk>";
		print "</td><td>&nbsp;</td>";
		if (adv_boss_chk($cur_boss, $ot, 'manage_res')){$chk='checked';}
		else {$chk=undef;}
		print "<td><input type=checkbox name=\"${ot}_manage_res\" $chk>";
		print "</td><td>&nbsp;</td>";
		print "<td><input type=checkbox name=\"${ot}_give_all\">";
		print "</td>";
		print "</tr>";

		print "</table>";
		print "</td>";
		print "</tr>";
	    }
	}#foreach
	print "</table>";
	print "<table width=80%><tr><td style=\"text-align:left;\">";
	print "<input type=hidden name=boss value=$cur_boss>";
	print "<input type=submit name=submit value=\"$msg{\"submit\"}\">";
	print "</form>";
	print "</td><td style=\"text-align:right;\">";
	print "<form method=\"POST\">";
	print "<input type=submit value=$msg{\"back\"}>";
	print "</form>";
	print "</td></tr></table>";

#<grant otdel>
print "
    <form action=bosses.cgi method=POST>
    <input type=hidden name=boss value=$cur_boss>
";

    print "<table width=50%>";
    print "<tr><td style=\"text-align:left;\">";
    print "$msg{\"grant_otdel\"}:</td>";
    print "<td style=\"text-align:right;\">";
    print "<select name=grant_otd>";
    my $freeotdel=undef;
    foreach (@otdels){
	if ($bosshash{"${usver}_o$_"}){next;}
	$freeotdel='windows_must_die';
        $name="";
        $name=$otdel_prn{$_};
        if ($name eq "") {$name="# $_";}
        print "<option value=\"$_\"";
#       if ($user_profile{"${usver}_otdel"} eq $_) {print " selected";}
        print ">$name</option>";
    }#for
    if (!$freeotdel){print "<option value=\"\">$msg{empty_otdel}</option>"};
    print "</select></td></tr>";

    print "<tr><td colspan=2 style=\"text-align:center;\">";
    if ($freeotdel){print "<input type=submit name=\"grant\" value=\"$msg{\"grant_button\"}\">";}
    print "</td></tr>";
    print "</table>";
    print "</form>";
    print "<br><br>";
#</grant otdel>

    }#if cur_boss
    else{
    #Output summary info
	&print_bosses();
    }
    print "</center>";
}#if ADMIN
else {
    print "<p align=center><font size=5>$msg[5]</font></p><br>";
}

&load_footer;
