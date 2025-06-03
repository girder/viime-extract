# Abstracts vs Full-Text

Tom put together a list of 94 abstracts in `Pubmed_metabolomics_AND_LitCLONGCOVID_filter_.csv`.

## Downloading the full-text PDFs

- Most were downloaded using PMC. A few more were provided by Bharat.

## Running

```bash
# cwd: experiments/Abstracts vs Full-Text
mkdir -p ./extracted
date
for file in ./allpdfs/*.pdf; do
  echo "Extracting from $file"
  uv run ../../bin/extract_from_pdf.py -c ./config.toml "$file" -o "./extracted/$(basename "$file").json" &> "./extracted/$(basename "$file").output.txt"
done
date
```

## run_csv_abstract_extraction.py

This will run the LLM pipeline on the abstracts in `Pubmed_metabolomics_AND_LitCLONGCOVID_filter_csv`.

```bash
uv run ./run_csv_abstract_extraction.py -c ./config.toml Pubmed_metabolomics_AND_LitCLONGCOVID_filter_.csv
```


## reformat-abstract-results.py

This file was used to convert the results of `run_csv_abstract_extraction.py` into two formats:
- `as_csv`: outputs results as CSV
- `as_layoutr`: outputs a Layoutr JSON file

Usage:

```bash
uv run reformat-abstract-results.py as-csv -a Pubmed_metabolomics_AND_LitCLONGCOVID_filter_.csv -r abstracts-results.json -o output.csv
uv run reformat-abstract-results.py as-layoutr -a Pubmed_metabolomics_AND_LitCLONGCOVID_filter_.csv -r abstracts-results.json -o output-layoutr.json
```

---

```
Wed May 28 16:56:55 EDT 2025
Extracting from ./allpdfs/37858739.pdf
Extracting from ./allpdfs/38368647.pdf
Extracting from ./allpdfs/39571342.pdf
Extracting from ./allpdfs/39914235.pdf
Extracting from ./allpdfs/40023939.pdf
Extracting from ./allpdfs/PMC10005061.pdf
Extracting from ./allpdfs/PMC10022496.pdf
Extracting from ./allpdfs/PMC10028820.pdf
Extracting from ./allpdfs/PMC10049539.pdf
Extracting from ./allpdfs/PMC10203989.pdf
Extracting from ./allpdfs/PMC10300098.pdf
Extracting from ./allpdfs/PMC10344451.pdf
Extracting from ./allpdfs/PMC10355065.pdf
Extracting from ./allpdfs/PMC10380980.pdf
Extracting from ./allpdfs/PMC10384698.pdf
Extracting from ./allpdfs/PMC10394026.pdf
Extracting from ./allpdfs/PMC10406961.pdf
Extracting from ./allpdfs/PMC10658082.pdf
Extracting from ./allpdfs/PMC10688311.pdf
Extracting from ./allpdfs/PMC10694626.pdf
Extracting from ./allpdfs/PMC10728085.pdf
Extracting from ./allpdfs/PMC10748708.pdf
Extracting from ./allpdfs/PMC10766651.pdf
Extracting from ./allpdfs/PMC10772081.pdf
Extracting from ./allpdfs/PMC10775146.pdf
Extracting from ./allpdfs/PMC10830702.pdf
Extracting from ./allpdfs/PMC10855192.pdf
Extracting from ./allpdfs/PMC11065031.pdf
Extracting from ./allpdfs/PMC11068918.pdf
Extracting from ./allpdfs/PMC11152273.pdf
Extracting from ./allpdfs/PMC11223383.pdf
Extracting from ./allpdfs/PMC11227373.pdf
Extracting from ./allpdfs/PMC11256945.pdf
Extracting from ./allpdfs/PMC11276903.pdf
Extracting from ./allpdfs/PMC11354507.pdf
Extracting from ./allpdfs/PMC11395921.pdf
Extracting from ./allpdfs/PMC11411991.pdf
Extracting from ./allpdfs/PMC11417410.pdf
Extracting from ./allpdfs/PMC11560803.pdf
Extracting from ./allpdfs/PMC11580917.pdf
Extracting from ./allpdfs/PMC11596941.pdf
Extracting from ./allpdfs/PMC11597208.pdf
Extracting from ./allpdfs/PMC11598993.pdf
Extracting from ./allpdfs/PMC11601417.pdf
Extracting from ./allpdfs/PMC11718655.pdf
Extracting from ./allpdfs/PMC11789121.pdf
Extracting from ./allpdfs/PMC11790113.pdf
Extracting from ./allpdfs/PMC11814416.pdf
Extracting from ./allpdfs/PMC11818272.pdf
Extracting from ./allpdfs/PMC11836394.pdf
Extracting from ./allpdfs/PMC11855089.pdf
Extracting from ./allpdfs/PMC11881263.pdf
Extracting from ./allpdfs/PMC11908298.pdf
Extracting from ./allpdfs/PMC11911085.pdf
Extracting from ./allpdfs/PMC11969314.pdf
Extracting from ./allpdfs/PMC7617446.pdf
Extracting from ./allpdfs/PMC7929060.pdf
Extracting from ./allpdfs/PMC8024622.pdf
Extracting from ./allpdfs/PMC8217552.pdf
Extracting from ./allpdfs/PMC8234252.pdf
Extracting from ./allpdfs/PMC8249176.pdf
Extracting from ./allpdfs/PMC8431319.pdf
Extracting from ./allpdfs/PMC8515786.pdf
Extracting from ./allpdfs/PMC8516480.pdf
Extracting from ./allpdfs/PMC8764736.pdf
Extracting from ./allpdfs/PMC8786632.pdf
Extracting from ./allpdfs/PMC8790565.pdf
Extracting from ./allpdfs/PMC8794466.pdf
Extracting from ./allpdfs/PMC8847098.pdf
Extracting from ./allpdfs/PMC8919172.pdf
Extracting from ./allpdfs/PMC9001849.pdf
Extracting from ./allpdfs/PMC9234841.pdf
Extracting from ./allpdfs/PMC9292080.pdf
Extracting from ./allpdfs/PMC9318602.pdf
Extracting from ./allpdfs/PMC9407385.pdf
Extracting from ./allpdfs/PMC9433334.pdf
Extracting from ./allpdfs/PMC9449332.pdf
Extracting from ./allpdfs/PMC9535314.pdf
Extracting from ./allpdfs/PMC9585783.pdf
Extracting from ./allpdfs/PMC9648868.pdf
Extracting from ./allpdfs/PMC9699059.pdf
Extracting from ./allpdfs/PMC9719844.pdf
Extracting from ./allpdfs/PMC9738241.pdf
Extracting from ./allpdfs/PMC9788519.pdf
Extracting from ./allpdfs/PMC9928611.pdf
Extracting from ./allpdfs/PMC9975567.pdf
Wed May 28 19:26:38 EDT 2025
```

Failed
```
PMC10203989.pdf
PMC11598993.pdf
PMC9318602.pdf
```