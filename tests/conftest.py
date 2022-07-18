import types
from typing import Iterable

import pytest
from koza.cli_runner import get_translation_table, get_koza_app, test_koza, set_koza_app
from koza.model.config.source_config import PrimaryFileConfig
from koza.model.source import Source


@pytest.fixture(scope="package")
def global_table():
    return "monarch_ingest/translation_table.yaml"


@pytest.fixture(scope="package")
def mock_koza():

    # This should be extracted out but for quick prototyping
    def _mock_write(self, *entities):
        if hasattr(self, '_entities'):
            self._entities.extend(list(entities))
        else:
            self._entities = list(entities)

    def _make_mock_koza_app(
        name: str,
        data: Iterable,
        transform_code: str,
        map_cache=None,
        filters=None,
        global_table=None,
        local_table=None,
    ):
        mock_source_file_config = PrimaryFileConfig(
            name=name,
            files=[],
            transform_code=transform_code,
        )
        mock_source_file = Source(mock_source_file_config)
        mock_source_file._reader = data

        set_koza_app(source=mock_source_file,
                     translation_table=get_translation_table(global_table, local_table))
        koza = get_koza_app(name)

        # TODO filter mocks
        koza._map_cache = map_cache
        koza.write = types.MethodType(_mock_write, koza)

        return koza


    def _transform(
            name: str,
            data: Iterable,
            transform_code: str,
            map_cache=None,
            filters=None,
            global_table=None,
            local_table=None,
    ):
        koza_app = _make_mock_koza_app(
            name,
            data,
            transform_code,
            map_cache=map_cache,
            filters=filters,
            global_table=global_table,
            local_table=local_table
        )
        test_koza(koza_app)
        koza_app.process_sources()
        if not hasattr(koza_app, '_entities'):
            koza_app._entities = []
        return koza_app._entities

    return _transform
