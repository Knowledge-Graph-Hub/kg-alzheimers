#!/bin/bash

echo "kgx transform to rdf"
poetry run kgx transform -i tsv -c tar.gz -f nt -d gz -o output/kg-alzheimers.nt.gz output/kg-alzheimers.tar.gz

echo "Building Neo4j Artifact"
docker rm -f neo || True
mkdir neo4j-v4-data || True
docker run -d --name neo -p7474:7474 -p7687:7687 -v neo4j-v4-data:/data --env NEO4J_AUTH=neo4j/admin neo4j:4.4
poetry run kgx transform --transform-config neo4j-transform.yaml > kgx-transform.log
docker stop neo
docker run -v $(pwd)/output:/backup -v neo4j-v4-data:/data --entrypoint neo4j-admin neo4j:4.4 dump --to /backup/kg-alzheimers.neo4j.dump
