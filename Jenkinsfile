// Step 8 - Pipeline as Code: checkout -> build -> package -> deploy to Tomcat.
// Runs on the local Jenkins node (Windows). Tool locations are parameters/env so they can be changed in one place.
pipeline {
    agent any

    parameters {
        // Parameterised environment setting: selects the Spring profile (application-<env>.properties)
        choice(name: 'DEPLOY_ENV', choices: ['dev', 'qa'], description: 'Target environment / Spring profile')
        string(name: 'APP_CONTEXT', defaultValue: 'dcmp', description: 'Tomcat context path for the WAR')
    }

    environment {
        JAVA_HOME   = 'C:\\Program Files\\Eclipse Adoptium\\jdk-11.0.32.101-hotspot'
        MVN         = 'C:\\Users\\damal\\tools\\apache-maven-3.9.9\\bin\\mvn.cmd'
        TOMCAT_HOME = 'C:\\Users\\damal\\tools\\apache-tomcat-9.0.98'
        CATALINA_HOME = "${TOMCAT_HOME}"
        CATALINA_PID_DIR = "${TOMCAT_HOME}\\temp"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                bat 'git log --oneline -1'
            }
        }

        stage('Build') {
            steps {
                bat '"%MVN%" -B clean package'
            }
            post {
                always {
                    junit 'target/surefire-reports/*.xml'
                }
            }
        }

        stage('Package') {
            steps {
                // Version the artefact with the Jenkins build number
                bat 'copy /Y target\\device-compliance-portal-0.1.0-SNAPSHOT.war target\\%APP_CONTEXT%.war'
                archiveArtifacts artifacts: 'target/*.war', fingerprint: true
            }
        }

        stage('Deploy') {
            steps {
                // 1. Tell Tomcat which environment (Spring profile) to run with
                bat '''
                    > "%TOMCAT_HOME%\\bin\\setenv.bat" echo set "JAVA_HOME=%JAVA_HOME%"
                    >> "%TOMCAT_HOME%\\bin\\setenv.bat" echo set "JAVA_OPTS=-Dspring.profiles.active=%DEPLOY_ENV%"
                '''
                // 2. Stop Tomcat if it is running (ignore errors when it is already stopped)
                bat '''
                    call "%TOMCAT_HOME%\\bin\\shutdown.bat"
                    ping -n 8 127.0.0.1 > nul
                    exit /b 0
                '''
                // 3. Replace the deployed application
                bat '''
                    if exist "%TOMCAT_HOME%\\webapps\\%APP_CONTEXT%" rmdir /S /Q "%TOMCAT_HOME%\\webapps\\%APP_CONTEXT%"
                    copy /Y target\\%APP_CONTEXT%.war "%TOMCAT_HOME%\\webapps\\%APP_CONTEXT%.war"
                '''
                // 4. Start Tomcat detached so the Jenkins build can finish
                bat '''
                    set "BUILD_ID=dontKillMe"
                    set "JENKINS_NODE_COOKIE=dontKillMe"
                    start "tomcat" /B cmd /c ""%TOMCAT_HOME%\\bin\\catalina.bat" run > "%TOMCAT_HOME%\\logs\\jenkins-run.log" 2>&1"
                    exit /b 0
                '''
            }
        }

        stage('Verify') {
            steps {
                // Wait for the app to come up, then check health
                bat '''
                    @echo off
                    set /a tries=0
                    :wait
                    curl -s -f http://localhost:8081/%APP_CONTEXT%/actuator/health && goto ok
                    set /a tries+=1
                    if %tries% GEQ 30 exit /b 1
                    ping -n 4 127.0.0.1 > nul
                    goto wait
                    :ok
                    echo.
                    echo Deployed: http://localhost:8081/%APP_CONTEXT%/ ^(env=%DEPLOY_ENV%^)
                '''
            }
        }
    }

    post {
        success { echo "Deployed to http://localhost:8081/${params.APP_CONTEXT}/ (env=${params.DEPLOY_ENV})" }
        failure { echo 'Pipeline failed - see stage logs' }
    }
}
