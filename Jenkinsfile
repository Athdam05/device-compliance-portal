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
        EDGE_DRIVER = 'C:\\Users\\damal\\tools\\edgedriver\\msedgedriver.exe'
        TEST_PORT   = '8082'
        REGISTRY       = 'localhost:5000'
        IMAGE_NAME     = 'dcmp'
        APP_VERSION    = "1.0.${BUILD_NUMBER}"
        CONTAINER_NAME = 'dcmp-app'
        DOCKER_PORT    = '8092'
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

        stage('Selenium Tests') {
            // Start the freshly built app on a private port with a throw-away in-memory database,
            // run the browser tests against it and ALWAYS stop it again. A failure here stops the
            // pipeline, so the Deploy stage below is never reached with a broken build.
            steps {
                bat '''
                    if exist selenium.pid del selenium.pid
                    powershell -NoProfile -Command "$p = Start-Process -FilePath '%JAVA_HOME%\\bin\\java.exe' -ArgumentList '-jar','target\\device-compliance-portal-0.1.0-SNAPSHOT.war','--server.port=%TEST_PORT%','--spring.datasource.url=jdbc:h2:mem:seleniumdb' -PassThru -WindowStyle Hidden; $p.Id | Out-File -Encoding ascii selenium.pid"
                '''
                bat '''
                    @echo off
                    set /a tries=0
                    :wait
                    curl -s -f http://localhost:%TEST_PORT%/actuator/health && goto up
                    set /a tries+=1
                    if %tries% GEQ 30 exit /b 1
                    ping -n 3 127.0.0.1 > nul
                    goto wait
                    :up
                    echo.
                    echo Test instance is up on port %TEST_PORT%
                '''
                bat '"%MVN%" -B failsafe:integration-test failsafe:verify -Pselenium -Dbase.url=http://localhost:%TEST_PORT% -Dwebdriver.edge.driver="%EDGE_DRIVER%"'
            }
            post {
                always {
                    junit testResults: 'target/failsafe-reports/*.xml', allowEmptyResults: true
                    archiveArtifacts artifacts: 'target/screenshots/*.png', allowEmptyArchive: true
                    bat '''
                        if exist selenium.pid (
                          for /f %%p in (selenium.pid) do taskkill /F /PID %%p
                          del selenium.pid
                        )
                        exit /b 0
                    '''
                }
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

        // ---- Step 12: continuous deployment with Docker (only reached when every stage above passed) ----
        stage('Docker Build') {
            steps {
                // Versioned image: 1.0.<build number>; "latest" always points at the newest good build
                bat '''
                    docker build --label git.commit=%GIT_COMMIT% -t %REGISTRY%/%IMAGE_NAME%:%APP_VERSION% -t %REGISTRY%/%IMAGE_NAME%:latest .
                    docker image ls %REGISTRY%/%IMAGE_NAME%
                '''
            }
        }

        stage('Docker Push') {
            steps {
                bat '''
                    docker push %REGISTRY%/%IMAGE_NAME%:%APP_VERSION%
                    docker push %REGISTRY%/%IMAGE_NAME%:latest
                    echo Tags now in the registry:
                    curl -s http://%REGISTRY%/v2/%IMAGE_NAME%/tags/list
                '''
            }
        }

        stage('Docker Deploy') {
            steps {
                // Replace the running container with a fresh one created from the image pulled back out of the registry
                bat '''
                    docker rm -f %CONTAINER_NAME% 2>nul
                    docker pull %REGISTRY%/%IMAGE_NAME%:%APP_VERSION%
                    docker run -d --name %CONTAINER_NAME% --restart unless-stopped -p %DOCKER_PORT%:8080 -v dcmp-app-data:/data -e SPRING_PROFILES_ACTIVE=%DEPLOY_ENV% %REGISTRY%/%IMAGE_NAME%:%APP_VERSION%
                    exit /b 0
                '''
                bat '''
                    @echo off
                    set /a tries=0
                    :wait
                    curl -s -f http://localhost:%DOCKER_PORT%/actuator/health && goto ok
                    set /a tries+=1
                    if %tries% GEQ 30 exit /b 1
                    ping -n 4 127.0.0.1 > nul
                    goto wait
                    :ok
                    echo.
                    echo Container %CONTAINER_NAME% is healthy: http://localhost:%DOCKER_PORT%/ ^(image %APP_VERSION%, env=%DEPLOY_ENV%^)
                    docker ps --filter name=%CONTAINER_NAME%
                '''
            }
        }
    }

    post {
        success { echo "Deployed to http://localhost:8081/${params.APP_CONTEXT}/ (env=${params.DEPLOY_ENV})" }
        failure { echo 'Pipeline failed - see stage logs' }
    }
}
