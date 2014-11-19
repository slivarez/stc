#!/usr/bin/perl
#Copyright (C) 2003  Didenko A.V.
#created by Didenko A.V. e-Mail:slivarez@list.ru

use Time::localtime;
$ucount = 0;

open cf, "</etc/stc.conf";
while(<cf>){
    @F=split(/\s+/);
    if ($F[0] eq '#'){next;}
    if ($F[0] eq 'stc_path'){
	$stc_path=$F[1];
    }
}
close (cf);

$tm = localtime;
$m = $tm->mon;

if ($m<1){$m=12;}

system ("cp $stc_path/cur_tr.users $stc_path/cur_tr.m$m");
