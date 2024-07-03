# service 실습 로그
  
## 서비스의 종류
- 파드는 일시적인 존재라 언제든지 할당된 IP 주소가 변경될 수 있음
- 늘 변경되는 파드의 IP 주소를 알기 어렵기 때문에 쿠버네티스의 서비스 오브젝트가 존재



| 서비스 타입 | 접근 가능 범위 |
|----------|----------|
|   ClusterIP  |   default값. 클러스터 내부의 파드에서 서비스의 이름으로 접근 가능  |
|   NodePort  |   clusterIP의 접근 범위 뿐만 아니라 K8s클러스터 외부에서도 IP 주소와 포트번호로 접근 가능  |
|   LoadBalancer  |   NodePort의 접근 범위뿐만 아니라 k8s 클러스터 외부에서도 노드의 IP주소와 포트번호로 접근 가능  |
|   ExternalName  |   k8s 클러스터 내의 파드에서 외부 ip 주소에 서비스의 이름으로 접근 가능  |

---   

   
### ClusterIP

**클러스터 내부에서** 
-  서비스는 서비스명과 대표 IP주소를 DNS에 등록해둔다.  
-  (클라이언트 역할의) 파드가 서비스에 연결된 파드들에게 (TCP/IP)요청을 보낸다.  
-  이때 클러스터 내부 DNS에 요청하여 [서비스 이름] -  [IP]로 변환한다.  
-  대표 IP를 통해 요청을 받은 서비스는 파드에 분배한다.  
  

`clusterIP:None` 으로 지정해두면 헤드리스 설정으로 서비스가 동작.  
-  헤드리스라는 말이 내용상 '앞단에서 요청을 받는 대표가 없다.' 라고 생각하면 될 것 같다.   
-  그래서 앞서처럼 서비스가 요청을 받아서 파드에 분산하는 작업을 하지 않고, 부하분산도 이루어지지 않는다.  
-  그대신 파드들의 IP 주소를 내부 DNS에 등록하여 파드IP 주소 변경에 대응하여 최신 상태를 유지한다.   
-  위의 말은, 파드가 새로 띄워지면 ip가 변경될텐데 새 ip로 DNS에 갱신해둔다.로 이해했음.  
-  이 내용은 "스테이트풀셋" 이라는 기능과 연관이 있나보다.  
   
   
---

### NodePort

**ClusterIP 기능 + 노드의 IP 주소에 공개포트가 열린다.**  
-  클러스터 외부에서 내부의 파드에 요청을 보낼 수 있게 됨.  
-  근데..내가 보기엔 클러스터에서 외부요청을 받을 수 있는 상태일 때, 노드로 요청을 보낼 수 있게 되는 것 같음..   
-  이건 내가 kind로 클러스터 올리고 삽질하면서 알게 된 것. KIND 클러스터를 생성할 때 외부 접근이 가능하도록 설정하는 부분이 있다. 이게 안 되어 있으면 뭔 짓을 해도 노드에 바로 접근이 안 된다.   
-  (디플로이먼트에서 MYSQL NODEPORT로 서비스 설정 해둔 다음에, 벤치마크에서 포트 접근하려 하는데...안되었음.)  
   
-  어쨋든간에, 책의 그림에서는 클러스터 외부로부터의 tcp/ip 요청이 노드로 바로 요청되서 처리되는 걸로 묘사되어 있음  
-  요청은 노드 안의 "KUBE-PROXY" 를 거쳐서 "**모든 노드의 POD**"에 부하분산되어 전송됨.   
-  노드1에서 받았다고 노드1 안의 POD에만 전달되는게 아님을 말하고 싶었음.  
   
-  물론 노드1에서 받은 요청을 노드1 안의 pod에서 처리하게 설정도 가능하다고 함.  
-  근데 특정노드의 Pod에서만 처리하게 설정해두면, 단점이 이 노드가 죽으면 요청 처리를 못 하게 된다.  
-  네임스페이스로 클러스터를 분할하여 운용할 떄 이런 문제가 발생할 수 있다고 함.  
-  그렇다면 네임스페이스로 클러스터의 특정 노드만 선택해서 사용할 수 있다는 건가..  
   
-  무튼, 이 노트포트는 편리하긴 하지만 정식 서비스에는 사용하긴 거시기하다고 함.  
   
   
---

### LoadBalancer

**ClusterIP 기능 + NodePort 기능 모두 포함**  
로드밸런서와 연동하여 파드의 애플리케이션을 외부에 공개  
-  외부에서 tcp/ip 요청이 들어오면 로드밸런서의 공인IP로 연결되어 있는 팟에 부하분산됨  
-  퍼블릭 클라우드에서는 각 업체가 제공하는 로드밸러서가 연동됨  
   
  
---

### ExternalName

**팟에서 k8s 외부 엔드포인트에 접속하기 위한 기능**   
-  예를 들어, 팟에서 퍼블릭클라우드의 db라던지, 인공지능 api 서비스에 접근할 떄 라던지..  
-  서비스의 이름와 외부 dns이름의 매핑을 dns에 설정한다.  
-  이 정보를 가지고 팟에서 서비스의 이름으로 외부 네트워크의 엔드포인트에 접근 가능하게 됨  
-  포트번호는 지정을 못 한다고 한다.  
-  외부 DNS 명을 등록시에 IP 주소로는 설정 불가능 하다고 함. 무조건 DNS를 생성해야 하는구나...  
-  서비스의 메니페스트에 IP 주소를 설정하려면 헤드리스 서비스를 이용하라고 함.  
   

---

### 서비스와 파드 연결

보통 디플로이로 파드를 생성하고, 파드에 요청을 보낼 수 있게 서비스를 연결하는데, 서비스가 디플로이의 파드를 인지하기 위해 `레이블`을 살펴본다.  
   
-  디플로이의 **metadata.label.app: `web`** 으로 되어 있을 때  
-  서비스에서 이 디플로이의 팟을 보고 싶으면 **spec.selector.app: `web`** 으로 설정해두면 된다.  

   

---
  
## ClusterIP 테스트
  
**파일**
- deploy.yml
- service_ci.yml
  
-  nginx 3개 레플리카 디플로이로 띄우고, 서비스 타입을 clusterIP로 두고 테스트  
-  `sessionAffinity` 설정으로 특정 파드에만 요청 전달하게 설정  

```bash
> k apply -f deploy.yml     
deployment.apps/web-deploy created

> k apply -f service_ci.yml  
service/web-service created

> k get all #진작에 가르쳐주지..
k get all                                                                             ✔  kind-kindcluster ○  19:24:50 
NAME                             READY   STATUS    RESTARTS   AGE
pod/web-deploy-ccbd58689-5qf96   1/1     Running   0          49s
pod/web-deploy-ccbd58689-95d68   1/1     Running   0          49s
pod/web-deploy-ccbd58689-mdfm8   1/1     Running   0          49s

NAME                  TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
service/kubernetes    ClusterIP   10.96.0.1      <none>        443/TCP   48m
service/web-service   ClusterIP   10.96.117.66   <none>        80/TCP    41s

NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web-deploy   3/3     3            3           49s

NAME                                   DESIRED   CURRENT   READY   AGE
replicaset.apps/web-deploy-ccbd58689   3         3         3       49s

```
  

busybox를 띄운 후에 Pod에 접근 확인.  
-  오..서비스 이름(web-service)로도 nginx 접근이 가능하네..  
```bash
k run -it busybox --restart=Never --rm --image=busybox sh                             ✔  kind-kindcluster ○  19:25:04 
If you don't see a command prompt, try pressing enter.
/ # 
/ # 
/ # wget -q -O - http://web-service
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
html { color-scheme: light dark; }
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
/ # env | grep WEB_SERVICE
WEB_SERVICE_SERVICE_PORT=80
WEB_SERVICE_PORT=tcp://10.96.117.66:80
WEB_SERVICE_PORT_80_TCP_ADDR=10.96.117.66
WEB_SERVICE_PORT_80_TCP_PORT=80
WEB_SERVICE_PORT_80_TCP_PROTO=tcp
WEB_SERVICE_PORT_80_TCP=tcp://10.96.117.66:80
WEB_SERVICE_SERVICE_HOST=10.96.117.66
/ # ^C

/ # 
```
  
서비스 접근시 pod에 분산접근하는 것 확인  
-  pod 의 nginx index.html 에 hostname을 출력하게 변경해줌  
```bash
# NR>1 {print $1}: 레코드 2번째 줄부터 첫번째 컬럼값을 출력해라
for pod in $(k get pods | awk 'NR>1 {print $1}' | grep web-deploy);
do k exec $pod -- /bin/sh -c "hostname>/usr/share/nginx/html/index.html";
done
```
awk커멘드 뭐찍는지 잠깐 테스트해본거..  
[[awk커멘드 참조페이지]](https://recipes4dev.tistory.com/171)
```bash
> k get pods  
NAME                         READY   STATUS    RESTARTS   AGE
web-deploy-ccbd58689-5qf96   1/1     Running   0          9m22s
web-deploy-ccbd58689-95d68   1/1     Running   0          9m22s
web-deploy-ccbd58689-mdfm8   1/1     Running   0          9m22s

> k get pods | awk 'NR>1 {print $1}'
web-deploy-ccbd58689-5qf96
web-deploy-ccbd58689-95d68
web-deploy-ccbd58689-mdfm8
```
   
busybox로 연결해보면  
```bash
/ # while true; do wget -q -O - http://web-service; sleep 3; done
web-deploy-ccbd58689-5qf96
web-deploy-ccbd58689-5qf96
web-deploy-ccbd58689-mdfm8
web-deploy-ccbd58689-95d68
web-deploy-ccbd58689-5qf96
web-deploy-ccbd58689-mdfm8
web-deploy-ccbd58689-mdfm8
web-deploy-ccbd58689-95d68
^C
/ #
```
  

sessionAffinity: ClientIP 로 뒀을 때 하나의 팟만 바라보는 것 확인  
-  먼저 설정 적용하고 서비스 상태 확인  
```bash
k describe service web-service                                                        ✔  kind-kindcluster ○  20:01:11 
Name:              web-service
Namespace:         default
Labels:            <none>
Annotations:       <none>
Selector:          app=web
Type:              ClusterIP
IP Family Policy:  SingleStack
IP Families:       IPv4
IP:                10.96.239.77
IPs:               10.96.239.77
Port:              <unset>  80/TCP
TargetPort:        80/TCP
Endpoints:         10.244.2.5:80,10.244.3.5:80,10.244.4.5:80
Session Affinity:  ClientIP
Events:            <none>
```
  
busybox로 확인  
```bash
> k run -it busybox --restart=Never --rm --image=busybox sh   
If you don't see a command prompt, try pressing enter.
/ # 
/ # 
/ # while true; do wget -q -O - http://web-service; sleep 1; done;
web-deploy-ccbd58689-5qf96
web-deploy-ccbd58689-5qf96
web-deploy-ccbd58689-5qf96
web-deploy-ccbd58689-5qf96
web-deploy-ccbd58689-5qf96
^C
/ #
```
  

---

## NodePort 와 LoadBalancer 테스트
저번 디플로이 테스트시 mysql 로 외부포트 접근되는지 확인함.  
**`deployment/check.md`** 문서에 정리함.  
  

---
## ExternalName 테스트
  
**dns 테스트**  
야후재팬은 잘 터지는데 네이버는 막아놨다 함...  
```bash
> k run -it busybox --restart=Never --rm --image=busybox sh 
If you don't see a command prompt, try pressing enter.
/ # 
/ # 
/ # ping www.yahoo.co.jp
PING www.yahoo.co.jp (182.22.31.252): 56 data bytes
64 bytes from 182.22.31.252: seq=0 ttl=253 time=43.215 ms
64 bytes from 182.22.31.252: seq=1 ttl=253 time=44.965 ms
64 bytes from 182.22.31.252: seq=2 ttl=253 time=44.603 ms
64 bytes from 182.22.31.252: seq=3 ttl=253 time=45.598 ms
^C
--- www.yahoo.co.jp ping statistics ---
4 packets transmitted, 4 packets received, 0% packet loss
round-trip min/avg/max = 43.215/44.595/45.598 ms
/ #


# 도메인 NAVER로 바꾸고 서비스 다시 실행
# 네이버는 ping 조회를 막아놨다 한다..
> k run -it busybox --restart=Never --rm --image=busybox sh
If you don't see a command prompt, try pressing enter.
/ # 
/ # 
/ # ping www.naver.com
PING www.naver.com (223.130.200.219): 56 data bytes
^C
--- www.naver.com ping statistics ---
28 packets transmitted, 0 packets received, 100% packet loss
/ # 
``` 
  

**ip로 접근하게 할 때는 엔드포인트 지정해줘야 함**
-  `svc-headless.yml` 파일  
-  원래 설정된거로는 안 터짐 ㅋㅋ ip 를 뭘로 넣으면 터지려나?   
있는 파트 ip를 넣어볼까..어쨋든 ip로 엔드포인트 잡고 접속이 되나 보는거니까..  
  
```bash
kind: Endpoints
apiVersion: v1
metadata:
  name: server1
subsets:
  - addresses:
    - ip: 10.244.4.5
---      
apiVersion: v1
kind: Service
metadata:
  name: server1
spec:
  clusterIP: None
```
  
실행시켜봄..잘 됨  
   
```bash
> k run -it busybox --restart=Never --rm --image=busybox sh
If you don't see a command prompt, try pressing enter.
/ # 
/ # 
/ # ping server1
PING server1 (10.244.4.5): 56 data bytes
64 bytes from 10.244.4.5: seq=0 ttl=62 time=0.113 ms
64 bytes from 10.244.4.5: seq=1 ttl=62 time=0.114 ms
64 bytes from 10.244.4.5: seq=2 ttl=62 time=0.110 ms
64 bytes from 10.244.4.5: seq=3 ttl=62 time=0.129 ms
64 bytes from 10.244.4.5: seq=4 ttl=62 time=0.113 ms
^C
--- server1 ping statistics ---
5 packets transmitted, 5 packets received, 0% packet loss
round-trip min/avg/max = 0.110/0.115/0.129 ms
/ # 
```

