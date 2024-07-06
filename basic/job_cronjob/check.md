# job/cronjob 실습 로그
잡 컨트롤러는 파드에 있느 ㄴ모든 컨테이너가 정상적으로 종료할 떄까지 재실행.(최대 재실행횟수 있음)  
크론잡은 UNIX의 크론과 같은 포맷으로 실행 스케줄을 지정할 수 있느 컨트롤러  
    
## 잡컨트롤러의 동작 방식
  
- 지정한 실행 횟수와 병행 개수에 따라 한 개 이상의 파드를 실행
- 파드 안에 있는 모든 컨테이너가 정상 종료해야 파드가 정상종료했다고 인정. 컨테이너중 하나라도 나가리나면..비정상 종료임.
- 잡에 설정한 파드의 실행횟수를 전부 정상 종료하면 -> 잡 종료. 
- 파드의 비정상 종료에 따른 재실행 횟수가 최대 재실행횟수에 도달해도 잡 중단.
- 노드 장애로 팟 제거 되면 다른 노드에서 파드 재실행
- 잡에 의해 실행된 파드는 잡이 삭제될 때까지 유지 -> 잡이 삭제되면 모든 파드도 삭제.
  
잡 컨트롤러 사용시 주의점
- 여러 프로그램의 실행 순서나 비정상 종료 시의 분기 등은 컨테이너 안의 쉘에서 제어함
- k get pod 해서 팟이 completed 상태여도 팟은 비정상 종료일 수 있음.
  

## 크론잡 동작 방식
- 지정한 시각에 잡을 만든다
- 생성된 파드의 개수가 정해진 수를 넘어서면 가비지 수집 컨트롤러가 종료된 파드를 삭제  
  
  
## 활용

### 잡

- 여러 파드를 띄워서 처리시 병렬처리/순차처리 모두 가능
- 여러 사양(cpu, gpu, memory..)의 파드를 띄워서 처리시 마스터 노드의 스케줄러가 적절한 노드를 선택해서 파드를 배치
- 메세지큐에 데이터를 넣으면 넣은 데이터를 처리하는 팟을 실행하여 처리하는..뭐 그런것도 할 수 있다. 쓰기 나름이겠지..
  

---

## 테스트
책이랑 좀 상이한 부분이 있어서 쿠베 doc이랑 같이 보면서 작업.  
파일:  
- job-abnormal-end.yml
  
컨테이너가 이 상종료할 때 동작:  
- `backoffLimit: 6` 으로 되어있어서 6번 반복하고는 종료됨
- k get pod 해도 status: Error로 뜨는데..???
```bash
k get pod   
NAME                   READY   STATUS   RESTARTS   AGE
abnormal-end-0-fbwzk   0/2     Error    0          3m38s
abnormal-end-0-qxrlw   0/2     Error    0          3m59s
abnormal-end-0-z6qsq   0/2     Error    0          4m11s
```
- 재실행할 때마다 다음 재실행이 겁나 느려지는데 재실행할 때마다 재실행까지 시간이 늘어난다고 본 듯..(왜 못 찾겠지-_-; )
```bash
> k describe job abnormal-end 
Name:               abnormal-end
Namespace:          default
Selector:           controller-uid=7cba0356-9588-44f5-b7f0-b77c43e7cdbe
Labels:             controller-uid=7cba0356-9588-44f5-b7f0-b77c43e7cdbe
                    job-name=abnormal-end
Annotations:        batch.kubernetes.io/job-tracking: 
Parallelism:        1
Completions:        1
Completion Mode:    Indexed
Suspend:            false
Backoff Limit:      6
Start Time:         Sat, 06 Jul 2024 21:21:46 +0900
Pods Statuses:      0 Active (0 Ready) / 0 Succeeded / 7 Failed
Completed Indexes:  <none>
Pod Template:
  Labels:  controller-uid=7cba0356-9588-44f5-b7f0-b77c43e7cdbe
           job-name=abnormal-end
  Containers:
   busybox:
    Image:      busybox:latest
    Port:       <none>
    Host Port:  <none>
    Command:
      sh
      -c
      sleep 5; exit 1
    Environment:   <none>
    Mounts:        <none>
  Volumes:         <none>
  Node-Selectors:  <none>
  Tolerations:     <none>
Events:
  Type     Reason                Age    From            Message
  ----     ------                ----   ----            -------
  Normal   SuccessfulCreate      12m    job-controller  Created pod: abnormal-end-0-4mfcl
  Normal   SuccessfulCreate      12m    job-controller  Created pod: abnormal-end-0-hxj6w
  Normal   SuccessfulCreate      12m    job-controller  Created pod: abnormal-end-0-xr4x8
  Normal   SuccessfulCreate      11m    job-controller  Created pod: abnormal-end-0-7c696
  Normal   SuccessfulCreate      10m    job-controller  Created pod: abnormal-end-0-qm4hd
  Normal   SuccessfulCreate      9m27s  job-controller  Created pod: abnormal-end-0-v6k4l
  Normal   SuccessfulCreate      6m38s  job-controller  Created pod: abnormal-end-0-t5zjj
  Warning  BackoffLimitExceeded  69s    job-controller  Job has reached the specified backoff limit
```
  
첫 실행 + 6번 재시도 = 7번 실행되고 job은 fail상태인 것 확인 가능
```bash
> k get -o yaml job abnormal-end     
apiVersion: batch/v1
kind: Job
metadata:
  annotations:
    batch.kubernetes.io/job-tracking: ""
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"batch/v1","kind":"Job","metadata":{"annotations":{},"name":"abnormal-end","namespace":"default"},"spec":{"completionMode":"Indexed","completions":1,"parallelism":1,"template":{"spec":{"containers":[{"command":["sh","-c","sleep 5; exit 1"],"image":"busybox:latest","name":"busybox"}],"restartPolicy":"Never"}}}}
  creationTimestamp: "2024-07-06T12:21:46Z"
  generation: 1
  labels:
    controller-uid: 7cba0356-9588-44f5-b7f0-b77c43e7cdbe
    job-name: abnormal-end
  name: abnormal-end
  namespace: default
  resourceVersion: "461085"
  uid: 7cba0356-9588-44f5-b7f0-b77c43e7cdbe
spec:
  backoffLimit: 6
  completionMode: Indexed
  completions: 1
  parallelism: 1
  selector:
    matchLabels:
      controller-uid: 7cba0356-9588-44f5-b7f0-b77c43e7cdbe
  suspend: false
  template:
    metadata:
      creationTimestamp: null
      labels:
        controller-uid: 7cba0356-9588-44f5-b7f0-b77c43e7cdbe
        job-name: abnormal-end
    spec:
      containers:
      - command:
        - sh
        - -c
        - sleep 5; exit 1
        image: busybox:latest
        imagePullPolicy: Always
        name: busybox
        resources: {}
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
      dnsPolicy: ClusterFirst
      restartPolicy: Never
      schedulerName: default-scheduler
      securityContext: {}
      terminationGracePeriodSeconds: 30
status:
  conditions:
  - lastProbeTime: "2024-07-06T12:33:24Z"
    lastTransitionTime: "2024-07-06T12:33:24Z"
    message: Job has reached the specified backoff limit
    reason: BackoffLimitExceeded
    status: "True"
    type: Failed
  failed: 7
  ready: 0
  startTime: "2024-07-06T12:21:46Z"
  uncountedTerminatedPods: {}
```
  

팟에 컨테이너가 2개이고 하나가 비정상종료할 떄도 job 은 실패로 뜨고, backofflimit 만큼 재실행 된 다음, fail처리 됨
```bash
k describe job abnormal-end  
Name:               abnormal-end
Namespace:          default
Selector:           controller-uid=07d33d8e-54c0-4bdd-8b14-3b45bcf59d02
Labels:             controller-uid=07d33d8e-54c0-4bdd-8b14-3b45bcf59d02
                    job-name=abnormal-end
Annotations:        batch.kubernetes.io/job-tracking: 
Parallelism:        1
Completions:        1
Completion Mode:    Indexed
Suspend:            false
Backoff Limit:      2
Start Time:         Sat, 06 Jul 2024 21:37:39 +0900
Pods Statuses:      0 Active (0 Ready) / 0 Succeeded / 3 Failed
Completed Indexes:  <none>
Pod Template:
  Labels:  controller-uid=07d33d8e-54c0-4bdd-8b14-3b45bcf59d02
           job-name=abnormal-end
  Containers:
   busybox-1:
    Image:      busybox:latest
    Port:       <none>
    Host Port:  <none>
    Command:
      sh
      -c
      sleep 5; exit 1
    Environment:  <none>
    Mounts:       <none>
   busybox-2:
    Image:      busybox:latest
    Port:       <none>
    Host Port:  <none>
    Command:
      sh
      -c
      sleep 5; exit 0
    Environment:   <none>
    Mounts:        <none>
  Volumes:         <none>
  Node-Selectors:  <none>
  Tolerations:     <none>
Events:
  Type     Reason                Age   From            Message
  ----     ------                ----  ----            -------
  Normal   SuccessfulCreate      79s   job-controller  Created pod: abnormal-end-0-z6qsq
  Normal   SuccessfulCreate      67s   job-controller  Created pod: abnormal-end-0-qxrlw
  Normal   SuccessfulCreate      46s   job-controller  Created pod: abnormal-end-0-fbwzk
  Warning  BackoffLimitExceeded  14s   job-controller  Job has reached the specified backoff limit
```