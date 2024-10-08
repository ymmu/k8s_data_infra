# ingress 실습 로그
- 인그레스를 이용하여 기존의 로드밸런서나 리버스 프록시를 대체할 수 있음
- 다른 컨트롤러와 달리 마스터상의 kube-controller-manager의 일부로 실행되지 않고, 다양한 인그레스 컨트롤러를 이용함. (nginx가 대표적)
- 퍼블릭 클라우드에는 처음부터 인그레스 컨트롤러가 포함되어 있음. 로컬환경에서는 설정해줘야 함  
  
## Ingress의 특징
- **url 경로/호스트 기반 라우팅**: 
    - 특정 url과 어플리케이션 매핑 -> 클라이언트의 요청을 여러 파드에 분산
    - example.com/order <-> order 서비스(파드)와 매핑 (부분경로에 매핑가능)
    - example.com/a <-> a 서비스(파드)와 매핑
    - example.com <-> Test 서비스(파드)와 매핑
- ssl/tls 인증서 관리, https 트래픽 처리
- **리버스 프록시**: 여러 서비스에 대한 단일 진입점을 제공
- **세션 어피니티 기능**
    - 세션 어피니티(Session Affinity)는 클라이언트의 요청을 항상 동일한 서버나 백엔드로 라우팅하는 기술입니다.
    - 이를 통해 세션 동안 상태 정보를 유지할 수 있으며, 주로 로드 밸런싱 환경에서 사용됩니다. 
    - 세션 어피니티는 "스티키 세션(Sticky Session)" 또는 "세션 지속성(Session Persistence)"이라고도 합니다.
  
## service 와 ingress 의 차이점
- 둘 다 포트를 노출하는 기능과 로드밸런싱을 수행함
- service=L4, ingress=L7 영역에서 통신할 떄 사용
    - Service는 주로 L4 (Transport Layer)에서 작동합니다. 이는 TCP/UDP 포트 및 IP 주소를 기반으로 네트워크 트래픽을 라우팅합니다.
    - Ingress는 주로 L7 (Application Layer)에서 작동합니다. 이는 HTTP/HTTPS 같은 애플리케이션 계층 프로토콜을 사용하여 트래픽을 라우팅합니다.
    - 네트워크에서 OSI(Open Systems Interconnection) 모델은 네트워크 통신을 계층으로 나눠 이해하기 쉽게 만든 모델입니다. OSI 모델에는 7개의 계층이 있으며, 각각의 계층은 특정한 네트워크 기능을 담당합니다.
        **[OSI 모델]**
        - Layer 1 (Physical Layer): 물리적 전송 매체, 전기 신호 등.
        - Layer 2 (Data Link Layer): MAC 주소 등을 이용한 데이터 프레임 전송.
        - Layer 3 (Network Layer): IP 주소 등을 이용한 데이터 패킷 전송.
        - Layer 4 (Transport Layer): TCP, UDP 등의 프로토콜을 이용한 세그먼트 전송.
        - Layer 5 (Session Layer): 세션 관리, 동기화.
        - Layer 6 (Presentation Layer): 데이터 인코딩, 암호화.
        - Layer 7 (Application Layer): 애플리케이션, 사용자 인터페이스.
    [[참조블로그]](https://imjeongwoo.tistory.com/130)
   - **서비스**: 여러 개로 복제된 한 종류의 파드를 로드밸런싱함  |  **인그레스**: 여러 서비스에 대해서 라우팅 역할을 담당
   - 일반적인 경우 온프렘에서는 servic의 Nodeport 타입을 사용, 퍼블릭클라우드 환경에서는 service의 loadbalancer 타입을 사용하면 대부분 서비스 운영이 가능하다고 한다..   

## 인그레스 환경 설정 (로컬)
### kind 설정 추가
- 하나의 노드에만 넣어도 클러스터의 트래픽을 처리하고 필요한 서비스로 라우팅 할 수 있음
- 여러 노드에 ingress 컨트롤러르 배포해야 하는 경우
    - **높은 트래픽부하** -> 여러 노드에서 분산 처리를 위해
    - **고가용성을 위해서** -> 노드에 장애가 발생할 경우를 대비해 다른 노드에도 추가
    - **지리적으로 분산된 환경일 때** -> 지연시간을 줄이기 위해
    - **특정 워크로드 분리**: 특정 워크로드만 특정 노드에서 실행되게 설정할 때, 이 노드에만 트래픽을 집중시킬 수 있음
```
# kind_init.yaml
# 컨트롤플레인에 추가

  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"

```
### kind 클러스터에서 ingress controller 쓰기
```
# k apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
# 위 사이트의 yaml을 다운로드했음
k apply -f ingress-nginx.yaml

```
### /etc/hosts 에 dns 추가
```
# 처음엔 컨트롤플레인 ip로 설정해서 동작했지만 클러스터를 다시 설치하는 등 이 후에는 제대로 동작하지 않음. 
# 컨트롤플레인에만 ingress nginx controller가 설치되도록 해두었으나..
# 127.0.0.1 로는 접근 가능
  
vim /etc/hosts
127.0.0.1  {도메인1 도메인2 ...} # ' '로 도메인 띄워줌
```
   
127.0.0.1에 도메인을 매핑하는 이유는 로컬 환경에서 Kind 클러스터를 실행할 때, Ingress를 통해 애플리케이션에 접근하기 위해 로컬 호스트 IP를 사용하는 것이 일반적이기 때문입니다. 로컬 개발 환경에서 `127.0.0.1` 또는 `localhost`는 로컬 머신 자체를 가리키며, Kind 클러스터의 Control Plane 노드는 Docker 컨테이너로 실행되므로 이 컨테이너는 로컬 머신에서 접근할 수 있는 IP로 포트가 매핑됩니다.

### 왜 `127.0.0.1`을 사용하는가?

1. **로컬 개발 환경**:
   - Kind 클러스터는 Docker 컨테이너 안에서 실행되며, 로컬 환경에서 클러스터와 상호작용할 때, 기본적으로 `127.0.0.1`로 포트가 매핑됩니다. 예를 들어, Ingress를 통해 웹 애플리케이션에 접근하려면 브라우저에서 `http://example.local`로 접속하는데, 이 도메인이 `127.0.0.1`로 매핑되어야 로컬 머신의 웹 브라우저가 클러스터 내 서비스에 접근할 수 있습니다.

2. **포트 포워딩**:
   - 클러스터의 Control Plane이 Docker 컨테이너 안에서 실행되기 때문에, 외부에서 접근하려면 호스트 머신의 포트와 컨테이너의 포트를 포워딩해야 합니다. `127.0.0.1`은 이 포트 포워딩이 이루어지는 기본 IP입니다. Ingress의 경우, `80`과 `443` 포트가 `127.0.0.1`에 매핑되며, 이를 통해 외부 트래픽이 컨테이너 내 서비스로 라우팅됩니다.

3. **단일 IP 사용**:
   - 로컬 환경에서 여러 Docker 컨테이너가 서로 다른 IP를 가질 수 있지만, `127.0.0.1`을 사용하면 이러한 복잡성을 피할 수 있습니다. 로컬 개발의 편의성을 위해 모든 도메인을 `127.0.0.1`에 매핑하여, 하나의 IP 주소로 여러 서비스를 테스트할 수 있습니다.

### Control Plane IP 매핑은 언제 사용하는가?

- Control Plane IP를 매핑하는 것은 로컬 개발 환경보다는 원격 클러스터나 멀티 노드 환경에서 유용합니다. 예를 들어, 클러스터가 네트워크 상에서 여러 노드로 구성되어 있고, 특정 노드의 IP를 직접 접근해야 할 때 사용합니다. 하지만 로컬 개발 환경에서는 Control Plane의 내부 IP(`10.x.x.x`와 같은 내부 네트워크 IP)를 외부에서 접근하기 어렵기 때문에, `127.0.0.1`을 사용하는 것이 더 실용적입니다.

따라서, 로컬 환경에서는 `127.0.0.1`에 도메인을 매핑하여 쉽게 클러스터 내 서비스에 접근할 수 있으며, 이는 일반적인 로컬 개발 워크플로우에서 사용됩니다.
   


   
## url 매핑 테스트
- url-mapping 폴더의 예제 포함.
- ingress.yml 부분 예제 수정 -> apiVersion 바꾸고, 몇몇 필드명 변경 (바뀐거 주석처리해둠)
- Ingress 에 명시된 dns /etc/hosts 에 적어줌
   

## ssl/tls 인증서 추가
인증기관으로 부터 인증서를 받는건 유료여서 자세 인증서로 대체
   
```
# ingress 에 어노테이션 추가
apiVersion: networking.k8s.io/v1 # 예제에서 수정
kind: Ingress
metadata:
  name: hello-ingres
  annotations:
    # -- 1. kubernetes.io/ingress.class: 'nginx'  # Warning: annotation "kubernetes.io/ingress.class" is deprecated, please use 'spec.ingressClassName' instead
    ingressClassName: 'nginx'  # 예제에서 수정
    # -- 2. 사용자가 http://abc.sample.com/apl2에 요청을 보내면, NGINX Ingress 컨트롤러는 요청 경로를 /로 재작성하고, 이를 nginx-svc로 전달합니다.
    # --    결과적으로, 백엔드 서비스 nginx-svc는 /app1이 아닌 / 경로를 처리하게 됩니다.
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/force-ssl-redirect: 'true'
```
인증서 생성 -> 시크릿 (tls 옵션) 등록
```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx-selfsigned.key -out nginx-selfsigned.crt
.+...+..+.+.....+......+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*........+...+...+....+...+......+..+....+.........+.....
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:KR
State or Province Name (full name) [Some-State]:Seoul 
Locality Name (eg, city) []:
Organization Name (eg, company) [Internet Widgits Pty Ltd]:
Organizational Unit Name (eg, section) []:

Common Name (e.g. server FQDN or YOUR name) []:abc.sample.com   ## 여기에 대상 도메인 적어줌
Email Address []:
```
시크릿에 인증서 등록
```
k create secret tls tls-certificate --key nginx-selfsigned.key --cert nginx-selfsigned.crt
secret/tls-certificate created
```
   

## 세션 어피니티 기능 사용
- 브라우저(http)는 무상태 프로토콜 -> 상태를 기록해두지 않음. 요청할 때가 커넥션이 열렸다 닫힘 (tcp/ip)
- 애플리케이션은 브라우저를 식별하기 위한 쿠키를 http 프로토콜의 헤더에 포함시켜서 전송
    -> 브라우저는 쿠키를 보관해 뒀다가 같은 url에 접근할 떄는 기억해 둔 쿠키를 http 헤더에 기재하여 전송
    -> 세션정보를 얻어 요청에 대한 처리를 수행
- 그런데 여러 대의 서버로 로드밸런싱할 때 세션기록이 없는 서버에 접근하게 되면 유저가 로그인을 했는데 다시 해야 하거나 장바구니 내역이 다 사라질 수 있음
    -> 보통.. 여러 대 서버를 사용하면..전체 서버가 공유할 수 있는 스토리지에 세션정보를 넣어놓지 않으려나??
- 클라우드 네이티브 애플리케이션 개발에서는 세션 정보를 외부 캐시에 보관하는 것을 추천 -> 파드 외부의 캐시에 보관해야 함
- (공유가 불가하다고 치면?) 유저가 접근했던 세션이 있는 서버로 항상 요청이 가야 하는데, 인그레스에 세션 어피니티 기능을 이용할 수도 있다
- 세션 어피니티 기능을 사용하면 최소한의 애플리케이션 변경으로 k8s 클러스터에 배포 가능. but 애플리케이션 가동 중에 롤아웃이 불가능..
         
- 인그레스는..L7에서 동작이라 쿠키를 기반으로 세션 정보를 가지고 있는 파드에 전송 이겠지
- 서비스의 로드밸런싱 기능은 L3에서 동작하기 때문에 ip로 전송할 파드를 고정 가능

```
apiVersion: networking.k8s.io/v1 # 예제에서 수정
kind: Ingress
metadata:
  name: hello-ingres
  annotations:
    # kubernetes.io/ingress.class: 'nginx'
    ingressClassName: 'nginx'  # 예제에서 수정
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/affinity: 'cookie'   ## <-- 이부분 추가
```
   
### 테스트용 파일
- nginx 에 연결된 애플리케이션(session-test) 준비 (이미지 생성, 디플로이/서비스 yaml 파일 작성)
- ingress-session.yaml 파일 준비
- 모두 k apply 해줌   
   
```
# 브라우저로 접속해도 되고,
# curl 로 접속해도 됨. 
# 단 curl 로 접속시 리다이렉트 설정 따르고, ssl 인증서 검증 비활성화 해야 함

# 첫번째 curl 시도시 -c 사용: HTTP 응답에서 쿠키 데이터를 파일에 저장
# -L: 리다이렉트된 URL을 따라감
# -k: SSL 인증서 검증을 무시 (--insecure와 동일)
curl -Lkc cookie.dat https://abc.sample.com  

# 그 다음엔 -b : HTTP 요청에 사용할 쿠키 데이터를 지정
curl -Lkb cookie.dat https://abc.sample.com  

```
  
  
### curl 참조..

| 옵션          | 설명                                                                 |
|---------------|----------------------------------------------------------------------|
| `-o`          | 출력 파일 지정 (단일 파일)                                          |
| `-O`          | URL에서 파일 이름을 유지하면서 파일을 다운로드                      |
| `-L`          | 리다이렉트된 URL을 따라감                                           |
| `-k`          | SSL 인증서 검증을 무시 (`--insecure`와 동일)                        |
| `-I`          | HTTP 헤더 정보만 요청 (`HEAD` 요청)                                 |
| `-X`          | 사용자가 지정한 HTTP 메서드로 요청 (`GET`, `POST`, `PUT` 등)        |
| `-d`          | POST 요청 시 전송할 데이터를 지정                                   |
| `-F`          | 폼 데이터 전송 (파일 업로드 등)                                     |
| `-H`          | 요청에 추가할 HTTP 헤더를 지정                                      |
| `-u`          | HTTP 인증을 위해 사용자 이름과 비밀번호를 지정                      |
| `-b`          | HTTP 요청에 사용할 쿠키 데이터를 지정                               |
| `-c`          | HTTP 응답에서 쿠키 데이터를 파일에 저장                             |
| `--compressed`| 압축된 응답을 자동으로 디코딩                                       |
| `-s`          | 진행률이나 오류 메시지를 출력하지 않음 (`--silent`와 동일)          |
| `-S`          | `-s` 옵션과 함께 사용되어야 하며, 오류가 발생하면 오류 메시지를 출력 |
| `-v`          | 요청과 응답의 디버그 정보를 출력 (`--verbose`와 동일)               |
| `--http2`     | HTTP/2 프로토콜을 사용                                              |
| `--http3`     | HTTP/3 프로토콜을 사용                                              |
| `-x`          | 프록시 서버를 지정하여 요청을 보냄 (`--proxy`와 동일)               |
| `--max-time`  | 최대 요청 시간을 초 단위로 지정                                     |
| `--cacert`    | 특정 CA 인증서를 사용하여 SSL 인증서를 검증                         |
| `-e`          | 요청에 포함될 리퍼러 URL을 지정 (`--referer`와 동일)                |
| `--cert`      | 클라이언트 인증서 파일을 지정 (SSL/TLS)                             |
| `--key`       | 클라이언트 인증서의 비밀 키 파일을 지정                             |
| `-A`          | 사용자 에이전트 문자열을 지정 (`--user-agent`와 동일)               |



## kube-keepalive-vip(virtual ip) 에 의한 virtual ip 획득과 고가용성(HA) 구성
- keepalive 가 하나의 노드에 virtual ip 를 할당. 이 노드가 요청을 받아서 ingress 컨트롤러에 전달
- **멀티 노드 클러스터에서 한 노드가 죽으면 다른 노드가 대체할 수 있도록 클러스터 앞에 로드밸런스를 두는 것이 더 낫지 않나?** 책에서는 이게 더 복잡하다는 뉘앙스로 적혀있는데.. 좀 이해가 안 되는 게 Metallb 등을 통해서 로드밸런서를 설치하면 엔드포인트가 생겨서 이쪽으로 접근하는게 더 쉽지 않나 싶고..
- 퍼블릭 클라우드에는 인그레스와 vip를 연결하는 기능이 있어서 그대로 사용하면 됨
    
- **service와 ingress의 차이**
    - **Service**는 클러스터 내부에서 Pod의 네트워크 트래픽을 관리하는 기본적인 네트워크 오브젝트
    - **Ingress**는 Service 위에서 동작하며, 클러스터 외부에서 들어오는 HTTP/HTTPS 트래픽을 클러스터 내부의 Service로 라우팅하는 고급 기능을 제공
- kind 클러스터를 사용해서 책 예제를 그대로 사용 못 하고 여러가지 설정을 해줘야 함
    - 요청 -> (keepalive가 노드에 ip 부여) -> nginx-ingress-svc -> ingress-controller -> service api - pod
    - nginx-ingress-svc에 metallb로 externalIP를 부여하는데 부여한 ip로 curl을 날렸을 때 응답실패가 나서 문제..
    - 그래서 간단한 서비스를 deploy/service로 띄우고, 해당 서비스에 externalip를 만들어서 curl을 날려봤는데도 잘 안 됨..왜일까..ㅠ
    - 이틀동안 삽질한듯..
    
