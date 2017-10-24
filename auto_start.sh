#!/usr/bin/env bash

services=('apache2' 'nginx' 'mongodb' 'bluetooth' 'cups' 'mysql'
'network-manager' 'NetworkManager' 'postgresql' 'redis-server' 'snmpd' 'ssh' 'tomcat8'
'virtualbox' 'virtualbox-guest-utils' 'cups-browsed' 'nmbd' 'smbd' 'samba-ad-dc')

function check()
{
    if [[ $(ps -ef | grep -v grep | grep $1 | wc -w) -eq 0 ]] ; then
        echo 'starting........................'$1
        sudo /etc/init.d/$1 start
        echo '.................................'
    fi;
    print $2
}

for service in "${!services[@]}"
do
    check ${services[$service]}
done


# Disable these services from auto starting at boot time
#for service in "${!services[@]}"
#do
#    sudo update-rc.d ${services[$service]} disable
#done

# Enable these services to auto start at boot time
#for service in "${!services[@]}"
#do
#    sudo update-rc.d ${services[$service]} enable
#done
