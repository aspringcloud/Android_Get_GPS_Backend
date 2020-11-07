pipeline{
    environment{
        SERVERIP = '52.231.51.213'
        SERVERUSER = 'azureuser'
        DEPLOYIP = '52.231.51.213'
        // SERVERSSH = 'azureuser@52.231.51.213'
        SERVERSSH = '$SERVERUSER@$SERVERIP'
        LOCALIMAGE = 'azuremap'
        LOCALIMAGETAG = 'latest'
        AZURECR = 'cwleecr.azurecr.io'
    }
    agent any
    stages{
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
        stage('ssh deploy') {
            steps{
                script{
                    // 작성해둔 젠킨스 크리덴셜 ID를 넣는다
                    withCredentials([usernamePassword( credentialsId: 'DeployServerUser', usernameVariable: 'USER', passwordVariable: 'PASSWORD')]){
                        sh 'sshpass -p $PASSWORD ssh -o StrictHostKeyChecking=no $USER@$DEPLOYIP'
                        script{
                            withCredentials([usernamePassword( credentialsId: 'cwleeazurecr', usernameVariable: 'USER', passwordVariable: 'PASSWORD')]) {
                                // sh 'ssh $SERVERSSH "sudo docker login -u $USER -p $PASSWORD $AZURECR"'
                                sh 'sudo docker login -u $USER -p $PASSWORD $AZURECR'
                            }
                        }
                        sh 'ssh $SERVERSSH "sudo docker pull $AZURECR/$LOCALIMAGE:$LOCALIMAGETAG"'
                        sh 'ssh $SERVERSSH "sudo docker stop test"'
                        sh 'ssh $SERVERSSH "sudo docker run -p 8000:8000 -d --name test --rm $AZURECR/$LOCALIMAGE:$LOCALIMAGETAG"'
                        
                    }
                }
            }
        }
    }
}

