#!/bin/bash

rm output/kg-alzheimers.db || true
echo "Decompressing tsv files..."
tar zxf output/kg-alzheimers.tar.gz -C output
gunzip output/qc/kg-alzheimers-dangling-edges.tsv.gz
gunzip output/kg-alzheimers-denormalized-edges.tsv.gz

echo "Loading nodes..."
sqlite3 -cmd ".mode tabs" output/kg-alzheimers.db ".import output/kg-alzheimers_nodes.tsv nodes"
echo "Loading edges..."
sqlite3 -cmd ".mode tabs" output/kg-alzheimers.db ".import output/kg-alzheimers_edges.tsv edges"
echo "Loading dangling edges..."
sqlite3 -cmd ".mode tabs" output/kg-alzheimers.db ".import output/qc/kg-alzheimers-dangling-edges.tsv dangling_edges"
echo "Loading denormalized edges..."
sqlite3 -cmd ".mode tabs" output/kg-alzheimers.db ".import output/kg-alzheimers-denormalized-edges.tsv denormalized_edges"

sqlite3 output/kg-alzheimers.db "CREATE TABLE closure (subject TEXT, predicate TEXT, object TEXT)"
sqlite3 -cmd ".mode tabs" output/kg-alzheimers.db ".import data/monarch/phenio-relation-graph.tsv closure"

echo "Creating indices..."
sqlite3 output/kg-alzheimers.db "create index if not exists edges_subject_index on edges (subject)"
sqlite3 output/kg-alzheimers.db "create index if not exists edges_object_index on edges (object)"
sqlite3 output/kg-alzheimers.db "create index if not exists closure_subject_index on closure (subject)"
sqlite3 output/kg-alzheimers.db "create index if not exists denormalized_edges_subject_index on denormalized_edges (subject)"
sqlite3 output/kg-alzheimers.db "create index if not exists denormalized_edges_object_index on denormalized_edges (object)"

echo "Cleaning up..."
rm output/kg-alzheimers_*.tsv
pigz --force output/qc/kg-alzheimers-dangling-edges.tsv
pigz --force output/kg-alzheimers-denormalized-edges.tsv

echo "Populate phenio db term_association..."
cp data/monarch/phenio.db.gz output/phenio.db.gz
gunzip output/phenio.db.gz
sqlite3 -cmd "attach 'output/kg-alzheimers.db' as monarch" output/phenio.db "insert into term_association (id, subject, predicate, object, evidence_type, publication, source) select id, subject, predicate, object, has_evidence as evidence_type, publications as publication, primary_knowledge_source as source from monarch.edges where category in ('biolink:GeneToPhenotypicFeatureAssociation','biolink:DiseaseToPhenotypicFeatureAssociation') and predicate = 'biolink:has_phenotype' and negated <> 'True' and has_count <> 0 and has_percentage <> 0"

echo "Compressing databases"
pigz --force output/phenio.db
pigz --force output/kg-alzheimers.db
