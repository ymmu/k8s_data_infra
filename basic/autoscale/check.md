# autoscale 실습시 체크사항

- 오토스케일은 cpu 와 메모리 사용츌에 따라 파드나 노드의 수를 자동으로 늘리고 줄이는 기능
- 퍼블릭 클라우드 -> 노드의 개수, 이용 시간에 따라 비용 발생하므로 관리 필요
- 온프렘 -> 제한된 서버 활용 필요 (ex. 업무시간대는 사용자 요청 처리하는 파드 비중 높이고, 심야 시간대에는 배치 처리를 수행하는 파드의 비중을 높이기)
- **오토스케일 프로젝트**
    - **수평 파드 오토스케일러 (Horizontal Pod Autoscaler, HPA)**
        - 파드의 cpu 사용률에 따라 파드 수를 자동 조절
            - 루프를 돌면서 대상 파드의 cpu 사용률을 정기적으로 수집
            - 파드의 cpu 사용률의 평균을 목표값이 되도록 레플리카 수 조절 (minReplica <= replicas <=MaxReplicas)
            - 파드 수 = 소수점 값을 올려 정수(파드들의 cpu 사용률 총합 / 목표 cpu 사용률)
            - 파드의 레플리카 수를 설정하는 간격은 기본적으로 30초
                - 설정: `-- horizontal-pod-autoscaler-sync-period`
                - 퍼블릭 클라우드에서는 일반 유저가 변경할 수 없음
        - 노드 수를 늘릴 수는 없음
        - 각 노드의 가용 자원 현황을 파악해서 최대 스케줄 가능한 파드 수를 미리 검토해 두는 것이 좋음 (노드 자원만큼만 파드 생성 가능)
    - **클러스터 오토스케일러 (Cluster Autoscaler, CA)**
        - 클라우드의 api 와 연동하여 노드를 늘리거나 줄여 비용 절약 가능
      
   
## kind 클러스터에서 Pod metric 관찰
```bash
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo update
helm install metrics-server metrics-server/metrics-server --namespace kube-system --set args={--kubelet-insecure-tls}

```
   
## 프로메테우스 설치
- cli도 있지만 프로메테우스가 생각나서 이 것도 설치해보자
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace

# 초기 아이디/비번
admin/prom-operator
```
   
   
## EKS 에서 HPA 테스트
- 이를 위해서 EKS 클러스터 생성 -> 딴 곳에 정리