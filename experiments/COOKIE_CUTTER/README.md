This README is structured for ingesting PubMed CSV exports.

## Processing

Input file is called `{{ MY-INPUT-CSV.csv }}`.

Extract entities into `{{ MY-JSON-RESULTS.json }}`:

```bash
uv run ./run_csv_abstract_extraction.py -c config.toml -o {{ MY-JSON-RESULTS.json}} {{ MY-INPUT-CSV.csv }} 2&> stdout.txt
```

The output JSON file contains a mapping from PMID to the extracted entities.

To convert the JSON results into a format Tom likes:

```bash
uv run ./reformat-abstract-results.py as-csv -a {{ MY-INPUT-CSV.csv }} -r {{ MY-JSON-RESULTS.json }} -o {{ TOMS-CSV.csv }}
```