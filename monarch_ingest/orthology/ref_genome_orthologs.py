"""
Ingest of Reference Genome Orthologs from Panther
"""
import uuid

import logging

from koza.cli_runner import koza_app

from biolink_model_pydantic.model import Gene, Predicate, GeneToGeneHomologyAssociation

from monarch_ingest.orthology.orthology_utils import parse_gene, lookup_predicate

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


row = koza_app.get_row()

uniprot_2_gene = koza_app.get_map('uniprot_2_gene')

gene_id = parse_gene(row['Gene'], uniprot_2_gene)
if not gene_id:
    logger.warning(f"Gene lacking Entrez Gene Id. Ignoring?")
else:
    # unpack the gene id and its species
    gene_id, gene_ncbitaxon = gene_id
    
    ortholog_id = parse_gene(row['Ortholog'], uniprot_2_gene)
    if not ortholog_id:
        logger.warning(f"Ortholog gene lacking Entrez Gene Id. Ignoring?")
    else:
        # unpack the orthogous gene id and its species
        ortholog_id, ortholog_ncbitaxon = ortholog_id

        # TODO: how do I discriminate between LDO and O?
        # ortholog_type = row['Type of ortholog']
        predicate = Predicate.orthologous_to
        relation = koza_app.translation_table.global_table['in orthology relationship with']

        # build the Gene and Orthologous Gene nodes
        gene = Gene(id=gene_id, in_taxon=gene_ncbitaxon, source="infores:entrez")
        ortholog = Gene(id=ortholog_id, in_taxon=ortholog_ncbitaxon, source="infores:entrez")
        
        # Instantiate the instance of Gene-to-Gene Homology Association
        association = GeneToGeneHomologyAssociation(
            id="uuid:" + str(uuid.uuid1()),
            subject=gene.id,
            object=ortholog.id,
            predicate=predicate,
            relation=relation,
            source="infores:panther"
        )
    
        # Write the captured Association out
        koza_app.write(gene, ortholog, association)
