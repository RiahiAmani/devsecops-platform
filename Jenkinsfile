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
          gitleaks detect --source=${WORKSPACE} --report-format=json \
            --report-path=${WORKSPACE}/gitleaks-report.json --redact
          '''
        }
        archiveArtifacts artifacts: 'gitleaks-report.json', allowEmptyArchive: true
      }
    }
    stage('Analyse statique du code (SonarCloud)') {
      steps {
        container('sonar-scanner') {
          withSonarQubeEnv('SonarCloud') {
            sh '''
            sonar-scanner \
              -Dsonar.host.url=${SONAR_HOST_URL} \
              -Dsonar.token=${SONAR_AUTH_TOKEN}
            '''
          }
        }
      }
    }
    stage('Quality Gate') {
      steps {
        timeout(time: 5, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true
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
            --destination=riahiamani/devsecops-test:${BUILD_NUMBER} \
            --push-retry=3
          '''
        }
      }
    }
  }
}
