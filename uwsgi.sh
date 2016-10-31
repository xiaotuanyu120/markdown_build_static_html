#!/bin/bash

function stop(){
    pid=`ps aux|grep uwsgi|grep 'S '|awk '{print $2}'`
    kill -9 $pid;
}

function start(){
    cd /data/www/linux_manual;
    nohup uwsgi myblog.ini &
}

case $1 in
    stop)
        stop;
    ;;
    start)
        start;
    ;;
    restart)
        stop;
        sleep 1;
        start;
    ;;
esac