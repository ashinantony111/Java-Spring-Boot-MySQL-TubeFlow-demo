
pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'
        EKS_CLUSTER = 'devops-practice'
        DOCKER_IMAGE = 'ashinantony/tubeflow-app'
        K8S_NAMESPACE = 'default'
    }

    stages {

        stage('Git Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Application Validation') {
            steps {
                sh '''
                    python3 -m compileall -q app run.py
                    echo "Python syntax validation successful"
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                    docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Docker Hub Push') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_TOKEN" | docker login \
                          -u "$DOCKER_USER" --password-stdin

                        docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                        docker push ${DOCKER_IMAGE}:latest

                        docker logout
                    '''
                }
            }
        }

        stage('Configure EKS') {
            steps {
                sh '''
                    aws eks update-kubeconfig \
                      --region ${AWS_REGION} \
                      --name ${EKS_CLUSTER}

                    kubectl get nodes
                '''
            }
        }

        stage('Deploy MySQL') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'mysql-root-password',
                        variable: 'MYSQL_ROOT_PASSWORD'
                    )
                ]) {
                    sh '''
                        kubectl create secret generic mysql-secret \
                          --from-literal=MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD" \
                          --dry-run=client -o yaml | kubectl apply -f -

                        kubectl create configmap mysql-init \
                          --from-file=schema.sql \
                          --dry-run=client -o yaml | kubectl apply -f -

                        cat <<'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_ROOT_PASSWORD
        - name: MYSQL_DATABASE
          value: tubeflow_db
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
        - name: mysql-init
          mountPath: /docker-entrypoint-initdb.d
        readinessProbe:
          tcpSocket:
            port: 3306
          initialDelaySeconds: 15
          periodSeconds: 5
      volumes:
      - name: mysql-data
        emptyDir: {}
      - name: mysql-init
        configMap:
          name: mysql-init
---
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
  type: ClusterIP
EOF

                        kubectl rollout status deployment/mysql \
                          --timeout=180s
                    '''
                }
            }
        }

        stage('Deploy TubeFlow Application') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'mysql-root-password',
                        variable: 'MYSQL_ROOT_PASSWORD'
                    )
                ]) {
                    sh '''
                        cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tubeflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tubeflow
  template:
    metadata:
      labels:
        app: tubeflow
    spec:
      initContainers:
      - name: wait-for-mysql
        image: mysql:8.0
        command:
        - sh
        - -c
        - until mysqladmin ping -h mysql -uroot -p"\\$MYSQL_ROOT_PASSWORD" --silent; do sleep 3; done
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_ROOT_PASSWORD
      containers:
      - name: tubeflow
        image: ${DOCKER_IMAGE}:${BUILD_NUMBER}
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: MYSQL_HOST
          value: mysql
        - name: MYSQL_PORT
          value: "3306"
        - name: MYSQL_USER
          value: root
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_ROOT_PASSWORD
        - name: MYSQL_DB
          value: tubeflow_db
---
apiVersion: v1
kind: Service
metadata:
  name: tubeflow-service
spec:
  selector:
    app: tubeflow
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
EOF

                        kubectl rollout status deployment/tubeflow \
                          --timeout=180s
                    '''
                }
            }
        }

        stage('Deployment Verification') {
            steps {
                sh '''
                    echo "===== PODS ====="
                    kubectl get pods

                    echo "===== SERVICES ====="
                    kubectl get services

                    echo "===== DEPLOYMENTS ====="
                    kubectl get deployments
                '''
            }
        }
    }

    post {
        success {
            echo 'TubeFlow CI/CD Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the Jenkins console output.'
        }
    }
}

