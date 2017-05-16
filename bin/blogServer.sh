#!/bin/bash

BASE_DIR=/data/www/linux_manual

function stop(){
    pid=`ps aux|grep uwsgi|grep 'S '|awk '{print $2}'`
    kill -9 $pid;
}

function start(){
    cd ${BASE_DIR}/conf
    nohup uwsgi blog.ini &
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
