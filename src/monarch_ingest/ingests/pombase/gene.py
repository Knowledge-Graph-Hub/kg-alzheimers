

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import Gene

from loguru import logger

koza_app = get_koza_app("pombase_gene")

while (row := koza_app.get_row()) is not None:

    gene = Gene(
        id=row["curie"],
        symbol=row["gene_systematic_id"],
        name=row["gene_systematic_id"],
        # full name is not yet available in biolink
        # full_name=row["gene_name"],
        # No place in the schema for gene type (SO term) right now
        # type=koza_app.translation_table.resolve_term(row["product type"].replace(' ', '_')),
        synonym=row["synonyms"].split(","),
        in_taxon=["NCBITaxon:4896"],
        provided_by=["infores:pombase"]
    )

    if row["UniProtKB accession"]:
        gene.xref = ["UniProtKB:" + row["UniProtKB accession"]]

    if row["synonyms"]:
        gene.synonym = row["synonyms"].split(",")

    koza_app.write(gene)
