Two datasets in this folder:
- Brain_Fog: brain fog abstracts
- Chronic_fatigue_syndrome: CFS abstracts

## Processing

Extract entities into `brain_fog.json`/`cfs.json`:

```bash
uv run ./run_csv_abstract_extraction.py -c config.toml -o brain_fog.json Brain_Fog_060625.csv
uv run ./run_csv_abstract_extraction.py -c config.toml -o cfs.json Chronic_fatigue_syndrome_060625.csv
```

Output extracted entities into CSVs, grouped by entity type.

```bash
uv run ingest-to-csvs.py -i brain_fog.json brain_fog/
uv run ingest-to-csvs.py -i cfs.json cfs/
```

Output extracted entities as a single CSV.

```bash
uv run reformat-abstract-results.py as-csv -a Brain_Fog_060625.csv -r brain_fog.json -o brain_fog/brain_fog_all.csv
uv run reformat-abstract-results.py as-csv -a Chronic_fatigue_syndrome_060625.csv -r cfs.json -o cfs/cfs_all.csv
```