# kafka(not operator), akhq 설치

## 적용과정
operator 사용을 지향하는 분위기여서 오퍼레이터를 쓰려고 했으나, config 조작이나 커스텀이 익숙치 않아서, 좀 더 익숙한 방식으로 관련 툴을 하나하나 설치하면서 config 등을 확인 후 적용 예정
  
  
## 정리

### 1. 기본 CONFIG 정보..
- [bitnami helm values.yaml](https://github.com/bitnami/charts/blob/main/bitnami/kafka/values.yaml)
- [kafka docs](https://kafka.apache.org/documentation/#topicconfigs)
1. **Zookeeper 모드와 KRaft 모드**
    - 설치시 KRaft 모드로 해둠. 
    - 아무래도 주키퍼에 의존성이 걸리면서 생기는 성능, 관리포인트 이슈가 가장 문제였던 것 같고, 이런 이슈들을 제거하기 위해 kraft 를 개발하게 된 것 같다. [[참조1]](https://brunch.co.kr/@peter5236/19)
    - **성능적 이슈**
        - 브로커는 모든 토픽과 파티션에 대한 메타데이터를 주키퍼에서 읽어야 함
            - 메타데이터는 주키퍼에서는 동기적으로 일어나고, 브로커에는 비동기 방식으로 전달됨
                -> 데이터 불일치가 일어날 수 있음
            - 컨트롤러 재시작 시 모든 메타데이터를 주키퍼로부터 읽어야 하는 부담. 토픽과 파티션이 많은 대규모 클러스터일 경우일 수록 시간이 더욱 오래 걸림 (항상 대규모일 때 문제이지..)
    - **관리 이슈**
        - 서로 다른 툴이기 때문에 두 가지의 어플을 운영해야 하는 부담
        - 의존성 때문에 하나가 업데이트 되면 다른 하나도 체크해야 함
        - 모니터링, 이슈 대응도 각각 처리 해야 함
    - **주키퍼-컨트롤러 관계**
        - 주키퍼가 1개의 컨트롤러를 선출 (주키퍼 임시노드에 먼저 연결한 브로커)
        - 선출한 컨트롤러가 파티션 리더 선출 -> 주키퍼에게 전달
    - **Kraft**
        - 카프카 내에서 메타데이터 관리 기능까지 하게 됨
        - 컨트롤러 3개, 그 중 하나가 리더 컨트롤러
        - 리더 컨트롤러는 write 역할 담당
        - 별도 토픽에 메타데이터 기록
        - 리더 컨트롤러가 장애시 알고리즘에 의해 새로운 리더 선출
    - **kraft의 장점**
        - 파티션 리더 선출의 최적화
            - 대량의 파티션에 대한 리더 선출작업은 시간이 소요됨. 이런 부분은 카프카와 클라이언트에 크리티컬할 수 있음
            - 주키퍼에선 이런 지연을 방지하고자 파티션 리미트가 약 20만 
            - kraft에선 이보다 더 많은 파티션 생성 가능
                - 컨트롤러는 메모리 내에 메타데이터 캐시 유지 -> 장애시 복제시간 줄어듦
                - 주키퍼 의존성 없어지면서 메타데이터 동기화와 관리 효율 높아짐

### 2. 보안
- [참조블로그-1](https://choiseokwon.tistory.com/290)
- [참조블로그-2](https://always-kimkim.tistory.com/entry/kafka101-security)
- [컨플루언트 docs](https://docs.confluent.io/platform/current/security/authorization/ldap/configure.html#configure-ldap-authorization)
  
1. **암호화 (encryption)**
    - 데이터 전송 중 ssl/tls를 통한 암호화 (ssl의 개선된 버전-> tls)
2. **인증 (authentication)**
    - SSL / SASL / OAuth/OIDC ...
    - SSL
        - 로그인(아이디/암호) 처럼 인증된 프로듀서/컨슈머에게만 카프카 서버에 접근할 수 있도록 하는 방법
        - SSL 인증서를 이용 : 카프카 클라이언트 -> 카프카 서버 (인증서 확인) -> 클라이언트 허용 혹은 의심
    - SASL
        - PLAINTEXT(약) / SCRAM(강): 클라이언트 아이티/비번을 통한 인증
        - GSSAPI(Kerberos)
3. **인가 (authorization)**
    - ACLs(주로) / RBAC / LDAP
    - ACLs(access control list): 해당 계정이 어떤 권한이 있는지 저장하고 확인하는 방식

#### [관련 이슈 & 삽질] 
1. **akhq, kafka-client 에서 토픽 생성 시도시 생성 안 됨**
- **원인** : 여기서 삽질 지옥이 시작되었는데.. 모든 문제는 authentication 에서 생김ㅜㅜ client-broker 간 설정.. 
- client 에서 토픽 작업시 에러메세지:
    ```
    [2024-07-29 16:37:05,748] INFO [SocketServer listenerType=BROKER, nodeId=0] Failed 
    authentication with /10.244.3.50 (channelId=10.244.1.41:9092-10.244.3.50:49108-819) 
    (Unexpected Kafka request of type METADATA during SASL handshake.) 
    (org.apache.kafka.common.network.Selector)
    ```
- **해결** : `listeners.client.protocol`: `PLAINTEXT`로 변경
- [참조링크 - 관련 포스팅](https://ssnotebook.tistory.com/entry/Kubernetes-bitnamikafka-Helm-Chart-SASL-Authentication-%EC%97%90%EB%9F%AC)
- [참조깃이슈 - client 테스트시 에러](https://github.com/bitnami/charts/issues/18659)
- [참조깃이슈 - controller간 통신 문제 1](https://github.com/bitnami/charts/issues/18793)
- [참조깃이슈 - controller간 통신 문제 2](https://github.com/bitnami/containers/issues/41415#issuecomment-1727256011)
- [bitnami kafka values.yaml](https://github.com/bitnami/charts/blob/main/bitnami/kafka/values.yaml)
  
    ```text
    # [참조깃이슈 - controller간 통신 문제 2] 마지막 코멘트.. 해결되지 않음
    As reported to Kafka, 
    controller-to-controller communications still do not support SCRAM,
    only the PLAIN mechanism is supported.

    Setting KAFKA_CFG_SASL_MECHANISM_CONTROLLER_PROTOCOL=PLAIN should fix the issue 
    until SCRAM support is added for controller-to-controller communications.
    ```
  
2. **ssl 설정**
- 보안 관련하여 `PLAINTEXT`로 변경하면서 적용하지는 않았으나 ssl 설정의 keystore.jks 부분을 찾아보면서 정리해둠
- [참조포스팅 - ssl 적용을 위한 인증서/키 생성법](https://limitrequestbody.com/kafka-ssl-%EC%84%A4%EC%A0%95%ED%95%98%EA%B8%B0-e26d3bd03cbb)
    ```
    # 정리 감사합니다...ㅠㅠ

    java의 keytool을 사용하여 트러스트스토어와 키스토어를 생성하였으며 
    SSL 적용은 

    CA 인증서/키 생성 
    → 트러스트스토어/키스토어 생성 
    → CSR 생성/서명 
    → 키스토어에 인증서 추가 
    → 브로커 Config 설정 
    순으로 진행합니다.
    ```
  
    
### 3. akhq 의 application.yml 적용
- **참조**
    - [akhq docs](https://akhq.io/docs/configuration/authentifications/jwt.html)
    - [akhq application.yaml 샘플](https://github.com/tchiotludo/akhq/blob/dev/application-dev.yml)
- **[실패] application.yml을 작성해서 적용할 수 있는데, 파일로 적용**
    - configmap을 생성한 다음에 akhq 헬름차트에 initcontainer와 볼륨마운트로 파일을 전달하려했으나 Initcontainer에서 계속 에러가 나는 바람에 취소.
    - 초기화컨테이너에 `command: ['sh', '-c', 'cp /config/application.yml /app/application.yml']` 이런 부분이 들어가는데.. /app 도 볼륨마운트해서 앱Pod에 연결했는데 이게 문제였을 것도 같다. helm chart 내에서도 /app을 볼륨마운트 한다던지 해서.. `k logs/describe..`로 로그를 확인할 수 없어서 정확한 실마리를 못 잡고 이 방법은 접었다. ([초기화 컨테이너 디버깅 방법](https://kubernetes.io/ko/docs/tasks/debug/debug-application/debug-init-containers/)도 있는 듯 한데..재현해봐야 하나;)
- **[실패] akhq 이미지에 applcaition.yml을 포함해서 새 이미지를 만들어 적용**
    - 원 akhq 이미지에 application.yml 파일을 추가하는 dockerfile 작성 -> 빌드 & 푸쉬 -> akhq values.yml 수정
    - 되는줄 알았지만..웬걸 akhq pod에 들어가서 파일을 들여다보니..전혀 적용이 되어있지 않았다 ㅋㅋㅋ ㅠ 
    - 처음에는 values.yaml 에 application.yml과 겹치는 설정을 주석처리를 해두지 않았는데 그 부분이 적용되어 있었다; 그 부분을 주석처리해도 어쨋든 application.yml 파일은 적용이 안 되었다.
    - 이미지를 이용해 pod을 띄울 때 서비스에서 작성한 파일로 기존 파일을 덮어쓰기 하는걸로 보였다.
    - 어쩐지 application.yml엔 로그인(basic-auth) 설정도 해두었는데 전혀 적용이 안 되더라니..;
  
- **[성공] values.yaml 의 configuration 부분에 내용 추가**
    - 위에서 작성해둔 application.yml 내용을 붙여넣으니 동작함
    - jwt과 basic-auth 의 secret은 sha256으로 처리해준 값을 넣어줘야 한다.
        - `echo -n "admin" | sha256sum`
  
### 4. External port
- 클러스터 외부에서 kafka 토픽에 메세지를 전달시키기 위해서 설정하였다.
- bitnami에서 설명해둔 대로 values.yml을 세팅했는데..kafka 브로커가 계속 크러쉬백오프가..후.. 그래서 nodeport로 적용하고 Port-forward 해서 사용중.
- 로드밸런서로 설정했을시 부분 왜 안 되는지 확인 필요하다..bitnami 여기 은근 잘못된 게 꽤 있는 것 같다.. 그리고 이슈 해결도 그닥 빠르지 않은 것 같다.
  
### 5. ingress 설정
- 위에서 port-forward가 너무 번거로웠는데 ingress를 공부하면서 akhq, schema-registry 모두 ingress 설정을 true로 해두고 clusterIP에 dns를 연결해두었다(/etc/hosts).
  
### 5. ExtraVolumes, VolumeMounts, ExtraVolumeMounts
- VolumneMount: 리소스 마운트
- ExtraVolumeMount: 
    - 표준 Kubernetes 리소스의 일부가 아니며, 특정 Helm 차트에서 제공하는 추가 설정 옵션. 
    - Helm 차트를 통해 배포 시, 차트 작성자가 미리 정의한 템플릿에 따라 추가적인 볼륨 마운트를 지원하기 위해 사용
    ```
    # Ex
    configmap.yaml 작성:
    ---
    apiVersion: v1
    kind: ConfigMap
    metadata:
    name: akhq-config
    data:
    application.yml: |
        micronaut:
        security:
            token:
            jwt:
                signatures:
                secret:
                    generator:
                    secret: "your-secret-key"
    ---

    # configmap 마운트.. 파일도 마운트 가능
    extraVolumes:
    - name: akhq-config
        configMap:
        name: akhq-config

    - name: app-data
        emptyDir: {}

    extraVolumeMounts:
    - name: akhq-config
        mountPath: /config/application.yml
        subPath: application.yml
    ```