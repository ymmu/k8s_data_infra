# kafka(not operator), akhq 설치

## 적용과정
operator 사용을 지향하는 분위기여서 오퍼레이터를 쓰려고 했으나, config 조작이나 커스텀이 익숙치 않아서, 좀 더 익숙한 방식으로 관련 툴을 하나하나 설치하면서 config 등을 확인 후 적용 예정




---
  
## 정리

### 1. 기본 CONFIG

### 2. 보안
카프카의 보안사항은 3가지로 볼 수 있다.
1. 암호화 (encryption)
2. 인증 (authentication)
3. 인가 (authorization) 

#### [관련 이슈 & 삽질] 
1. **akhq, kafka-client 에서 토픽 생성 시도시 생성 안 됨**
- **원인** : 
    - 여기서 삽질 지옥이 시작되었는데.. 모든 문제는 authentication 에서 생김ㅜㅜ client-broker 간 설정.. 
- **해결** : `listeners.client.protocol`: `PLAINTEXT`로 변경
- [참조링크 - 관련 포스팅](https://ssnotebook.tistory.com/entry/Kubernetes-bitnamikafka-Helm-Chart-SASL-Authentication-%EC%97%90%EB%9F%AC)
- [참조깃이슈 - client 테스트시 에러](https://github.com/bitnami/charts/issues/18659)
- [참조깃이슈 - controller간 통신 문제 1](https://github.com/bitnami/charts/issues/18793)
- [참조깃이슈 - controller간 통신 문제 2](https://github.com/bitnami/containers/issues/41415#issuecomment-1727256011)
  
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
- 

  
  
### 3. akhq 의 application.yml 적용
- **[실패] application.yml을 작성해서 적용할 수 있는데, 파일로 적용**
    - configmap을 생성한 다음에 akhq 헬름차트에 initcontainer와 볼륨마운트로 파일을 전달하려했으나 Initcontainer에서 계속 에러가 나는 바람에 취소.
    - 초기화컨테이너에 `command: ['sh', '-c', 'cp /config/application.yml /app/application.yml']` 이런 부분이 들어가는데 아마..저 /app 폴더가 있기 전이라 그랬을까;; `k logs/describe..`로 로그를 확인할 수 없어서 정확한 실마리를 못 잡고 이 방법은 접었다.
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

