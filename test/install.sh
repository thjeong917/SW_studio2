#!/bin/bash

/root/zookeeper/bin/zkServer.sh start && sleep 5 && cd /root/nbase-arc/confmaster && ./confmaster-*.sh

sleep 10 && nohup bash -c "echo cm_start | nohup nc 127.0.0.1 1122" &

/etc/init.d/ssh start

sleep 10 && cd /root/nbase-arc/mgmt && ./setup.sh

/bin/sh -c "sleep infinity"
