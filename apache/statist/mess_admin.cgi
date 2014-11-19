#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru
$language="rus-1251";

use Time::localtime;
$scode="ok";
require "./init_stc.pl";
&get_conf;
&get_profile("$user");
&load_header("View Messages for Admin");
&init_stc;

$query=new CGI;

$suser=$ENV{"REMOTE_USER"};
$start_usver=$query->param(start_user);
$back_url=$query->param(back_url);
$back_otd=$query->param(back_otd);
$back_url1=$query->param(back_url1);
$mess_kill=$query->param(mess_kill);
$mess_id=$query->param(mess_id);
$page=$query->param(page);
if ($page eq ''){$page=0;}

print "<center>";
#Security check
if (!safe_url($back_url, 'mess_admin.cgi')){goto l1;}
#end of security check

if ($admin{$suser} eq 'yep'){
print "Hi, <b>$suser</b>.<br><br>";

print "<form method=\"POST\">";
print "<input type=submit value=\"$msg[55]\">";
print "</form>";

print "<form action=\"mess_send.cgi\" method=\"POST\">";
print "<input type=hidden name=back_url value=mess_admin.cgi>";
print "<input type=hidden name=start_from_admin value=\"on\">";
print "<input type=submit value=\"$msg[56]\">";
print "</form>";

print "<form action=\"mess_msend.cgi\" method=\"POST\">";
print "<input type=hidden name=start_from_admin value=\"on\">";
print "<input type=hidden name=back_url value=mess_admin.cgi>";
print "<input type=submit value=\"$msg[57]\">";
print "</form>";

print "<form action=\"mess_view.cgi\" method=\"POST\">";
print "<input type=submit value=\"$msg[58] $suser\">";
print "</form><br>";

print "$msg[59]<br><br>";
$user="Administrator";
open lastfil, "<$conf_stc_path/messages/users/$user/lastmess.$suser";
while(<lastfil>){
    @F=split (' ');
    if ($F[0] ne '') {$last_mess=$F[0];}
}
close (lastfil);

if (($conf_web_messages eq 'admin') or ($conf_web_messages eq 'all')){
if ($mess_kill eq "yes"){
        my $logfile="$conf_stc_path/messages/users/$user/messages.dat";
        my @thisarray;
        open(LR,"$logfile") or print "$msg[2] $logfile: $!<br>";
        flock(LR,1) or print "$msg[3] $logfile: $!<br>";
        @thisarray = <LR>;
        close(LR) or print "$msg[4] $logfile: $!<br>";
	my @tmp;
	$killing="FALSE";
        foreach (@thisarray) {
	    @tmp = split('#');
	    $k=@tmp;
    	    if (($tmp[0] eq "ID") and ($tmp[1] == $mess_id)){
		$tmp[0] = "";
		$tmp[1] = "";
                $_ = join('', @tmp);
        	$killing="TRUE";
	    }
	    if (($killing eq "TRUE") and ($tmp[0] eq "ID")){
		$killing="FALSE";
	    }
	    if($killing eq "TRUE"){
		$tmp[0]="";
		$tmp[1]="";
		$_ = join('', @tmp);
	    }
        }#foreach thisarray
        open(LR,"> $logfile") or print "$msg[2] $logfile: $!<br>";
        flock(LR,1) or print "$msg[3] $logfile: $!<br>";
        print LR @thisarray;
        close(LR) or print "$msg[4] $logfile: $!<br>";
}

$mess_count=0;
open messfil, "<$conf_stc_path/messages/users/$user/messages.dat";
while(<messfil>){
    @F=split('#');
    if ($F[0] eq 'ID'){
	++$mess_count;
	$messages[$mess_count]{id}=$F[1];
	$last_id=$F[1];
    }
    if ($F[0] eq 'From'){
	$messages[$mess_count]{from}=$F[1];
    }
    if ($F[0] eq 'Tema'){
	$messages[$mess_count]{tema}=$F[1];
    }
    if ($F[0] eq 'Body'){
	$messages[$mess_count]{body}=$F[1];
    }
}
close (messfil);

if($page == 0){
open lastfil, ">$conf_stc_path/messages/users/$user/lastmess.$suser";
printf lastfil "$last_id\n";
close (lastfil);
}#if page==0

$cur_page=0;
$max_page=0;
for ($i=$mess_count; $i>=1; --$i){
	++$cur_page;
	if($cur_page>$conf_web_mes_per_page){
	    $cur_page=int($cur_page/$conf_web_mes_per_page);
	    ++$max_page;
	}
	$messages[$i]{page}=$max_page;
}#for
if ($page>$max_page){$page=$max_page;}
if ($page<0){$page=0;}

for ($i=$mess_count; $i>=1; --$i){
    if ($messages[$i]{page} != $page){next;}
    $tt=localtime($messages[$i]{id});
	$yy = $tt->year+1900;
	$hh = $tt->hour;
	$mi = $tt->min;
	$ss = $tt->sec;
	$dd = $tt->mday;
	$mm = $tt->mon+1;
    print "<table border=1 width=80%>";
    print "<tr>";
    print "<td class=\"mess_head\"><b>$msg[60]: </b>";
    print "<a href=\"profile.cgi?user=$messages[$i]{from}&back_url=mess_admin.cgi\">$messages[$i]{from}</a>";
    if ($last_mess < $messages[$i]{id}){
	print "<br><font color=\"$web_red_font\"><b>$msg[61]</b></font>";
    }
    print "</td>";
    printf ("<td class=\"mess_head\"><b>$msg[62]: </b>%02d.%02d.%04d<br><b>$msg[82]: </b>%02d:%02d:%02d</td>",$dd,$mm,$yy,$hh,$mi,$ss);
    print "</tr>";

    print "<tr>";
    print "<td colspan=2 class=\"mess_head\"><b>$msg[63]: </b>$messages[$i]{tema}</td>";
    print "</tr>";

    print "<tr>";
    print "<td colspan=2 class=\"mess_body\">$messages[$i]{body}</td>";
    print "</tr>";
    print "</table>";

    print "<table border=0>";
    print "<tr>";
    print "<td>";
    print "<form action=\"mess_send.cgi\" method=\"POST\">";
    print "<input type=hidden name=start_user value=$messages[$i]{from}>";
    print "<input type=hidden name=start_from_admin value=\"on\">";
    print "<input type=hidden name=start_tema value='Re:$messages[$i]{tema}>'";
    print "<input type=hidden name=back_url value=mess_admin.cgi>";
    print "<input type=submit value=\"$msg[64]\">";
    print "</form>";
    print "</td>";

    print "<td>";
    print "<form method=\"POST\">";
    print "<input type=hidden name=mess_id value=$messages[$i]{id}>";
    print "<input type=hidden name=mess_kill value=\"yes\">";
    print "<input type=submit value=\"$msg[65]\">";
    print "</form>";
    print "</td>";
    print "</tr>";

    print "</table>";
    print "<br>";
}
    $next_page=$page+1;
    $prev_page=$page-1;

    print "<table width=50%><tr>";
    if($page>0){
	print "<form action=\"mess_view.cgi\" method=\"POST\">";
        print "<input type=hidden name=page value=$prev_page>";
        print "<td>";
	print "<input type=submit value=\"$msg[66]\">";
        print"</form>";
        print "</td>";
    }
    else{
	print "<td><font color=$web_grey_font>$msg[66]</font></td>";
    }
    if ($page<$max_page){
	print "<form action=\"mess_view.cgi\" method=\"POST\">";
        print "<input type=hidden name=page value=$next_page>";
        print "<td style=text-align:right>";
	print "<input type=submit value=\"$msg[67]\">";
	print"</form>";
        print "</td>";
    }
    else{
	print "<td style=text-align:right><font color=$web_grey_font>$msg[67]</font></td>";
    }
    print "</tr></table>";

}#if web_messages
else{
    print "$msg[68]<br>";
}
}#if admin
else{
    print "$msg[5]<br>";
}
l1:
print "</center>";

#open foot, "$www_data_path/stat/footer.htm" or print "</body>";
#while (<foot>){
#    print;    
#}#while foot
#close (foot);
&load_footer;
