#!/usr/bin/perl
#STC fixperms.pl script - version 0.5
print "\nReading /etc/stc.conf file ... ";

open cf, "</etc/stc.conf" or die "Can't open /etc/stc.conf: $! \n";
while($line=<cf>){
   chomp($line);
   $line=~ s/#.*//;
   $line=~ s/[\s\t]{1,}/ /;
   $line=~ s/^[\s\t]{0,}//;
   if (!$line){next;}
   @parts=split(" ", $line);
   $var=shift(@parts);
   @$var=@parts;
   $$var=$parts[0];
}
close (cf);
print "done\n";

print "Changing file attributes... ";
    system("chown -R $apache_user $stc_path >> $log_file 2>&1");
    system("chmod 755 $stc_path >> $log_file 2>&1");
    system("chmod 755 $stc_path/profiles >> $log_file 2>&1");
    system("chmod 644 $stc_path/profiles/* >> $log_file 2>&1");
    system("chmod 755 $stc_path/lang >> $log_file 2>&1");
    system("chmod 644 $stc_path/lang/* >> $log_file 2>&1");
    system("chmod 755 $stc_path/includes >> $log_file 2>&1");
    system("chmod 644 $stc_path/includes/* >> $log_file 2>&1");
    system("chown $apache_user $reports_dir >> $log_file 2>&1");
    system("chmod 755 $reports_dir >> $log_file 2>&1");
    system("chown root $stc_path/trusted_users >> $log_file 2>&1");
    system("chown root $stc_path/admin.users >> $log_file 2>&1");
    system("chown $apache_user $stc_path/dpools >> $log_file 2>&1");
    system("chmod 755 $stc_path/messages >> $log_file 2>&1");
    system("chmod 755 $stc_path/messages/users >> $log_file 2>&1");
    system("chmod 755 $stc_path/dpools >> $log_file 2>&1");

    system("chown $apache_user:$apache_group $www_data_path/stat/* >> $log_file 2>&1");
    system("chown $apache_user:$apache_group $www_data_path/stat/statist/* >> $log_file 2>&1");
    system("chown $apache_user:$apache_group $www_data_path/stat/messages/* >> $log_file 2>&1");
    system("chown $apache_user:$apache_group $www_data_path/stat/themes >> $log_file 2>&1");
    system("chown $apache_user:$apache_group $stc_path/messages/users >> $log_file 2>&1");
    system("chown $apache_user:$apache_group $stc_path >> $log_file 2>&1");
    system("chmod -R 755 $limit_path >> $log_file 2>&1");
    system("chmod -R 755 $www_data_path/stat/statist/  >> $log_file 2>&1");
    system("chmod -R 755 $www_data_path/stat/messages/  >> $log_file 2>&1");
    system("chmod 755 $www_data_path/stat/  >> $log_file 2>&1");
    system("chmod 755 $www_data_path/stat/themes/  >> $log_file 2>&1");
print "done\n";
