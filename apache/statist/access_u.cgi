#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

$conf_mega_byte=1000000;
$language="rus-1251";

$scode="ok";
require "./init_stc.pl";
&get_conf;
&get_profile("$user");
&load_header("Access control page");
&init_stc;

$query=new CGI;

$back_url=$query->param(back_url)."?";
$usver=$query->param(user);
$action=$query->param(action);
$otdel=$query->param("otdel");
if ($otdel ne ""){$back_url=$back_url."&otdel=$otdel";}
if (!safe_url($back_url, 'access_u.cgi')){goto l1;}

if($admin{$user} eq 'yep'){
    &get_profile($usver);
    if ($action eq "block"){
	if ($blocked{$usver} ne "TRUE"){
	    if (block_user("$usver")) {print "$msg[155]";}
	}		
    }
    if ($action eq "unblock"){
	if (unblock_user("$usver")){
	   print "$msg[156]";
	}
    }
}#if admin
else{
    print "$msg[5]<br>";
}

print "<center><font size=3><a href=\"$back_url\">$msg[6]</a></font></center>";
l1:

&load_footer;
