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

$stat="OK";
$scode="ok";
require "./init_stc.pl";

&get_conf;
&get_profile("$user");
&load_header("Delay pool control");
&init_stc;

$query=new CGI;
$squid_reconf = $query->param('squid_reconf');

if( $admin{$user} eq 'yep') { # Если юзверь админ - пускаем. Иначе - нет
    print "<center>";
    print "<big>$msg[2000]</big><br><br>";

    #Checking for dpools
    $squidv=`$conf_squid_path/squid -v`; # достаем список опций с которыми был скомпилирован прокси

    if ( $squidv =~ /--enable-delay-pools/ ) {
	$status = "enable";
    } else {
	$status = "disable";
    }

    if ($status ne "enable"){ # Если не включены пулы - зря работал :)
    print "<font color=$web_red_font><b>$msg[2001]:</b></font> $msg[2002].<br><br>"; # отображаем ошибку с сообщением
    print "<font>$msg[2003]<br></font>"; # советуем :)
    $stat="GLUCK: no --enable-delay-pools!"; # Непонятно зачем это надо :\
    goto the_end; # идем в лес... :) Точнее на вывод нижней части.
    }

    #If service_to_reconf not equal 'squid' then we will add squid reconf button
    if ($conf_service_to_reconf ne 'squid'){

	if ($squid_reconf and !(-e "$conf_stc_path/squid_reconf.lock")){
	    open tmpf, ">$conf_stc_path/squid_reconf.lock" or $ERR=$!;
	    close tmpf;
	}
	print "<hr>";
	print "<font size=1>$msg{'dpools_header'}</font><br>";
	print "<form method=POST>";
	my $ERR = undef;
	if (!(-e "$conf_stc_path/squid_reconf.lock")){
	    print "<input type=submit name=\"squid_reconf\" value=\"$msg{squid_reconf}\">";
	}
	else {
	    print "$msg{squid_reconf_queued}<br>";
	}
	print "</form>";
	print "<hr>";
    }#if

    if ($ERR){
	print "$msg{error}Can't create $conf_stc_path/squid_reconf.lock: $ERR<br>";
	logmsg(__FILE__." line ".__LINE__.":[ERROR] $user dpools.cgi can't create $conf_stc_path/squid_reconf.lock: $ERR");
    }


# Начало основной части работы с конфигом

  @delay_users=(); # все пользователи - сбрасываем на 0
  @otdel_acls=();
  $broken_otdels = ' ';
    foreach (@otdels)
        { # просматриваем папку stc/etc/
	     $o=$_;
	     my $usercount=0;
             open(USERLIST, "$conf_stc_path/o$_.users"); # открываем этот файл
	     open DPOOLOTDEL, ">$conf_stc_path/dpools/o$o.users" or $broken_otdels .= "$o ";
             while ($delay_cuser=<USERLIST>) # читаем оттуда список юзверей
                     {
                      $delay_cuser=~ s/[\s\t]{0,}#.*$//; # обрубаем имя юзверя и пробелы
		      $delay_cuser =~ s/\s+//;
                      chomp($delay_cuser); # удаляем мусор
                      if ($delay_cuser){
		        push @delay_users, $delay_cuser; # добавляем логин в массив
                        $delay_user_otdel{$delay_cuser}=$_; # не помню... :(
		        printf DPOOLOTDEL "\^$delay_cuser\$\n";
			++$usercount;
		      }
                     }
             close (USERLIST); # закрываем список юзверей
	     close DPOOLOTDEL;
	     if ($usercount < 1){
	        $broken_otdels .= "$o ";
	     }
	     else {
	        push (@otdel_acls, "$o:otdel_$o");
	        $otdel_acls_name[$o]=$parts[1];
	        $otdel_acls_id[$parts[1]]=$o;
	     }
        }
# Обработка конфига, создание нового, внесение изменений и т.д.

$dpools_num=0; # инициализация переменной кол-ва пулов

system ("cp -f $conf_squid_conf_path/squid.conf ./squid.conf.old"); # копируем squid.conf в текущую директорию. из него будем читать.
$err=0;
open SCF, "./squid.conf.old" or $err=1;
   if ($err eq 1)
   {print "<font color=#BB0000>$msg[2000]</font> $msg[2007] ./squid.conf.old: $!\n"; # открываем скопированный файл на чтение
    goto the_end;
   }
$err=0;
open NEWCONF, ">$conf_squid_conf_path/squid.conf" or $err=1;
   if ($err eq 1)
   {
   print "<font color=#BB0000>$msg[2000]</font> $msg[2007] $conf_squid_conf_path/squid.conf: $!\n"; # открываем оригинальный конфиг на запись
   goto the_end;
   }
$stc=0; # отметка о начале секции STC

while ($beg_line=<SCF>) # читаем файл конфига
    {
    $mod=0; # отметка о сделанной модификации строки
    $line=$beg_line; # оригинальную строку конфига - храним :)
    if ($line =~ /^#DO NOT REMOVE OR MODIFY THIS LINE!!!/) # если встречаем заветную строчку...
    {$stc=1;} # ставим отметку что мы находимся в секции STC. Это означает что мы теперь не будем переносить настройки пулов вниз, а просто считаем их. Запишем позже.
    chomp($line); # убираем мусор
#    $line=~ s/#.*//; # убираем коментарии по-моему это лишнее... Там коментарии только в начале строки можно писать.
    $line=~ s/[\s\t]{1,}/ /; # все пробелы и табы - заменяем на один
    $line=~ s/^[\s\t]{1,}//; # убираем все пробелы и табы с начала строки
    if (!$line && $stc eq 0) # если получилась пустая строка (тобиш коментарии или просто пусто) и мы находимся в общей секции
            {print NEWCONF "$beg_line"; next;} # запишем строку в неизменном виде
    @parts=split(" ", $line); # разбиваем строку с разделителем пробел
#    if ($parts[0] eq "acl") # если мы встретили параметр acl
#    {
#    }
    if ($parts[0] eq "delay_pools") # если мы встретили параметр delay_pools
    {
    $mod=1;  # метка о том, что надо модифицировать строку (в смысле перенести ее в конец, если мы находимся не в секции STC)
    $dpools_num=$parts[1]; # записываем кол-во пулов
    } # если мы встретили параметр delay_pools
    if ($parts[0] eq "delay_class" ) # если мы встретили параметр delay_class
    {
    $mod=1; # метка о том, что надо модифицировать строку (в смысле перенести ее в конец, если мы находимся не в секции STC)
    $delay_class[$parts[1]]=$parts[2]; # в массивчик забиваем класс каждого пула
    } # если мы встретили параметр delay_class
    elsif ($parts[0] eq "delay_access")  # если мы встретили параметр delay_access
    {
    $mod=1; # метка о том, что надо модифицировать строку (в смысле перенести ее в конец, если мы находимся не в секции STC)
    $clients=$line; # забираем отдельно список клиентов. Их может быть несколько через пробел
    $clients=~ s/^delay_access[\s]{1,}[0-9]{1,}[\s]{1,}(allow|deny)[\s]{1,}//; # удаляем мусор и собственно "delay_access"
    if ($parts[2] eq "allow" | $parts[2] eq "deny") # если allow или deny - запишем их по массивам. если другое - исправим ошибку удалив строку ;)
        {
        if ($parts[2] eq "allow"){
	    $delay_access{"$parts[2]_$parts[1]"}.="DELAYACCESS ".$clients."\n"; # получается по 2 массива на пул allow_$i, deny_$i, в котором список юзверей
	}
	else{
	    $delay_access{"$parts[2]_$parts[1]"}.=" ".$clients;
	}
        # также может быть несколько строк в которых юзвери к одному пулу приписаны. это тоже поддерживается ;)
	} # если allow или deny - запишем их по массивам.
    } # если мы встретили параметр delay_access
    elsif ($parts[0] eq "delay_parameters")  # если мы встретили параметр delay_parameters
    {
    $mod=1; # метка о том, что надо модифицировать строку (в смысле перенести ее в конец, если мы находимся не в секции STC)
    $param=$line; # записываем параметры в отдельную переменную
    $param=~s/^delay_parameters\s[0-9]{1,}[\s]{1,}//; # убираем мусор и "delay_parameters"
    $delay_parameters{"$parts[1]"}=$param; # записываем параметры в строку.
    }  # если мы встретили параметр delay_parameters

    if ($mod eq 1 && $stc eq 0) # если нужны модификации, и мы не в секции STC
    {
    print NEWCONF "\n#MOVED TO THE BOTTOM\n#$beg_line"; # Написать в конфиге что перенесли эту строку в секцию STC
    } # если нужны модификации, и мы не в секции STC
    elsif ($stc eq 0) # если мы не в секции STC
    {print NEWCONF "$beg_line";} # просто записать строку в неизменом виде.
    } # закончили читать файл конфига
close (SCF); # закрываем его

if ($ENV{'REQUEST_METHOD'} eq "POST") # если метод запроса - POST - значит кто-то хочет что-то подправить :)
    {
    $query=new CGI;

    if ($query->param('addnew')) # добавить новый пул
           {
        $ADD_pool_q=1; # метка что будем добавлять пул
            $ADD_pool=$query->param('insert_order'); # очередность, перед каким пулом будет вставлен текущий.
print "INSERT: $ADD_pool<br>";
            $ADD_pool_class=$query->param('pool_class'); # клас пула
            $ADD_delay_parameters=$query->param('param1')."/".$query->param('param2'); # параметры 1
            if ($ADD_pool_class eq "2") # если клас - 2 - добавить вторую пару параметров
                 {$ADD_delay_parameters.=" ".$query->param('param3')."/".$query->param('param4');} # добавление второй пары параметров
        if (!($query->param('param1') =~ /[\-0-9]{1,}/ && $query->param('param2') =~ /[\-0-9]{1,}/)) # если какой-то параметр из первой пары пропущен, или не число
            {
            $ADD_pool="";
            $ADD_pool_q=""; # снимаем метку добавления
            print ("<font color=#BB0000>$msg[2001]!</font> $msg[2004]!<br>"); # выдаем ошибку
            } # первая пара не указана
        if ($ADD_pool_class eq 2 && !($query->param('param3') =~ /[\-0-9]{1,}/ && $query->param('param4') =~ /[\-0-9]{1,}/)) # если клас пула - 2 и не указана вторая пара или там ошибка
            {
            $ADD_pool="";
            $ADD_pool_q=""; # снимаем метку добавления
            print ("<font color=#BB0000>$msg[2001]!</font> $msg[2005]!"); # выводим сообщение об ошибке
            } # если класс=2 и ошибка во второй паре
            $ADD_pool_access=""; # инициализируем переменную юзверей пула.

	my $pervyjnah = undef;
        foreach ($query->param('users')) # юзвери передаются с помощью multiple select - листаем
            {
	    if ($_ =~ /otdel_/s){
		my $otd = $_;
		$otd =~ s/otdel_//g;
		$otd = 0 + $otd;
		$ADD_pool_access .="DELAYACCESS otdel_$otd\n";
	    }#if
	    else {
		$ADD_pool_access.="DELAYACCESS $_\n";
            }
	}#foreach
        if (!($ADD_pool_access =~ /[^\s\t]/)) # Если в юзверях пула - болт
            {
            $ADD_pool="";
            $ADD_pool_q=""; # снимаем метку добавления
            print ("<font color=#BB0000>$msg[2001]!</font> $msg[2006]!"); # выводим сообщение
            } # если в юзверях пула - болт
        if (!match_users($ADD_pool_access)) # если $user не имеет власти над юзверями, которых хочет добавить в пул
            {
            $ADD_pool="";
            $ADD_pool_q=""; # снимаем метку добавления
            print ("<font color=#BB0000>$msg[2001]!</font> $msg[2027]!"); # выводим сообщение
            } # если $user не имеет власти над юзверями, которых хочет добавить в пул
           } # добавить новый пул
    elsif ($query->param('refresh')) # изменить существующий пул
    {
        $MOD_pool=$query->param('pool_id'); # получаем номер пула, который хотим отредактировать
        $MOD_pool_class=$query->param('pool_class'); # получаем новый клас пула
        $MOD_parameters[1]=$query->param('param1'); # параметры
        $MOD_parameters[2]=$query->param('param2'); # параметры
        $MOD_parameters[3]=$query->param('param3'); # параметры
        $MOD_parameters[4]=$query->param('param4'); # параметры
        # вобщем все аналогично добавлению, токо переменные не $ADD_... а $MOD_...
    if (!($MOD_parameters[1] =~ /[\-0-9]{1,}/ && $MOD_parameters[2] =~ /[\-0-9]{1,}/))
        {
        $MOD_pool="";
        print ("<font color=#CC0000>$msg[2001]!</font> $msg[2004]!<br>");
        }
    if ($MOD_pool_class eq 2 && !($MOD_parameters[3] =~ /[\-0-9]{1,}/ && $MOD_parameters[4] =~ /[\-0-9]{1,}/))
        {
        $MOD_pool="";
        print ("<font color=#CC0000>$msg[2001]!</font> $msg[2005]!");
        }
        $MOD_pool_access="";
    foreach ($query->param('users'))
        {
        $MOD_pool_access.="DELAYACCESS $_\n";
        }
    if (!($MOD_pool_access =~ /[^\s\t]/))
        {
        $MOD_pool="";
        print ("<font color=#CC0000>$msg[2001]!</font> $msg[2006]!");
        }
        if (!match_users($MOD_pool_access))
            {
            $MOD_pool="";
            print ("<font color=#BB0000>$msg[2001]!</font> $msg[2027]!");
            }
    } # изменить существующий пул

    elsif ($query->param('delete')) # удалить пул
           {
           $DEL_pool=$query->param('pool_id'); # достаем номер пула, подлежащий удалению. Проверка прав - после чтения конфига
           } # удалить пул
    } # конец обработки POST запроса


# начинаем писать секцию STC в конфиг

 print NEWCONF "#DO NOT REMOVE OR MODIFY THIS LINE!!!\n#\n"; # записываем разделитель

# User and otdel ACL's...

#        print NEWCONF "\n#########################################\n# STC otdel acls\n#\n";
#   foreach (@otdels) # записываем все отделы, которые нашли в stc/etc/
#       {
#        print NEWCONF "acl STC_otdel_$_ proxy_auth \"$conf_stc_path/o$_.users\"\n";
#       }

        print NEWCONF "\n#########################################\n# STC users acls\n#\n";
   foreach (@delay_users) # записываем всех юзверей, которых нашли в отделах
    {
        print NEWCONF "acl STC_user_$_ proxy_auth_regex ^$_\$\n";
    }
    print NEWCONF "\n#########################################\n# STC otdel acls\n#\n";
    foreach (@otdel_acls){
	($totd, $foo) = split (':');
	if ($broken_otdels =~ /\ $totd\ /s){print "!!!!!!<br>";next;}
	print NEWCONF "acl otdel_$totd proxy_auth_regex \"$conf_stc_path/dpools/o$totd.users\"\n";
    }
# End User and Otdel ACL's

if ($DEL_pool) # Если был помечен пул на удаление
    {
        if (!match_users($delay_access{"allow_$DEL_pool"})) # если нет прав у данного юзера это делать - не делаем
            {
            $DEL_pool=""; # снимаем отметку об удалении
            print ("<font color=#BB0000>$msg[2001]!</font> $msg[2028]!"); # выводи сообщение об ошибке
            $dpools_num_new=$dpools_num; # записываем новое кол-во пулов равным старому кол-ву...
            }
        else # если есть права у данного юзера это делать - делаем
       {$dpools_num_new=$dpools_num-1;} # записываем новое кол-во пулов на 1 меньше чем старое, ввиду удаления одного...
    }
elsif ($ADD_pool_q) # если стоит отметка о добавлении пула
    {$dpools_num_new=$dpools_num+1;} # записываем новое кол-во пулов равным на один больше
else {$dpools_num_new=$dpools_num;} # если нет изменений - записываем новое кол-во пулов равным старому кол-ву...

if ($dpools_num_new) # Если у нас есть какие-то пулы
    {print NEWCONF "\n\n#########################################\n# STC delay pools configuration\n#\ndelay_pools $dpools_num_new\n\n";} # записываем в конфиг кол-во пулов

$deleted=0; # отметка об осуществленном удалении
$added=0; # отметка об осуществленном добавлении
for ($i=1; $i<=$dpools_num; ++$i){ # цикл добавления пулов. добавляем пока они есть :)
    if ($ADD_pool eq $i) # если надо добавить пул перед текущим
    {
print "ADD_pool = $ADD_pool<br>";
        $added=1; # добавляем и ставим отметку об осуществленном добавлении
        # записываем конфиг
        print NEWCONF "#########################################\n# pool number $i\n#\n";
        print NEWCONF "delay_class $i $ADD_pool_class\n";
	$ADD_pool_access =~ s/DELAYACCESS/delay_access\ $i\ allow/ig;
        print NEWCONF $ADD_pool_access."\n";
        print NEWCONF "delay_access $i deny all\n";
        print NEWCONF "delay_parameters $i ".$ADD_delay_parameters."\n\n";
    }
    elsif ($DEL_pool eq $i) # если необходимо удалить текущий пул
    {$deleted=1; next;} # удаляем и ставим отметку
    elsif ($MOD_pool eq $i) # есди необходимо модифицировать текущий пул
    { # записываем новые параметры
        $delay_parameters{"$i"}="$MOD_parameters[1]/$MOD_parameters[2]"; # первая пара задержек
        if ($MOD_pool_class eq 2) # если класс = 2
        {
	    $delay_parameters{"$i"}.=" $MOD_parameters[3]/$MOD_parameters[4]"; # вторая пара задежек
	}
        $delay_class[$i]=$MOD_pool_class; # новый класс
	$MOD_pool_access =~ s/DELAYACCESS/delay_access\ $i\ allow/ig;
        $delay_access{"allow_$i"}=$MOD_pool_access; # новые юзвери
        $modified=1; # ставим отметку об осуществленной модификации
    } # есди необходимо модифицировать текущий пул

    if ($deleted) # если был удален какой-то пул
    {
	$num=$i-1; # присутствует сдвиг на 1. Новые номера пулов будут на 1 меньше, а параметры о них - хранятся по старому номеру. Сдвигаем
        $delay_class[$num]=$delay_class[$i];
        $delay_access{"allow_$num"}=$delay_access{"allow_$i"};
        $delay_access{"deny_$num"}=$delay_access{"deny_$i"};
        $delay_parameters{"$num"}=$delay_parameters{"$i"};
    }
    elsif ($added)
    { # тоже самое при удалении, но сдвиг в противоположную сторону
        $num=$i+1;
#print "DEBUG: I=$i ($delay_class[$i] $delay_access{\"allow_$i\"}) NUM=$num ($delay_class[$num] $delay_access{\"allow_$num\"})<br>";
        $new_delay_class[$num]=$delay_class[$i];
        $new_delay_access{"allow_$num"}=$delay_access{"allow_$i"};
        $new_delay_access{"deny_$num"}=$delay_access{"deny_$i"};
        $new_delay_parameters{"$num"}=$delay_parameters{"$i"};
    }
    else {$num=$i;} # если нет сдвига - пишем что параметры хранятся под текущим номером
    if (!$delay_access{"deny_$i"}){$delay_access{"deny_$i"}=" all";}
    # записываем все в конфиг-файл
    print NEWCONF "#########################################\n# pool number $num\n#\n";
    print NEWCONF "delay_class $num $delay_class[$i]\n";
    my $tmp_access = $delay_access{"allow_$i"};
    $tmp_access =~ s/DELAYACCESS/delay_access\ $num\ allow/ig;
    print NEWCONF $tmp_access;
    print NEWCONF "delay_access $num deny ".$delay_access{"deny_$i"}."\n";
    print NEWCONF "delay_parameters $num ".$delay_parameters{"$i"}."\n\n";
}#for

if ($added){
for ($i=1; $i<=$dpools_num_new; ++$i){
    if ($i <= $ADD_pool){next;}
    else{
        $delay_class[$i]=$new_delay_class[$i];
        $delay_access{"allow_$i"}=$new_delay_access{"allow_$i"};
        $delay_access{"deny_$i"}=$new_delay_access{"deny_$i"};
        $delay_parameters{"$i"}=$new_delay_parameters{"$i"};
    }
}#for
}#if
    if ($ADD_pool eq 0 && $ADD_pool_q) # если было установлено добавить пул в конец очереди
        {
        # записываем в конфиг-файл новый пул
        print NEWCONF "#########################################\n# pool number $i\n#\n";
        print NEWCONF "delay_class $i $ADD_pool_class\n";
	$ADD_pool_access =~ s/DELAYACCESS/delay_access\ $i\ allow/ig;
        print NEWCONF $ADD_pool_access."\n";
        print NEWCONF "delay_access $i deny all\n";
        print NEWCONF "delay_parameters $i ".$ADD_delay_parameters."\n\n";
        # устанавливаем параметры для отображения в таблице, которая будет ниже.
        $delay_class[$i]=$ADD_pool_class;
        $delay_access{"allow_$i"}=$ADD_pool_access;
        $delay_access{"deny_$i"}="all";
        $delay_parameters{"$i"}=$ADD_delay_parameters;
        } # если было установлено добавить пул в конец очереди
    elsif ($added eq 1) # если добавлено не в конец очереди - получился сдвиг и в результате - два пула с одинаковыми параметрами в памяти (в конфиге верно ;))
        { # один из них мы задействуем под новый пул
        $delay_class[$ADD_pool]=$ADD_pool_class;
        $delay_access{"allow_$ADD_pool"}=$ADD_pool_access;
        $delay_access{"deny_$ADD_pool"}="all";
        $delay_parameters{"$ADD_pool"}=$ADD_delay_parameters;
    }

close (NEWCONF); # закрываем новый конфиг-файл

system ("rm -f ./squid.conf.old"); # удаляем старый временный конфиг

$dpools_num=$dpools_num_new; # записываем кол-во пулов в соответствующую переменную
# конец обработки файла конфига

# вывод на екран всей информации и форм...

print ("<table width=\"100%\" border=0 cellspacing=0 align=center>"); # объявление таблицы

# название класа пулов для юзверей
$dclass[1]=$msg[2009];
$dclass[2]=$msg[2010];

for ($i=1; $i<=$dpools_num; $i++)
    { # пролистываем все пулы
    print ("<tr><form action=dpools.cgi method=post><input type=hidden name=pool_id value=$i>\n"); # каждая строка - отдельная форма
    print ("<td valign=top><br><b>$msg[2011]:</b> <select name=pool_class style=\"width:auto;\">
            <option value=1>$dclass[1]</option>
            <option value=2");
    if ($delay_class[$i] eq 2) {print (" selected");}
    print (">$dclass[2]</option>
            </select><br>\n");
    print ("<b>$msg[2012]:</b><br>\n<select multiple name=users style=\"width:100%; height:120;\">\n");

   foreach (@otdel_acls) # Список отделов
       {
       # если к данному пулу присвоены пользователи, которые подчиняются текущему юзверю - выводим ТОЛЬКО тех юзверов, которые в подчинении
       # если присвоены пользователи из других отделов - выводим всех пользователей, но убираем кнопочки ;)
        ($id, $acl) = split (':');
       if (match_users($delay_access{"allow_$i"}) eq 1 && match_users("$acl") eq 0)
           {
            next;
           }
        print ("<option value=\"$acl\"");
           if (($delay_access{"allow_$i"} =~ /^$acl[\s]/) || ($delay_access{"allow_$i"} =~ /[\s]$acl$/) || ($delay_access{"allow_$i"} =~ /[\s]$acl[\s]/))
           {print (" selected");}
        print (">$msg[2013]");
	if ($otdel_prn[$id]) {print $otdel_prn[$id];}
	else {print $id;}
	print ("</option>\n");

       }

   foreach (@delay_users)
       {
       if (match_users($delay_access{"allow_$i"}) eq 1 && match_users("STC_user_$_") eq 0)
           {
            next;
           }
        print ("<option value=\"STC_user_$_\"");
           if ($delay_access{"allow_$i"} =~ /STC_user_$_/)
           {print (" selected");}
        print (">$_</option>\n");
       }

    print ("</select></td>\n<td width=\"220\"><br><center><b>$msg[2014]:</b></center>");
    $delay_parameters{"$i"} =~ s/(^[\t\s]{1,}|[\t\s]{1,}$)//; # параметры задержки
    @l1=split(" ", $delay_parameters{"$i"});
    @l2=split("/", $l1[0]);
    @l3=split("/", $l1[1]);
    print ("<b>$msg[2015]:</b><br>");
    print ("$msg[2016]: <input type=text name=param1 value=\"$l2[0]\" style=\"width:60;\"> $msg[2018]<br>\n");
    print (" &nbsp; &nbsp; $msg[2017]: <input type=text name=param2 value=\"$l2[1]\" style=\"width:60;\"> $msg[2019]<br>\n");
    print ("<br><b>$msg[2020]:</b><br>");
    print ("$msg[2016]: <input type=text name=param3 value=\"$l3[0]\" style=\"width:60;\"> $msg[2018]<br>\n");
    print (" &nbsp; &nbsp; $msg[2017]: <input type=text name=param4 value=\"$l3[1]\" style=\"width:60;\"> $msg[2019]<br><br>\n");
    print ("</td>");
    print ("<td valign=top align=center><br><br>$msg[2021]: <b>$i</b><br><br>");
    if (match_users($delay_access{"allow_$i"}) eq 1 )
        {
        print ("<input type=submit name=refresh value=\"$msg[2022]\" style=\"width:100;\"><br><br>\n");
        print ("<input type=submit name=delete value=\"$msg[2023]\" style=\"width:100;\">\n");
        }
    print ("</td></form></tr>\n<tr><td colspan=3><hr></td></tr>\n\n");
    }

## Форма добавления... аналогично предыдущей
if ($admin{$user}){
    print ("<tr><form action=dpools.cgi method=post>\n");
    print ("<td><br><b>$msg[2011]:</b> <select name=pool_class style=\"width:auto;\">
            <option value=1>$dclass[1]</option>
            <option value=2>$dclass[2]</option>
            </select><br>\n");
    print ("<b>$msg[2012]:</b><br>\n<select multiple name=users style=\"width:100%; height:120;\">\n");

   foreach (@otdel_acls)
       {
       ($id, $acl) = split(":");
       if (match_users("STC_otdel_$id") eq 1)
        {
	print ("<option value=\"".$acl."\">$msg[2013]");
	if ($otdel_prn[$id]) {print $otdel_prn[$id];}
	else {print $id;}
	print ("</option>\n");
	}
       }
#   foreach (@otdels)
#       {
#       if (match_users("STC_otdel_$_") eq 1)
#        {print ("<option value=\"STC_otdel_$_\">$msg[2013] $_</option>\n")};
#       }

   foreach (@delay_users)
       {
       if (match_users("STC_user_$_") eq 1 )
        {print ("<option value=\"STC_user_$_\">$_</option>\n")};
       }

    print ("</select></td>\n<td><br><center><b>$msg[2014]:</b></center>");
    print ("<b>$msg[2015]:</b><br>");
    print ("$msg[2016]: <input type=text name=param1 value=\"\" style=\"width:60;\"> $msg[2018]<br>\n");
    print (" &nbsp; &nbsp; $msg[2017]: <input type=text name=param2 value=\"\" style=\"width:60;\"> $msg[2019]<br>\n");
    print ("<br><b>$msg[2020]:</b><br>");
    print ("$msg[2016]: <input type=text name=param3 value=\"\" style=\"width:60;\"> $msg[2018]<br>\n");
    print (" &nbsp; &nbsp; $msg[2017]: <input type=text name=param4 value=\"\" style=\"width:60;\"> $msg[2019]<br><br>\n");
    print ("</td>");
    print ("<td><br><br>
            <select name=insert_order>
            <option value=0>$msg[2024]</option>");
       for ($i=1; $i<=$dpools_num; $i++) # тут пишем куда этот пул добавлять. В конец или перед каким-то...
            {print "<option value=$i>$msg[2025] $i</option>\n";}
    print ("</select><br><br>
            <input type=submit name=addnew value=\"$msg[2026]\" style=\"width:100;\"><br><br>\n");
    print ("</form></tr>\n\n");
}#if admin

print ("</table>"); # закрываем таблицу

# конец вывода...


sub match_users # функция проверки принадлежности юзверей к отделу текущего начальника, или проверка админа...
    {

    if ($admin{$user}) # если юзер - админ
      { return 1;} # все можно, не надо гемороиться :)
    else {return 0;}
      my ($users)=@_; # юзеры, переданные в качестве параметра
      @sub_users=split(" ", $users); # разделитель - пробел

      foreach (@sub_users)
          { # листаем всех юзверей
           if ($_ =~ /^STC_user_/) # если юзверь - это логин
               {
               $_=~ s/^STC_user_//; # выдираем логин
               $_=$delay_user_otdel{$_}; # достаем номер отдела для этого логна. Считывание происходило раньше.

               if (!( (" ".join(" ", @user_boss)." ") =~ /\s$_\s/)) # если не подчинен текущему босу
                      {return 0;} # в лес
               } # если юзверь - это логин
           else # если юзверь - это отдел
               {
#               print $_;
               $_= $otdel_acls_id[$_]; # выдираес номер отдела
#               print "-".$boss_users{$user}."- =~ -$_-";
               if (!( (" ".join(" ", @user_boss)." ") =~ /\s$_\s/)) # если бос - не бос этого отдела
                      {return 0;} # в лес
               } # если юзверь - это отдел
          }
      return 1; # если мы сюда дошли - значит юзверь - босс над всеми переданчми юзверями
    }

}
else # а если юзверь никакой не админ и не бос - сообщаем ему что он нехороший человек :)
    {
     print "$msg[5]<br>"; # вот так!
    }

# КОНЕЦ!
the_end:

&load_footer; # одна строка все сделает, так лучше

# СПАСИБО ЗА ВНИМАНИЕ! :)))
# Blin! Orkan, gde ty takuju travu beresh?! 2 dnya razabiralsya/peredelyval script! /slivarez/
