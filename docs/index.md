# KG-Alzheimers

## Overview

KG-Alzheimers generates [KGX](https://github.com/biolink/kgx/blob/master/specification/kgx-format.md) formatted files conforming to the [BioLink Model](https://biolink.github.io/biolink-model/) from a wide variety of biomedical data sources focused on Alzheimer's disease.

The eventual output of the KG-Alzheimers process is the **Alzheimer's Knowledge Graph**.  
The latest version can be found at [kghub.io](https://kghub.io/kg-alzheimers/current/).

KG-Alzheimers is built using [Poetry](https://python-poetry.org), which will create its own virtual environment.

## Installation

kg-alzheimers is a Python 3.8+ package, installable via [Poetry](https://python-poetry.org).  

1. <a href="https://python-poetry.org/docs/" target="_blank">Install Poetry</a>, if you don't already have it:  
```bash
curl -sSL https://install.python-poetry.org | python3 -

# Optional: Have poetry create its venvs in your project directories
poetry config virtualenvs.in-project true
```

1. Clone the repo and build the code:
```bash
git clone git@github.com:Knowledge-Graph-Hub/kg-alzheimers.git
```

1. Install kg-alzheimers:
```bash
cd kg-alzheimers
poetry install
```

1. (Optional) Activate the virtual environment:
```bash
# This step removes the need to prefix all commands with `poetry run`
poetry shell
```

## Usage

For a detailed tutorial on ingests and how to make one, see the [Create an Ingest tab](Create-an-Ingest/index.md).

CLI usage is available in the [CLI tab](CLI.md), or by running `ingest --help`.

??? tip "Run the whole pipeline!"
    - Download the source data:
    ```bash
    ingest download --all
    ```

    - Run all transforms:  
    ```bash
    ingest transform --all
    ```

    - Merge all transformed output into a tar.gz containing one node and one edge file
    ```bash
    ingest merge
    ```

    - (Optional) Generate closure-enriched denormalized tables and prepare release artifacts
    ```bash
    ingest closure
    ingest prepare-release
    ```

    - (CI only) Artifact publication to S3 is automated by Jenkins (`Jenkinsfile`); the
      local `ingest release` command now emits a deprecation notice.

<meta http-equiv='cache-control' content='no-cache'> 
<meta http-equiv='expires' content='0'> 
<meta http-equiv='pragma' content='no-cache'>
