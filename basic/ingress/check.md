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
k apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

```
### /etc/hosts 에 dns 추가
```
# kind 컨트롤 플레인 ip 확인
docker container inspect kindcluster-control-plane --format '{{ .NetworkSettings.Networks.kind.IPAddress }}'

vim /etc/hosts
{컨트롤플레인}  {도메인1 도메인2 ...} # ' '로 도메인 띄워줌
```
    
   
## url 매핑 테스트
- url-mapping 폴더의 예제 포함.
- ingress.yml 부분 예제 수정 -> apiVersion 바꾸고, 몇몇 필드명 변경 (바뀐거 주석처리해둠)
- Ingress 에 명시된 dns /etc/hosts 에 적어줌


