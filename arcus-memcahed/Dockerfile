From ubuntu:14.04

RUN sed -i 's/archive.ubuntu.com/ftp.jaist.ac.jp/g' /etc/apt/sources.list

RUN apt-get update && apt-get install -y curl openssh-server supervisor

RUN apt-get install openjdk-7-jdk -y \
  && echo "export JAVA_HOME=/usr" \
  && echo "export PATH=$PATH:$JAVA_HOME/bin"  

RUN useradd -M -s /sbin/nologin memcached \
  && mkdir -p /var/run/memcached && chown memcached:memcached /var/run/memcached


RUN mkdir -p /var/log/supervisor
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir /root/.ssh && mkdir /var/run/sshd
RUN sed -i 's/without-password/yes/g' /etc/ssh/sshd_config
RUN sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config

RUN echo 'root:memcached' |chpasswd
#RUN echo 'passwd -d root'

EXPOSE 22 2181 11211 11212

CMD ["/usr/bin/supervisord"]
