pipeline{
    environment{
        SERVERIP = '52.231.51.213'
        SERVERUSER = 'azureuser'
        SERVERSSH = 'azureuser@52.231.51.213'
        // SERVERSSH = '$SERVERUSER@$SERVERIP'
        LOCALIMAGE = 'azuremap'
        LOCALIMAGETAG = 'latest'
        AZURECR = '$AZURECR'
    }
    agent any
    stages{
        stage('build $LOCALIMAGE:$LOCALIMAGETAG images'){
            steps{
                sh 'docker build -t $LOCALIMAGE:$LOCALIMAGETAG .'
                sh 'echo $SERVERSSH'
            }
        }
    }
}

