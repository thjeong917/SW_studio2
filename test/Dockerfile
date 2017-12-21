From hyeongseok05/nbase-arc

ADD zoo.cfg ./zookeeper/conf/zoo.cfg

RUN sed -i 's/CONF_MASTER_IP = .*/CONF_MASTER_IP = "127.0.0.1"/g' /root/nbase-arc/mgmt/config/conf_mnode.py

RUN sed -i "s/confmaster.ip=0.0.0.0 .*/confmaster.ip=127.0.0.1/g" /root/nbase-arc/confmaster/cc.properties

WORKDIR /root/nbase-arc/mgmt

ADD setup.sh ./setup.sh
ADD install.sh ./install.sh


#ENTRYPOINT ./install.sh
