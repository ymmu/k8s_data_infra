# kind(Kubernetes In Docker) 선택 이유

- kind로 로컬환경에서 멀티 노드 클러스터를 구축 가능
- 운영 환경에서는 대부분 멀티 노드를 사용하기 때문에 로컬에서도 유사한 환경을 만들어 테스트하기 위해 kind 선택




| 항목 | 미니큐브 | 도커데스크탑 | kind |
|----------|----------|----------|----------|
|   버전선택   |   O   |   X   |   O   |
|----------|----------|----------|----------|
|   멀티 클러스터   |   O   |   X   |   O   |
|----------|----------|----------|----------|
|   멀티 노드   |   X   |   X   |   O   |
|----------|----------|----------|----------|
|   기능성   |   O   |   ^   |   O   |
|----------|----------|----------|----------|
|   단순성   |   O   |   O   |   O   |
|----------|----------|----------|----------|




# kind 기본 사용법

```bash
kind version  # 버전 확인 
```


## 클러스터 생성

0. 도커 데스크톱의 도커환경이 기동되고 있어야 한다.
1. yaml 파일에 클러스터 설정을 정의한다. (./kind.yaml 파일 참조)
2. 클러스터 실행 커멘드
```bash
> kind create cluster --config kind.yaml --name kindcluster
```

3. 클러스터 확인
 context 이름은 `kind-{클러스터이름}` 으로 생긴다.
```bash
> kubectl cluster-info --context kind-kindcluster

Creating cluster "kindcluster" ...
 ✓ Ensuring node image (kindest/node:v1.25.16) 🖼
 ✓ Preparing nodes 📦 📦 📦 📦 📦 📦  
 ✓ Configuring the external load balancer ⚖️ 
 ✓ Writing configuration 📜 
 ✓ Starting control-plane 🕹️ 
 ✓ Installing CNI 🔌 
 ✓ Installing StorageClass 💾 
 ✓ Joining more control-plane nodes 🎮 
 ✓ Joining worker nodes 🚜 
Set kubectl context to "kind-kindcluster"
You can now use your cluster with:

kubectl cluster-info --context kind-kindcluster

```

## 컨텍스트 전환
```bash
> kubdctl config use-context kind-kindcluster

Switched to context "kind-kindcluster".
``` 

## 노드 확인
- 도커 명령어로도 해당 노드의 컨테이너를 확인 가능하다.
```bash
kubdctl get nodes
``` 

## 클러스터 삭제
```bash
kubdctl delete cluster -- name kindcluster
``` 

## config 확인
- .kube/config
```bash
kubdctl config view
``` 

# 트러블슈팅

## kind 클러스터 삭제 -> 재생성시 port aleady in use 문제
- 이전에 해둔 바인딩이 남아있어서 -> 관련 pid 찾아 삭제하고, kubelet 재시작
   
```
# ex.
docker: Error response from daemon: Ports are not available:
 exposing port TCP 0.0.0.0:443 -> 0.0.0.0:0: 
 listen tcp 0.0.0.0:443: bind: address already in use.
```
  
포트 사용 프로세스 검색
```
# ex
sudo lsof -i :6444

#COMMAND       PID USER   FD   TYPE    DEVICE SIZE/OFF NODE NAME
#docker-pr 2500852 root    4u  IPv4 303948257      0t0  TCP localhost:sge-qmaster (LISTEN)

sudo kill 2500852
```
  
kublete 재시작
```
sudo service kubelet restart 
```
