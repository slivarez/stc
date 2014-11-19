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

$url = 'logout:logout@' . $ENV{'HTTP_HOST'};
$url .= $ENV{'SCRIPT_NAME'};
if (!$ENV{'HTTPS'}){$url = "http://$url";}
else {$url = "https://$url";}

print "<br><br><center>$msg{'logout_msg'}<br><br>";
print "<a href=\"$url\">$msg{'logout_confirm'}</a><br></center>";

&load_footer;

