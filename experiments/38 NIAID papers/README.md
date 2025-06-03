# Extracting entities from the 38 NIAID papers

- You can find the data here: https://drive.google.com/drive/folders/1TW3uvsJyqKxdvQntXVuGj3Ax1q7yv1_8?usp=drive_link

The following is the command used to extract the JSONs.

```bash
root="./experiments/38 NIAID papers"
mkdir -p "$root/extracted"
date
for file in "$root"/papers/*.pdf; do
  echo "Extracting from $file"
  uv run ./bin/extract_from_pdf.py -c "$root/config.toml" "$file" -o "$root/extracted/$(basename "$file").json" &> "$root/extracted/$(basename "$file").output.txt"
done
date
```

Extraction timing results:
- Start: Thu May 22 16:29:35 EDT 2025
- End: Thu May 22 17:48:16 EDT 2025

Once the extraction results are generated, use `ingest-to-csvs.py` to write out csv outputs to `output/`

```bash
uv run ingest-to-csvs.py output extracted/*.json
```

To reformat the data:

```bash
# as CSV:
uv run reformat-output.py as-csv -o output.csv extracted/*.json
# as linkage JSON for layoutr:
uv run reformat-output.py as-layoutr -o output.json extracted/*.json
```