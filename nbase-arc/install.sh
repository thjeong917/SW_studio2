#!/bin/bash

ip_addr=127.0.0.1

rm -rf ~/nbase-arc/pgs
rm -rf ~/nbase-arc/gw
rm -rf /tmp/zookeeper

sed -i "s/confmaster\.ip=.*/confmaster\.ip=$ip_addr/g" /root/nbase-arc/confmaster/cc.properties
sed -i "s/CONF_MASTER_IP =.*/CONF_MASTER_IP = \"$ip_addr\"/g" ~/nbase-arc/mgmt/config/conf_mnode.py


/root/zookeeper/bin/zkServer.sh start && sleep 5 && cd /root/nbase-arc/confmaster && ./confmaster-*.sh

sleep 5 && nohup bash -c "echo cm_start | nohup nc 127.0.0.1 1122" &

/etc/init.d/ssh start

sleep 5 && cd /root/nbase-arc/mgmt && ./setup.sh

/bin/sh -c "sleep infinity"
