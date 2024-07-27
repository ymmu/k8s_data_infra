# storage 실습 로그
  
- k8s에 배포한 애플리케이션 데이터를 보존하려면 내부 혹은 외부의 스토리지 시스템과 연결하여 퍼시스턴트 볼륨을 이용해야 함
- 외부 스토리지 시스템을 사용하여 여러 개의 물리적인 장비를 묶어 단일 장애점을 극복하고 가용성을 높여 데이터 자산의 분실을 방지 가능
- 외부 스토리지를 사용하는 방법으로는
    - 전용 스토리지 장비를 사용
    - 소프트웨어로 일반적인 서버를 클러스터화하여 저장장치로 사용 (softwear defined storage)
    - 전용 스토리지 + sds 조합 사용
  

---
  
## 스토리지의 종류와 클러스터 구성
- 노드 내부에서 간단하게 사용할 수 있는 볼륨
    - emptyDir: 
        - 노드의 디스크를 파드가 일시적으로 사용하는 방법
        - 같은 파드의 컨테이너 간에는 볼륨을 공유 가능 (한 파드에만 종속되어 있다.) 
        - 다른 파드 간에는 공유 불가
        - 파드 종료하면 삭제됨
    - hostPath
        - 같은 노드의 파드들끼리 공유 가능 (emptyDir과 차이점)
        - 파드와 함꼐 지워지지 않음
        - 다른 노드 간에는 공유 불가
        - 노드 정지하면 데이터 접근 불가.
- 외부 스토리지 시스템을 사용해도 반드시 여러 노드에서 볼륨을 공유할 수 있는 것은 아니다. -> 스토리지 동작 방식에 따라 다름
    - 서버와 스토리지를 연결하는 프로토콜 (nfs, iSCSI 등), 소프트웨어, 클라우드의 스토리지 서비스에 따라 다름
    - NFS 처럼 파일 시스템을 공유하는 시스템의 경우, 여러 노드에서 볼륨을 공유할 수 있으나 iSCSI처럼 블록 스토리지를 기반으로 하는 경우에는 한 개의 노드에서만 접근 가능
  

---
## 스토리지 시스템의 방식
- 책의 표에서 **READWRITE** 가 MANY이면 클러스터단위로 엑세스(모든 노드가 접근가능이라 이해)가 가능하고, ONCE 면 하나의 노드에만 연결되는거니 "노드"라고 표기되어야 하는 것 같은데 그렇지 않아서 CHATGPT를 이용함.   
- K8S 공식문서 봤는데 쿠버네티스 v1.30 에서는 EBS나 AZUREDISK는 deprecated 되었네..써드파티 드라이버 쓰라고; [링크](https://kubernetes.io/docs/concepts/storage/volumes/)
- 기존 이런식으로 마운트했음
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: ebs-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  awsElasticBlockStore:
    volumeID: vol-0abcd1234
    fsType: ext4
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: azurefile-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  azureFile:
    secretName: azure-secret
    shareName: k8s
    readOnly: false

```
### 엑세스 범위의 의미

- **노드**: 특정 노드에 물리적으로 연결된 스토리지로, 해당 노드에서만 접근 가능합니다. 이 경우 다른 노드에서는 해당 스토리지를 사용할 수 없습니다.
- **클러스터**: 클러스터 내의 모든 노드에서 네트워크를 통해 접근할 수 있는 스토리지입니다. 이러한 스토리지는 여러 노드에서 동시에 사용될 수 있습니다.

### 정리된 표

| 스토리지 종류명            | 분류                  | 엑세스 범위               | READWRITE             | 개요                                                                                     |
|-----------------------------|-----------------------|---------------------------|-----------------------|------------------------------------------------------------------------------------------|
| NFS                         | OSS(오픈소스 소프트웨어) | 클러스터                  | RWX (ReadWriteMany)   | Network File System (NFS)는 분산 파일 시스템 프로토콜로, 여러 클라이언트가 네트워크를 통해 공유 스토리지에 액세스할 수 있습니다. |
| CephFS                      | OSS(오픈소스 소프트웨어) | 클러스터                  | RWX (ReadWriteMany)   | CephFS는 Ceph의 분산 파일 시스템으로, 고가용성 및 확장성을 제공합니다.                            |
| GlusterFS                   | OSS(오픈소스 소프트웨어) | 클러스터                  | RWX (ReadWriteMany)   | GlusterFS는 분산 파일 시스템으로, 대규모 스토리지 클러스터를 구축할 수 있습니다.                      |
| EBS                         | 클라우드 서비스          | 노드                      | RWO (ReadWriteOnce)   | Amazon Elastic Block Store (EBS)는 AWS에서 제공하는 블록 스토리지 서비스로, EC2 인스턴스에 연결되며 한 번에 하나의 노드에만 마운트할 수 있습니다.    |
| GCE Persistent Disks        | 클라우드 서비스          | 노드                      | RWO (ReadWriteOnce)   | Google Compute Engine Persistent Disks는 GCP에서 제공하는 블록 스토리지로, VM 인스턴스에 연결되며 한 번에 하나의 노드에만 마운트할 수 있습니다.   |
| Azure Disks                 | 클라우드 서비스          | 노드                      | RWO (ReadWriteOnce)   | Azure Managed Disks는 Azure에서 제공하는 블록 스토리지 서비스로, VM 인스턴스에 연결되며 한 번에 하나의 노드에만 마운트할 수 있습니다.            |
| Azure Files                 | 클라우드 서비스          | 클러스터                  | RWX (ReadWriteMany)   | Azure Files는 Azure에서 제공하는 파일 스토리지 서비스로, SMB 프로토콜을 통해 여러 노드에서 동시에 액세스할 수 있습니다.     |
| HostPath                    | K8S 노드                | 노드                      | RWO (ReadWriteOnce)   | HostPath는 Kubernetes 노드의 파일 시스템 경로를 사용하는 스토리지입니다.                              |
| Local Persistent Storage    | K8S 노드                | 노드                      | RWO (ReadWriteOnce)   | Local Persistent Storage는 특정 노드에 물리적으로 연결된 디스크를 사용하는 스토리지입니다.              |

  

---
  
## 퍼시스턴트 볼륨 이용하기

- "동적 프로비저닝" 과 "수동 스토리지 설정" 방식이 있다.
- 동적 프로비저닝은 pvc만 작성하면 나머지는 프로비저너에 의해서 알아서 pv를 설정해준다.
- gpt한테 프로비저닝 뜻이 뭐냐고 물어봄.
```
프로비저닝은 컴퓨팅 환경에서 필요한 리소스를 준비하고 배포하는 과정을 의미합니다. 
Kubernetes에서 프로비저닝은 스토리지 리소스를 생성하고 관리하는 과정으로, 
정적 프로비저닝과 동적 프로비저닝이 있습니다. 
정적 프로비저닝은 관리자가 수동으로 PV를 생성하는 것이고, 
동적 프로비저닝은 Kubernetes가 자동으로 PV를 생성하는 것입니다.
```
  
### 동적 프로비저닝 테스트
- pvc만 yaml로 apply 했는데 Peding이 되서 봤더니 pv를 이용하는 파드가 없으면 그런 것 같다.
- pvc를 사용하는 Pod도 같이 apply 해야한다
```bash
> k get pvc
NAME                                      STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
persistentvolumeclaim/data-storage-test   Pending                                      standard       4m33s

> k describe pvc data-storage-test                                             1 х  test Py  kind-kindcluster ○  15:26:11 
Name:          data-storage-test
Namespace:     default
StorageClass:  standard
Status:        Pending
Volume:        
Labels:        <none>
Annotations:   <none>
Finalizers:    [kubernetes.io/pvc-protection]
Capacity:      
Access Modes:  
VolumeMode:    Filesystem
Used By:       <none>
Events:
  Type    Reason                Age                From                         Message
  ----    ------                ----               ----                         -------
  Normal  WaitForFirstConsumer  14s (x21 over 5m)  persistentvolume-controller  waiting for first consumer to be created before binding
```
pvc와 pv를 모두 apply 하면 이렇게 뜬다.
```bash
> k get pvc,pv,pod

NAME                                      STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
persistentvolumeclaim/data-storage-test   Bound    pvc-50e1b21b-ad05-4b8b-a132-eb96389f0ef7   1Gi        RWO            standard       2m16s

NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS        CLAIM                                STORAGECLASS   REASON   AGE
persistentvolume/pvc-27e32bf7-da3a-4ad7-a6ea-683c08eb524c   10Gi       RWO            Delete           Terminating   kafka/data-0-mycluster-dual-role-0   standard                3d
persistentvolume/pvc-50e1b21b-ad05-4b8b-a132-eb96389f0ef7   1Gi        RWO            Delete           Bound         default/data-storage-test            standard                13s

NAME       READY   STATUS    RESTARTS   AGE
pod/pod1   1/1     Running   0          17s
```
  
pv를 이용하지 않고 프로비저닝했으므로 프로비저너를 확인해보면
```bash
> k get storageclasses

NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  3d20h
```
Pod 안에 들어가서 어떤 경로로 마운트 되어있는지 확인
```bash
> k exec -it pod1 -- sh

# df -h 
Filesystem      Size  Used Avail Use% Mounted on
overlay         413G  101G  291G  26% /
tmpfs            64M     0   64M   0% /dev
/dev/nvme0n1p8  413G  101G  291G  26% /mnt
...
```
  

### nfs 서버 사용
책에서는 Minikube를 이용해서 세팅을 했는데, 나는 kind를 사용해서 있는 내용을 그대로 쓰지 않았다.  
kind는 도커를 이용해서 쿠버네티스 클러스터를 구축하는 것이어서 다른 방법이 필요하다..  
gpt를 통해서 작성하고, 모르는 부분과 이상한 부분들은 의미를 물어보고, 수정을 요청함
  
  
#### 스텝
yaml에서 궁금한 내용은 파일에 주석처리해둠
각 pv,pvc,daemonset 등 확인
```bash
k get daemonset -n kube-system {데몬셋이름}
k get pv,pvc
k describe pvc {pvc 이름}
```
  
  
1. **로컬 환경에 필요한 패키지를 설치한다.**
  
```bash
# NFS 서버 설치 (Ubuntu 예시)
sudo apt update
sudo apt install nfs-kernel-server

# NFS 공유 디렉토리 생성
sudo mkdir -p /srv/nfs/k8s
sudo chown nobody:nogroup /srv/nfs/k8s

# /etc/exports 파일 수정
echo "/srv/nfs/k8s *(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports

# NFS 서버 재시작
sudo exportfs -rav
sudo systemctl restart nfs-kernel-server

# NFS 서버 방화벽
sudo ufw allow from {} to any port nfs
sudo ufw reload
```
2. **Kind 노드에 필요한 패키지를 설치한다.**
    - Kind 클러스터 세팅 yaml 에는 이 작업에 관련하여 바뀌는건 없음
    - 데몬셋 yaml을 사용해서 각 노드에 필요한 패키지 설치 (nfs-common)
    - 데몬셋은 실행되고 작업을 끝마쳐도 job 오브젝트처럼 종료되지 않고 계속 살아있음
3. **(Pv, pvc, 디플로이먼트 Pod) yaml 작성**
    - pv 서버는 로컬머신 내부 아이피 사용. 아이피 변경 다이나믹하게 해두지 않음. 지금상태에선 관리포인트만 늘어나서..
4. **파일 생성해보고 두 개의 Pod에서 공유파일 확인**
    - 디플로이먼트로 생성한 Pod 하나에 접속해서 nfs 폴더 안에 파일 생성
    - md5sum 으로 파일 해쉬 확인
    - 다른 Pod에 들어가서 해당 파일의 해쉬 확인 -> 위의 해쉬와 같은지 확인