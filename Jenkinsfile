pipeline {
  agent {
    kubernetes {
      yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: gitleaks
    image: zricethezav/gitleaks:latest
    command: [sleep]
    args: [infinity]
  - name: sonar-scanner
    image: sonarsource/sonar-scanner-cli:latest
    command: [sleep]
    args: [infinity]
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command: [sleep]
    args: [infinity]
    volumeMounts:
    - name: docker-config
      mountPath: /kaniko/.docker
  volumes:
  - name: docker-config
    secret:
      secretName: docker-hub-creds
      items:
      - key: .dockerconfigjson
        path: config.json
"""
    }
  }
  stages {
    stage('Analyse des secrets (Gitleaks)') {
      steps {
        container('gitleaks') {
          sh '''
          gitleaks detect --source=${WORKSPACE} --report-format=json --report-path=${WORKSPACE}/gitleaks-report.json --exit-code=0
          '''
        }
        archiveArtifacts artifacts: 'gitleaks-report.json', allowEmptyArchive: true
      }
    }
    stage('Analyse statique du code (SonarCloud)') {
      steps {
        container('sonar-scanner') {
          withCredentials([string(credentialsId: 'sonarcloud-token', variable: 'SONAR_TOKEN')]) {
            sh '''
            sonar-scanner \
              -Dsonar.host.url=https://sonarcloud.io \
              -Dsonar.token=${SONAR_TOKEN}
            '''
          }
        }
      }
    }
    stage('Build et push avec Kaniko') {
      steps {
        container('kaniko') {
          sh '''
          /kaniko/executor \
            --context=dir://${WORKSPACE} \
            --dockerfile=${WORKSPACE}/Dockerfile \
            --destination=riahiamani/devsecops-test:${BUILD_NUMBER}
          '''
        }
      }
    }
  }
}
