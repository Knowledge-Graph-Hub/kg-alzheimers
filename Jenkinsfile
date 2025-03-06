pipeline {
    agent {
        docker {
            reuseNode false
            image 'caufieldjh/kg-hub-3_10:2'
        }
    }
    environment {
        HOME = "${env.WORKSPACE}"
        RELEASE = sh(script: "echo `date +%Y-%m-%d`", returnStdout: true).trim()
        BUILD_TIMESTAMP = sh(script: "echo `date +%s`", returnStdout: true).trim()
        PATH = "/opt/poetry/bin:${env.PATH}"
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        GH_RELEASE_TOKEN = credentials('GH_RELEASE_TOKEN')
    }
    options {
        timestamps()
        disableConcurrentBuilds()
    }
    stages {
        stage('setup') {
            steps {
                sh '''
                    echo "Current directory: \\$(pwd)"
                    echo "Path: $PATH"

                    python3 --version
                    pip --version
                    poetry --version

                    poetry install --with dev
                    poetry run which ingest
                '''
            }
        }
        stage('download') {
            steps {
                sh '''
                    mkdir data || true
                    gsutil -q -m cp -r gs://monarch-ingest-data-cache/* data/
                    ls -lafs
                    ls -la data
                '''
            }
        }
        stage('post-process') {
            steps {
                sh '''
                    scripts/after_download.sh
                '''
            }
        }
        stage('transform') {
            steps {
                sh 'poetry run ingest transform --all --log --rdf --write-metadata'
                sh '''
                   sed -i.bak 's@\r@@g' output/transform_output/*.tsv
                   rm output/transform_output/*.bak
                '''
                sh '''
                  gunzip output/rdf/*.gz
                  sed -i.bak 's@\\r@@g' output/rdf/*.nt
                  rm output/rdf/*.bak
                  gzip output/rdf/*.nt
                '''
            }
        }
        stage('merge') {
            steps {
                sh 'poetry run ingest merge'
            }
        }
        stage('upload files') {
            steps {
                sh 'poetry run ingest release --kghub'
            }
        }
        stage('create github release') {
            steps {
                sh 'poetry run python scripts/create_github_release.py --kg-version ${RELEASE}'
            }
        }
    }
    post {
        always {
            echo 'Cleaning workspace...'
            cleanWs()
        }
        success {
            echo 'Success!'
        }
        unstable {
            echo 'Build unstable'
        }
        failure {
            echo 'haz fail oh noes'
        }
        changed {
            echo 'A change has happened'
        }
    }
}
