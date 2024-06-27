# 정리


## 1. docker

### 도커 빌드
알다시피.. dockerfile 있는 곳에서 
```bash
# 레포에 업데이트 하려면 도커허브의 id를 붙여줘야 함.
# 다른 명칭을 사용하면 access denied 에러 생김

docker build --tag {dockerhub user id}/{tag}:{version} .
```
성공시
```bash
The push refers to repository [docker.io/{dockerhub user id}/webapl]
4cf4630f5159: Pushed 
3648e3adf39f: Pushed 
820c3890a904: Pushed 
6c8a2cdc3fd3: Pushed 
94e5f06ff8e3: Pushed 
0.1: digest: sha256:d8f507d6fd36eac31385b79ac589f9a7562e4bdb0a9bb8db2532617e7b8ed71b size: 1365
```

다른 명칭 썼을 경우 에러 메세지
```bash
The push refers to repository [docker.io/test/webapl]
4cf4630f5159: Preparing 
3648e3adf39f: Preparing 
820c3890a904: Preparing 
6c8a2cdc3fd3: Preparing 
94e5f06ff8e3: Preparing 
denied: requested access to the resource is denied
```

### 도커 푸쉬

```bash
docker push {dockerhub user id}/{tag}:{version}

he push refers to repository [docker.io/{dockerhub user id}/{tag}]
49698c415800: Pushed 
d94d8a8e8f60: Pushed 
b92e8115ecca: Layer already exists 
1251204ef8fc: Layer already exists 
47ef83afae74: Layer already exists 
df54c846128d: Layer already exists 
be96a3f634de: Layer already exists 
0.4: digest: sha256:9069dac7308f56e2514f2093e32e76b72987039afb48e3e9979b116f841a992f size: 1776
```

## 2. dockerfile 변경시 태그버전을 올리자
그냥 같은 태그 이미지에 계속 붙여넣으면 현재 수정 내용이 반영이 잘 안 되는 경우가 있었다. 로컬에 있는 docker 이미지와 빌드캐쉬를 지우고, 허브쪽 레포를 날려도 잘 안되서 태그를 다시 지정하고 새로 이미지를 만드니 현재 수정버전으로 잘 실행되었다.

```bash
docker builder prune # build 캐쉬 날리기

# 도커허브 레포는 브라우저에서 수동으로 삭제함
# 로컬 이미지는 도커 데스크탑에서 삭제
```


# 2. Kubernetes

## 컨테이너 계속 띄워놔야 할 때
컨테이너를 하나 띄워놓고 뭐를 작업해야 하는 경우가 있음. alpine 컨테이너는 apply로 띄워두면 그냥 종료되어버려서 컨테이너 안 쪽을 봐야 하는 경우는 종료되지 않게 조치해야 함.
```yaml
# 도커 컨테이너 띄워두기라고도 볼 수 있음

...

containers:
  - name: main
    image: alpine
    resources:
      limits:
        cpu: "0.5"
        memory: "512Mi"
    # 무한히 스핀하고 기다립니다
    # 공식문서에도 있는 내용이다.
    # https://kubernetes.io/ko/docs/tasks/inject-data-application/define-command-argument-container/
    command: [ sh, -c, -- ]
    args: [ while true; do sleep 30; done; ]
    volumeMounts:
    - name: contents-volume
      mountPath: /git
...
```
