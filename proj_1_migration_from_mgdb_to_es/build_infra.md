# 인프라 빌드

## 1. Helm chart 다운로드 

### MongoDB
```bash
# mongodb
helm repo add mongodb https://mongodb.github.io/helm-charts
helm repo update
helm pull mongodb/community-operator --untar --untardir .
helm install mongodb-operator ./mongodb/community-operator -f ./mongodb/community-operator/values-apply.yaml
```
  
### Jenkins
```bash

helm repo add jenkins https://charts.jenkins.io
helm repo update
helm pull jenkins/jenkins --untar --untardir ./jenkins
helm install jenkins jenkins/jenkins -f ./jenkins/values-apply.yaml
helm upgrade jenkins jenkins/jenkins -f ./jenkins/values-apply.yaml

# jenkins: 
# 8080번호는 너무 흔해서 8090으로 변경하여 포트포워딩
k --namespace default port-forward svc/jenkins 8090:8090
# 비번조회
k exec --namespace default -it svc/jenkins -c jenkins -- /bin/cat /run/secrets/additional/chart-admin-password && echo
# 아이디는 뭐냐: admin
k exec --namespace default -it svc/jenkins -c jenkins -- /bin/cat /run/secrets/additional/chart-admin-username && echo
``` 

jenkins 배포시 로그
```bash
Release "jenkins" has been upgraded. Happy Helming!
NAME: jenkins
LAST DEPLOYED: Sun Jul 14 19:25:30 2024
NAMESPACE: default
STATUS: deployed
REVISION: 2
NOTES:
1. Get your 'admin' user password by running:
  kubectl exec --namespace default -it svc/jenkins -c jenkins -- /bin/cat /run/secrets/additional/chart-admin-password && echo
2. Get the Jenkins URL to visit by running these commands in the same shell:
  echo http://127.0.0.1:8090
  kubectl --namespace default port-forward svc/jenkins 8090:8090

3. Login with the password from step 1 and the username: admin
4. Configure security realm and authorization strategy
5. Use Jenkins Configuration as Code by specifying configScripts in your values.yaml file, see documentation: http://127.0.0.1:8090/configuration-as-code and examples: https://github.com/jenkinsci/configuration-as-code-plugin/tree/master/demos

For more information on running Jenkins on Kubernetes, visit:
https://cloud.google.com/solutions/jenkins-on-container-engine

For more information about Jenkins Configuration as Code, visit:
https://jenkins.io/projects/jcasc/


NOTE: Consider using a custom image with pre-installed plugins
```
  

### Kafka & AKHQ & schema registry
- 참조: https://github.com/banzaicloud/koperator/tree/master/charts/kafka-operator
- 테스트용 카프카오퍼레이터 + 카프카 + 카프카 토픽 설치
- 테스트로 컨슈머/프로듀서 팟을 띄우고는 실시간 메세지확인 하려 했더니 cpu 먹통..;;;
- akhq 서비스로 띄울 때 namespace=kafka 에사 8080 포트로 띄웠을 때 에러..port를 변경했는데 잘 안되서 다시 확인 필요 
- akhq application.yaml 설정 추가 필요
```bash
helm repo add banzaicloud-stable https://kubernetes-charts.banzaicloud.com 
helm repo update  
helm pull banzaicloud-stable/kafka-operator --untar --untardir ./kafka
helm install kafbka-operator . -f values.yaml

```

```bash
# values.yaml은 git에서 복사해서 폴더에 생성
helm repo add akhq https://akhq.io/   
helm repo update


```