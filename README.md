# Building a data infra on k8s

### 작업 배경
- 데이터 엔지니어링 작업을 하면서 k8s로 관리되던 데이터 인프라는 sre팀에 의존하여 관리해왔으나, 실무에서는 데이터 엔지니어도 k8s에 대한 이해도도 요구하는 상황
- k8s 이해도를 높여 인프라 구축 부분에도 타팀에 의존도를 낮추고, 다양한 데이터 엔지니어링 시도에 좀 더 자유로워질 수 있고자 함..! 

### 목표 (원하는 아웃풋)
조금씩 추가/수정될 듯.
1. k8s에 데이터 인프라 구축
    - 현 목표는 인프라 **"구축"** 에 있으므로.. 고도화는 나중에 

    - (기본) 람다 아키텍처와 같은 배치/스트리밍/서빙 작업을 모두 할 수 있는 환경 (airflow, kafka, spark, bigquery,...)
    - 통합 거버넌스 환경 (datahub,,)
    - 엔지니어링이 주업무가 아닌 데이터 관련팀의 작업을 도울 수 있는 환경 (dbt ?)




### Steps
러프한 계획. 작업하면서 추가/수정될 듯.
1. k8s 기본 지식, helm 실습
2. 인프라 구축 
    - [[data infra on k8s] argocd+gitops 세팅 (1)](https://www.notion.so/ymmu/39cf374c9c2e4c6693992847414f83f4?v=cb824b080a4a41e19626bcef159aecfc&p=1330adbc6aa245c1822bb45f521cb2b8&pm=s)
    - [[data infra on k8s] app of apps 패턴 적용해서 data infra 구축 (2)](https://www.notion.so/ymmu/data-infra-on-k8s-app-of-apps-data-infra-2-a2355112030540319c2686e58a06f6d1?pvs=4)
    - [[data infra on k8s] 쿠버네티스 리소스 관리 정리 (3)](https://www.notion.so/ymmu/data-infra-on-k8s-3-bb0fac393fd84685a325a84b6154dba1?pvs=4)
3. 간단한 테스트용 유사? 서비스 인프라 생성 (스트리밍, 배치 작업 테스트)
  
  