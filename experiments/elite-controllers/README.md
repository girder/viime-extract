## Processing

Extract entities into `elite-controllers.json`:

```bash
uv run ./run_csv_abstract_extraction.py -c config.toml -o elite-controllers.json Elite_controllers_072225.csv 2&> stdout.txt
```

Output extracted entities as a single CSV.

```bash
uv run ./reformat-abstract-results.py as-csv -a Elite_controllers_072225.csv -r elite-controllers.json -o elite-controllers.csv
```