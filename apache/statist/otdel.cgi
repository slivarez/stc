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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with STC; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

$scode="ok";
require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("Units");
&init_stc;
print "$jf_SubmitDelete";

$q = new CGI;
$save = $q->param(save);
$action = $q->param(action);
$in_otdel = $q->param(otdel);
$add_otdel = $q->param(add_otdel);
$otd_name = $q->param(otd_name);

print "<p align=center>$msg[111] <b>$user</b>!</p>";

#$tt = adv_boss_chk($user, $in_otdel, "manage_res");
#print "U: $user; IN: $in_otdel; !: $tt  SAVE: $save<br>";

#print "DEBUG: $user == $admin{$user}; add_otd == $add_otdel<br>";
if (($admin{$user}) and ($add_otdel)){
#print "addinf new otdel<br>";
    $in_otdel =~ s/\D+//g;
    $in_otdel = 0 + $in_otdel;
    $ERR = "Empty unit number!";
    if ($in_otdel != 0){
       $ERR="unit $in_otdel already exists!";
       open tmp, "<$conf_stc_path/o${in_otdel}.users" or $ERR=undef;
       close (tmp);
    }
    if (!$ERR){
	open tmp, ">$conf_stc_path/o${in_otdel}.users" or $ERR=$!;
	close (tmp);
        if (!$ERR){
	    system ("echo $in_otdel:$otd_name >> $conf_stc_path/allign.otdel");
	    push @otdels, $in_otdel;
	    $otdel_prn{$in_otdel}=$otd_name;
        }
	else {
	    print "$msg{error} $conf_stc_path/o${in_otdel}.users: $ERR<br>";
	    logmsg(__FILE__." line ".__LINE__.":[ERROR] $user otdel.cgi $conf_stc_path/allign.otdel: $ERR");
	}
    }
    else {
	print "$msg{error} $conf_stc_path/o${in_otdel}.users: " if ($ERR ne "Empty unit number!");
 	print "$ERR<br>";
	logmsg(__FILE__." line ".__LINE__.":[ERROR] $user otdel.cgi $conf_stc_path/allign.otdel: $ERR");
    }

}

if ($save){
    my @otdels1 = @otdels;
    foreach (@otdels1){
	my $otdel = $_;
	if (!$otdel){next;}
	$new_res = $q->param("res_$otdel");
	$new_res = $new_res * $conf_mega_byte;
	if (!$new_res){next;}
	if (!adv_boss_chk($user, $otdel, "manage_res")){next;}

	my $logfile="$conf_stc_path/cur_tr.otdel";
        my @thisarray;
        open(LR,"$logfile") or print "Can't open $logfile: $!<br>";
        flock(LR,1) or print "Can't flock $logfile: $!<br>";
        @thisarray = <LR>;
        close(LR) or print "Can't close $logfile: $!<br>";
        my @tmp;
	$done=undef;
        foreach (@thisarray) {
            @tmp = split(/\s+/);
	    if (($tmp[0] == $otdel) and $done){
		$tmp[0]="";$tmp[1]="";$_ = join('', $tmp[0], $tmp[1]);
	    }
	    if (($tmp[0] == $otdel) and !$done){
		$tmp[1]="$new_res\n";
		$_ = join(' ', $tmp[0], $tmp[1]);
		$done="done";
	    }#if tmp[0]
        }#foreach thisarray
        open(LR,"> $logfile") or print "Can't open $logfile: $!<br>";
        flock(LR,1) or print "Can't flock $logfile: $!<br>";
        print LR @thisarray;
        close(LR) or print "Can't close $logfile: $!<br>";
    }#foreach
}#if save

if (adv_boss_chk($user, $in_otdel, "manage_res")){
  if ($action eq "enable"){system ("echo \"$in_otdel 0\" >> $conf_stc_path/cur_tr.otdel");}
  if ($action eq "disable"){
	my $logfile="$conf_stc_path/cur_tr.otdel";
        my @thisarray;
        open(LR,"$logfile") or print "Can't open $logfile: $!<br>";
        flock(LR,1) or print "Can't flock $logfile: $!<br>";
        @thisarray = <LR>;
        close(LR) or print "Can't close $logfile: $!<br>";
        my @tmp;
        foreach (@thisarray) {
            @tmp = split(/\s+/);
	    if ($tmp[0] == $in_otdel){$tmp[0]="";$tmp[1]="";$_ = join('', $tmp[0], $tmp[1]);}
        }#foreach thisarray
        open(LR,"> $logfile") or print "Can't open $logfile: $!<br>";
        flock(LR,1) or print "Can't flock $logfile: $!<br>";
        print LR @thisarray;
        close(LR) or print "Can't close $logfile: $!<br>";

  }#if action
  if ($admin{$user} and ($action eq "delete")){
    &delete_otdel($in_otdel);
    foreach (@otdels){
	if ($_ == $in_otdel){$_="";}
    }#foreach
  }#if action
}#if adv_boss_chk
else {
  if ($action eq "enable"){print "ERROR: $msg[5]<br>";}
  if ($action eq "disable"){print "ERROR: $msg[5]<br>";}
} 

print "<center>";
print "<form method=GET>";
print "<table width=70% border=1>";
print "<tr><th>#</th><th>$msg{otdel_name}</th>";
print "<th>$msg{reserve}</th><th>$msg{otd_res_action}</th>";
if ($admin{$user}){print "<th>\u$msg{delete} $msg{otdel}</th>";}
print "</tr>";

    @otdels=sort(@otdels);
    foreach (@otdels){
	my $otdel = $_;
	if (!$otdel){next;}
	if (!adv_boss_chk($user, $otdel, "view_stat")){next;}
        $name="";
        $name=$otdel_prn{$otdel};
        if ($name eq "") {$name="# $_";}
	my $reserv = get_otdel_reserv($otdel);
	print "<tr><td>$otdel</td><td>$name</td>";
	
	if ($reserv eq 'DENIED'){
	    print "<td>$msg{res_blocked}</td>";
	    if (adv_boss_chk($user, $otdel, "manage_res")){
		print "<td><a href=\"otdel.cgi?otdel=$otdel&action=enable\">$msg{enable}</a></td>";
	    }
	    else{
		print "<td>$msg{enable}</td>";
	    }
	}
	else{
	    $reserv = $reserv/$conf_mega_byte;
	    if (adv_boss_chk($user, $otdel, "manage_res")){
		print "<td><input size=9 type=edit name=res_${otdel} value=$reserv></td>";
		print "<td><a href=\"otdel.cgi?otdel=$otdel&action=disable\" onClick=\"javascript:return SubmitDelete('$msg{submit_ores_disable}');\">$msg{disable}</a></td>";
	    }
	    else{
		print "<td>$reserv</td>";
#		print "<td>$msg{disable}</td>";
		print "<td>&nbsp;</td>";
	    }
	}
	if ($admin{$user}){
	    print "<td><a href=\"otdel.cgi?otdel=$otdel&action=delete\" onClick=\"javascript:return SubmitDelete('$msg{submit_otdel_delete}');\">$msg{delete}</td>";
	}
	print "</tr>";
    }#for
print "</table><br>";
print "<input type=submit name=save value=\"$msg{submit}\">";
print "</form>";

if ($admin{$user}){
    print "<br><br>";
    print "<form method=POST>";
    print "<b>$msg{create_otdel}</b>";
    print "<table border=0>";
    print "<tr><td>$msg{otdel_num}:</td>";
    print "<td><input type=edit size=3 name=otdel></td></tr>";
    print "<tr><td>$msg{otdel_name}:</td>";
    print "<td><input type=edit size=25 name=otd_name></td></tr>";
    print "</table>";
    print "<input type=submit name=add_otdel value=\"$msg{add_otdel}\">";
    print "</form>";
}#if admin

print "</center>";

&load_footer;
