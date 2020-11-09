pipeline{
    environment{
        SERVERIP = '52.231.51.213'
        SERVERUSER = 'azureuser'
        DEPLOYIP = '52.231.51.213'
        LOCALIMAGE = 'azuremap'
        LOCALIMAGETAG = 'latest'
        AZURECR = 'cwleecr.azurecr.io'
    }
    agent any
    stages{
        stage('build $LOCALIMAGE:$LOCALIMAGETAG images'){
            steps{
                sh 'sudo docker build -t $LOCALIMAGE:$LOCALIMAGETAG .'
            }
        }
        stage('docker push to azurecr'){
            steps {
                script{
                    // 작성해둔 젠킨스 크리덴셜 ID를 넣는다
                    withCredentials([usernamePassword( credentialsId: 'cwleeazurecr', usernameVariable: 'USER', passwordVariable: 'PASSWORD')]){
                        sh "sudo docker login -u $USER -p $PASSWORD $AZURECR"
                        sh "sudo docker tag $LOCALIMAGE:$LOCALIMAGETAG $AZURECR/$LOCALIMAGE:$LOCALIMAGETAG"
                        sh "sudo docker push $AZURECR/$LOCALIMAGE:$LOCALIMAGETAG"
                    }
                }
            }
        }
        stage('Remove prune docker images'){
            steps{
                sh 'docker image prune'
            }
        }
        stage('ssh deploy') {
            steps{
                script{
                    // 작성해둔 젠킨스 크리덴셜 ID를 넣는다
                    withCredentials([usernamePassword( credentialsId: 'DeployServerUser', usernameVariable: 'USER', passwordVariable: 'PASSWORD')]){
                        sh 'sshpass -p $PASSWORD ssh -o StrictHostKeyChecking=no $USER@$DEPLOYIP'
                        docker container prune --filter 'NAME=cwleecr.azurecr.io/azuremap'
                        script{
                            withCredentials([usernamePassword( credentialsId: 'cwleeazurecr', usernameVariable: 'CRUSER', passwordVariable: 'CRPASSWORD')]) {
                                // sh 'ssh $SERVERUSER@$SERVERIP "sudo docker login -u $USER -p $PASSWORD $AZURECR"'
                                sh 'sshpass -p $PASSWORD ssh $USER@$DEPLOYIP "sudo docker login -u $CRUSER -p $CRPASSWORD $AZURECR"'
                            }
                        }
                        sh 'sshpass -p $PASSWORD ssh $USER@$DEPLOYIP "sudo docker pull $AZURECR/$LOCALIMAGE:$LOCALIMAGETAG"'
                        withCredentials([string(credentialsId: 'mygittoken', variable: 'SECRET')]) { //set SECRET with the credential content
                            sh 'sshpass -p $PASSWORD ssh $USER@$DEPLOYIP "curl -s https://alphanewbie:${SECRET}@raw.githubusercontent.com/Alphanewbie/azuremap/master/docker-compose.yml > docker-compose.yml"'
                        }
                        // sh 'sshpass -p $PASSWORD ssh $USER@$DEPLOYIP "sudo docker run -p 8000:8000 -d -it -v /home/azureuser/Documents/YMLdir:/code/YMLdir --name test $AZURECR/$LOCALIMAGE:$LOCALIMAGETAG"'
                        sh 'sshpass -p $PASSWORD ssh $USER@$DEPLOYIP "sudo docker-compose up -d"'
                        sh 'sshpass -p $PASSWORD ssh $USER@$DEPLOYIP "sudo docker rmi $(sudo docker images $AZURECR/$LOCALIMAGE -f dangling=true -q)"'
                        sh 'sshpass -p $PASSWORD ssh $USER@$DEPLOYIP "sudo docker image prune"'
                    }
                }
            }
        }
        stage('test') {
            steps{
                script{
                    withCredentials([usernamePassword( credentialsId: 'DeployServerUser', usernameVariable: 'USER', passwordVariable: 'PASSWORD')]){
                        sh 'sshpass -p $PASSWORD ssh -o StrictHostKeyChecking=no $USER@$DEPLOYIP'
                        sh 'docker ps -a > dock.txt'
                    }
                }
            }
        }
    }
}

