# kubectl 기본 cli

`alias k=kubectl` 로 설정
기본 cli 테스트와 궁금한 점들 정리

---
## 자주 쓰는 커멘드 정리
```bash
# 디플로이먼트, pod,service 정보 출력
> k get deploy,po,service
# 혹은 all로 
> k get all

> k get po -o wide

# Pod 로그보기
> k logs {pod이름} 

# Pod 이벤트 보기
> k get event | grep {pod이름}

# Pod 정보 출력
> k describe po {pod이름}

# deployment모드에서 scale 수정
> k scale replicas={수정된숫자} {디플로이명}/{파드명}

# 롤백
> k rollout undo deployment {파드명}

# 가동 중인 파드를 다른 노드로 이동
> k drain {노드명}
# 노드에 새로운 파드의 스케줄 금지
> k cordon {노드명}
# 노드에 새로운 타드의 스케줄 재개
> k uncordon {노드명}


```



---
## pod 실행
- 실행 자체는 도커랑 비슷해서 익숙..

먼저 Test 네임스페이스를 만들어서 그곳에 파드를 만들 예정
```
kubectl create namespace test
```

헬로월드 pod을 생성
```
> kubectl run hello-world \
--image=hello-world \
-it \
--restart=Never  \ # 컨트롤러없이 파드만 독립적 실행
--namespace test \
--rm #파드 종료 후 자동삭제


Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

Q. 여기서 이 팟은 여러 노드중에 어디에 만들어지지? 
라는 생각을 했는데, 이전에 쿠버네티스가 알아서 램덤으로 임의의 워커노드에 만든다고 들은 것 같다.

Pod 확인은 test namespace에 만들었기 때문에 namespace를 명시해줘야 한다. 명시하지 않으면 default 네임스페이스에 만들어진다.
```
> kubectl get pod --namespace test
NAME          READY   STATUS      RESTARTS   AGE
hello-world   0/1     Completed   0          28s

> kubectl get pod
No resources found in default namespace.
```
파드 삭제
```
> kubectl delete pod hello-world --namespace test
pod "hello-world" deleted
```
파드 로그 확인
```
> kubectl logs hello-world
```

---

## 컨트롤러로 pod 실행
- 웹서버나 API 서버처럼 지속적으로 서비스를 제공해야 하는 워크로드에 적합
- Run시에 --restart 옵션 설정을 하면 컨트롤러 제어 하에 실행이 가능하다. 
- 보통 옵션을 주지 않으면 `--restart=Always`로 들어가 있음. 디플로이먼트 컨트롤러(=디플로이먼트)의 제어하에 실행됨

```
> kubectl run hello-world --image=hello-world
```
--> 라고 책에 적혀있었으나 아닌 것 같음..
왜냐하면, 일단 deployment 가 안 생김.. 왜 안 보이지 하고 삽질했는데, 안 생기는게 맞는 것 같고.. 그냥 Pod 삭제하면 사라짐...옛날 책이어서 최신게 반영이 안되어 있는건가;
```
> kubectl get deploy,po
NAME              READY   STATUS             RESTARTS     AGE
pod/hello-world   0/1     CrashLoopBackOff   1 (9s ago)   16s

# 없어..디플로이먼트
> kubectl delete deployment hello-world
Error from server (NotFound): deployments.apps "hello-world" not found

#그냥 지우면 됨
> kubectl delete pod hello-world                 
pod "hello-world" deleted

# 깨끗하게 지워짐
> kubectl get deploy,po 
No resources found in default namespace.

```

디플로이먼트로 던지려면 이렇게 해야하는 것 같다.
코파일럿에게 물어봄.
```
kubectl create deployment my-deployment --image=nginx --replicas=5
deployment.apps/my-deployment created

> kubectl get deploy,po                                                                                                 ✔  kind-kindcluster ○  15:50:36 
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/my-deployment   0/3     3            0           16s

NAME                                 READY   STATUS              RESTARTS   AGE
pod/my-deployment-67b5d4bf57-52z45   0/1     ContainerCreating   0          16s
pod/my-deployment-67b5d4bf57-klzpk   0/1     ContainerCreating   0          16s
pod/my-deployment-67b5d4bf57-v2z75   0/1     ContainerCreating   0          16s


# 잠시 뒤 다시 확인
> kubectl get deploy,po                               
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/my-deployment   3/3     3            3           52s

NAME                                 READY   STATUS    RESTARTS   AGE
pod/my-deployment-67b5d4bf57-52z45   1/1     Running   0          52s
pod/my-deployment-67b5d4bf57-klzpk   1/1     Running   0          52s
pod/my-deployment-67b5d4bf57-v2z75   1/1     Running   0          52s
```
pod 하나 지우고 다시 실행하니 빠르게 다시 시작된다
```
> kubectl delete pod my-deployment-67b5d4bf57-52z45                                                                   1 х  kind-kindcluster ○  15:54:18 
pod "my-deployment-67b5d4bf57-52z45" deleted

> kubectl get deploy,po   
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/my-deployment   3/3     3            3           3m58s

NAME                                 READY   STATUS    RESTARTS   AGE
pod/my-deployment-67b5d4bf57-82529   1/1     Running   0          3s
pod/my-deployment-67b5d4bf57-klzpk   1/1     Running   0          3m58s
pod/my-deployment-67b5d4bf57-v2z75   1/1     Running   0          3m58s
```
디플로이먼트 삭제
```
> kubectl delete deployment my-deployment 
deployment.apps "my-deployment" deleted

> kubectl get deploy,po    
No resources found in default namespace.
```

---
## JOB으로 POD 실행
- 잡컨트롤러의 제어하에 파드가 기동됨
- 배치 처리와 같은 워크로드에 적합
- 파드가 비정상 종료하면 재시작하고 파드가 정상 종료할 떄까지 지정한 횟수만큼 재실행한다..
```
# 정상종료 
kubectl create job job-1 --image=ubuntu -- /bin/bash -c "exit 0"

# 비정상종료
kubectl create job job-1 --image=ubuntu -- /bin/bash -c "exit 1"
```
확인 및 삭제
```
> kubectl get jobs 
NAME    COMPLETIONS   DURATION   AGE
job-1   1/1           12s        19s

 > kubectl get po 
NAME          READY   STATUS      RESTARTS   AGE
job-1-rkhcc   0/1     Completed   0          26s

 > kubectl get po  
NAME          READY   STATUS      RESTARTS   AGE
job-1-rkhcc   0/1     Completed   0          29s
 > kubectl delete job job-1  
job.batch "job-1" deleted
```
   

---

## 클러스터에 내부에서만 팟끼리 통신 가능할 때 확인법

-> busybox라는 팟을 띄워가지고 테스트해볼 수 있음 

```bash
k run -it busybox --restart=Never --rm --image=busybox sh
```
  
## pod 실행이 제대로 안 될 때
### pod unexpected error creating file watcher: too many open files
- 참조: https://github.com/kubeflow/manifests/issues/2087  
- KIND 클러스터를 사용할 때 나타나는 에러로 보임.
- fs.inotify는 리눅스 커널에서 제공하는 inotify 기능과 관련된 커널 파라미터들을 관리하기 위한 네임스페이스.
   - inotify는 파일 시스템 이벤트를 모니터링하는 기능. 특정 파일이나 디렉토리에서 발생하는 변경 사항(생성,삭제,수정 등) 을 감지하고 알림을 받을 수 있도록 도와줌.
   - 파일 시스템의 변화에 실시간으롣 대응해야 하는 애플리케이션에서 사용됨

```bash
sudo sysctl -a | grep fs.inotify 

# inotify 인스턴스에서 큐에 넣을 수 있는 최대 이벤트 수를 설정
# 이 값을 추과하면 새로운 이벤트가 큐에 들어오지 못 하고 손실됨
fs.inotify.max_queued_events = 16384

# 한 사용자(uid)가 생성할 수 있는 inotify 인스턴스의 최대 수
fs.inotify.max_user_instances = 1280

# 한 사용자(UID)가 생성할 수 있는 inotify watch의 최대 수
# 각 인스턴스에서 모니터링할 수 있는 파일이나 디렉토리의 최대 개수
# 예를 들어, 파일 시스템의 많은 파일을 모니터링하는 프로그램(예: 텍스트 에디터, 파일 인덱서 등)은 이 값을 높게 설정해야 할 수 있음
fs.inotify.max_user_watches = 655360
```

fs.inotify 값 업데이트
```bash
sudo sysctl fs.inotify.max_user_instances=1280
sudo sysctl fs.inotify.max_user_watches=655360
```