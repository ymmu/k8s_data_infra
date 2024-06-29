# deployment 실습시 체크사항

## deployment의 역할
- 파드의 개수를 관리하는 것. 시스템의 처리 능력, 서비스를 중단하지 않는 가용성, 비용 측면에서 매우 중요
- k8s 클러스터에서는 파드가 서버의 역할을 담당 -> 처리능력을 높이려면 파드 개수를 조절하면 됨
- 파드를 늘릴 수록 cpu와 메모리가 많이 사용되니 주의 필요
- 장애 등으로 파드의 개수가 줄어들면 새롭게 파드를 만들어 기동함
- 애플리케이션의 버전을 업그레이드할 때 새로운 버전의 파드로 조금씩 바꾸는 기능도 제공
- 로드밸런서 기능은 디플로이먼트에 포함되어있지 않음. 이 기능은 쿠버네티스의 "**서비스**"가 제공

**나:** 결국 확장 가능한 서버를 띄우려면 **디플로이먼트 & 서비스** 콤보로 올려야겠네..


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