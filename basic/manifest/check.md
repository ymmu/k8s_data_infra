
# manifest/pod healthcheck 실습시 체크

## 1. yaml에 resources 정의
예제에는 포함이 안 되어 있는데
server appply 시 Resources 정의해줘야 함
```yaml
... 생략
containers:
  - name: webapl
    image: myohyun/webapl:0.1
    resources:  # 안 들어가 있으면 apply시 오류 발생
      limits:
        cpu: "1"
        memory: "512Mi"
      requests:
        cpu: "0.5"
        memory: "256Mi"
    livenessProbe:
... 생략
```
정의 안 했을 경우 에러
```bash
kubectl apply -f webapl-pod.yml
error: error when retrieving current configuration of:
Resource: "/v1, Resource=pods", GroupVersionKind: "/v1, Kind=Pod"
Name: "", Namespace: "default"
from server for: "webapl-pod.yml": resource name may not be empty

```

## 2. 실행 후 로그 확인

```bash
> kubectl logs webapl
# 위가 가장 오래된거 -> 아래로 갈 수록 최신
GET /healthz 200
GET /healthz 200
GET /healthz 200
GET /ready 500  # 20초 전에는 500 응답
GET /healthz 200
GET /ready 200  # ReadinessProve 성공 -> kubectl get pod 시 READY -> 1/1로 변경됨
```

/healthz 에서 계속 500 응답이 떨어지게 되어 있고, 활성프로브가 반복해서 실패하면 kubelete이 새로운 컨테이너를 기동하고 실패를 반복하는 컨테이너를 강제 종료함.
kubectl describe > event 에서 확인 가능
```bash
> kubectl describe po webapl

...생략

Events:
  Type     Reason     Age                    From               Message
  ----     ------     ----                   ----               -------
  Normal   Scheduled  17m                    default-scheduler  Successfully assigned default/webapl to kindcluster-worker2
  Normal   Pulling    17m                    kubelet            Pulling image "myohyun/webapl:0.1"
  Normal   Pulled     17m                    kubelet            Successfully pulled image "myohyun/webapl:0.1" in 9.904043241s (9.904051107s including waiting)
  Normal   Created    14m (x3 over 17m)      kubelet            Created container webapl
  Normal   Started    14m (x3 over 17m)      kubelet            Started container webapl
  Normal   Pulled     14m (x2 over 15m)      kubelet            Container image "myohyun/webapl:0.1" already present on machine
  Warning  Unhealthy  13m (x3 over 16m)      kubelet            Readiness probe failed: HTTP probe failed with statuscode: 500
  Normal   Killing    13m (x3 over 16m)      kubelet            Container webapl failed liveness probe, will be restarted
  Warning  Unhealthy  12m (x10 over 16m)     kubelet            Liveness probe failed: HTTP probe failed with statuscode: 500
  Warning  BackOff    2m8s (x21 over 7m11s)  kubelet            Back-off restarting failed container
```
시간이 지난 후 다시 확인하면, Pod 로그가 새로 바뀌어 있고 -> 이로 인해 컨테이너가 다시 띄워진걸 확인 가능
```bash
Events:
  Type     Reason     Age                   From               Message
  ----     ------     ----                  ----               -------
  Normal   Scheduled  21m                   default-scheduler  Successfully assigned default/webapl to kindcluster-worker2
  Normal   Pulling    21m                   kubelet            Pulling image "myohyun/webapl:0.1"
  Normal   Pulled     21m                   kubelet            Successfully pulled image "myohyun/webapl:0.1" in 9.904043241s (9.904051107s including waiting)
  Normal   Created    18m (x3 over 21m)     kubelet            Created container webapl
  Normal   Started    18m (x3 over 21m)     kubelet            Started container webapl
  Normal   Pulled     18m (x2 over 19m)     kubelet            Container image "myohyun/webapl:0.1" already present on machine
  Warning  Unhealthy  18m (x3 over 20m)     kubelet            Readiness probe failed: HTTP probe failed with statuscode: 500
  Normal   Killing    17m (x3 over 20m)     kubelet            Container webapl failed liveness probe, will be restarted
  Warning  BackOff    6m16s (x21 over 11m)  kubelet            Back-off restarting failed container
  Warning  Unhealthy  80s (x26 over 20m)    kubelet            Liveness probe failed: HTTP probe failed with statuscode: 500
```

# manifest/init container 실습시 체크
파일명: `initcontainer-pod.yml`

## 1. 실행 후 로그 확인
yml에 대문자오타가 나서..
```
Error from server (BadRequest): error when creating "initcontainer-pod.yml": Pod in version "v1" cannot be handled as a Pod: strict decoding error: unknown field "spec.containers[0].volumeMOunts"
```
수정하고 다시 실행하믄.. 초기화컨테이너에서 만든 html 폴더를 볼 수 있다.
`mountpath`="해당 컨테이너가 공유볼륨을 접근할 때 사용하는 경로"이다..

```bash
> kubectl apply -f initcontainer-pod.yml
pod/initcontainer created

> kubectl get po
NAME            READY   STATUS            RESTARTS   AGE
initcontainer   0/1     PodInitializing   0          11s

> kubectl get po
NAME            READY   STATUS    RESTARTS   AGE
initcontainer   1/1     Running   0          20s

> kubectl exec -it initcontainer -c main sh  #이거 이제 deprecated
> kubectl exec -it initcontainer -c main -- sh # 이게 맞는듯?

kubectl exec [POD] [COMMAND] is DEPRECATED and will be removed in a future version. Use kubectl exec [POD] -- [COMMAND] instead.
# ls -al /docs
total 12
drwxrwxrwx 3 root     root     4096 Jun 27 04:14 .
drwxr-xr-x 1 root     root     4096 Jun 27 04:14 ..
drwxr-xr-x 2 www-data www-data 4096 Jun 27 04:14 html
```


