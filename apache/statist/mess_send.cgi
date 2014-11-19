#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

$max_word=30;
$max_tema=80;

use Time::localtime;
$scode="ok";
require "./init_stc.pl";
&get_conf;
&get_profile("$user");
&load_header("Send Messages");
&init_stc;

$query=new CGI;

$user=$ENV{"REMOTE_USER"};
$start_usver=$query->param(start_user);
$start_tema=$query->param(start_tema);
$back_url=$query->param(back_url);
$back_otd=$query->param(back_otd);
$back_url1=$query->param(back_url1);
$start_from_admin=$query->param(start_from_admin);
$page=$query->param(page);
$language="rus-1251";

print "<center>";
if (!safe_url($back_url, 'mess_send.cgi')){goto l1;}

if (($conf_web_messages eq 'admin') or ($conf_web_messages eq 'all')){
    print "$msg[69]<br>";
    print "<br>$msg[70]<br>";
    print "<form method=\"POST\">";

    print "<input type=hidden name=user value=$usver>";
    print "<input type=hidden name=start_from_admin value=$start_from_admin>";
    print "<input type=hidden name=start_user value=$start_usver>";
    print "<input type=hidden name=back_url value=$back_url>";
    print "<input type=hidden name=back_url1 value=$back_url1>";
    print "<input type=hidden name=back_otd value=$back_otd>";
    print "<input type=hidden name=page value=$page>";    

    print "<table width=50%>";
    print "<tr>";
    print "<td>$msg{mess_to}:</td>";
    print "<td><input type=text name=usver size=20 value=\"$start_usver\"></td>";
    print "</tr>";
    if ($admin{$user}){
	print "<tr>";
	
	if($start_from_admin eq 'on'){
	    print "<td><input type=checkbox name=from_admin checked></td><td>$msg[74]</td>";
	}else{
	    print "<td><input type=checkbox name=from_admin></td><td>$msg[74]</td>";
	}
	print "</tr>";
    }
    print "<tr>";
    print "<td>$msg[63]:</td>";
    print "<td><input type=text name=tema size=60 value=\"$start_tema\"></td>";
    print "</tr>";
    print "<tr>";
    print "<td>$msg[75]:</td>";
    print "<td><textarea name=message rows=10 cols=60></textarea></td>";
    print "</tr>";
    print "<tr align=center>";
    print "<td align=center><input type=submit value=\"$msg[76]\"></td>";
    print "<td style=text-align:right><input type=reset value=\"$msg[77]\"></td>";
    print "</tr>";
    print "</table>";
    print "</form>";
    
    $usver=$query->param(usver);
    $message=$query->param(message);
    $tema1=$query->param(tema);
    $from_admin=$query->param(from_admin);

    $message1="";
    @tmp=split(//,$message);
    $k=@tmp;
    $word_count=0;
    for($i=0;$i<=$k;++$i){
	++$word_count;
	if($tmp[$i] eq " "){$word_count=0;}
	if($tmp[$i] eq "<"){next;}
	if($tmp[$i] eq ">"){next;}
	if($tmp[$i] eq ""){next;}
	if($tmp[$i] eq "#"){next;}
	if($word_count>=$max_word){
	    $message1=$message1."-<br>";
	    $word_count=0;
	}
	if($tmp[$i] eq "\n"){
	    $message1=$message1."<br>";
	}
	else{
	    $message1=$message1.$tmp[$i];
	}
    }

    $tema="";
    @tmp=split(//,$tema1);
    $k=@tmp;
    if ($k>$max_tema){$k=$max_tema;}
    for($i=0;$i<=$k;++$i){
	if($tmp[$i] eq "<"){next;}
	if($tmp[$i] eq ">"){next;}
	if($tmp[$i] eq ""){next;}
	if($tmp[$i] eq "#"){next;}
	if($tmp[$i] eq "\n"){
	    $tema=$tema."<br>";
	}
	else{
	    $tema=$tema.$tmp[$i];
	}
    }

  if ($usver ne ''){
    if((($admin{$user} eq 'yep') and ($conf_web_messages eq 'admin')) or ($usver eq 'Administrator') or ($conf_web_messages eq 'all')){
	if(($u_exist{"\L$usver"} eq "TRUE") or ($usver eq 'Administrator')){
	    mkdir ("$conf_stc_path/messages/users/$usver", 0755);
	    open usmesfil, ">>$conf_stc_path/messages/users/$usver/messages.dat" or print "Error: $conf_stc_path/messages/users/$usver/messages.dat $!";
	    $loctime=time();
	    $tt=localtime($loctime);
	    printf ("$msg[80] TIME:%02d:%02d:%02d<br>",$tt->hour,$tt->min,$tt->sec);
	    if (($admin{$user} eq 'yep') and ($from_admin eq 'on')){
		$from_user="Administrator";
	    }
	    else{
		$from_user=$user;
	    }
	    printf usmesfil "ID#$loctime\nFrom#$from_user\nTema#$tema\nBody#$message1\n";
	    close(usmesfil);
	}
	else{
	    print "<font color=$web_red_font>$msg[78] <b>$usver</b></font><br>";
        }
    }# if messages
    else{
	print "$msg[79]<br>";
    }
  }#if $usver ne ''
    print "<form action=\"$back_url\" method=\"POST\">";
    print "<input type=hidden name=user value=$start_usver>";
    print "<input type=hidden name=back_url value=$back_url1>";
    print "<input type=hidden name=back_otd value=$back_otd>";
    print "<input type=hidden name=page value=$page>";
    print "<input type=submit value=\"$msg[53]\">";
    print "</form>";
}#if web_messages
else{
    print "$msg[68]<br>";
}

print "</center>";
l1:
#open foot, "$www_data_path/stat/footer.htm" or print "</body>";
#while (<foot>){
#    print;    
#}#while foot
#close (foot);
&load_footer;
