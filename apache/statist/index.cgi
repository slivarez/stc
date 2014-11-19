#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

$language="rus-1251";
$scode="ok";
require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("Index page");
&init_stc;
$query=new CGI;
$action=$query->param(action);

open tmp, "$conf_www_data_path/stat/index.html";
while(<tmp>){
    print;
}
close tmp;

&load_footer;
