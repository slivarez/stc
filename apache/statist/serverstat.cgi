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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. =See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with STC; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA =02111-1307 =USA
#
use MIME::Base64();

$stat="OK";
$scode="ok";

require "./init_stc.pl";
&get_conf;
&get_profile("$user");
&load_header("Server Status");
&init_stc;
$open_error=0;
my $pass="";
my $remote;

#This is only for serverstatus
$conf_site_ip = 'localhost';

if ($admin{$user} ne 'yep' and $user_boss{$user} ne 'yep') {
    print "$msg[5]<br>";
    &load_footer;
    exit;
}

if (!-r "$conf_squid_conf_path/squid.conf")
{
    print "<br>".$msg[2060]." $conf_squid_conf_path/".$msg[2052];
    goto the_end;
}
    open SQUID, "<$conf_squid_conf_path/squid.conf" or die($!);
    %parsed = ();

LINE: while (<SQUID>)
      {
      if (!m/^(http_port|cachemgr_passwd)/) {next LINE;}
      @parts=split(" "); # разбиваем строку с разделителем пробел
      if ($parts[0] eq "http_port")
          {
          ($host, $port) = split (":", $parts[1]);
          if ($host eq $parts[1])
              {
              $host="";
              $port=$parts[1];
              }
	  next LINE;
          }
      if ($parts[0] eq "cachemgr_passwd") 
        {
	$pass=$parts[1];
	}
      if (($host || $port) && $pass) 
        {
	last LINE;
        }
      }
close SQUID;

if (!$host)     {$host = "127.0.0.1";}
if (!$port)     {$port = "3128";}

$pos="header"; # Вывод начинается с заголовка :) Устанавливаем указатель

#print "Pass:$pass<br>";
print ("<br><br><b>$msg[2030]:</b><br>");
$num=0; # порядковый номер текущей записи
#print "Serverstat_type:",$conf_serverstat_type,"<br>";

if ($conf_serverstat_type == 1) { # ORKAN
#    print "Host:",$host;
#    print "<br>Port:",$port;
#    print "<br>Site IP:",$conf_site_ip,"<br>";
    use IO::Socket;
    $remote = IO::Socket::INET->new( Proto => "tcp",
            PeerAddr => $host,
	    PeerPort => $port,
	    LocalAddr=> $conf_site_ip,
	        );
    unless ($remote) { print "<font color=#BB0000>$msg[2001]!</font> $msg[2029] $host:$port.<br>$@";
	goto the_end;
    }
    $remote->autoflush(1);
    print $remote "GET cache_object://$conf_site_ip/active_requests HTTP/1.0\r\n"; # Посылаем HTTP запрос
    if ($pass ne "none") {print $remote "Authorization: Basic ".MIME::Base64::encode("cachemgr:".$pass);}
    print $remote "\r\n";
}
else { # Igor-itl
    $prg="$conf_squid_path/squidclient";
    $arg="-h $host -p $port -l $conf_site_ip -m GET -U $user -W $pass";
    my $url="cache_object://$conf_site_ip/active_requests";
    open ($remote,"$prg $arg $url |") or $open_error=$!;
    if ($open_error) { 
	print "<font color=#BB0000>$msg[2051]!</font> $prg<br>$open_error";
	goto the_end; 
    }
} # end serverstat_type

########## alexnin 20090601 #####################

while ( $dump = <$remote> ) # Читаем ответ сервера
   {
    ($k,$v)=split(" ",$dump,2);
    unless ($k=~m/^[Ca-z]+[:]{0,}/){next;}
    $k=~s/://;
#    if ($k) {print $k."<br>\n"};
    if($h==1 and $dump=="") {$h=0;next;}
    $v=~s/\n//;
    if ($k eq 'Connection') {$connection=substr($v,0,9);next;}
    if($connection)
	{
#            /* username field is avaible in Squid 2.6 stable */
        if($dump =~ /^out\.offset\s\d+,\sout.size\s(\d+)/) {$parsed{$connection}{"bytes"}=int($1); next; }
        if($dump =~ /^start \d+\.\d+ \((\d+).\d+ seconds ago\)/) {$parsed{$connection}{"seconds"}=int($1); next; }
        if($k eq 'uri')
    	    {
            if(substr($v,0,13) eq "cache_object:")
        	{
                delete $parsed{$connection};
                $connection='';
                $h=0;
        	}
            else
        	{
                $parsed{$connection}{"uri"}=substr($v,0);
        	}
            next;
    	    }
        $parsed{$connection}{$k}=substr($v,0);
	}
    }
    close $remote;

&killcheck;

    print ("\t\t<table border=0 CELLPADDING=3 CELLSPACING=2>\n");
    print ("\t\t<tr>
            <th class=stat align=center>User\@IP&nbsp;/&nbsp;URL</th>
            <th class=stat align=center>Time</th>
            <th class=stat align=center>AVG&nbsp;Speed</th>
            <th class=stat align=center>Size</th>");
    if ($admin{$user} eq 'yep') { print ("<th class=stat >&nbsp;</th>"); }
    print ("</tr>\n");

    while (($k, $v) = each %parsed)
            {
            $new_hash_key=($parsed{$k}{"username"}?$parsed{$k}{"username"}.'@':'').$parsed{$k}{"peer"};
            $view_users{$new_hash_key}=$v;
            ($view_users{$new_hash_key}{'peer_ip'},$view_users{$new_hash_key}{'peer_port'}) = split (":", $parsed{$k}{"peer"});
            }


#print serverstat
    $cur_host='';
    $count_b_users=0;
    $total_b_users=0;
    $avg_total_b_users=0;
    $colspan_count=($admin{$user} eq 'yep')?6:5;

    foreach $ku (sort keys %view_users)
    {
        $uri=$view_users{$ku}{"uri"};
        $_=$view_users{$ku}{"uri"};
        $div_uri = tr/[0-9a-zA-Z\%\-\.\\\/\?_=:]//;
        $ts_uri='';
        if ($div_uri>48)
            {
            $ts_uri=substr($view_users{$ku}{"uri"},0, 38);
            $te_uri=substr($view_users{$ku}{"uri"},-9);
            }

        if ($cur_host ne ($view_users{$ku}{'username'}.'@'.$view_users{$ku}{'peer_ip'}))
            {
            if ($cur_host ne '')
                {
                print ("\t\t<tr><td class=row_ip align=right colspan=". ($colspan_count-4) ."><b>$cur_user_name:</b></td>\n");
                print ("\t\t<td class=row_ip>".conv_digit_to_metriks($avg_b_user)."</td>\n");
                print ("\t\t<td class=row_ip colspan=". ($colspan_count-4) .">".conv_digit_to_metriks(int($count_b_users))."</td></tr>\n");
                $avg_b_user = 0;
                $count_b_users = 0;
                }
            $cur_user_name = ($view_users{$ku}{'username'}?$view_users{$ku}{'username'}.'@':'').$view_users{$ku}{'peer_ip'};
            print "\t\t<tr><td class=row_ip colspan=$colspan_count align=left>".$cur_user_name."</td></tr>\n";
            }
        $cur_host = ($view_users{$ku}{'username'}.'@'.$view_users{$ku}{'peer_ip'});
        $avg_speed=0;
        if ($view_users{$ku}{'seconds'} > 0)
            {
            $avg_speed = int($view_users{$ku}{'bytes'});
            $avg_speed /= int($view_users{$ku}{'seconds'});
            $avg_b_user += int($avg_speed);
            $avg_b_total += int($avg_speed);
            }
        $count_b_users +=$view_users{$ku}{'bytes'};
        $total_b_users +=$view_users{$ku}{'bytes'};
        $print_avg_speed=(int($avg_speed) > 0 ? conv_digit_to_metriks(int($avg_speed)) : "&nbsp;");
        $print_cur_speed=(int($view_users{$ku}{'bytes'}) > 0 ? conv_digit_to_metriks(int($view_users{$ku}{'bytes'})) : "&nbsp;");

        print ("\t\t<tr>\n");
        if ($ts_uri ne '')
            {
            print ("\t\t<td class=\"row_stat\" nowrap align=left><a target=\"blank\" title=\"$uri\" href=\"$uri\">$ts_uri\...$te_uri</td>\n");
            }
        else
            {
            print ("\t\t<td class=\"row_stat\" nowrap align=left><a target=\"blank\" title=\"$uri\" href=\"$uri\">".$uri."</td>\n");
            }
        print ("\t\t<td width=70 class=\"row_stat\" align=right>".nice_time($view_users{$ku}{'seconds'})."&nbsp;</td>\n");
        print ("\t\t<td width=70 class=\"row_stat\" align=right>$print_avg_speed</td>\n");
        print ("\t\t<td width=50 class=\"row_stat\" align=right>$print_cur_speed</td>\n");
        if ($admin{$user} eq 'yep' and (nice_time($view_users{$ku}{'seconds'}) ne '00:00:00' or $view_users{$ku}{'bytes'})!=0)
            {
            print ("\t\t<td class=\"row_stat\">");
            print ("<a class=\"a_killconnect\" href=\"serverstat.cgi?kill_connection=".$view_users{$ku}{'peer_ip'}."%3A".$view_users{$ku}{'peer_port'});
            print ("\"title=\"!!kill connect!!\"><IMG class=\"img_killconnect\" src=\"/stat/kill.png\"></a></td>\n");
            }
        else
            {
            print "\t\t<td class=\"row_stat\">&nbsp;</td>\n";
            }
        print ("\t\t</tr>\n");
    }

    print ("\t\t<tr><td class='row_ip' align=right colspan='". ($colspan_count-4) ."'><b>$cur_user_name:</b></td>\n");
    print ("\t\t<td class='row_ip'>".conv_digit_to_metriks($avg_b_user)."</td>\n");
    print ("\t\t<td class='row_ip' colspan='". ($colspan_count-4) ."'>".conv_digit_to_metriks(int($count_b_users))."</td></tr>\n");

    print ("\t\t<tr><td class='row_ip' colspan='$colspan_count'>&nbsp;</td></tr>");
    print ("\t\t<tr><td class='row_ip' align=right colspan='". ($colspan_count-4) ."'><b>Total:</b></td>\n");
    print ("\t\t<td class='row_ip'>".conv_digit_to_metriks($avg_b_total)."</td>\n");
    print ("\t\t<td class='row_ip' colspan='". ($colspan_count-4) ."'>".conv_digit_to_metriks(int($total_b_users))."</td></tr>\n");

    print ("\t\t</table>\n");

########## alexnin 20090601 #####################

clients_list:
$http_res="";
print ("<br><br><b>$msg[2035]:</b><br>");

$pos="header"; # Вывод начинается с заголовка :) Устанавливаем указатель
$num=0; # порядковый номер текущей записи
if ($conf_serverstat_type == 1) { # Orkan
    use IO::Socket;
    $remote = IO::Socket::INET->new( Proto => "tcp",
            PeerAddr => $host,
	    PeerPort => $port,
	    LocalAddr=> $conf_site_ip,
	    );
    unless ($remote) { print "<font color=#BB0000>$msg[2001]!</font> $msg[2029] $host:$port.<br>$@";
	goto the_end;
    }
    $remote->autoflush(1);
    print $remote "GET cache_object://$conf_site_ip/client_list HTTP/1.0\r\n"; # Посылаем HTTP запрос
    if ($pass ne "none") {print $remote "Authorization: Basic ".MIME::Base64::encode("cachemgr:".$pass);}
    print $remote "\r\n";
}
else { # Igor-itl
    my $url="cache_object://$conf_site_ip/client_list";
    open ($remote,"$prg $arg $url |") or $open_error=$!;
    if ($open_error) { 
	print "<font color=#BB0000>$msg[2051]!</font> $prg<br>$open_error";
	goto the_end; 
    }
} # end serverstat_type

while ( $dump = <$remote> ) # Читаем ответ сервера
   {
    if ($pos eq "header") # Если указатель установлен на заголовок
    {
    if (!$http_res) # Первая строка - результат запроса, если мы его еже не получили, >
        {
        $http_res_full=$dump; # целая строка, чтоб было что вывести на случай ошибки
        $dump=~ s/.*?\s([0-9]{3})\W.*/\1/s; # Нас интересует только число
        $http_res=$dump;
        } # Первая строка
    if ($dump eq "\r\n") # Если встретили конец заголовка
        {
        $pos = "body"; # Меняем указатель
        } # Если конец заголовка
    } # Если указатель на заголовке
    else
    { # В противном случае - переходим к телу
    if ($http_res ne "200") # Если из заголовка мы узнали что результат запроса не 200 OK - умираем
        {print ("<font color=#BB0000>$msg[2001]!</font> $msg[2031].<br>$http_res_full"); goto server_info;}

    if ($dump =~ /^Address:\s/) # Достаем адрес клиента
        {
        $dump =~ s/^Address:\s([0-9\.]{7,15})\n$/\1/;
        $$num{'client_ip'} = $dump;
        } # Достаем адрес клиента

    if ($dump =~ /^Currently established connections:\s/) # Достаем кол-во соединений
        {
        $dump =~ s/^Currently established connections:\s([0-9\.]{1,})\n$/\1/;
        $$num{'num'} = $dump;
        } # Достаем кол-во соединений

    if ($dump eq "\n") # строка, содержащия только символ перевода строки - разделитель между соединениями
        {
        if ($$num{'client_ip'} ne $host) # если мы обнаружили соединение, которое сами установили - не увеличиваем счетчик. Зачем оно нам надо :)
        { $num+=1; }
        } # если разделитель
    }
   }
close $remote;

print ("\t\t<table border=0 CELLPADDING=3 CELLSPACING=2>\n");
print ("<tr><th class=stat align=center>$msg[2032]</th><th class=stat align=center>$msg[2036]</th>");
        if ($admin{$user} eq 'yep')
           {print ("<th class=stat>&nbsp;</th>");}
print ("</tr>");
for ($i=0; $i<$num; $i++)
    {
     print ("<tr><td class=\"row_stat\" align=left>".$$i{'client_ip'}."</td><td class=\"row_stat\" align=center>".$$i{'num'}."</td>");
        if ($admin{$user} eq 'yep')
         {print ("<td class=\"row_stat\"><a href=\"serverstat.cgi?kill_connection=".$$i{'client_ip'}.":0\">$msg[2053]</a></td>");}
     print ("</tr>");
    }
print ("</table>");

server_info:
print ("<br><br><b>$msg[2037]</b><br>");
$pos="header"; # Вывод начинается с заголовка :) Устанавливаем указатель
$http_res="";

if ($conf_serverstat_type == 1) { # Orkan
    use IO::Socket;
    $remote = IO::Socket::INET->new( Proto => "tcp",
            PeerAddr => $host,
	    PeerPort => $port,
	    LocalAddr=> $conf_site_ip,
	    );
    unless ($remote) { print "<font color=#BB0000>$msg[2001]!</font> $msg[2029] $host:$port.<br>$@";
	goto the_end;
    }
    $remote->autoflush(1);
    print $remote "GET cache_object://$conf_site_ip/info HTTP/1.0\r\n"; # Посылаем HTTP запрос
    if ($pass ne "none") {print $remote "Authorization: Basic ".MIME::Base64::encode("cachemgr:".$pass);}
    print $remote "\r\n";
}
else { # Igor-itl
    my $url="cache_object://$conf_site_ip/info";
    open ($remote,"$prg $arg $url |") or $open_error=$!;
    if ($open_error) { 
	print "<font color=#BB0000>$msg[2051]!</font> $prg<br>$open_error";
	goto the_end; 
    }
} # end serverstat_type

while ( $dump = <$remote> ) # Читаем ответ сервера
   {
    if ($pos eq "header") # Если указатель установлен на заголовок
    {
    if (!$http_res) # Первая строка - результат запроса, если мы его еже не получили, >
        {
        $http_res_full=$dump; # целая строка, чтоб было что вывести на случай ошибки
        $dump=~ s/.*?\s([0-9]{3})\W.*/\1/s; # Нас интересует только число
        $http_res=$dump;
        } # Первая строка
    if ($dump eq "\r\n") # Если встретили конец заголовка
        {
        $pos = "body"; # Меняем указатель
        } # Если конец заголовка
    } # Если указатель на заголовке
    else
    { # В противном случае - переходим к телу
    if ($http_res ne "200") # Если из заголовка мы узнали что результат запроса не 200 OK - умираем
        {print ("<font color=#BB0000>$msg[2001]!</font> $msg[2031].<br>$http_res_full"); goto the_end;}

    if ($dump =~ /^\tUP\sTime:\t/) # Достаем время работы SQUID
        {
        $dump =~ s/^\tUP\sTime:\t([0-9\.]{1,})\s.*\n$/\1/;
        $info{'uptime'} = $dump;
        } # Достаем Время работы SQUID

    if ($dump =~ /^\tCPU\sUsage:\t/) # Достаем загрузку CPU
        {
        $dump =~ s/^\tCPU\sUsage:\t([0-9\.%]{1,})\n$/\1/;
        $info{'cpu'} = $dump;
        } # Достаем загрузку CPU

    if ($dump =~ /^\tCPU\sUsage,\s5\sminute\savg:\t/) # Достаем загрузку CPU
        {
        $dump =~ s/^\tCPU\sUsage,\s5\sminute\savg:\t([0-9\.%]{1,})\n$/\1/;
        $info{'cpu5'} = $dump;
        } # Достаем загрузку CPU

    if ($dump =~ /^\tCPU\sUsage,\s60\sminute\savg:\t/) # Достаем загрузку CPU
        {
        $dump =~ s/^\tCPU\sUsage,\s60\sminute\savg:\t([0-9\.%]{1,})\n$/\1/;
        $info{'cpu60'} = $dump;
        } # Достаем загрузку CPU

    }
   }
    close $remote; # Закрываем соединение с сервером

print ("<table border=0 cellspacing=3>");
print ("<tr><td align=right>$msg[2038]:</td><td><b>".nice_time($info{'uptime'})."</b></td></tr>");
print ("<tr><td align=right>$msg[2039]:</td><td><b>".$info{'cpu'}."</b></td></tr>");
print ("<tr><td align=right>$msg[2040]:</td><td><b>".$info{'cpu5'}."</b></td></tr>");
print ("<tr><td align=right>$msg[2041]:</td><td><b>".$info{'cpu60'}."</b></td></tr>");
print ("</table>");

the_end:

#open foot, "$www_data_path/stat/footer.htm" or print "</body>"; # открываем низ
#while (<foot>){
#    print; # все выводим
#}#while foot
#close (foot); # закрываем низ

&load_footer;



sub nice_time
    {
    my ($sec) = @_;
    $sec=int($sec);
    if ( $sec > 3600)
    {
    $h = int ($sec / 3600);
    if ($h<10) {$hh="0".$h;}
       else {$hh="".$h;}
    } else {$h=0; $hh="00";}
    $sec = ($sec - ($h*3600));
    if ( $sec > 60 )
    {
    $m = int ($sec / 60);
    if ($m<10) {$mm="0".$m;}
       else {$mm="".$m;}
    } else {$m=0; $mm="00";}
    $sec = ($sec - ($m*60));
    if ($sec<10) {$ss="0".$sec;}
        else {$ss="".$sec;}
    return "${hh}:${mm}:${ss}";
    }

sub killcheck
    {
    $query=CGI::new();
    if ($query->param('kill_connection') =~ /[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]{1,5}/)
        {
        if ($admin{$user} ne 'yep')
            {
             print "<font color=#CC0000>$msg[2001]!</font> $msg[2050].<br>";
            return 0;
            }
         my ($ip, $port)=split(":", $query->param('kill_connection'));
         $error=0;

         if (!(-d "/tmp/stc"))
                {
                system ('mkdir /tmp/stc');
                system ('chmod 700 /tmp/stc');
                }

         if (-e "/tmp/stc/kill.queue.lock" && -e "/tmp/stc/kill.queue")
              {
               sleep 2;
               if (-e "/tmp/stc/kill.queue.lock" && -e "/tmp/stc/kill.queue")
                    {
                     print ("<font color=#990000>$msg[2042].</font><br>$msg[2043].<br>");
                     $error=1;
                    }
              }

         if (-w '/tmp/stc' && (-w 'tmp/stc/kill.queue' || !(-e 'tmp/stc/kill.queue')) && $error eq 0)
              {
              open (KILLFILE, '>>/tmp/stc/kill.queue');
              print KILLFILE "\n${ip}:${port}" or $error=1;
              close (KILLFILE);
              if ($error eq 0)
                  {print "<font color=#009900>$msg[2044] ${ip}:${port} $msg[2045]</font>.<br>$msg[2046].<br>";}
              else
                  {print "<font color=#CC0000>$msg[2047]</font>: $!";}
              }
         elsif ($error eq 0)
              {print "<font color=#CC0000>$msg[2048].</font><br>$msg[2049].<br>";}
        }
    }

sub conv_digit_to_metriks()
{
    if($_[0] ne '0') {
    @conv_metrics = ('','K','M','G','T','P');
    $perf=int(($_[0] =~ tr/0-9//)/3);
    return sprintf "%0.2f&nbsp;%s", $_[0]/(1024**$perf), $conv_metrics[$perf].'b';
    }
}
            
