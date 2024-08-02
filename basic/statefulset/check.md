# statefulset 실습로그
- 노드 장애시 스테이트풀셋의 상태를 보기 위한 실습이 있음 
    -> 노드 장애가 나더라도 이 부분을 어찌하는건 스테이트풀셋의 역할이 아니기 때문에 
    -> 노드 장애가 나면 -> 노드를 자동 종료시키는 데몬셋을 작성해서 적용하는 내용이 있음
    -> 이를 위해 필요한 작업
        - serviceaccount (서비스 어카운트 정의, 소속된 네임스페이스와 이름)
        - clusterrole (클러스터내 역할 정의)
        - clusterRoleBinding (서비스어카운트 - 클러스터롤 매핑)
        - daemonset 작성 (k8s 클러스터 뒤에서 다양한 백그라운드 일들을 처리해주는 파드의 컨트롤러)
            - 준비된 이미지에서 노드를 감시하다 장애시 종료하는 Python 코드를 dockerfile 로 build
            - daemonset 세팅시 위에 만드어둔 서비스어카운트를 연결시킴
        - 위에서 만든 yml을 모두 배포하고, 노드를 하나 정지시켜서 데몬셋이 잘 동작하는지 확인


## 특징
- 데이터를 보관해야 하는 애플리케이션에 적합한 컨트롤러임
    - 데이터를 분실하지 않도록 설계됨. 
        -> 하드웨어 장애나 네트워크 장애로 특정 노드가 마스터와의 연결이 끊어졌을 떄, 스테이트풀셋은 새로운 POD 기동 안 함
        -> 만약 POD이 살아있는데 새 POD을 기동해서 persistent volume 에 연결되면 데이터가 망가질 수 있기 때문
    - 스테이트풀셋을 만들 때 퍼시스턴트 볼륨도 함꼐 만들어진다. **스테이트풀셋이 지워질 때 퍼시스턴트 볼륨은 안 사라짐**
    - 노드에 장애가 났을 시 데이터 보호하기 위해서 함부로 파드를 다른 노드로 안 옮김. 파드가 죽었다는 확실한 신호가 있지 않은 이상..
    
- 스테이트풀셋 파드에 접근하는 **서비스는 헤드리스 모드** 사용
- 파드에 순차적으로 번호가 붙음
   
   
## deployment 와 statefulset 의 차이
- **디플로이먼트**: 레플리카셋(컨트롤러)로 pod의 갯수를 관리 | **스테이트풀셋**: Pod 갯수와 각 pod에 연결된 스토리지클래스도 관리
- **POD 이름**
    - 스테이트풀셋에 의해 만들어지는 pod의 이름은 스테이트풀셋 이름 뒤에 순서대로 번호가 붙음!
        - my-kafka-controller-0
        - my-kafka-controller-1
        - my-kafka-controller-2
    - 디플로이먼트는 뒤에 해시값이 붙는다.
- **노드 정지시 동작**
    - 디플로이먼트는 노드가 정지되면 다른 노드에 POD을 띄움
    - 스테이트풀셋은 다음의 경우에만 POD을 다른 노드에 재기동함 (POD이나 POD이 속한 노드가 완전히 종료되었다는 시그널이 없으면 계속 놔둔다.)
        - 장애 노드를 클러스터 멤버에서 제거
        - 문제가 있는 파드를 강제 종료
        - 장애로 인해 정지한 노드를 재기동
- **서비스와 연결시 대표 ip 여부**
    - 스테이트풀셋은 파드에 요청을 전송하기 위해 서비스를 연결시 대표 ip를 가지지 않고, clusterIP headless 모드를 사용한다. 
        - (pod의 dns를 부여하여 사용..)
        - pod dns 패턴: `<statefulset_name>-<ordinal>.<service_name>.<namespace>.svc.cluster.local`
            - example-statefulset-0.example-headless.default.svc.cluster.local
            - example-statefulset-1.example-headless.default.svc.cluster.local
            - example-statefulset-2.example-headless.default.svc.cluster.local

