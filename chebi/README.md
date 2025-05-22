Steps to download:
1. Go to https://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited/
2. Download `names.tsv.gz` and `compounds.tsv.gz`. Compounds is the central table, while names contains alternate names for compounds. See [schema](https://docs.google.com/document/d/11G6SmTtQRQYFT7l9h5K0faUHiAaekcLeOweMOOTIpME/edit?tab=t.0) for more info.
3. Run `gunzip names.tsv.gz` and `gunzip compounds.tsv.gz`
4. Run `uv run ./merge_db.py compounds.tsv names.tsv > db.tsv` to merge the database tables