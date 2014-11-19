#Include file for LIMIT scripts
#use Time::localtime;


#<get u_exist> and <get users>
@u_exist=undef;
my $fname="$stc_path/password";
if (!-r $fname)
    {
    logmsg (__FILE__." line ".__LINE__." :[ERROR] Cannot open '$fname'");
    die __FILE__." line ".__LINE__." $msg{'cannot_open'} '$fname'";
    }
else 
    {
    open pasfil, "<$fname" or logmsg (__FILE__." line ".__LINE__." :[ERROR] Can't open $fname: $!"); #'
    while(<pasfil>)
	{
	~s/^([a-z]+).+$/$1/;    
	~s/\n//;    
	if ($_ ne ''){$u_exist{$_}="TRUE";}
	}
    close (pasfil);
    }
$u_exist{'administrator'}="FALSE";
$u_exist{'looser'}="FALSE";
$u_exist{'root'}="FALSE";
$u_exist{''}=undef;
#</get u_exist> and </get users>

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


#---------------------------------------------------------
#<exculde_hosts>
if (-r "$exclude_hosts")
    {
    open (EXCLUDELIST, "<$exclude_hosts");
    while (<EXCLUDELIST>)
      {
            s/(#.*|\s+)//g;
            next if /^\n$/;
            if (/^([0-9\.\-a-z]{1,})([:]{0,}[0-9]{0,})$/) {$exclude_sites.=$_;}
      }
    close (EXCLUDELIST);
    }
else
    {
    logmsg (__FILE__." line ".__LINE__." :[WARNING] Unable to read exclude IP file $exclude_hosts");
    }
#</exclude_hosts>
#---------------------------------------------------------

if (-r "$sarg_exclude_codes_filelist")
    {
        open ec, "<$sarg_exclude_codes_filelist";
        while (<ec>)
        {
            s/(#.*|\s+)//g;
            next if /^\n$/;
            if (~m/[A-Z\_]{4,6}\/[0-9]{1,3}/) {$sarg_exclude_codes{$_}++;}
        }
        close(ec);
    }
else
    { if ($sarg_exclude_codes_filelist ne '')
	{
	    logmsg (__FILE__." line ".__LINE__." :[WARNING] Cannot open '$$sarg_exclude_codes_filelist'");
	}
    }


#---------------------------------------------------------
# FUNCTIONS
#---------------------------------------------------------
sub get_profile
{
    my $tempory=$_[0];
    my $name1=$value1=undef;
    my $fname="$stc_path/profiles/$tempory.profile";
    
if (!-r $fname)
    {
    logmsg (__FILE__." line ".__LINE__." :[WARNING] Cannot open '$fname'");
    print __FILE__." line ".__LINE__." $msg{'cannot_open'} '$fname'";
    return 0;
    }
else
    {
    open upf, "<$fname" or logmsg (__FILE__." line ".__LINE__." :[WARNING] Can't open $fname: $!");
    while (<upf>)
	{
	($name1, $value1)=split(':');
	if ($name1 eq 'domain')
	    {
	    $domain{$tempory}=$value1;
	    }
	}
    close (upf);
    chomp($domain{$tempory});
    if($domain{$tempory})
	{
    	if ($ntlm_userdomain eq 'domainfirst')
	    {
	    $logu{$tempory}="$domain{$tempory}".$divide_char.$tempory;
	    }
	else 
	    {
	    $logu{$tempory}=$tempory.$divide_char."$domain{$tempory}";
	    }
	}
    else {$logu{$tempory}=$tempory;}
    $realuser{$logu{$tempory}}=$tempory;

    $_[0]=$tempory;
    }
}
#sub get_profile
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
#        $ip="(".$ip."):$port"; # пока отменить, для дальнейшего анализа
        }
    else
        {$ip=~s/(\d+)\.(\d+)\.(\d+)\.\d+/\($ip)|($1.$2.$3.0)|($1.$2.0.0)|($1.0.0.0)/;}
    #Делаем регулярное выражение, заменяя . на \.
    $ip=~s/\./\\\./;
    return ($exclude_sites =~ /$ip/) || 0;
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
    if (!$realuser{$user_name}){next;}


    #Определяем откуда были взяты данные - из инета или из кеша
    unless($squid_result_codes{$codestatus}){next;}

    # Пропустить все записи, которые определены для пропуска по коду, а так же пропускаем код ошибки ERR_*.

    if ($skip_cache eq 'yes')
        {
        if ($sarg_exclude_codes{$code} or $code=~m/^ERR_.+/) {next;}
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

    # Пропустить все записи, которые определены для пропуска по хосту.
    if (exclude_ip($ip_sp.$port) or exclude_ip($site)) {next;}

    return ($user_name, $size);
}

#---------------------------------------------------------


#---------------------------------------------------------
sub get_all_traffic{


my $access_log_in = $_[0];

unless (-r "$access_log_in")
	{
	logmsg (__FILE__." line ".__LINE__." :[ERROR] Cannot open squid access log '$access_log_in': $!");
	print "$msg{'cannot_open'} '$access_log_in': $!";
	return 0;
	}

open(LOG, "<$access_log_in");
    while(<LOG>)
    {
	my ($user_name, $size) = log_line($_);
	$totaltraffic += $size;
        $traffic{$realuser{$user_name}} +=  $size;
	$usage{$realuser{$user_name}}{$site} += $size;
    }# while LOG
close(LOG);

open cur_tr, "<$stc_path/cur_tr.users";
    while (<cur_tr>)
    {
    ($cur_user,$cur_traffic)=split(' ');

    if ($u_exist{"$cur_user"}="TRUE") {
        $traffic{$cur_user}+=$cur_traffic;
        }
    }
close (cur_tr);


return 1;
}#get_all_traffic

#---------------------------------------------------------
sub logmsg
{
    my ($mess) = @_;
    my($y,$m,$d) =  (localtime)[5,4,3];
    $y+=1900;
    $m++;
    my $time_now = sprintf "%02d.%02d.%04d %02d:%02d:%02d", $d, $m, $y, (localtime)[2,1,0];

unless (-w $log_file)
	{
	logmsg (__FILE__." line ".__LINE__." :[ERROR] Cannot open '$log_file'");
	print __FILE__." line ".__LINE__.": $msg{'cannot_open'} '$log_file'";
	}
    else 
	{
	open LOG_FILE, ">>$log_file";
    	    print LOG_FILE "$time_now - ", $mess, "\n";
	close (LOG_FILE);
	}
}#logmsg
#---------------------------------------------------------
sub get_latest_version
{  
   my $local_version = $_[0];
   my $result = "ERROR: Could not get version.";
   my $url = "http://stc.nixdev.org/get_latest_ver.cgi";
   my $content = undef;

   eval "use LWP::Simple;";
   if ($@){
        $result = "ERROR: <font color=red>LWP::Simple perl module not found. Please install it.</font>";
   } else {
        my $browser = LWP::UserAgent->new;
        $browser->timeout(1);
        my $response = $browser->post( $url, [ 'myver' => $local_version ] );
        return "ERROR: Could not get version." unless $response->is_success;
        return "ERROR: Could not get version." unless $response->content_type eq 'text/html';
        if($response->content =~ /\[(\d+\.\d+\.\d+)?\]\[(\d+\.\d+\.\d+)?\]/i) {
           $result = "[$1][$2]";
        }
        else {
           $result = "ERROR: Could not get version.";
        }
   }
   return $result;
}
#---------------------------------------------------------

1;
