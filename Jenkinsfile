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
  - name: trivy
    image: aquasec/trivy:latest
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
              -Dsonar.token=${SONAR_TOKEN} \
              -Dsonar.qualitygate.wait=true \
              -Dsonar.qualitygate.timeout=300
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
    stage('Scan de vulnérabilités de l\\'image (Trivy)') {
      steps {
        container('trivy') {
          sh '''
          trivy image \
            --severity HIGH,CRITICAL \
            --format json \
            --output trivy-report.json \
            --exit-code 0 \
            riahiamani/devsecops-test:${BUILD_NUMBER}
          '''
          sh '''
          trivy image \
            --severity HIGH,CRITICAL \
            --format table \
            --exit-code 0 \
            riahiamani/devsecops-test:${BUILD_NUMBER}
          '''
        }
        archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
      }
    }
  }
}
