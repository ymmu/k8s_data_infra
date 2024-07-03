# deployment 실습시 체크사항

## deployment의 역할
- 파드의 개수를 관리하는 것. 시스템의 처리 능력, 서비스를 중단하지 않는 가용성, 비용 측면에서 매우 중요
- k8s 클러스터에서는 파드가 서버의 역할을 담당 -> 처리능력을 높이려면 파드 개수를 조절하면 됨
- 파드를 늘릴 수록 cpu와 메모리가 많이 사용되니 주의 필요
- 장애 등으로 파드의 개수가 줄어들면 새롭게 파드를 만들어 기동함
- 애플리케이션의 버전을 업그레이드할 때 새로운 버전의 파드로 조금씩 바꾸는 기능도 제공
- 로드밸런서 기능은 디플로이먼트에 포함되어있지 않음. 이 기능은 쿠버네티스의 "**서비스**"가 제공

**나:** 
- 결국 확장 가능한 서버를 띄우려면 **디플로이먼트 & 서비스** 콤보로 올려야겠네..
- 노드가 죽으면 해당 노드에 있던 팟들을 다른 노드로 자동으로 옮김. 근데 5분이나 걸려..
- db를 노드에 올리면 큰일나겠다..아니면 데이터가 날라가도 무방할 때만..


**디플로이먼트에 의해 생성된 파드의 특징:**
- 요청을 계속 받아들이며 종료하지 않음
- 수평 스케일
- 비정상 종료 시 재기동


```
+------------------+
|   Deployment     |
|  +-------------+ |
|  | ReplicaSet  | |
|  |  +-------+  | |
|  |  |  Pod  |  | |
|  |  +-------+  | |
|  |  +-------+  | |
|  |  |  Pod  |  | |
|  |  +-------+  | |
|  |  +-------+  | |
|  |  |  Pod  |  | |
|  |  +-------+  | |
|  +-------------+ |
+------------------+

```

## YAML 특징
```
spec:
  replicas: 3  <-- 기동할 파드 갯수. 언제나 이 값만큼의 파드를 유지하려고 함
  selector:
    matchLabels:
      app: web  <-- 이 레이블이 붙어있는 파드를 관리하겠다. 파드에 이 레이블이 붙어있어야 함
  
  tamplate:  <-- 파드 템플릿
    metadata:
      labels:
        app: web  <-- 파드의 레이블.
    spec:
      containers:
      - name: nginx
        image: nginx:latest  
    ...
```

## 레플리카수 조정하기 (SCALE)
yaml에서 replica수를 수정하는 방법도 있지만, 커멘드를 통해서도 수정 가능.
```
k scale --replicas={새로운 레플리카 갯수} {deployment이름}
```
파드의 개수를 늘리는 중에 k8s 클러스터의 자원(cpu & memory)이 부족해지면 노드를 추가하여 자원이 생길 때까지 파드 생성이 보류된다. 
파드 개수 늘리기 전에 가용 자원 확인 필요 !

```bash
> k apply -f deployment1.yml 
deployment.apps/web-deploy created

> k scale --replicas=5 deployment.apps/web-deploy  
deployment.apps/web-deploy scaled

> k get deploy,po
NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web-deploy   5/5     5            5           13s

NAME                             READY   STATUS    RESTARTS   AGE
pod/web-deploy-8d6dc84fb-d97jb   1/1     Running   0          7s
pod/web-deploy-8d6dc84fb-ddqwm   1/1     Running   0          7s
pod/web-deploy-8d6dc84fb-jfhg8   1/1     Running   0          13s
pod/web-deploy-8d6dc84fb-n9mjj   1/1     Running   0          13s
pod/web-deploy-8d6dc84fb-vzb2r   1/1     Running   0          13s
```

## 롤아웃 기능
롤아웃이란 "**컨테이너의 업데이트**"를 의미함
**나:** 롤아웃=이미지의 업데이트라고 볼 수 있는 것 같다..책에 의하면?

describe로 롤아웃설정을 보면 다음처럼 적혀있는데,
```
RollingUpdateStrategy:  25% max unavailable, 25% max surge
```
이 말의 의미는 새로운 이미지의 파드로 업데이트하는 와중에
레플리카수 N의 최소 (N*0.75)개 ~ (N*1.25)개의 파드가 떠 있도록 하면서 롤아웃이 점진적으로 진행된다는 말. 


```bash
k describe deployment web-deploy                                            1 х  test Py  kind-kindcluster ○  19:01:45 
Name:                   web-deploy
Namespace:              default
CreationTimestamp:      Sat, 29 Jun 2024 19:00:45 +0900
Labels:                 <none>
Annotations:            deployment.kubernetes.io/revision: 1
Selector:               app=web
Replicas:               5 desired | 5 updated | 5 total | 5 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Pod Template:
  Labels:  app=web
  Containers:
   nginx:
    Image:      nginx:1.14.2
    Port:       80/TCP
    Host Port:  0/TCP
    Limits:
      cpu:     500m
      memory:  512Mi
    Requests:
      cpu:         100m
      memory:      256Mi
    Environment:   <none>
    Mounts:        <none>
  Volumes:         <none>
  Node-Selectors:  <none>
  Tolerations:     <none>
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Progressing    True    NewReplicaSetAvailable
  Available      True    MinimumReplicasAvailable
OldReplicaSets:  <none>
NewReplicaSet:   web-deploy-8d6dc84fb (5/5 replicas created)
Events:
  Type    Reason             Age   From                   Message
  ----    ------             ----  ----                   -------
  Normal  ScalingReplicaSet  15m   deployment-controller  Scaled up replica set web-deploy-8d6dc84fb to 3
  Normal  ScalingReplicaSet  15m   deployment-controller  Scaled up replica set web-deploy-8d6dc84fb to 5 from 3
```

## 롤백 기능
- 롤아웃 전에 사용하던 예전 컨테이너로 되돌리는 것을 의미
- 롤백을 할 때도 롤아웃과 마찬가지로 사용자의 요청을 처리하면서 파드를 점진적으로 교체
- 기능에 문제가 발견되었을 때 출시 이전으로 되돌릴 수 있으나, 데이터베이스등에 적대된 데이터까지 롤백되는 것은 아님. (그렇네 맞는 말인데 아무 생각없으면 놓치겠네..)
- **나:** 근데 롤백이 된다는건 쿠버네티스도 지난 상태를 기록하고 있다는거네?

```bash
k rollout undo deployment web-deploy
> deployment.apps/web-deploy rolled back
```

## 파드 IP 주소 변경되는 시점
- 파드가 지워지고 새로운 파드가 생성될 때 새로운 IP 가 할당된다.
- 파드 안의 컨테이너가 재시작될 때는 IP 변경 없음.
- pod 조회시 RESTARTS 값이 컨테이너가 재시작한 숫자임
```bash
> k get deploy,po
# pod 조회시 RESTARTS 값이 컨테이너가 재시작한 숫자임

NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web-deploy   3/3     3            3           3h41m

NAME                             READY   STATUS    RESTARTS   AGE
pod/web-deploy-8d6dc84fb-jkxtz   1/1     Running   0          8m8s
pod/web-deploy-8d6dc84fb-lf2sx   1/1     Running   0          8m7s
pod/web-deploy-8d6dc84fb-zk8r5   1/1     Running   0          8m6s
```

## 자동복구
- 단독 Pod은 pod 안의 컨테이너에 대해서 자동복구 시도하고
- 디플로이먼트는 pod 수준에서 자동복구를 시도한다
- 노드가 정지되면 -> 그 노드에 포함한 팟이 unknown으로 변경됨 -> 정상인 노드에 새로운 Pod 생성 -> 정지된 노드를 다시 실행하면 -> unknown 팟이 (상태가 불분명했는데 상태확인이 되면서) 삭제됨

### 자동복구 테스트
노드에 문제가 생기면 **5분 이후**에 다른 정상 노드에 파드가 생긴다.

1. 노드별 파드 상태 확인. web-deploy 디플로이먼트 하나만 올려둔 상태
```bash
> k get po -o wide
NAME                         READY   STATUS    RESTARTS   AGE   IP            NODE                  NOMINATED NODE   READINESS GATES
web-deploy-8d6dc84fb-jkxtz   1/1     Running   0          12h   10.244.3.13   kindcluster-worker3   <none>           <none>
web-deploy-8d6dc84fb-lf2sx   1/1     Running   0          12h   10.244.4.13   kindcluster-worker2   <none>           <none>
web-deploy-8d6dc84fb-zk8r5   1/1     Running   0          12h   10.244.5.15   kindcluster-worker    <none>           <none>
```

2. Kind 노드 worker를 중지시킴. docker 커멘드를 이용
```bash
# kind 클러스터 노드 확인
> docker ps --filter "name=kind"
CONTAINER ID   IMAGE                                COMMAND                  CREATED      STATUS      PORTS                       NAMES
5de517719e0b   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days                               kindcluster-worker
b2ffa8ecafe1   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days                               kindcluster-worker2
38b8367ef586   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days   127.0.0.1:34341->6443/tcp   kindcluster-control-plane3
eb23e2dce2f7   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days   127.0.0.1:38225->6443/tcp   kindcluster-control-plane2
fa01e66ab40f   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days   127.0.0.1:45505->6443/tcp   kindcluster-control-plane
fe02fe4f6dd1   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days                               kindcluster-worker3
0e7efcc9e6c9   kindest/haproxy:v20230606-42a2262b   "haproxy -W -db -f /…"   2 days ago   Up 2 days   127.0.0.1:43287->6443/tcp   kindcluster-external-load-balancer


# 중지시킴
> docker stop kindcluster-worker
kindcluster-worker      ✔  test Py  11:14:57 


# 상태확인
docker ps --filter "name=kind"            ✔  test Py  11:16:11 
CONTAINER ID   IMAGE                                COMMAND                  CREATED      STATUS      PORTS                       NAMES
b2ffa8ecafe1   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days                               kindcluster-worker2
38b8367ef586   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days   127.0.0.1:34341->6443/tcp   kindcluster-control-plane3
eb23e2dce2f7   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days   127.0.0.1:38225->6443/tcp   kindcluster-control-plane2
fa01e66ab40f   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days   127.0.0.1:45505->6443/tcp   kindcluster-control-plane
fe02fe4f6dd1   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days                               kindcluster-worker3
0e7efcc9e6c9   kindest/haproxy:v20230606-42a2262b   "haproxy -W -db -f /…"   2 days ago   Up 2 days   127.0.0.1:43287->6443/tcp   kindcluster-external-load-balancer
```

3. 시간별 pod 상태 확인. (pod 상태 변경이 5분 이상 걸린다.)
```bash
>k get po -o wide             ✔  test Py  kind-kindcluster ○  11:14:44 
NAME                         READY   STATUS    RESTARTS   AGE   IP            NODE                  NOMINATED NODE   READINESS GATES
web-deploy-8d6dc84fb-jkxtz   1/1     Running   0          12h   10.244.3.13   kindcluster-worker3   <none>           <none>
web-deploy-8d6dc84fb-lf2sx   1/1     Running   0          12h   10.244.4.13   kindcluster-worker2   <none>           <none>
web-deploy-8d6dc84fb-zk8r5   1/1     Running   0          12h   10.244.5.15   kindcluster-worker    <none>           <none>

...

# 5분 지남
k get po -o wide              ✔  test Py  kind-kindcluster ○  11:20:12 
NAME                         READY   STATUS    RESTARTS   AGE   IP            NODE                  NOMINATED NODE   READINESS GATES
web-deploy-8d6dc84fb-jkxtz   1/1     Running   0          12h   10.244.3.13   kindcluster-worker3   <none>           <none>
web-deploy-8d6dc84fb-lf2sx   1/1     Running   0          12h   10.244.4.13   kindcluster-worker2   <none>           <none>
web-deploy-8d6dc84fb-zk8r5   1/1     Running   0          12h   10.244.5.15   kindcluster-worker    <none>           <none>


# 6분 지난 후
k get po -o wide              ✔  test Py  kind-kindcluster ○  11:21:33 
NAME                         READY   STATUS              RESTARTS   AGE   IP            NODE                  NOMINATED NODE   READINESS GATES
web-deploy-8d6dc84fb-jkxtz   1/1     Running             0          12h   10.244.3.13   kindcluster-worker3   <none>           <none>
web-deploy-8d6dc84fb-k5jtm   0/1     ContainerCreating   0          0s    <none>        kindcluster-worker2   <none>           <none>
web-deploy-8d6dc84fb-lf2sx   1/1     Running             0          12h   10.244.4.13   kindcluster-worker2   <none>           <none>
web-deploy-8d6dc84fb-zk8r5   1/1     Terminating         0          12h   10.244.5.15   kindcluster-worker    <none>           <none>


# 터미네이팅 상태로 바뀌지만 이후로 계속 검색해보면 사라지진 않음

k get po -o wide              ✔  test Py  kind-kindcluster ○  11:21:35 
NAME                         READY   STATUS        RESTARTS   AGE   IP            NODE                  NOMINATED NODE   READINESS GATES
web-deploy-8d6dc84fb-jkxtz   1/1     Running       0          12h   10.244.3.13   kindcluster-worker3   <none>           <none>
web-deploy-8d6dc84fb-k5jtm   1/1     Running       0          21s   10.244.4.14   kindcluster-worker2   <none>           <none>
web-deploy-8d6dc84fb-lf2sx   1/1     Running       0          12h   10.244.4.13   kindcluster-worker2   <none>           <none>
web-deploy-8d6dc84fb-zk8r5   1/1     Terminating   0          12h   10.244.5.15   kindcluster-worker    <none>           <none>

```

4. 노드 다시 재시작

```bash
docker start kindcluster-worker                         ✔  test Py  11:23:47 
kindcluster-worker


# 터미네이팅 상태던 노드가 사라짐
k get po -o wide                                        ✔  test Py  kind-kindcluster ○  11:23:55 
NAME                         READY   STATUS    RESTARTS   AGE     IP            NODE                  NOMINATED NODE   READINESS GATES
web-deploy-8d6dc84fb-jkxtz   1/1     Running   0          12h     10.244.3.13   kindcluster-worker3   <none>           <none>
web-deploy-8d6dc84fb-k5jtm   1/1     Running   0          2m24s   10.244.4.14   kindcluster-worker2   <none>           <none>
web-deploy-8d6dc84fb-lf2sx   1/1     Running   0          12h     10.244.4.13   kindcluster-worker2   <none>           <none>


# 노드 상태 확인
docker ps --filter "name=kind"                          ✔  test Py  11:23:59 
CONTAINER ID   IMAGE                                COMMAND                  CREATED      STATUS          PORTS                       NAMES
5de517719e0b   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 22 seconds                               kindcluster-worker
b2ffa8ecafe1   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days                                   kindcluster-worker2
38b8367ef586   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days       127.0.0.1:34341->6443/tcp   kindcluster-control-plane3
eb23e2dce2f7   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days       127.0.0.1:38225->6443/tcp   kindcluster-control-plane2
fa01e66ab40f   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days       127.0.0.1:45505->6443/tcp   kindcluster-control-plane
fe02fe4f6dd1   kindest/node:v1.25.16                "/usr/local/bin/entr…"   2 days ago   Up 2 days                                   kindcluster-worker3
0e7efcc9e6c9   kindest/haproxy:v20230606-42a2262b   "haproxy -W -db -f /…"   2 days ago   Up 2 days       127.0.0.1:43287->6443/tcp   kindcluster-external-load-balancer

```

---
## 액티브 스탠바이 HA(아마도 high availability?)세팅
- 예제는 노드 정지시켜서 다른 노드에 팟 생겨서 서비스가 계속 지속되는걸 보여주려고 한 예제이지만, 디비가 5분 동안 죽어있는게 과연 적절한 거신가 ㅋㅋ
- 그것보단 yml 파일 설정에서 로컬 세팅에서 persistant volumn 설정이 빠져있어서 이 부분 추가하면서 확인한 것들 기록


예제에 있는 yml로 apply 하면 Pod이 Pending상태로 유지가 됨.
내용을 찾아보니..persistantvolume이 없어서 그런 것으로 보였다.
```bash
# 아..로그가..지워졌다; gpt한테 물어본 내용으로 
The error message 
"pod has unbound immediate PersistentVolumeClaims" 
indicates that the PersistentVolumeClaim (PVC) required by your MySQL pod, 
as defined in mysql_w_pvc.yml, 
cannot be bound to any PersistentVolume (PV). 
This situation can occur due to several reasons, such as no available PVs that meet the claim's requirements, 
or all suitable PVs are already bound to other PVCs. 
The part about "preemption: 0/6 nodes are available: 
6 Preemption is not helpful for scheduling" suggests that even considering node preemption, the scheduler cannot find a node where the pod's requirements, including its PVC, can be satisfied.
...
```

gpt가 말해준 방법대로 일단 Pvc와 Pv 검색..
근데 내가 만든 적이 없고, default값으로 생성되는 pv가 없으면...없지
```bash
k get pvc -n <namespace>
k get pv
```

GPT가 추천해준 대로 PV 관련 SPEC을 추가 &수정
```YAML
# 로컬에서 테스트시에 pv가 따로 없으면 먼저 만들어줘야 한다.
# 얘는 그냥 yaml을 분리해서 보관해도 될 듯?? 공용으로 사용하려면...
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mysql-pv
spec:
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: standard
  local:
    path: /data/mysql
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - your-node-name
```

local 경로를 마운트한 경로에 추가해주려고 몇 가지 설정
- /dev/sda 에 파티션 (정리와)추가 -> 경로 마운트
- 안 쓰는 파티션 그냥 삭제하고 새로 마운트
```
umount /dev/sda1
df -l # 마운트 확인
gnome-fdisks  # data 라는 이름의 파티션 생성
sudo mkdir -p /data/mysql # 마운트할 경로는 /data
mount -t vfat /dev/sda1 /data
mount | grep /data
/dev/sda1 on /data type vfat (...)

# 재부팅하더라도 마운트 유지되게
sudo vim /etc/fstab

# 확인
df -l

# 혹시 몰라서 권한수정..(관리자:그룹:사용자)
# 별로 바람직하진 않지만;;
chmod 777 /data/mysql

# 그룹도 체크해보려다가..그냥 일단
groups # 그룹 리스트
getent group {그룹명} # 그룹에 속한 유저
```

이렇게 해준 후 다시 apply 해보면 Pod이 제대로 뜬다.
pod 로그 확인..

```bash
> k get po -o wide
NAME                            READY   STATUS              RESTARTS   AGE   IP       NODE                  NOMINATED NODE   READINESS GATES
mysql-deploy-558cd58c54-q84g9   0/1     ContainerCreating   0          27s   <none>   kindcluster-worker3   <none>           <none>

> k get events | grep mysql-deploy-558cd58c54-q84g9
58s                 Normal   SuccessfulCreate        ReplicaSet/mysql-deploy-558cd58c54   Created pod: mysql-deploy-558cd58c54-q84g9
52s                 Normal   Scheduled               Pod/mysql-deploy-558cd58c54-q84g9    Successfully assigned default/mysql-deploy-558cd58c54-q84g9 to kindcluster-worker3
52s                 Normal   Pulling                 Pod/mysql-deploy-558cd58c54-q84g9    Pulling image "mysql:5.7"
30s                 Normal   Pulled                  Pod/mysql-deploy-558cd58c54-q84g9    Successfully pulled image "mysql:5.7" in 22.207180046s (22.207193762s including waiting)
30s                 Normal   Created                 Pod/mysql-deploy-558cd58c54-q84g9    Created container mysql
30s                 Normal   Started                 Pod/mysql-deploy-558cd58c54-q84g9    Started container mysql


> k get po -o wide
NAME                            READY   STATUS    RESTARTS   AGE   IP            NODE                  NOMINATED NODE   READINESS GATES
mysql-deploy-558cd58c54-q84g9   1/1     Running   0          63s   10.244.3.15   kindcluster-worker3   <none>           <none>

> k logs mysql-deploy-558cd58c54-q84g9
2024-06-30 04:43:54+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 5.7.44-1.el7 started.
2024-06-30 04:43:55+00:00 [Note] [Entrypoint]: Switching to dedicated user 'mysql'
2024-06-30 04:43:55+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 5.7.44-1.el7 started.
'/var/lib/mysql/mysql.sock' -> '/var/run/mysqld/mysqld.sock'
2024-06-30T04:43:56.183546Z 0 [Warning] TIMESTAMP with implicit DEFAULT value is deprecated. Please use --explicit_defaults_for_timestamp server option (see documentation for more details).
2024-06-30T04:43:56.184874Z 0 [Note] mysqld (mysqld 5.7.44) starting as process 1 ...
2024-06-30T04:43:56.188591Z 0 [Note] InnoDB: PUNCH HOLE support available
2024-06-30T04:43:56.188621Z 0 [Note] InnoDB: Mutexes and rw_locks use GCC atomic builtins
2024-06-30T04:43:56.188624Z 0 [Note] InnoDB: Uses event mutexes
2024-06-30T04:43:56.188627Z 0 [Note] InnoDB: GCC builtin __atomic_thread_fence() is used for memory barrier
2024-06-30T04:43:56.188629Z 0 [Note] InnoDB: Compressed tables use zlib 1.2.13
2024-06-30T04:43:56.188634Z 0 [Note] InnoDB: Using Linux native AIO
2024-06-30T04:43:56.188893Z 0 [Note] InnoDB: Number of pools: 1
2024-06-30T04:43:56.188993Z 0 [Note] InnoDB: Using CPU crc32 instructions
2024-06-30T04:43:56.190561Z 0 [Note] InnoDB: Initializing buffer pool, total size = 128M, instances = 1, chunk size = 128M
2024-06-30T04:43:56.197125Z 0 [Note] InnoDB: Completed initialization of buffer pool
2024-06-30T04:43:56.199179Z 0 [Note] InnoDB: If the mysqld execution user is authorized, page cleaner thread priority can be changed. See the man page of setpriority().
2024-06-30T04:43:56.211103Z 0 [Note] InnoDB: Highest supported file format is Barracuda.
2024-06-30T04:43:56.223527Z 0 [Note] InnoDB: Creating shared tablespace for temporary tables
2024-06-30T04:43:56.223576Z 0 [Note] InnoDB: Setting file './ibtmp1' size to 12 MB. Physically writing the file full; Please wait ...
2024-06-30T04:43:56.247825Z 0 [Note] InnoDB: File './ibtmp1' size is now 12 MB.
2024-06-30T04:43:56.248557Z 0 [Note] InnoDB: 96 redo rollback segment(s) found. 96 redo rollback segment(s) are active.
2024-06-30T04:43:56.248566Z 0 [Note] InnoDB: 32 non-redo rollback segment(s) are active.
2024-06-30T04:43:56.248908Z 0 [Note] InnoDB: 5.7.44 started; log sequence number 12219281
2024-06-30T04:43:56.249122Z 0 [Note] InnoDB: Loading buffer pool(s) from /var/lib/mysql/ib_buffer_pool
2024-06-30T04:43:56.249239Z 0 [Note] Plugin 'FEDERATED' is disabled.
2024-06-30T04:43:56.250033Z 0 [Note] InnoDB: Buffer pool(s) load completed at 240630  4:43:56
2024-06-30T04:43:56.253517Z 0 [Note] Found ca.pem, server-cert.pem and server-key.pem in data directory. Trying to enable SSL support using them.
2024-06-30T04:43:56.253526Z 0 [Note] Skipping generation of SSL certificates as certificate files are present in data directory.
2024-06-30T04:43:56.253529Z 0 [Warning] A deprecated TLS version TLSv1 is enabled. Please use TLSv1.2 or higher.
2024-06-30T04:43:56.253530Z 0 [Warning] A deprecated TLS version TLSv1.1 is enabled. Please use TLSv1.2 or higher.
2024-06-30T04:43:56.253913Z 0 [Warning] CA certificate ca.pem is self signed.
2024-06-30T04:43:56.253942Z 0 [Note] Skipping generation of RSA key pair as key files are present in data directory.
2024-06-30T04:43:56.254154Z 0 [Note] Server hostname (bind-address): '*'; port: 3306
2024-06-30T04:43:56.254181Z 0 [Note] IPv6 is available.
2024-06-30T04:43:56.254195Z 0 [Note]   - '::' resolves to '::';
2024-06-30T04:43:56.254212Z 0 [Note] Server socket created on IP: '::'.
2024-06-30T04:43:56.256825Z 0 [Warning] Insecure configuration for --pid-file: Location '/var/run/mysqld' in the path is accessible to all OS users. Consider choosing a different directory.
2024-06-30T04:43:56.280885Z 0 [Note] Event Scheduler: Loaded 0 events
2024-06-30T04:43:56.281038Z 0 [Note] mysqld: ready for connections.
Version: '5.7.44'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  MySQL Community Server (GPL)
```

pv와 Pvc 확인
```bash
> k get pv     
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM               STORAGECLASS   REASON   AGE
mysql-pv                                   1Gi        RWO            Retain           Available                       standard                49m
pvc-a48c71b0-4d46-4492-9cd6-c81843ff382b   1Gi        RWO            Delete           Bound       default/mysql-pvc   standard                49m


> k get pvc    
NAME        STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
mysql-pvc   Bound    pvc-a48c71b0-4d46-4492-9cd6-c81843ff382b   1Gi        RWO            standard       49m
```

---
<br/>

### [트러블슈팅] mysql previlage 문제..

그냥 그렇구나 하고 yaml 안 돌려봤으면 재미없었을 뻔..ㅎㅎㅎㅎ...
트러블슈팅하면서 커멘드에도 익숙해지고 서비스/컨피그맵/시크릿도 강제 예습을 ㅋㅋㅋㅋ
  <br/>
위에서 제대로 뜨는 줄 알았는데; pod restart가 엄청나게 일어나서 로그를 보니,
LivenessProve에서 alive 응답을 못 받고 있다...  
login 이 제대로 안되서 denied가 떨어지는 상황ㅠ
  <br/>
일단 yml의 env쪽 패스워드 변수를 모두 secret과 config로 바꿈.
그리고 `MYSQL_ROOT_HOST` 설정도 추가..아무데서나 접속도 못하게 해둬서;

**configmap과 secret 설정**
```bash
> k create configmap mysql-configmap \
--from-literal MYSQL_USER={유저} \
--from-literal MYSQL_ROOT_HOST=% 


> k create secret generic mysql-pass \
--from-literal MYSQL_PASSWORD={password} \
--from-literal MYSQL_ROOT_PASSWORD={password}

secret/mysql-pass created
```
yaml 쪽 변경사항
```yaml
env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-pass
              key: MYSQL_ROOT_PASSWORD
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-pass
              key: MYSQL_PASSWORD
        - name: MYSQL_USER
          valueFrom:
            configMapKeyRef:
              name: mysql-configmap
              key: MYSQL_USER
        - name: MYSQL_ROOT_HOST
          valueFrom:
            configMapKeyRef:
              name: mysql-configmap
              key: MYSQL_ROOT_HOST 
```

일단 이렇게 바꾸고 `exec -it` 로 ymal의 livenessProve 실행 cmd를 날렸는데..계속 패스워드를 물어봄;;
그래서 커멘드를 바꾸니 제대로 된다..하...
```yaml 
# 변경전
  livenessProbe:
    exec:
      command: ["mysqladmin","-p$MYSQL_ROOT_PASSWORD","ping"]

# 변경후 ----
  livenessProbe:
    exec:
      command: 
        - bash
        - "-c"
        - |
          mysqladmin -uroot -p$MYSQL_ROOT_PASSWORD ping
```
---
### [트러블슈팅] mysql 포트로 접속 에러 (해결방법 2가지)
  
**[방법1]**  
**PORT-FORWARD로 잠깐 열어서 MYSQL benchmark 에 접속**
  
  
**먼저 포트에 열결할 벤치마크 설치 (ubuntu 22.04)**
벤치마크 설치하는 것도 일이었음;; 
처음에 메뉴얼로 설치했다가 또 지우고..하..

```
- mysql 홈페이지에 가서 config Deb 를 먼저 다운로드 받아서 dpkg
여기서: https://dev.mysql.com/downloads/repo/apt/
- 그러면 버전 설정 등을 할 수 있는 화면이 하나 뜨는데 그대로 그냥 두고 ok
> sudo dpkg -i mysql-apt-config_0.8.30-1_all.deb && sudo apt-get update 


# 그러고 doc에는 apt install로 벤치마크 커뮤니티를 다운받으라는데..없음;;
> sudo apt-get install mysql-workbench-community
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
E: Unable to locate package mysql-workbench-community


# 그래서 snap으로 설치해줘야 함..하..
sudo snap install mysql-workbench-community  

```

**Portforward 로 접속**
service 설정하고 -> 공유기에 설정해둔 외부 포트를 열어뒀는데..안됨;;  
그래도 Portforward로 localhost에서 접속은 해볼 수 있었다..
```bash
> k port-forward pod/mysql-deploy-5b48f458f-gw9zb 30007:3306

Forwarding from 127.0.0.1:30007 -> 3306
Forwarding from [::1]:30007 -> 3306
Handling connection for 30007
Handling connection for 30007
Handling connection for 30007

```
   
---
  
**[방법2]**  
**Kind cluster control-plane에 포트포워딩 설정**
[[참조페이지]](https://iamunnip.medium.com/kind-local-kubernetes-cluster-part-4-cf47c46c812e)
이 역시 벤치마크와 잘 연결됨.
  
외부에서 노드의 포트에 접근하려면 kind 에 포트를 열어줘야 함
컨트롤플레인이 여러개면 하나에만 달아주면 됨. 여러개에 같은 포트 설정 못 함.

```bash
- role: control-plane
  extraPortMappings:
  - containerPort: 30007    # 호스트 포트와 컨테이너 포트를 매핑. service에서 nodePort를 사용하려면 노드포트=컨테이너포트 여야 함
    hostPort: 30007
    listenAddress: "0.0.0.0"
    protocol: TCP
  image: kindest/node:v1.25.16
```
  
그리고 Mysql 서비스에 포트 확인. 
노드포트와 위의 kind쪽에서 열어둔 포트랑 같아야 함
```bash
# mysql service, 요청을 파드에게 전달
apiVersion: v1
kind: Service
metadata:
  name: mysql-svc
  labels:
    app: mysql
spec:
  type: NodePort
  ports:
  - protocol: TCP
    port: 3306
    targetPort: 3306
    nodePort: 30007  ## NodePort 서비스의 포트 범위는 30000~32767
  selector:
    app: mysql
```

---
  
**[방법3]**  
**서비스 LoadBalance로 설정시 externalIP 부여하는 방법**
요거는 테스트해봐야 한다. [[참조페이지]](https://medium.com/groupon-eng/loadbalancer-services-using-kubernetes-in-docker-kind-694b4207575d)
  
  