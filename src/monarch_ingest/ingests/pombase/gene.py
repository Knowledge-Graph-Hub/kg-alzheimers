

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import Gene

from loguru import logger

koza_app = get_koza_app("pombase_gene")
taxon_labels = koza_app.get_map("taxon-labels")

while (row := koza_app.get_row()) is not None:

    in_taxon = "NCBITaxon:4896"
    in_taxon_label = taxon_labels[in_taxon]["label"]

    gene = Gene(
        id=row["curie"],
        symbol=row["gene_systematic_id"],
        name=row["gene_systematic_id"],        
        full_name=row["gene_name"],
        # No place in the schema for gene type (SO term) right now
        # type=koza_app.translation_table.resolve_term(row["product type"].replace(' ', '_')),
        in_taxon=[in_taxon],
        in_taxon_label=in_taxon_label,
        provided_by=["infores:pombase"]
    )

    if row["uniprot_id"]:
        gene.xref = ["UniProtKB:" + row["uniprot_id"]]

    if row["synonyms"]:
        gene.synonym = row["synonyms"].split(",")

    koza_app.write(gene)
