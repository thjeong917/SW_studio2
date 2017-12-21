From ubuntu:14.04
MAINTAINER SangU

RUN sed -i 's/archive.ubuntu.com/ftp.jaist.ac.jp/g' /etc/apt/sources.list

RUN apt-get update && apt-get install -y supervisor openssh-server aptitude net-tools iputils-ping nano \
 git netcat build-essential make gcc g++ autoconf automake libtool libextutils-pkgconfig-perl libcppunit-dev python2.7-dev python-setuptools subversion
 
RUN apt-get install openjdk-7-jdk -y \
  && echo "export JAVA_HOME=/usr" \
  && echo "export PATH=$PATH:$JAVA_HOME/bin"  


ENV ANT_VERSION 1.9.6

RUN cd && apt-get install ant -y \
  && echo "export ANT_HOME=/usr" \
  && echo "export PATH=$PATH:$ANT_HOME/bin"

RUN mkdir -p /opt 

RUN cd /opt && git clone https://github.com/ruo91/arcus.git 
RUN cd /opt/arcus/scripts && ./build.sh

ADD conf.json /opt/arcus/scripts/conf/conf.json

WORKDIR opt/arcus/scripts

RUN ssh-keygen -t dsa -P '' -f "/root/.ssh/id_dsa"
RUN cat /root/.ssh/id_dsa.pub >> /root/.ssh/authorized_keys
RUN chmod 644 /root/.ssh/authorized_keys

RUN mkdir -p /var/log/supervisor
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir /var/run/sshd
RUN sed -i 's/without-password/yes/g' /etc/ssh/sshd_config
RUN sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config

RUN sudo echo 'root:arcus' |chpasswd
#RUN echo 'passwd -d root'

EXPOSE 22 2181 11211 11212

CMD ["/usr/bin/supervisord"]


