import pytest
from koza.utils.testing_utils import mock_koza  # noqa: F401


@pytest.fixture
def source_name():
    return "hgnc_gene"


@pytest.fixture
def script():
    return "./src/kg_alzheimers/ingests/hgnc/gene.py"


@pytest.fixture
def gene_row():
    return {
        "hgnc_id": "HGNC:24086",
        "pubmed_id": "11072063",
        "symbol": "A1CF",
        "name": "APOBEC1 complementation factor",
        "ensembl_gene_id": "ENSG00000148584",
        "omim_id": "618199",
        "alias_symbol": "ACF|ASP|ACF64|ACF65|APOBEC1CF",
        "alias_name": "",
        "prev_symbol": "",
        "prev_name": "",
    }


@pytest.fixture
def so_term_map_cache():
    return {"hgnc-so-terms": {"HGNC:24086": {"so_term_id": "SO:0001217"}}}


@pytest.fixture
def pax2a(mock_koza, source_name, gene_row, script, taxon_label_map_cache, so_term_map_cache, global_table):
    row = gene_row
    return mock_koza(
        source_name,
        row,
        script,
        map_cache=taxon_label_map_cache | so_term_map_cache,
        global_table=global_table,
    )


def test_gene(pax2a):
    gene = pax2a[0]
    assert gene
    assert gene.id == "HGNC:24086"


def test_gene_information_synonym(pax2a):
    gene = pax2a[0]
    assert gene.synonym
    assert gene.synonym == ["ACF", "ASP", "ACF64", "ACF65", "APOBEC1CF", "", "", ""]


def test_gene_information_xref(pax2a):
    gene = pax2a[0]
    assert gene.xref
    assert gene.xref == ["ENSEMBL:ENSG00000148584", "OMIM:618199"]


def test_gene_information_so_term(pax2a):
    gene = pax2a[0]
    assert gene.type
    assert gene.type == ["SO:0001217"]


# Commenting out publication ingests at least temporarily
# def test_publication(pax2a):
#     publication = pax2a[1]
#     assert publication
#     assert publication.id == "PMID:11072063"
#
#
# def test_association(pax2a):
#     association = pax2a[2]
#     assert association
#     assert association.subject == "HGNC:24086"
#     assert association.object == "PMID:11072063"
