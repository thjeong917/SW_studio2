# **Software Studio 2 : Open Source Software Project**

*This markdown is for ITE3068, Hanyang University Software Studio 2 course. <br>*

## **<br>Project Objective** 
-------------------------------------------------------------------
네이버의 오픈소스 프로젝트인 Naver의 OSS(Open Source Software)인 Arcus(Memory Cache Cloud)를 사용한 샘플 프로젝트 구현 및 Arcus 도입의 전/후 간의 성능 비교.

### <br>Team

소속 | 학번 | 이름
-------- | --------- | ------------
한양대학교 컴퓨터공학부 컴퓨터전공 | 2013011695 | 정태화
한양대학교 컴퓨터공학부 소프트웨어전공 | 2013010971 | 김상우

### <br>Evaluation criteria
* 도커 사용 : *Done*
* Arcus 사용 전/후의 성능 비교 : *Done*
* nBase-ARC 사용 : *Done*
* 멀티노드 사용 : *Done*
* Hubblemon 사용 : *Done*
* nGrinder 사용 : *Done*
* Contribution : *total 4 contributes accepted(in develop branch)* 


## **<br><br>Project Repository**
---------------------------------------------------------------------------------

* **dashbd** : mysql을 사용하기 위해 mysql을 서버로 구현한 웹 애플리케이션
* **arcus_dashbd** : arcus를 사용하기 위해 mysql과 애플리케이션 사이에 arcus를 연결해준 웹 애플리케이션
* **redis_dashbd** : nbase-arc를 사용하기 위해 redis로 서버를 구현한 웹 애플리케이션
* **arcus** : arcus의 컨트롤러 역할을 하는 컨테이너 생성을 위한 이미지
* **arcus-memcached** : arcus의 cache-cloud를 위한 추가적인 스토리지 역할을 하는 컨테이너 생성을 위한 이미지
* **Performance_report** : ngrinder를 이용한 웹 어플리케이션의 stress test 결과가 들어있다. 서버로 mysql만 사용했을 경우, arcus와 함께 사용했을 경우, nbase-arc와 함께 사용했을 경우에 대한 test result 파일이 들어있다.
* **hubblemon** : hubblemon을 이용한 test result 출력파일이 들어있다.



## **<br><br>Docker**
-------------------------------------------------------------------
### 도커를 사용한 가상 환경 구축

* 도커란 컨테이너 기반의 오픈소스 가상화 플랫폼으로, 기존의 가상환경과 다르게 하드웨어는 같은 리소스를 유지하며 실행환경만을 분리하여 각 컨테이너를 수행하는 방식이다.
* 두 대의 노트북으로, 하나는 OS X 기반의 도커, 하나는 ubuntu기반의 도커를 이용하여 같은 프로젝트를 동시에 진행하였다.


<img width="1230" alt="ss" src="https://user-images.githubusercontent.com/33930852/64950176-c65a5600-d8b5-11e9-86dd-ee3a022838ec.png">



## **<br><br>web-application**
--------------------------------------------------------------------------------
### python-flask을 통해 구현한 web-application

Dashboard | 
:--------: | 
<img width="1440" alt="ss2" src="https://user-images.githubusercontent.com/33930852/64950178-c6f2ec80-d8b5-11e9-952f-ded48e5baef5.png"> | 


* 웹 어플리케이션의 구현은 오픈소스를 사용하였다.
>  https://github.com/Prev/askhy

* 위의 웹 어플리케이션을 포크하여 가져와, mysql과 연동, arcus와 연동, nbase-arc와 연동을 모두 직접 세팅하였다.
* localhost의 8080번 포트와 클라이언트의 80번 포트를 binding 하여 로컬호스트에서 클라이언트에 접속할 수 있게 하였다.
* 어플리케이션은 글과 댓글을 작성하는 구조로 구현되어 있는데, 글을 작성할 때마다 글의 내용, 작성 ip, 작성 시간을 mysql database에 저장하게 된다.
* arcus 또는 nbase-arc와의 연동을 위하여 flask 상의 코드에서 직접 수정을 해주었다. 자세한 내용은 아래의 arcus 파트와 nbase-arc 파트에 작성하였다.
* arcus의 경우 함께 제공되는 [arcus-python-client](https://github.com/naver/arcus-python-client)를 받아 import하여 사용하였고, nbase-arc의 경우에는 redis 기반이므로 쉽게 pip install redis로 import하여 사용하였다. 


## **<br><br>Arcus**
---------------------------------------------------------------------------------
### Arcus를 사용한 메모리 캐시 클라우드 구축
>  https://github.com/naver/arcus

* Arcus는 memcached 프로토콜을 지원하여 백엔드 데이터베이스 앞에 위치하여 데이터 캐싱을 통해 데이터베이스 과부하를 막아주고 서비스에게 빠른 응답성을 제공한다.
* 컨트롤러 역할을 하는 1대의 Arcus-admin과, resource 역할을 하는 3대의 Arcus-memcached로 구성되어 있다.
* Dockerfile로 빌드된 image를 이용하여 도커 위의 가상 환경에서 Arcus-admin, Arcus-memcached를 각각의 컨테이너로 구축하였다.
* admin에서 tcp port 22, zookeeper port 2181, memcached port 11211 & 11212,  hubblemon port 22 를 열어 연동이 가능하게 해주었다.
* memcached에서는 zookeeper를 위한 포트와 Arcus memcached를 위한 포트를 열어주었다.
* password와 previlege issue가 계속 발생하여 각 memcached에 admin의 ssh key를 직접 배포하여 연동시켰다.
* 위 컨테이너들을 전부 구축 후 Arcus의 zookeeper와 memcached를 모두 init 및 start하여 connection을 확인하였다.

### <br>Cache Use
* Arcus와의 캐시 연동을 위하여 mysql과 연동해주었다.
* [Arcus-python-client](https://github.com/naver/arcus-python-client)의 `arcus.py`와, `arcus_mc_node.py`를 라이브러리로 가져와 web application에서 flask의 `main.py`에 import하였다.
* Cache 정책으로 글이나 댓글을 남길 시에 저장되는 ip address를 캐싱하게 하였다.
* webpage가 로드될 때 먼저 arcus에 캐싱된 key를 찾아 get하여 존재여부를 체크한 후, 없을 경우 mysql에서 가져온 후 set으로 캐싱에 저장하게 하였다.

### <br>Result
* Zookeeper<br>
`./arcus.sh zookeeper stat`
<p align="center"><img width="1440" alt="ss3" src="https://user-images.githubusercontent.com/33930852/64950181-c6f2ec80-d8b5-11e9-9862-0f8ec07dfdd9.png"></p><br>

* Memcached<br>
`./arcus.sh memcached list cloudname`
<img width="732" alt="ss4" src="https://user-images.githubusercontent.com/33930852/64950182-c6f2ec80-d8b5-11e9-9c25-acc3e8a99df4.png">

## **<br><br>nbase-arc**
---------------------------------------------------------------------------------
### nbase-arc를 사용한 redis clustering
* nbase_arc는 redis 기반의 분산 메모리 스토리지로, 레디스 서버를 자동으로 클러스터링하여 데이터를 빠르고 안정적으로 가져오는 기능을 제공한다.
* master-slave 관계를 통해 구성하여 명령어를 빠르고 정확하게 실행할 수 있다.

### <br>Cache Use
* nbase-arc의 사용을 위하여 mysql과 redis를 연동해주었다.
* web application 상에서 requirements redis를 추가한 후, `main.py`에 import하여 사용하였다.
* Cache 정책으로 글이나 댓글을 남길 시에 저장되는 ip address를 캐싱하게 하였다.
* webpage가 로드될 때 먼저 redis에 캐싱된 key를 찾아 get하여 존재여부를 체크한 후, 없을 경우 mysql에서 가져온 후 set으로 캐싱에 저장하게 하였다.
* arcus와 같이 멀티노드를 사용하기 위해 nbase-arc-admin 컨테이너와 nbase-arc-node 컨테이너들을 생성한 후 port를 공유하여 multi-node로 클러스터링이 가능하게 하였다.

### <br>Result
* nbase-arc installation<br>
<img width="1440" alt="ss5" src="https://user-images.githubusercontent.com/33930852/64950183-c78b8300-d8b5-11e9-9b0f-a60a78e8c9f4.png">


## **<br><br>nGrinder**
-------------------------------------------------------------------------------

### nGrinder를 사용한 Performance Test

>  https://github.com/naver/ngrinder

* nGrinder는 web page에 스트레스 테스트를 하고 이에 따른 속도를 보여주는 testing tool이다.
* 도커를 이용하여 controller 1대, agent 1대 각각의 가상화 컨테이너를 구축하여 ngrinder를 실행시켰다.
* localhost에서 접속하여 test를 진행할 필요가 있어 localhost의 80번 포트에 바인딩하여 컨테이너를 생성하였다.
* 9010-9019번 포트는 controller에 agent를 연결할 포트, 12000번부터 12029번 포트는 stress test를 보낼 포트로 할당해주었다.
* 이를 통해 mysql, Arcus, nbase-arc 3가지 서버 경우의 애플리케이션에 대한 스트레스 테스트를 해보았다.

### <br>How To
Screenshot | 
:--------: | 
<img width="1440" alt="ss6" src="https://user-images.githubusercontent.com/33930852/64950198-cf4b2780-d8b5-11e9-9496-8f4e690caf8d.png"> |

* stress test를 실행할 URL을 입력받고, stress test에 사용될 agent의 개수를 지정해줄 수 있다.
* 또한 test 개수, 혹은 test할 시간을 정하여 testing하거나, 예약 test도 가능하다.
* Java를 이용한 Groovy와 Python을 이용한 Jython을 제공하는데, 본인은 Jython을 이용하여 진행하였다.
* Testing 동안 실시간으로 그래프를 볼 수 있으며, 종료 후에도 Performance Test 기록이 저장된다.



### <br>Test Result
* [mysql](https://github.com/thjeong917/SW_studio2/blob/master/Performance_report/Performance%20Test%20Report.pdf)
* [arcus](https://github.com/thjeong917/SW_studio2/blob/master/Performance_report/Performance%20Test%20Report_arcus.pdf)
* [nbase-arc](https://github.com/thjeong917/SW_studio2/blob/master/Performance_report/Performance%20Test%20Report_nbase.pdf)



## **<br><br>Hubblemon**
-----------------------------------------------------------------------------
### hubblemon을 사용한 Performance Test
> https://github.com/naver/hubblemon.git

* hubblemon은 web client에 대한 system testing tool이다.
* ngrinder는 스트레스 테스트를 통한 속도를 측정하는 반면, hubblemon은 이를 통해 cpu, memory 등 System Performance를 보여준다.
* mysql 서버에 설치하면서 8100 포트에 바인딩하여, 로컬호스트에서 접속하여 그래프를 확인할 수 있게 하였다.

### <br>How To
* hubblemon을 사용하기 전에 필요한 dependency들을 우선 설치해 준다. apt-get과 pip3를 이용해서 rrdtool, psutil, kazoo, django를 설치해준다.
* 설치를 마친 후에 [링크](https://github.com/naver/hubblemon.git) 로부터 hubblemon을 클론한다.
* [installation.md](https://github.com/naver/hubblemon/blob/master/doc/install.md) 의 내용을 따라 각각의 서버에 맞게 수정할 내용들을 수정해 준다. (아커스의 경우 common의 settings.py에 zookeeper주소 추가, nbase-arc의 경우 redis를 위한 코드 추가 등)
* 멀티노드인 경우에는 클라이언트들에게도 클라이언트에 필요한 코드들을 복사해준다.
* 각각에 대해 web client와 연결 후 아래의 코드를 bash shell에서 실행 시키면 localhost의 해당 포트에서 결과를 볼 수 있다.

* arcus의 경우
```
nohup python3 run_server.py &
nohup python3 run_listener.py &
nohup python3 run_client.py &
nohup python3 manage.py runserver [YOUR_IP]:[PORT] &
```

* mysql과 nbase-arc의 경우
```
nohup python3 run_server.py &
nohup python3 run_listener.py &
nohup python3 run_client.py &
nohup python3 manage.py migrate&
nohup python3 manage.py runserver 0.0.0.0:[PORT] &
```

### <br>Execution Result (nbase-arc)
![ss7](https://user-images.githubusercontent.com/33930852/64950297-f7d32180-d8b5-11e9-8c36-d3ccc9420a93.png)

### <br>Test Result
![ss8](https://user-images.githubusercontent.com/33930852/64950324-07526a80-d8b6-11e9-8a0a-cfc89f4f53de.jpg)


## **<br><br>Contribution**
-----------------------------------------------------------------------------
### arcus-memcached
* https://github.com/naver/arcus-memcached/pull/133
* https://github.com/naver/arcus-memcached/pull/134

### arcus-java-client
* https://github.com/naver/arcus-java-client/pull/135

### nbase-arc
* https://github.com/naver/nbase-arc/pull/133

### ngrinder
* https://github.com/naver/ngrinder/pull/264
