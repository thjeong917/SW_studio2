From java:8

RUN apt-get update && apt-get install -y build-essential maven git wget ssh fabric netcat expect ca-certificates
 
RUN mkdir -p /root/temp && cd /root/temp && git clone https://github.com/naver/nbase-arc.git

RUN cd /root/temp/nbase-arc && make release && cp -r release/nbase-arc /root

WORKDIR /root

RUN cd / && wget https://archive.apache.org/dist/zookeeper/zookeeper-3.4.9/zookeeper-3.4.9.tar.gz && tar -zxvf zookeeper-3.4.9.tar.gz && rm /zookeeper-3.4.9.tar.gz

ADD zoo.cfg ./zookeeper/conf/zoo.cfg

RUN sed -i "s/REDIS_VERSION = .*/REDIS_VERSION = \"\"/g" /root/nbase-arc/mgmt/config/conf_dnode.py
RUN sed -i "s/GW_VERSION = .*/GW_VERSION = \"\"/g" /root/nbase-arc/mgmt/config/conf_dnode.py
RUN sed -i "s/SMR_VERSION = .*/SMR_VERSION = \"\"/g" /root/nbase-arc/mgmt/config/conf_dnode.py

RUN sed -i "s/CONF_MASTER_PORT = .*/CONF_MASTER_PORT = 1122/g" /root/nbase-arc/mgmt/config/conf_mnode.py
RUN sed -i "s/CONF_MASTER_MGMT_CONS = .*/CONF_MASTER_MGMT_CONS = 1/g" /root/nbase-arc/mgmt/config/conf_mnode.py
RUN sed -i "s/USERNAME = .*/USERNAME = \"root\"/g" /root/nbase-arc/mgmt/config/conf_mnode.py

RUN sed -i "s/confmaster.ip=0.0.0.0 .*/confmaster.ip=127.0.0.1/g" /root/nbase-arc/confmaster/cc.properties

RUN ssh-keygen -f /root/.ssh/id_rsa -N "" && cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

WORKDIR /root/nbase-arc/mgmt

ADD setup.sh ./setup.sh
ADD install.sh ./install.sh


ENTRYPOINT ./install.sh
