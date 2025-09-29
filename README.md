# KG-Alzheimers
[![documentation](https://img.shields.io/badge/-Documentation-purple?logo=read-the-docs&logoColor=white&style=for-the-badge)](https://Knowledge-Graph-Hub.github.io/kg-alzheimers/)

KG-Alzheimers builds and distributes an Alzheimer’s disease-focused biomedical
knowledge graph by harmonizing Monarch Initiative and partner data sources into
BioLink Model-compliant KGX exports, DuckDB/SQLite databases, JSONL feeds, and
search indexes.

## Highlights

- Integrates dozens of genomics, phenomics, pathway, and literature resources
  behind a repeatable ETL pipeline.
- Ships a Typer-powered CLI (`ingest`) that orchestrates download, transform,
  merge, QC, export, and packaging steps.
- Produces denormalized TSV bundles, RDF/JSONL snapshots, and Solr-ready
  indexes suitable for analytics or downstream applications.
- Uses Poetry for dependency management and reproducible environments; CI/CD via
  Jenkins keeps public releases up to date.

## Getting Started

> Requires Python 3.10+ and [Poetry](https://python-poetry.org/).

```bash
git clone https://github.com/Knowledge-Graph-Hub/kg-alzheimers.git
cd kg-alzheimers
poetry install

# Optional: activate the virtual environment created by Poetry
poetry shell
```

To download all referenced datasets and run the full build pipeline locally:

```bash
# Retrieve source data declared in src/kg_alzheimers/download.yaml
poetry run ingest download --all --write-metadata

# Execute Phenio preprocessing plus all Koza ingests
poetry run ingest transform --all --log --rdf --write-metadata

# Merge transformed outputs into a unified KG bundle with QC checks
poetry run ingest merge

# (Optional) Generate closure-enriched denormalized tables
poetry run ingest closure

# Prepare release artifacts (gzipped DuckDB/TSV/JSONL bundles)
poetry run ingest prepare-release
```

Additional commands are documented in [`docs/CLI.md`](docs/CLI.md) and include:

- `poetry run ingest export` &mdash; create filtered TSV/JSONL dumps defined in
  `src/kg_alzheimers/data-dump-config.yaml`.
- `poetry run ingest report` &mdash; run DuckDB QC SQL scripts to audit the merge.
- `poetry run ingest sqlite` / `poetry run ingest solr` &mdash; load artifacts into
  local SQLite or Solr instances for exploration.

> **Note:** The `ingest release` command is deprecated; releases are created by
> the Jenkins pipeline described in `Jenkinsfile`.

## Documentation

- Detailed guides, modeling principles, and ingest walkthroughs live at
  [Knowledge-Graph-Hub.github.io/kg-alzheimers](https://Knowledge-Graph-Hub.github.io/kg-alzheimers/).
- Source for the documentation site resides in the [`docs/`](docs) directory
  and is built with MkDocs Material (`mkdocs.yaml`).

## Development

- Run the unit test suite:

  ```bash
  poetry run pytest
  ```

- Format and lint using the configured tooling (Black and Ruff):

  ```bash
  poetry run black src tests
  poetry run ruff check src tests
  ```

Issues and contributions are welcome via GitHub. To propose a new ingest, follow
the workflow documented under `docs/Create-an-Ingest/`.
