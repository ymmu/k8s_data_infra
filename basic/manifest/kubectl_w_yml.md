# manifest 적용하기
```
> kubectl apply -f nginx-pod.yml
pod/nginx-pod created

> kubectl get po  
NAME        READY   STATUS    RESTARTS   AGE
nginx-pod   1/1     Running   0          6s
```

- 이 파드는 백그라운드로 돌면서 클러스터 네트워크의 TCP 80번 포트에서 요청 대기
- 클러스터 네트워크는 k8s 클러스터를 구성하는 노드 간의 통신을 위한 폐쇄형 네트워크임 (a.k.a 파드 네트워크)
- 클러스터 네트워크에서 오픈한 포트는 k8s 클러스터를 호스팅하는 컴퓨터에서도 접근이 어렵다.

파드 접속시도를 해보즈아.
팟의 ip를 알아내서..curl로 접속 시도 -> 실패

```
# 오 어느 노드에 있는지도 알수있긴 하네..
> kubectl get po nginx -o wide
NAME        READY   STATUS    RESTARTS   AGE     IP           NODE                  NOMINATED NODE   READINESS GATES
nginx-pod   1/1     Running   0          6m45s   10.244.3.4   kindcluster-worker2   <none>           <none>

> curl -m 3 http://10.244.3.4/ 
curl: (28) Connection timed out after 3000 milliseconds
```

busybox 라는 대화형 파드로 Nginx 파드에 접근해봄
```
>   main  kubectl run busybox --image=busybox --restart=Never --rm -it sh 
If you don't see a command prompt, try pressing enter.
/ # 
/ # 
/ # wget -q -O - http://10.244.3.4/
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
/ # 
```

클러스터간 네트워크 상에서 Pod은 각각 IP를 가지며 파드와 파드간 통신할 수 있음.
```
kubectl get po -o wide  
NAME        READY   STATUS       RESTARTS   AGE     IP           NODE                  NOMINATED NODE   READINESS GATES
busyboc     0/1     StartError   0          3m29s   10.244.4.5   kindcluster-worker    <none>           <none>
busybox     0/1     Completed    0          2m54s   10.244.4.6   kindcluster-worker    <none>           <none>
nginx-pod   1/1     Running      0          16m     10.244.3.4   kindcluster-worker2   <none>           <none>
```
