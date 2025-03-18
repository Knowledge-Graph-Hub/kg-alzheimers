pipeline {
    agent {
        docker {
            reuseNode false
            image 'caufieldjh/kg-hub-3_10:4'
        }
    }
    environment {
        HOME = "${env.WORKSPACE}"
        RELEASE = sh(script: "echo `date +%Y-%m-%d`", returnStdout: true).trim()
        BUILD_TIMESTAMP = sh(script: "echo `date +%s`", returnStdout: true).trim()
        PATH = "/usr/local/bin/:${env.PATH}"
        POETRY_CACHE_DIR="~/.cache/pypoetry"
        // AWS credentials are handled in the withCredentials block in the upload stage
        // AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        // AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        // AWS_CLOUDFRONT_DISTRIBUTION_ID = credentials('AWS_CLOUDFRONT_DISTRIBUTION_ID')
        // Comment out until the credential is set up in Jenkins
        // GH_RELEASE_TOKEN = credentials('GH_RELEASE_TOKEN')
    }
    options {
        timestamps()
        disableConcurrentBuilds()
    }
    stages {
        stage('setup') {
            steps {
                dir('./gitrepo') {
                    git(
                            url: 'https://github.com/Knowledge-Graph-Hub/kg-alzheimers',
                            branch: env.BRANCH_NAME
                    )
                    sh 'echo "Current directory: \\$(pwd)"'
                    sh 'echo "Path: $PATH"'
                    sh 'python3 --version'
                    sh 'pip --version'

                    sh 'id'
                    sh 'whoami' //should be jenkinsuser

                    sh 'which poetry'
                    sh 'poetry --version'
                    sh 'poetry config cache-dir'
                    sh 'poetry config virtualenvs.in-project true'
                    sh 'poetry -v install'
                    sh 'poetry run which ingest'
                }
            }
        }
        stage('download') {
            steps {
                dir('./gitrepo') {
                    sh 'poetry run ingest download --all --write-metadata'
                }
            }
        }
        stage('post-process') {
            steps {
                dir('./gitrepo') {
                    sh 'scripts/after_download.sh'
                }
            }
        }
        stage('transform') {
            steps {
                dir('./gitrepo') {
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
        }
        stage('merge') {
            steps {
                dir('./gitrepo') {
                    sh 'poetry run ingest merge'
                }
            }
        }
        stage('upload files') {
            steps {
                dir('./gitrepo') {
                    script {
                        // Extract release version from metadata.yaml
                        def release_ver = sh(script: "grep 'kg-version' output/metadata.yaml | cut -d' ' -f2", returnStdout: true).trim()
                        echo "Creating dated release: ${release_ver}"

                        // Convert the release version for kghub (remove hyphens)
                        def kghub_release_ver = release_ver.replaceAll("-", "")
                        echo "Uploading to kghub: ${kghub_release_ver}"

                        // Ensure files that should be compressed are
                        sh '''
                            if [ ! -f output/kg-alzheimers.duckdb.gz ] && [ -f output/kg-alzheimers.duckdb ]; then
                                pigz -f output/kg-alzheimers.duckdb
                            fi

                            if [ ! -f output/kg-alzheimers-denormalized-edges.tsv.gz ] && [ -f output/kg-alzheimers-denormalized-edges.tsv ]; then
                                pigz -f output/kg-alzheimers-denormalized-edges.tsv
                            fi

                            if [ ! -f output/kg-alzheimers-denormalized-nodes.tsv.gz ] && [ -f output/kg-alzheimers-denormalized-nodes.tsv ]; then
                                pigz -f output/kg-alzheimers-denormalized-nodes.tsv
                            fi
                        '''

                        // Index files locally
                        sh "multi_indexer -v --directory output --prefix https://kghub.io/kg-alzheimers/${kghub_release_ver} -x -u"

                        // Upload to S3 bucket using s3cmd
                        withCredentials([
                            file(credentialsId: 's3cmd_kg_hub_push_configuration', variable: 'S3CMD_CFG'),
                            file(credentialsId: 'aws_kg_hub_push_json', variable: 'AWS_JSON'),
                            string(credentialsId: 'aws_kg_hub_access_key', variable: 'AWS_ACCESS_KEY_ID'),
                            string(credentialsId: 'aws_kg_hub_secret_key', variable: 'AWS_SECRET_ACCESS_KEY')
                        ]) {
                            // Upload to dated release folder
                            sh "s3cmd -c \$S3CMD_CFG put -pr --acl-public --cf-invalidate output/kg-alzheimers.tar.gz output/merged_graph_stats.yaml s3://kg-hub-public-data/kg-alzheimers/${kghub_release_ver}/"

                            // Remove current directory and update with latest content
                            sh "s3cmd -c \$S3CMD_CFG rm -r s3://kg-hub-public-data/kg-alzheimers/current/ || true"
                            sh "s3cmd -c \$S3CMD_CFG put -pr --acl-public --cf-invalidate output/kg-alzheimers.tar.gz output/rdf/ output/merged_graph_stats.yaml s3://kg-hub-public-data/kg-alzheimers/current/"

                            // Index files on S3
                            sh "multi_indexer -v --prefix https://kghub.io/kg-alzheimers/ -b kg-hub-public-data -r kg-alzheimers -x"
                            sh "s3cmd -c \$S3CMD_CFG put -pr --acl-public --cf-invalidate ./index.html s3://kg-hub-public-data/kg-alzheimers/"

                            // Invalidate CloudFront cache
                            sh '''
                                echo "[preview]" > ./awscli_config.txt
                                echo "cloudfront=true" >> ./awscli_config.txt
                            '''
                            echo "Skipping CloudFront invalidation until AWS_CLOUDFRONT_DISTRIBUTION_ID credential is set up"
                            // sh "AWS_CONFIG_FILE=./awscli_config.txt aws cloudfront create-invalidation --distribution-id \$AWS_CLOUDFRONT_DISTRIBUTION_ID --paths \"/*\""
                        }

                        // Clean up files
                        sh """
                            echo "Cleaning up files..."
                            if [ -d "output/${release_ver}" ]; then
                                rm -rf output/${release_ver}
                            fi
                            echo "Successfully uploaded release!"
                        """
                    }
                }
            }
        }
        stage('create github release') {
            steps {
                dir('./gitrepo') {
                    echo 'Skipping GitHub release creation until GH_RELEASE_TOKEN credential is set up'
                    // sh 'poetry run python scripts/create_github_release.py --kg-version ${RELEASE}'
                }
            }
        }
    }
    post {
        always {
            echo 'Cleaning workspace completed.'
            // Removed cleanWs step as it's causing issues in this environment
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
