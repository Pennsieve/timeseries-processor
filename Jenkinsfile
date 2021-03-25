#!groovy
try {
  node('executor') {
    checkout scm

    def authorName  = sh(returnStdout: true, script: 'git --no-pager show --format="%an" --no-patch')
    def commitHash  = sh(returnStdout: true, script: 'git rev-parse HEAD | cut -c-7').trim()
    def imageTag    = "${env.BUILD_NUMBER}-${commitHash}"

    env.IMAGE_TAG = imageTag
    env.AUTHOR_NAME = authorName
  
    stage("Test") {
      withCredentials([usernamePassword(
        credentialsId: "pennsieve-nexus-ci-login",
        usernameVariable: "PENNSIEVE_NEXUS_USER",
        passwordVariable: "PENNSIEVE_NEXUS_PW"
      )]) {
        sh """make test"""
      }
    }
    
    if (env.BRANCH_NAME == "main") {
      def allProcessors = sh(returnStdout: true, script: 'cat docker-compose*yml | egrep "_(processor|exporter):" | sed \'s/\\://g\' | sed \'s/_/-/g\' | sort | uniq | xargs').split()

      stage("Build Image") {
        withCredentials([usernamePassword(
          credentialsId: "pennsieve-nexus-ci-login",
          usernameVariable: "PENNSIEVE_NEXUS_USER",
          passwordVariable: "PENNSIEVE_NEXUS_PW"
        )]) {
          sh "IMAGE_TAG=${env.IMAGE_TAG} make build"
          sh "IMAGE_TAG=latest make build"
        }
      }

      stage("Push Image") {
        sh "IMAGE_TAG=${env.IMAGE_TAG} make push"
        sh "IMAGE_TAG=latest make push"
      }

      stage("Deploy") {
        allProcessors.each { proc ->
          build job: "service-deploy/pennsieve-non-prod/us-east-1/dev-vpc-use1/dev/${proc}",
            parameters: [
            string(name: 'IMAGE_TAG', value: env.IMAGE_TAG),
            string(name: 'TERRAFORM_ACTION', value: 'apply')
          ]
        }
      }

    }
  }
  slackSend(color: '#006600', message: "SUCCESSFUL: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL}) by ${env.AUTHOR_NAME}")
} catch (e) {
  slackSend(color: '#b20000', message: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL}) by ${env.AUTHOR_NAME}")
  throw e
}
