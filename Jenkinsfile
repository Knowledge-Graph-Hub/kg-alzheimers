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
        // AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        // AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
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
                    sh '''
                    # Extract release version from metadata.yaml
                    release_ver=$(grep "kg-version" output/metadata.yaml | cut -d' ' -f2)
                    echo "Creating dated release: ${release_ver}..."
                    
                    # Ensure the files that should be compressed are
                    if [ ! -f output/kg-alzheimers.duckdb.gz ] && [ -f output/kg-alzheimers.duckdb ]; then
                        pigz -f output/kg-alzheimers.duckdb
                    fi
                    
                    if [ ! -f output/kg-alzheimers-denormalized-edges.tsv.gz ] && [ -f output/kg-alzheimers-denormalized-edges.tsv ]; then
                        pigz -f output/kg-alzheimers-denormalized-edges.tsv
                    fi
                    
                    if [ ! -f output/kg-alzheimers-denormalized-nodes.tsv.gz ] && [ -f output/kg-alzheimers-denormalized-nodes.tsv ]; then
                        pigz -f output/kg-alzheimers-denormalized-nodes.tsv
                    fi
                    
                    # Convert the release version for kghub (remove hyphens)
                    kghub_release_ver=$(echo ${release_ver} | tr -d '-')
                    echo "Uploading to kghub: ${kghub_release_ver}..."
                    
                    # Index files locally and upload to s3
                    multi_indexer -v --directory output --prefix https://kghub.io/kg-alzheimers/${kghub_release_ver} -x -u
                    
                    kg_hub_files="output/kg-alzheimers.tar.gz output/rdf/ output/merged_graph_stats.yaml"
                    gsutil -q -m cp -r -a public-read ${kg_hub_files} s3://kg-hub-public-data/kg-alzheimers/${kghub_release_ver}
                    gsutil -q -m cp -r -a public-read ${kg_hub_files} s3://kg-hub-public-data/kg-alzheimers/current
                    
                    # Index files on s3 after upload
                    multi_indexer -v --prefix https://kghub.io/kg-monarch/ -b kg-hub-public-data -r kg-alzheimers -x
                    gsutil -q -m cp -a public-read ./index.html s3://kg-hub-public-data/kg-alzheimers
                    
                    # Clean up files
                    echo "Cleaning up files..."
                    if [ -d "output/${release_ver}" ]; then
                        rm -rf output/${release_ver}
                    fi
                    
                    echo "Successfully uploaded release!"
                    '''
                }
            }
        }
        stage('create github release') {
            steps {
                dir('./gitrepo') {
                    sh 'poetry run python scripts/create_github_release.py --kg-version ${RELEASE}'
                }
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
