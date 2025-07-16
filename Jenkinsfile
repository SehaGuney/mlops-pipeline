pipeline {
  agent any
  stages {
    stage('Checkout') {
      steps {
        git url: 'https://github.com/SehaGuney/mlops-pipeline.git', branch: 'main', credentialsId: 'github-creds'
      }
    }
    stage('Build') {
      steps {
        echo 'Building...'
        // docker.build vs. adımları buraya ekle
      }
    }
  }
}
