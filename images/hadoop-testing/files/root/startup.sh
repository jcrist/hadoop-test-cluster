#! /bin/bash

case "$HADOOP_TESTING_CONFIG" in
simple|SIMPLE|"")
    CONFIG_PATH="/etc/hadoop/conf.simple"
    ;;
kerberos|KERBEROS)
    CONFIG_PATH="/etc/hadoop/conf.kerberos"
    ;;
custom|CUSTOM)
    CONFIG_PATH="/etc/hadoop/conf.custom"
    ;;
*)
    CONFIG_PATH="$HADOOP_TESTING_CONFIG"
    ;;
esac

alternatives --install /etc/hadoop/conf hadoop-conf $CONFIG_PATH 50 \
    && alternatives --set hadoop-conf $CONFIG_PATH

exec supervisord --configuration $1
