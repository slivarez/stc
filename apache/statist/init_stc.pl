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
#<GLOBAL> - This will execute for all scripts

#use Time::localtime;
#use CGI qw(:standard);
use CGI qw(:standard -no_xhtml);

$user=$ENV{'REMOTE_USER'};

#</GLOBAL>
#--------------------------------------------
sub get_conf{
#Set some inportant vars 
#(default values, in case we can't find them in stc.conf)
$conf_language="english";
$conf_mega_byte=1000000;

#Get vars from conf
    open cf, "</etc/stc.conf" or die "$!";
    while($line=<cf>){
           chomp($line);
           $line=~ s/\#.*$//;
           $line=~ s/[\s\t]{1,}/ /;
           $line=~ s/^[\s\t]{0,}//;
           if (!$line)
                {next;}
           @parts=split(" ", $line);
           $var=shift(@parts);
           $var="conf_".$var;
           @$var=@parts;
           $$var=$parts[0];
    }
    close (cf);
    require "$conf_stc_path/includes/ver.inc";
  #<get_lang>
  $conf_language_file="$conf_stc_path/lang/$conf_language.lng";
  if (-e "$conf_language_file")
    {
    open lfil, $conf_language_file;
    while (<lfil>)
        {
        chomp;
        @F=split(':');
        if ($F[0] ne '')
            {
            $num=0+$F[0];
            $num_=$F[0];
            chomp($num_);
            if ($num)
                {
                $msg[$num]=$F[1];
                chomp ($msg[$num]);
                }
            elsif ($num_)
                {
                $msg{$num_}=$F[1];
                chomp ($msg[$num_]);
                }
            }
        }
    close(lfil);
    }
  else
    {
    logmsg (__FILE__." line ".__LINE__.":[ERROR] Unable to read language file '$conf_language_file'");
  #    exit;
    }
#</get_lang>


################<GLOBAL VARS>
$trotd="$conf_stc_path/cur_tr.otdel";
#@user_boss=undef;
#$user_boss=undef;
#@bosshash=undef;

$set_pointer="
<script language=\"JavaScript\">
<!--
function setPointer(theRow, theRowNum, theAction, thenewColor)
{

    var theCells = null;

    // 1. Pointer and mark feature are disabled or the browser can't get the
    //    row -> exits
    if (typeof(theRow.style) == 'undefined') {
        return false;
    }

    // 2. Gets the current row and exits if the browser can't get it
    if (typeof(document.getElementsByTagName) != 'undefined') {
        theCells = theRow.getElementsByTagName('td');
    }
    else if (typeof(theRow.cells) != 'undefined') {
        theCells = theRow.cells;
    }
    else {
        return false;
    }

    // 3. Gets the current color...
    var rowCellsCnt  = theCells.length;
    var domDetect    = null;
    var currentColor = null;
    var newColor     = null;
    // 3.1 ... with DOM compatible browsers except Opera that does not return
    //         valid values with \"getAttribute\"
    if (typeof(window.opera) == 'undefined'
        && typeof(theCells[0].getAttribute) != 'undefined') {
        currentColor = theCells[0].getAttribute('bgcolor');
        domDetect    = true;
    }
    // 3.2 ... with other browsers
    else {
        currentColor = theCells[0].style.backgroundColor;
        domDetect    = false;
    } // end 3



    // 5. Sets the new color...
//    if (thenewColor) {
        var c = null;
        // 5.1 ... with DOM compatible browsers except Opera
        if (domDetect) {
            for (c = 0; c < rowCellsCnt; c++) {
                theCells[c].setAttribute('bgcolor', thenewColor, 0);
            } // end for
        }
        // 5.2 ... with other browsers
        else {
            for (c = 0; c < rowCellsCnt; c++) {
                theCells[c].style.backgroundColor = thenewColor;
            }
        }
//    } // end 5

    return true;
} // end of the 'setPointer()' function
-->
</script>
";

$jf_SubmitDelete="
<script language=\"JavaScript\">
<!--
function SubmitDelete(msg)
     {
     conf = confirm(msg);
     if (conf) return true;
     else return false;
     }
-->
</script>
";

################</GLOBAL VARS>

#<get u_exist> and <get users>
@users=undef;
@u_exist=undef;
open pasfil, "<$conf_stc_path/password" or logmsg (__FILE__." line ".__LINE__.":[ERROR] Can't open $conf_stc_path/password: $!");
while(<pasfil>){
    my @F=split(':');
	$F[0]=~s/\n//;
    if ($F[0] ne ""){
#	chomp ($F[0]);
	
	push @users, $F[0];
	my $FF="\L$F[0]";
	$u_exist{$FF}="TRUE";
	$user_pass_list{$FF}="TRUE";
    }
}
close (pasfil);
$u_exist{'administrator'}="TRUE";
$u_exist{'looser'}="TRUE";
$u_exist{'logout'}="TRUE";
$u_exist{'root'}="TRUE";
$u_exist{''}=undef;
$user_pass_list{'administrator'}="FALSE";
$user_pass_list{'looser'}="FALSE";
$user_pass_list{'root'}="FALSE";
$user_pass_list{''}="FALSE";
#</get u_exist> and </get users>

#<get_themes>
if (-d "$conf_www_data_path/stat/themes")
    {
    opendir DIR,"$conf_www_data_path/stat/themes";
    foreach $dirs (sort readdir(DIR)) {
        next if ($dirs eq "." || $dirs eq ".." || (!-d "$conf_www_data_path/stat/themes/$dirs") );
        $dirs=~s/^wm_//;
        push (@theme, $dirs);
        }
    closedir (DIR);
    }
else
    {
    logmsg (__FILE__." line ".__LINE__.":[ERROR] Unable to read themes dir '$conf_www_data_path/stat/themes'");
    }
#</get_themes>

#<get_admins>
if (-e "$conf_stc_path/admin.users")
    {
    open bf1, "<$conf_stc_path/admin.users";
    while (<bf1>)
        {
        @F=split (' ');
        $a=$F[0];
        $admin{$a}='yep';
        }
    close (bf1);
    }
else
    {
    logmsg (__FILE__." line ".__LINE__.":[ERROR] Unable to read '$conf_stc_path/admin.users' file");
    }
#</get_admins>

&get_bosses;
    #The following result codes were taken from a Squid-2
    $squid_result_codes{"TCP_HIT"}=0;
    $squid_result_codes{"TCP_MISS"}=1;
    $squid_result_codes{"TCP_REFRESH_HIT"}=0;
    $squid_result_codes{"TCP_REFRESH_FAIL_HIT"}=0;
    $squid_result_codes{"TCP_REFRESH_MISS"}=1;
    $squid_result_codes{"TCP_CLIENT_REFRESH_MISS"}=1;
    $squid_result_codes{"TCP_IMS_HIT"} =0;
    $squid_result_codes{"TCP_SWAPFILE_MISS"}=1;
    $squid_result_codes{"TCP_NEGATIVE_HIT"}=1;
    $squid_result_codes{"TCP_MEM_HIT"} =0;
    $squid_result_codes{"TCP_DENIED"} =0;
    $squid_result_codes{"TCP_OFFLINE_HIT"}=0;
    $squid_result_codes{"TCP_STALE_HIT"}=0;
    $squid_result_codes{"TCP_ASYNC_HIT"}=0;
    $squid_result_codes{"TCP_ASYNC_MISS"}=0;

    $squid_result_codes{"UDP_HIT"} =0;
    $squid_result_codes{"UDP_MISS"} =1;
    $squid_result_codes{"UDP_DENIED"}=0;
    $squid_result_codes{"UDP_INVALID"}=0;
    $squid_result_codes{"UDP_MISS_NOFETCH"}=1;
    $squid_result_codes{"NONE"}=0;

    #The following result codes were taken from a Squid-3
    $squid_result_codes{"UDP_HIT_OBJ"}=0;
    $squid_result_codes{"UDP_RELOADING"}=0;
    $squid_result_codes{"TCP_CLIENT_REFRESH"}=1;
    $squid_result_codes{"TCP_SWAPFAIL"}=1;
    $squid_result_codes{"TCP_IMS_MISS"} =0;
    $squid_result_codes{"TCP_REFRESH_UNMODIFIED"}=0;
    $squid_result_codes{"TCP_REFRESH_MODIFIED"}=1;
    $squid_result_codes{"TCP_SWAPFAIL_MISS"}=1;




if (-r "$conf_sarg_exclude_codes_filelist")
    {
        open ec, "<$conf_sarg_exclude_codes_filelist";
        while (<ec>)
        {
            s/(#.*|\s+)//g;
            next if /^\n$/;
            if (~m/[A-Z\_]{4,6}\/[0-9]{1,3}/) {$sarg_exclude_codes{$_}++;}
        }
        close(ec);
    }

}# get_conf
#---------------------------------------------------------
sub logmsg
{
    my ($mess) = @_;
    my($y,$m,$d) =  (localtime)[5,4,3];
    $y+=1900;
    $m++;
    my $time_now = sprintf "%02d.%02d.%04d %02d:%02d:%02d", $d, $m, $y, (localtime)[2,1,0];
    open LOG_FILE, ">>$conf_log_file";
      print LOG_FILE "$time_now - ", $mess, "\n";
    close (LOG_FILE);
}#logmsg
#---------------------------------------------------------
sub init_stc {
#Set GLOBAL VARS 2
#fff2c0

#<exclude_ip>
if (-e "$conf_exclude_hosts")
    {
    open (EXCLUDELIST, "$conf_exclude_hosts");
    while (<EXCLUDELIST>)
      {
            s/(#.*)//;
            next if /^\n$/;
            if (/^([0-9\.\-a-z]{1,})([:]{0,}[0-9]{0,})\n$/) {$conf_exclude_sites.=$_;}
      }
    close (EXCLUDELIST);
    }
else
    {
    logmsg (__FILE__." line ".__LINE__.":[ERROR] Unable to read exclude IP file '${conf_exclude_hosts}'");
    }
#</exclude_ip>

#<get_onames>
if (-e "$conf_stc_path/allign.otdel")
    {
      open oaf, "<$conf_stc_path/allign.otdel";
      while (<oaf>){
          @F=split('\n');
          $k=@F;
          @name= split(':',$F[0]);
          $otdel_prn{$name[0]}=$name[1];
	  if ($otdel_prn{$name[0]} eq "") {$otdel_prn{$name[0]}="# $otdel";}
      }
      close (oaf);
    }
else
    {
    logmsg (__FILE__." line ".__LINE__.":[ERROR] Unable to read '$conf_stc_path/allign.otdel' file");
    }
#</get_onames>


#<her_ego_znaet>
if ($admin{$user} eq 'yep' || $user_boss{$user} eq 'yep')
{
  opendir(STCETC, $conf_stc_path) or logmsg (__FILE__." line ".__LINE__.":[ERROR] Cannot open '$conf_stc_path' for reading");
  @otdels=();
    foreach (sort readdir(STCETC))
    { # просматриваем папку stc/etc/
        if ($_ =~ /^o[0-9]{1,3}\.users$/) # Если увидели файл типа "o###.users" - который является с
        {
            $otdel=$_;
            $otdel =~ s/^o([0-9]{1,3})\.users$/$1/; # из названия файла получаем название отдела
	    $otdel=0+$otdel;
	    $o_exist{$otdel}='yep';
	    push @total_otd, $otdel;
	    if ($otdel_prn{$otdel} eq "") {$otdel_prn{$otdel}="# $otdel";}
            if (chk_boss_otdel($otdel) eq 'ok')
	    {
                   push @otdels, $otdel;
            } # вставляем в массив отделов текущий номер
        }#if $_
    }#foreach
    closedir(STCETC); # закрываем папку stc/etc/

    #Reading blocked users array
    open blockfil, "$conf_stc_path/blocked.users" or print "$msg[2] $conf_stc_path/blocked.users";
    while (<blockfil>){
        @F=split(' ');
        if ($F[0] eq '') {next;}
        $blocked{$F[0]}="TRUE";
    }
    close (blockfil);

}
#</her_ego_znaet>
$apply_pointer="onmouseover=\"setPointer(this, 0, 'over', '$web_pointer_color');\" onmouseout=\"setPointer(this, 0, 'out', '');\"";
}#init_stc
#---------------------------------------------------------
sub chk_boss_otdel
{
      if ($admin{$user} eq "yep")
          {return 'ok';}

       if ($bosshash{"${user}_o$_[0]"})
               {return 'ok';}
      return 'sux';
}#chk_boss_otdel
#---------------------------------------------------------
sub get_profile
{
#<DEBUG BLOCK>
#$tmpu=$_[0];
#chomp($tmpu);
#$ttm=localtime;
#$megastr1="$ttm GETTING USER_PROFILE: $tmpu<br>";
#print "$megastr1";
#</DEBUG BLOCK>
    $temp=$_[0];
    my $key;
    my $value;
    if ($temp eq '')
        {
        logmsg (__FILE__." line ".__LINE__." :[ERROR] user undefine.");
        goto get_profile_profile_end;
        }
    if (!-e "${conf_stc_path}/profiles/${temp}.profile")
        {
        $user_profile{"${temp}_iface"}="standart";
        logmsg (__FILE__." line ".__LINE__." :[ERROR] user profile file ${conf_stc_path}/profiles/${temp}.profile does not exists");
        goto get_profile_profile_end;
        }
    open upf, "<${conf_stc_path}/profiles/${temp}.profile" or logmsg (__FILE__." line ".__LINE__." :[ERROR] cannot open user profile file '${conf_stc_path}/profiles/${temp}.profile'");
    while (<upf>)
    {
        chomp;
	($key,$value)=split(":");
        $user_profile{"${temp}_${key}"}=$value;
#Handling otdel-boss stuff
#moved to init_stc function 18.02.2005
#	my $tkey=$key;
#	$tkey=~s/o//;
#	$tkey=0+$tkey;
#	if (($tkey<=999) and ($tkey>=1)){
#	    $bosshash{"${temp}_o${tkey}"}='ok';
#	    $user_boss='yep';
#	}
    }
    close (upf);
    if ($user_profile{"${temp}_domain"} ne ''){
        if ($conf_ntlm_userdomain eq 'domainfirst'){
	    $user_profile{"${temp}_logname"} = $user_profile{"${temp}_domain"}.$conf_divide_char.$temp;
	}
	else{
	    $user_profile{"${temp}_logname"} = $temp.$conf_divide_char.$user_profile{"${temp}_domain"};
	}
    }
    else
        {$user_profile{"${temp}_logname"} = "$temp";}

#Global hash $logu and $realuser
    $logu{$temp}=$user_profile{"${temp}_logname"};
    $realuser{$logu{$temp}}=$temp;

    # get limit
get_profile_profile_end:
    open upf, "<${conf_stc_path}/traffic.users" or logmsg (__FILE__." line ".__LINE__.":[ERROR] cannot open limits file '${conf_stc_path}/traffic.users'");
    while (<upf>)
        {
        chomp;
        @F=split(" ");
        if ($F[0] eq $temp)
            {
             $user_profile{"${temp}_limit"}=$F[1];
             goto traffic_users_file_end;
            }
        }
traffic_users_file_end:
    close (upf);
    #get limit end

    #get otdel
  opendir(STCETC, $conf_stc_path) or logmsg (__FILE__." line ".__LINE__.":[ERROR] Cannot open '$conf_stc_path' for reading");
    foreach (readdir(STCETC))
        { # просматриваем папку stc/etc/
        if ($_ =~ /^o[0-9]{1,3}\.users$/) # Если увидели файл типа "o###.users" - который является с
            {
            my $otdelin=$_;
            $otdelin =~ s/^o([0-9]{1,3})\.users$/$1/; # из названия файла получаем название отдела
#system("echo \"$temp: $otdelin\" >> $conf_stc_path/debug");
            open upf, "<${conf_stc_path}/$_" or logmsg (__FILE__." line ".__LINE__.":[ERROR] cannot open otdel file '${conf_stc_path}/$_'");
            while (<upf>)
                {
                chomp;
		@T=split(/\s+/);
                if ($T[0] eq $temp)
                    {
                     $user_profile{"${temp}_otdel"}=$otdelin;
#$megastr=$otdel." User=".$temp." User_profile_otdel=".$user_profile{"${temp}_otdel"};
#system("echo OTDEL FOUND: $megastr >> $conf_stc_path/debug1");
                     close (upf);
                     goto otdel_users_dir_end;
                    }
                }
            close (upf);
            }
        }
   otdel_users_dir_end:
   closedir(STCETC); # закрываем папку stc/etc/
    #get_otdel_end
}#get_profile

#---------------------------------------------------------
sub load_header
{
    my $uri=$ENV{'REQUEST_URI'};
    $Name_Page="STC - $_[0]";
    print header(-charset=>$msg[600]);
    print start_html(-title=>$Name_Page);
    if ($user){open Head, "<$conf_www_data_path/stat/themes/wm_".$user_profile{"${user}_iface"}."/header.htm" or print "<body bgcolor=\"#F4F4F4\">\n";}
    else {open Head, "<$conf_www_data_path/stat/themes/wm_".$conf_default_interface."/header.htm" or print "<body bgcolor=\"#F4F4F4\">\n";}
    $THEME_menu=undef;
    $THEME_menu_row=undef;
#$t=undef;
#open TTF, ">/tmp/tmp.html";
    while (<Head>){
	#Common for all tag-tpl parsing
	$_ =~ s/\@theme\@/wm_$user_profile{"${user}_iface"}/g;
#printf TTF "$win\n";
	#End of tag-tpl parsing
        if ($THEME_menu eq 1){
         if ($_ =~ /\@theme_menu_row_end\@/)
            {
            $tmp=$_;
            $tmp=~s/\@theme_menu_row_end.*\@//;
            $THEME_menu_row.=$tmp;

            &make_menu($THEME_menu_row,$_[1]);

            $THEME_menu=undef;
            $_=~s/\@theme_menu_row_end\@.*//;
            print;
            }
         else
             {$THEME_menu_row.=$_;}
        }
    elsif ($_ =~ /\@theme_menu_row_begin\@/)
        {
        $tmp=$_;
        $_=~s/\@theme_menu_row_begin\@.*//;
        print;
        $tmp=~s/.*\@theme_menu_row_begin\@//;
        $THEME_menu_row=$tmp;
        $THEME_menu=1;
        }
    else
        {
        $_ =~ s/\@msg\[([0-9]{1,})\]\@/$msg[$1]/g;
        $_ =~ s/\@msg\[([a-z_]{1,})\]\@/$msg{$1}/g;
        
#       if ($user){$_ =~ s/\@wmod\@/http:\/\/$conf_site_ip\/stat\/themes\/wm_$user_profile{"${user}_iface"}/g;}
#	else {$_ =~ s/\@wmod\@/http:\/\/$conf_site_ip\/stat\/themes\/wm_$conf_default_interface/g;}
	
	if ($_[1] eq 'fullpaths') { $tmp_wmod = 'http://'.$conf_site_ip.'/stat/themes/'; }
        else { $tmp_wmod = '/stat/themes/'; }
        if ($user){ $tmp_wmod.= 'wm_'.$user_profile{"${user}_iface"}; }
        else { $tmp_wmod.= 'wm_'.$conf_default_interface; }
        $_ =~ s/\@wmod\@/$tmp_wmod/g;
        
	$_ =~ s/\@page\@/$Name_Page/;
	$_ =~ s/\@header_text\@/@conf_header_text/;
#printf TTF "$_\n";
        print;
        }
    }#while head
    close(Head);
#close TTF;
#Get some web-interface constants
my $tfile=undef;
if ($user){$tfile="$conf_www_data_path/stat/themes/wm_".$user_profile{"${user}_iface"}."/header.htm";}
else {$tfile="$conf_www_data_path/stat/themes/wm_".$conf_default_interface."/header.htm";}
open tf, "<$tfile" or logmsg(__FILE__." line ".__LINE__.":[ERROR] Can't open header.htm file ($tfile): $!");
my $start_conf=undef;
while ($line=<tf>){
#    my @s=split(/\s+/, $stin);
#    if (!$s[0]){next;}
#    $var="conf_".$s[0];
#    $$var=$s[1];
   chomp($line);
   $line=~ s/\#.*$//;
   $line=~ s/\@/\#/;
   $line=~ s/[\s\t]{1,}/ /;
   $line=~ s/^[\s\t]{0,}//;
   if (!$line)
        {next;}
   @parts=split(/\s+/, $line);
   if ($parts[0] eq '<!--STC_CONF'){$start_conf="start"; next;}
   if ($parts[0] eq 'STC_END-->'){$start_conf=undef; goto l2;}
   if (!$start_conf){next;}
   $var=shift(@parts);
   $var="web_".$var;
   @$var=@parts;
   $$var=$parts[0];
}#while
l2:
close tf;
}#load_header

#---------------------------------------------------------
sub make_menu
    {
    $FullPaths=$_[1];
     ($tmp, $tmp_sep)=@_;
#     $tmp_menu='stc.nixdev.org--http://stc.nixdev.org/-=-';
     $tmp_menu.=$msg{'menu_index'}.'--index--user-=-';
     $tmp_menu.=$msg{'menu_info'}.'--info--user-=-';
     $tmp_menu.=$msg{'menu_stat'}.'--statistic--user-=-';
     if ($user){
         $tmp_menu.=$msg{'menu_reports'}.'--report--user-=-';
         $tmp_menu.=$msg{'menu_chpasswd'}.'--chpasswd--user-=-';

         $tmp_menu.=$msg{'menu_users'}.'--user--boss-=-';
         $tmp_menu.=$msg{'menu_otdels'}.'--otdel--boss-=-';
	 $tmp_menu.=$msg{'menu_bosses'}.'--bosses--admin-=-';
         $tmp_menu.=$msg{'menu_dpools'}.'--dpools--admin-=-';
         $tmp_menu.=$msg{'menu_serverstat'}.'--serverstat--boss-=-';
	 $tmp_menu.=$msg{'menu_adminpage'}.'--admin--admin-=-';
         $tmp_menu.=$msg{'logout'}.'--logout--user-=-';
     }
     @tmp_menu=split("-=-", $tmp_menu);
     foreach (@tmp_menu){
        ($tmp_name, $tmp_href, $tmp_access)=split("--");
        if ($admin{$user} || ($tmp_access eq 'user') || ($user_boss{$user} eq 'yep' && $tmp_access eq 'boss')){
            $tmp_var=$tmp;
            $tmp_var=~s/\@name\@/$tmp_name/sg;
	    if (!($tmp_href =~ /^http\:\/\//)){$tmp_href.='.cgi';}
	    if ((!($tmp_href =~ /^http\:\/\//)) && ($tmp_href =~ /\.cgi$/) && ($FullPaths eq 'fullpaths'))
	      { $tmp_href = 'http://'.$conf_site_ip.'/stat/cgi/'.$tmp_href; }
            $tmp_var=~s/\@href\@/$tmp_href/sg;
	    if ($FullPaths eq 'fullpaths') { $tmp_wmod = 'http://'.$conf_site_ip.'/stat/themes/'; }
	    else { $tmp_wmod = '/stat/themes/'; }
            if ($user){ $tmp_wmod.= 'wm_'.$user_profile{"${user}_iface"}; }
	    else { $tmp_wmod.= 'wm_'.$conf_default_interface; }
	    $tmp_var =~ s/\@wmod\@/$tmp_wmod/g;
            print $tmp_var;
        }
    }
    $tmp_name=$tmp_href=$tmp_access=$tmp_var=undef;
}#make_menu
#---------------------------------------------------------
sub load_footer
{
    #Do not change strings bellow
    print "<br><br><br><center><font size=\"1\">";
    if ($_[0] eq "fullinfo"){
        my $last_ver_info = get_latest_version_from_cache();
        my $lwp_test = check_lwp();
        print "<a href=http://stc.nixdev.org/>Squid Traffic Counter</a> - squid traffic and user managment system.<br>";
        print "Currently installetd version: $version  Release date: $date<br>";
        print "Latest available version: $last_ver_info<br>" unless $last_ver_info =~ /^ERROR:/i;
        print "$lwp_test" unless $lwp_test eq "OK";
        print "<br>";
        print "&copy; 2004-2011 STC Developers Team<br>";
    }
    else{
        print "Powered by <a href=http://stc.nixdev.org/>stc-$version</a> &copy; 2004 STC Developers Team<br>";
    }
    print "</font>";
    print "</center>";
    if ($user){open Head, "<$conf_www_data_path/stat/themes/wm_".$user_profile{"${user}_iface"}."/footer.htm" or print "</body>\n";}
    else{open Head, "<$conf_www_data_path/stat/themes/wm_".$conf_default_interface."/footer.htm" or print "</body>\n";}
    while (<Head>){
    $_ =~ s/\@msg\[([0-9]{1,})\]\@/$msg[$1]/g;
    $_ =~ s/\@msg\[([a-z_]{1,})\]\@/$msg{$1}/g;
    if ($_[1] eq 'fullpaths') { $tmp_wmod = 'http://'.$conf_site_ip.'/stat/themes/'; }
    else { $tmp_wmod = '/stat/themes/'; }
    if ($user){ $tmp_wmod.= 'wm_'.$user_profile{"${user}_iface"}; }
    else { $tmp_wmod.= 'wm_'.$conf_default_interface; }
    $_ =~ s/\@wmod\@/$tmp_wmod/g;
    $_ =~ s/\@footer_text\@/@conf_footer_text/g;
    print;
    }#while head
    close(Head);
}#load_footer
#---------------------------------------------------------
sub get_otdel_reserv{
#INPUT: 	OTDEL_NUMBER
#RETURN:	reserv dlya OTDEL_NUMBER ili 'DENIED' esli net v cur_tr.otdel
#OUTPUT:	NONE
    my $oot=$_[0];
    my $oq="DENIED";
    open fil,"<$trotd"  or print "$msg[7] $msg[2] $trotd: $!<br>";
    while(<fil>){
    @F=split(' ');
    if ($F[0] == $oot){
        $oq=$F[1];
    }#if $ot
    
    }#while fil
    close (fil);
    return $oq;
} #get_oquota
#---------------------------------------------------------
#Security check
sub safe_url{
#INPUT:		URL, PARENT_SCRIPT_NAME
#RETURN:	1- esli URL pravil'naja
#		0- esli URL podozritel'naja
#OUTPUT:	zapis v log esli RETURN=0

my $cur_url=$_[0];
my $script=$_[1];

$danger="NO";
@url_string=split(//, $cur_url);
$uk=@url_string;
for ($i=0;$i<=$uk;++$i){
    if ($url_string[$i] eq '/'){$danger="!";}
    if ($url_string[$i] eq "\\"){$danger="!";}
    if ($url_string[$i] eq '/'){$danger="!";}
    if ($url_string[$i] eq '"'){$danger="!";}
    if ($url_string[$i] eq '`'){$danger="!";}
    if ($url_string[$i] eq '%'){$danger="!";}
    if ($url_string[$i] eq ':'){$danger="!";}
}

if ($danger ne "NO"){
    print "<font color=\"red\" size=4>$msg[10]</font><br><br>";
    $tm=localtime;
#    $day=$tm->mday;
#    $mon=$tm->mon + 1;
#    $year=$tm->year + 1900;
#    $h=$tm->hour;
#    $m=$tm->min;
#    $s=$tm->sec;

    open log_f, ">>$conf_stc_path/users.log";
#    printf log_f "!! $day:$mon:$year $h:$m $user $script $cur_url\n";
    printf log_f "!! $tm $user $script $cur_url\n";
    close(log_f);
    return 0;
}
return 1;
}#chk_url
#end of security check

#---------------------------------------------------------
sub adv_boss_chk{
#INPUT:		USERNAME, OTDEL, ACTION
#RETURN:	1- esli USERNAME imeet pravo vypolnyat' ACTION v otdele #OTDEL
#		0- esli USERNAME ne imeet prava na ACTION v otdele #OTDEL
#OUTPUT:	NONE

    my $user_in=$_[0];
    my $otd_in=$_[1];
    my $act_in=$_[2];

    if ($admin{$user_in} eq 'yep'){return 1;}
    if (($act_in eq 'view_stat') and ($bosshash{"${user_in}_o$otd_in"})){return 1;}
    get_profile($user_in);
    my $str_in=$user_profile{"${user_in}_o$otd_in"};
#print "Ostr: $str_in<br>";
    
    my @tmps=split (/\s+/,$str_in);
    my $k=@tmps;
    for (my $ti=0; $ti<$k; ++$ti){
	if ($tmps[$ti] eq $act_in){return 1;}
    }
    return 0;
}
#---------------------------------------------------------
sub print_bosses{
# INPUT: 	NONE
# RETURN:	NONE
# OUTPUT:	List of bosses and their permissions (main bosses.cgi page)

    print "<table width=80% border=1>";
    print "<th>$msg{user}</th><th>$msg{otdels}</th><th>$msg{action}</th>";
#    print "<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>";
    foreach (@users){
	my $us=$_;
	if (!$u_exist{"\L$us"}){next;}
#	print ">$us: ";
	if ($user_boss{$us}){
	print "<tr><td style=\"text-align:center;vertical-align:middle\"><b><a href=\"user_mod.cgi?user=$us&back_url=bosses.cgi\">$us</a></b></td>";
	print "<td style=\"text-align:center;vertical-align:middle\">";
	foreach (@total_otd){
	    my $ot=$_;
#	    print "$ot="."${us}_o$ot ";
	    if ($bosshash{"${us}_o$ot"}){
	        print " $ot;";
	    }
	}#foreach
	print "</td><td style=\"text-align:center;vertical-align:middle\">";
	print "<form action=\"bosses.cgi\" method=\"GET\">";
	print "<input type=hidden name=boss value=$us>";
	print "<input type=submit value=\"$msg{change_perms}\">";
	print "</form></td></tr>";
	}#if user_boss
    }#foreach
#    }#while pf
#    close pf;
    print "</table>";
}# print_bosses

#---------------------------------------------------------
sub exclude_ip
    {
    if ($_[0]=~m/^\[.+/)         {return 0;}
    my ($ip,$port) = split(/:/,$_[0]);
    # если указан порт
    if ($port ne '')  
	{
	 # если $ip цифровой, то заменится, иначе останется как было.
	 $ip=~s/(\d+)\.(\d+)\.(\d+)\.\d+/\(($ip)|($1.$2.$3.0)|($1.$2.0.0)|($1.0.0.0)|(0.0.0.0)):$port/;
	 #добавим порт для проверки на выходе 
#	 $ip="(".$ip."):$port";
	}
    else
	{$ip=~s/(\d+)\.(\d+)\.(\d+)\.\d+/\($ip)|($1.$2.$3.0)|($1.$2.0.0)|($1.0.0.0)/;}
    #Делаем регулярное выражение, заменяя . на \.
    $ip=~s/\./\\\./;
    return ($conf_exclude_sites =~ /$ip/) || 0;
    }
#sub exclude_ip

#---------------------------------------------------------
sub log_line
    {
     my ($line) = @_;
     ($udate, $loadtime, $user_ip, $code, $size, $method, $url, $user_name, $ip) = split(' ', $line);
     my ($direct, $ip_sp)=split('/', $ip);

    # Пропустить все записи, где не было внешней загрузки и ни каких загрузок
    if ($direct eq 'NONE') {next;}
    if ($url eq '') {next;}

     my ($codestatus, $foo)=split('/', $code);


#MOD# do not remove this!!!
#print "U: $user_profile{\"${usver}_logname\"} <--> L: $user_name <--> R: $realuser{$user_name}<br>";
    # Если пользователь определен, то пропустить все записи, не относящиеся к этому пользователю
    if ($usver ne '') {if ($user_profile{"${usver}_logname"} ne $user_name) {next;}}


    #Определяем откуда были взяты данные - из инета или из кеша
    $no_skip_cache=$squid_result_codes{$codestatus};

    # Отметить "-2" все записи, которые определены для пропуска по коду, а так же пропускаем код ошибки ERR_*.

    if ($conf_skip_cache eq 'yes')
        {
        if ($sarg_exclude_codes{$code} or $code=~m/^ERR_.+/) 
	    {
	    $no_skip_cache=-2;
#	    return ($user_name, $size, $user_ip, -2);
	    }
        }

    #Выделяем хост из URL
    if ($method eq 'CONNECT')
        {
        ($host, $port) = ($url =~ /^([0-9\.\-\_a-z]{1,})([:]{0,}[0-9]{0,})$/);
        if ($host=~m/^(http|error)$/) {next;}
        }
    else
        {
	($proto, $host, $port)=  ($url =~ /([htpf]{0,}):[\/]+([a-z\.\_\-0-9]+)([:]{0,}[0-9]{0,})[\/]{0,}.{0,}/);
        }
    #Формируем ссылку на хост с портом, если он есть.
    $site=$host.$port;
    #Если хост и порт не определились, то берем URL целиком.
    if ($site eq '') {$site = $url;}

    # Отметить "-1" все записи, которые определены для пропуска по хосту.
    if (exclude_ip($ip_sp.$port) or exclude_ip($site)) {return ($user_name, $size, $user_ip, -1);} 

    return ($user_name, $size, $user_ip, $no_skip_cache);

}#log_line

#---------------------------------------------------------
sub get_all_traffic{

if (!-r "$conf_access_log")
    {
    logmsg (__FILE__." line ".__LINE__.":[WARNING] Cannot open log '$conf_access_log': $!");
    print "$msg{'cannot_open'} '$conf_access_log': $!";
    return 0;
    }

open(LOG, "<$conf_access_log") or die "$!";
    while(<LOG>)
    {
    my ($user_name, $size,$foo,$skip_cache) = log_line($_);
#    if ($skip_cache!=1){next;}
    $totaltraffic += $size;
    $traffic{$realuser{$user_name}} +=  $size;
    $usage{$realuser{$user_name}}{$site} += $size;
    }# while LOG
close(LOG);

if (!-r "$conf_stc_path/cur_tr.users")
    {
    logmsg (__FILE__." line ".__LINE__.":[WARNING] Cannot open '$conf_stc_path/cur_tr.users': $!");
    print "$msg{'cannot_open'} '$conf_stc_path/cur_tr.users': $!";
    return 0;
    }
open cur_tr, "<$conf_stc_path/cur_tr.users" or die "$!";
    while (<cur_tr>)
    {
    ($cur_user,$cur_traffic)=split(' ');

    if ($u_exist{"$cur_user"}) {
	$traffic{$cur_user}+=$cur_traffic;
	}
    }
close (cur_tr);


return 1;
}#get_all_traffic

#---------------------------------------------------------
sub get_traffic{

  my $userin=$_[0];
  my $line = undef;

if (!-r "$conf_access_log")
    {
    logmsg (__FILE__." line ".__LINE__.":[ERROR] Cannot open log '$conf_access_log': $!");
    print "$msg{'cannot_open'} '$conf_access_log': $!";
    return 0;
    }

open(LOG, "<$conf_access_log") or die "$!";
while($line=<LOG>)
{
    my ($udate, $loadtime, $user_ip, $code, $size, $method, $url, $user_name, $ip) = split(' ', $line);
    my ($direct, $ip_sp)=split('/', $ip);
    my ($codestatus, $foo)=split('/', $code);

#MOD# do not remove this!!!

    if ($url eq '') {next;}
    if ($logu{$userin} ne $user_name){next; }
    if ($direct eq 'NONE') {next;}
    if ($conf_skip_cache eq 'yes') {if ($sarg_exclude_codes{$code} or $code=~m/^ERR_.+/)  {next;} }
    if (!$squid_result_codes{$codestatus}) {next;}
    if ($method eq 'CONNECT')
        {
        ($host, $port) = ($url =~ /^([0-9\.\-\_a-z]{1,})([:]{0,}[0-9]{0,})$/);
        if ($host eq '' or $host =~ /(http|error)/) {next;}
        }
    else
        {
	($proto, $host, $port)=  ($url =~ /([htpf]{0,}):[\/]+([a-z\.\_\-0-9]+)([:]{0,}[0-9]{0,})[\/]{0,}.{0,}/);
        }
    if (exclude_ip($ip_sp) or exclude_ip($host)) {next;}
    $traffic{$userin} += $size;
}

close(LOG);

open cur_tr, "<$conf_stc_path/cur_tr.users";
while (<cur_tr>)
    {
    if ($_ eq '') {next;}
    my ($cur_user,$cur_traffic)=split(' ');
    if ($cur_user eq $userin) {$traffic{$cur_user}+=int($cur_traffic)};
    }
close (cur_tr);

return 1;
}# get_traffic
#---------------------------------------------------------
#<sub get_bosses>
sub get_bosses{
if (-e "$conf_stc_path/boss.users")
    {
    open bf, "<$conf_stc_path/boss.users";
    while (<bf>)
        {
        @F=split (' ');
#        $tmp_user=shift(@F);
	my $k=@F;
        if ($F[0] ne ""){
	    my $user1=$F[0];
	    $user_boss{$user1}='yep';
	    for ($i=1; $i<$k;++$i){
		if ($F[$i] ne ""){
		    $bosshash{"${user1}_o$F[$i]"}='ok';
		}
	    }
        }
    }
    boss_end_file:
    close (bf);
    }
else
    {
	logmsg (__FILE__." line ".__LINE__.":[ERROR] Unable to read '$conf_stc_path/boss.users'. Analyzing user profiles.");
    }
#</get_bosses>

#<get_bosses_from_profiles>
foreach (@users){
    my $us=$_;
    if (!$u_exist{"\L$us"}){next;}
    if (!-e "${conf_stc_path}/profiles/${us}.profile"){
        logmsg (__FILE__." line ".__LINE__.":[WARNING] user profile file ${conf_stc_path}/profiles/${us}.profile does not exists");
    }#if !-e profile
    else{
	open upf1, "<${conf_stc_path}/profiles/${us}.profile" or logmsg (__FILE__." line ".__LINE__.":[ERROR] cannot open user profile file '${conf_stc_path}/profiles/${us}.profile'");
	while ($stin=<upf1>)
	{
    	    chomp ($stin);
            my $key=$stin;
	    my $value=$stin;
    	    $key=~s/:.*$//;
    	    $value=~s/^.*?://;
	    #Handling otdel-boss stuff
	    my $tkey=$key;
	    $tkey=~s/o//;
	    $tkey=0+$tkey;
	    if (($tkey<=999) and ($tkey>=1)){
		$bosshash{"${us}_o${tkey}"}='ok';
		$user_boss{$us}='yep';
if ($DEBUG){
    print "<font size=1>";
    print "<b>BOSSHASH:</b> $us & $tkey = $bosshash{\"${us}_o${tkey}\"}<br>";
    print "</font>";
}

	    }
	}#while upf
        close (upf1);
    }#else -> if !-e profile
}#foreach
#</get_bosses_from_profiles>
}#sub get_bosses
#---------------------------------------------------------
#sub get_reserve {
#    my $otdel_in = $_;
#    my $otd = undef;
#    my $res = 'BLOCKED';
#    open cto, "$conf_stc_path/cur_tr.otdel" or return 'BLOCKED';
#    while (<cto>){
#	($otd, $res) = split (' ');
#	if (!$res){$res = 0;}
#	$res = $res/$conf_mega_byte;
#	if ($otd == $otdel_in){return $res;}
#    }
#    close(cto);
#    return 'BLOCKED';
#}
#---------------------------------------------------------
sub delete_otdel {
#INPUT:		OTDEL_NUMBER
#RETURN:	NONE
#OUTPUT:	NONE if successed or error if failed (write error msg to ERROR_LOG)
#RUN:		removes whole otdel from STC
    my $in_otdel = $_[0];
    $ERR=undef;
    open tmp, "<$conf_stc_path/o${in_otdel}.users" or $ERR="$conf_stc_path/o${in_otdel}.users: Can't open for read";
#print "DEBUG after readopen = $ERR<br>";
    while(<tmp>){
	my @FD=split (/\s+/);
	my $tmp=$FD[0];
	if (!$tmp){next;}
	&del_from_file ("${conf_stc_path}/password", $tmp);
        &del_from_file ("${conf_stc_path}/password.digest", $tmp);
        &del_from_file ("${conf_stc_path}/o${in_otdel}.users", $tmp);
        &del_from_file ("${conf_stc_path}/traffic.users", $tmp);
        unlink("$conf_stc_path/messages/users/$tmp/messages.dat");
        unlink("$conf_stc_path/messages/users/$tmp/lastmess.dat");
        unlink("$conf_stc_path/profiles/$tmp.profile");
        rmdir ("$conf_stc_path/messages/users/$tmp");
        logmsg (__FILE__." line ".__LINE__.":[INFO] User $tmp was deleted by '$user'");
#        print "<center>$msg{'user'} <b>$tmp</b> $msg{'was_deleted'}</center><br>";
    }
    close (tmp);
    open tmp, ">>$conf_stc_path/o${in_otdel}.users" or $ERR=$!;
    close (tmp);
    if (!$ERR){
	system ("rm -f $conf_stc_path/o${in_otdel}.users");
	my $logfile="$conf_stc_path/allign.otdel";
        my @thisarray;
        open(LR,"$logfile") or print "Can't open $logfile: $!<br>";
        flock(LR,1) or print "Can't flock $logfile: $!<br>";
        @thisarray = <LR>;
        close(LR) or print "Can't close $logfile: $!<br>";
        my @tmp;
        foreach (@thisarray) {
            @tmp = split(':');
	    if ($tmp[0] == $in_otdel){$tmp[0]="";$tmp[1]="";$_ = join('', $tmp[0], $tmp[1]);}
        }#foreach thisarray
        open(LR,"> $logfile") or print "Can't open $logfile: $!<br>";
        flock(LR,1) or print "Can't flock $logfile: $!<br>";
        print LR @thisarray;
        close(LR) or print "Can't close $logfile: $!<br>";

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
        print "<center>$msg{'otdel'} <b>$in_otdel</b> $msg{'was_deleted'}</center><br>";
    }
    else {
	print "$msg{error} $conf_stc_path/o${in_otdel}.users: Can't remove file $ERR<br>";
	logmsg(__FILE__." line ".__LINE__.":[ERROR] $user otdel.cgi $conf_stc_path/allign.otdel: Can't remove file $ERR");
    }
} #sub delete_otdel
#---------------------------------------------------------
sub del_from_file
{
    my ($filename, $delu) = @_;
          $err='ok';
    my $out="";
          open f1, "<${filename}" or $err="gluk";
           if ($err eq "gluk")
                {
                print "<b class=error>$msg{'error'}</b> $msg{'cannot_open'} ${filename} ($msg{'read'})";
                logmsg (__FILE__." line ".__LINE__.":[ERROR] cannot open file '${filename}' for reading: $!");
                goto userlist;
                }
           while (<f1>)
              {
              $tmpu=$_;
              $tmpu=~s/:.*$//;
              $tmpu=(split(" ", $tmpu))[0];
              if ($tmpu eq $delu) {next;}
              $out.=$_;
              }
          close (f1);
          open f1, ">${filename}" or $err="gluk";
           if ($err eq "gluk")
                {
                print "<b class=error>$msg{'error'}</b> $msg{'cannot_open'} ${filename} ($msg{'write'})";
                logmsg (__FILE__." line ".__LINE__.":[ERROR] cannot open file '${filename}' for writing: $!");
                goto userlist;
                }
          print f1 $out;
          close (f1);
    }
#---------------------------------------------------------
sub clean {
#INPUT:         target string, additional prohibited symbols (optional)
#RETURN:        clean string
#RUN:		removing all prohibited symbols
#OUTPUT:	NONE

   my $in = $_[0];
   my $adv = $_[1];
   $in =~ s/\/|\\|\:|\'|\"|\<|\>|\||\`|\&//ig; #`
   if ($adv){
      $in =~ s/$adv//ig;
   }
   return $in;
}
			      
#---------------------------------------------------------
sub block_user {
#INPUT:		username
#RETURN:	bool (OK or ERROR)
#RUN:		blocks user
#OUTPUT:	none
   my $usver = $_[0];

   open blfil, ">>$conf_stc_path/blocked.users";
   printf blfil "$usver\n";
   if ($user_profile{"${usver}_domain"}){printf blfil "$logu{$usver}\n";}
   close blfil;
   return 1;
}
#---------------------------------------------------------
sub unblock_user {
#INPUT:         username
#RETURN:        bool (OK or ERROR)
#RUN:           unblocks user
#OUTPUT:        none
   my $usver = $_[0];
        my $logfile="$conf_stc_path/blocked.users";
        my @thisarray;
        open(LR,"$logfile") or print "$msg[2] $logfile: $!<br>";
        flock(LR,1) or print "$msg[3] $logfile: $!<br>";
        @thisarray = <LR>;
        close(LR) or print "#msg[4] $logfile: $!<br>";
        my @tmp;
        foreach (@thisarray) {
            @tmp = split(' ');
            if (($tmp[0] eq $usver) or ($tmp[0] eq $logu{$usver})) {
                $tmp[0] = "";
                $_ = join(' ', @tmp);
            }
        }#foreach thisarray
        open(LR,"> $logfile") or print "$msg[2] $logfile: $!<br>";
        flock(LR,1) or print "$msg[3] $logfile: $!<br>";
        print LR @thisarray;
        close(LR) or print "$msg[4] $logfile: $!<br>";

   return 1;
}
#---------------------------------------------------------
sub get_latest_version
{
   my $result = "ERROR: Could not get version.";
   my $url = "http://stc.nixdev.org/get_latest_ver.cgi";
#my $url = "http://ya.ru:81/aaa";

   my $content = undef;

   eval "use LWP::Simple;";
   if ($@){
        $result = "ERROR: <font color=red>LWP::Simple perl module not found. Please install it.</font>";
   } else {
        my $browser = LWP::UserAgent->new;
        $browser->timeout(1);
        my $response = $browser->post( $url, [ 'myver' => $version ] );
        return "ERROR: Could not get version." unless $response->is_success;
        return "ERROR: Could not get version." unless $response->content_type eq 'text/html';
        if($response->content =~ /\[(\d+\.\d+\.\d+)?\]\[(\d+\.\d+\.\d+)?\]/i) {
           $result = "$1 Release date: $2";
        }
        else {
           $result = "ERROR: Could not get version.";
        }
   }

   return $result;
}
#---------------------------------------------------------
sub check_lwp
{  
   my $result="OK";
   eval "use LWP::Simple;";
   if ($@){
        $result = "<font color=red><b>LWP::Simple</b> perl module not found. Please install it.</font>";
   }
   return $result;
}
#---------------------------------------------------------
sub get_latest_version_from_cache
{  
   my $result = "ERROR:";
   my $err = undef;
   my $line = undef;
   my $cfile = "$conf_stc_path/version.cache";
   open CF, "< $cfile" or $err=1;
   if (!$err){
        while ($line = <CF>){
                chomp($line);
                if ($line =~ /^LATEST_VERSION:\[(\d+\.\d+\.\d+)?\]\[(\d+\.\d+\.\d+)?\]/i) {
                        $result = "$1 Release date: $2";
                }
           }
   } # iff
   close CF;
   return $result;
}

#---------------------------------------------------------

#print "Content-type: text/html; charset=windows-1251\n\n";
#print "<TITLE>Admin page</TITLE>";
#print "<center>Hi there ;)<br> Visit our website <a href=\"http://stc.nixdev.org\">http://stc.nixdev.org!</a></center><br>";

1;
