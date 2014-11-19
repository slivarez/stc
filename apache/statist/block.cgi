#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

$language="rus-1251";
$scode="ok";
require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("Total access control");
&init_stc;
$query=new CGI;
$action=$query->param(action);

if($admin{$user} eq 'yep'){
    $tm=localtime;
    if ($action eq 'block'){
        system ("cp $conf_stc_path/squidGuard.conf.profil $conf_SGC_path/squidGuard.conf");
        print ("$msg[38]<BR>");
    
        open log_f, ">>$conf_stc_path/users.log";
        printf log_f "BL $tm $user\n";
        close(log_f);
    }
    if ($action eq 'unblock'){
        system ("cp $conf_stc_path/squidGuard.conf.allow $conf_SGC_path/squidGuard.conf");
        print ("$msg[143]<BR>");

        open log_f, ">>$conf_stc_path/users.log";
        printf log_f "UB $tm $user\n";
        close(log_f);
    }
}#if ADMIN
else {
    print "<p align=center><font size=5>$msg[5]</font></p><br>";
}

&load_footer;
