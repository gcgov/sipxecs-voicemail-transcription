#!/bin/sh
# chkconfig: 123456 90 10
#
workdir=/usr/voicemailtranscription

start() {
    cd $workdir
    /usr/bin/env python3 /usr/voicemailtranscription/vrmilter.py &
    echo "Server started."
}

stop() {
    pid=`ps -ef | grep '[p]ython3 /usr/voicemailtranscription/vrmilter.py' | awk '{ print $2 }'`
    echo $pid
    kill $pid
    sleep 2
    echo "Server killed."
}

case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    stop
    start
    ;;
  *)
    echo "Usage: /etc/init.d/voicemailtranscription {start|stop|restart}"
    exit 1
esac
exit 0