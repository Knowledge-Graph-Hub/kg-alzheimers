import pytest
from biolink_model.datamodel.pydanticmodel_v2 import Gene, GeneToPhenotypicFeatureAssociation, PhenotypicFeature
from koza.utils.testing_utils import mock_koza  # noqa: F401


@pytest.fixture
def entities(mock_koza, global_table):
    row = {
        "Database name": "PomBase",
        "Gene systematic ID": "SPAC24B11.06c",
        "FYPO ID": "FYPO:0004058",
        "Allele description": "",
        "Expression": "",
        "Parental strain": "972 h-",
        "Strain name (background)": "",
        "Genotype description": "",
        "Gene name": "sty1",
        "Allele name": "sty1delta",
        "Allele synonym": "",
        "Allele type": "deletion",
        "Evidence": "cell growth assay evidence",
        "Condition": "",
        "Penetrance": "",
        "Severity": "FYPO_EXT:0000001",
        "Extension": "",
        "Reference": "PMID:19436749",
        "Taxon": "4896",
        "Date": "2014-11-21",
    }

    return mock_koza(
        name="pombase_gene_to_phenotype",
        data=row,
        transform_code="./src/kg_alzheimers/ingests/pombase/gene_to_phenotype.py",
        global_table=global_table,
    )


# TODO: can this test be shared across all g2p loads?
@pytest.mark.parametrize("cls", [Gene, PhenotypicFeature, GeneToPhenotypicFeatureAssociation])
def confirm_one_of_each_classes(cls, entities):
    class_entities = [entity for entity in entities if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 1
    assert class_entities[0]


def test_pombase_g2p_association_publication(entities):
    association = [
        association for association in entities if isinstance(association, GeneToPhenotypicFeatureAssociation)
    ][0]
    assert association.subject == "PomBase:SPAC24B11.06c"
    assert association.predicate == "biolink:has_phenotype"
    assert association.object == "FYPO:0004058"
    assert association.publications[0] == "PMID:19436749"
    assert association.primary_knowledge_source == "infores:pombase"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
