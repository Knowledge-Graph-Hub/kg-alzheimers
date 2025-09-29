# `ingest`

**Usage**:

```console
$ ingest [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version`
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `closure`
* `download`: Downloads data defined in download.yaml
* `export`
* `jsonl`
* `merge`: Merge nodes and edges into kg
* `prepare-release`
* `release`: Deprecated wrapper for legacy Monarch uploads
* `report`: Run Koza QC on specified Monarch ingests
* `solr`
* `sqlite`
* `transform`: Run Koza transformation on specified...

## `ingest closure`

**Usage**:

```console
$ ingest closure [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ingest download`

Downloads data defined in download.yaml

**Usage**:

```console
$ ingest download [OPTIONS]
```

**Options**:

* `--ingests TEXT`: Which ingests to download data for
* `--all / --no-all`: Download all ingest datasets  [default: no-all]
* `--write-metadata / --no-write-metadata`: Write versions of ingests to metadata.yaml  [default: no-write-metadata]
* `--help`: Show this message and exit.

## `ingest export`

**Usage**:

```console
$ ingest export [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ingest jsonl`

**Usage**:

```console
$ ingest jsonl [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ingest merge`

Merge nodes and edges into kg

**Usage**:

```console
$ ingest merge [OPTIONS]
```

**Options**:

* `--input-dir TEXT`: Directory with nodes and edges to be merged  [default: output/transform_output]
* `--output-dir TEXT`: Directory to output data  [default: output]
* `-d, --debug / -q, --quiet`: Use --quiet to suppress log output, --debug for verbose
* `--help`: Show this message and exit.

## `ingest prepare-release`

**Usage**:

```console
$ ingest prepare-release [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ingest release`

Deprecated wrapper for the historical release workflow; Jenkins now handles
remote publication and this command only prints a deprecation notice.

**Usage**:

```console
$ ingest release [OPTIONS]
```

**Options**:

* `--dir TEXT`: Directory with kg to be released  [default: output]
* `--help`: Show this message and exit.

## `ingest report`

Run Koza QC on specified KG-Alzheimers ingests

**Usage**:

```console
$ ingest report [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ingest solr`

**Usage**:

```console
$ ingest solr [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ingest sqlite`

**Usage**:

```console
$ ingest sqlite [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ingest transform`

Run Koza transformation on specified KG-Alzheimers ingests

**Usage**:

```console
$ ingest transform [OPTIONS]
```

**Options**:

* `-o, --output-dir TEXT`: Directory to output data  [default: output]
* `-i, --ingest TEXT`: Run a single ingest (see ingests.yaml for a list)
* `--phenio / --no-phenio`: Run the phenio transform  [default: no-phenio]
* `-a, --all`: Ingest all sources
* `-f, --force`: Force ingest, even if output exists (on by default for single ingests)
* `--rdf / --no-rdf`: Output rdf files along with tsv  [default: no-rdf]
* `-d, --debug / -q, --quiet`: Use --quiet to suppress log output, --debug for verbose, including Koza logs
* `-l, --log`: Write DEBUG level logs to ./logs/ for each ingest
* `-n, --row-limit INTEGER`: Number of rows to process
* `--write-metadata / --no-write-metadata`: Write data/package versions to output_dir/metadata.yaml  [default: no-write-metadata]
* `--help`: Show this message and exit.
