# 5 COVID-19 paper experiments

Data overview:
- Data available from the [COVID-19.zip](https://drive.google.com/file/d/1LaMoBEkPFNVXJ5FOa1EFKMx8rksxdMAZ/view?usp=drive_link) archive
- 5 PDF files corresponding to the 5 COVID-19 papers
- 5 XLSX files corresponding to the list of metabolites measured in the studies

Goals:
- extract metabolites from the 5 papers with LLMs, then map them to RefMet and ChEBI IDs and compare with the metabolites in the xlsx files.

The `outputs/` folder contains the outputs and results from extracting the metabolites.
- `ST*.json` files are the LLM-extracted JSONs containing metabolite names
- `name-*.txt` files are cleaned and deduplicated metabolite names from LLM-based extraction
- `refmet_*.txt` files are results from feeding in `names-*.txt` to the RefMet Name to ID online converter tool
- `chebi-candidates-*.tsv` are the candidate lists from dice and jaro fuzzy metrics, respectively

## Overview of Pipeline

Required software:
- `uv`
- `jq`
- GNU coreutils (for `sort` and `cat`)

The pipeline for metabolite extraction and analysis:
1. Extract the metabolite names from the PDFs
2. Match the metabolite names to RefMet standard names
   1. Compare the extracted metabolite RefMet names list to the metabolites listed in the XLSX metabolite list
2. Match the metabolite names to ChEBI IDs
   1. Pass in the ChEBI IDs to the Reactome Pathway Browser

## Extracting the metabolites from the PDFs

The following commands will extract the metabolites from each paper and write them out to `XXXX.json`, where `XXXX` is the associated study ID.

```bash
# cwd: viime-extract root

uv run ./bin/extract_from_pdf.py -c ./experiments/refine-only_metabolites.toml ./COVID-19/ST001933\ Plasma\ metabolome\ and\ cytokine\ panel\ profile\ reveals\ glcylproline\ modulating\ antibody\ fading\ in\ convalescent\ COVID-19\ patients.pdf -o ./outputs/ST001933.json
uv run ./bin/extract_from_pdf.py -c ./experiments/refine-only_metabolites.toml ./COVID-19/ST002087\ PLoSPathogens\ Profiling\ metabolites\ and\ lipoproteins\ in\ COMETA\ an\ Italian\ cohort\ of\ COVID-19\ patients.pdf -o ./outputs/ST002087.json
uv run ./bin/extract_from_pdf.py -c ./experiments/refine-only_metabolites.toml ./COVID-19/ST001933\ Plasma\ metabolome\ and\ cytokine\ panel\ profile\ reveals\ glcylproline\ modulating\ antibody\ fading\ in\ convalescent\ COVID-19\ patients.pdf -o ./outputs/ST001933.json
uv run ./bin/extract_from_pdf.py -c ./experiments/refine-only_metabolites.toml ./COVID-19/ST002194\ Metabolic\ profiling\ at\ COVID-19\ onset\ shows\ disease\ severity\ and\ sex-specific\ dysregulation.pdf -o ./outputs/ST002194.json
uv run ./bin/extract_from_pdf.py -c ./experiments/refine-only_metabolites.toml ./COVID-19/ST002829\ Nucleotide,\ Phospholipid,\ and\ Kynurenine\ Metabolites.PDF -o ./outputs/ST002829.json
```

## Match the metabolite names to RefMet standard names

First, map the output JSON files from the previous step to lists of metabolite names. Duplicate names are removed from the JSON before being written out to text files.

```bash
# extract the unique sorted names from the study JSONs. -u keeps unique, and -f ignores case
cat ./outputs/ST001933.json| jq -r '.keywords.mentioned_metabolites[].name' | sort -uf > outputs/names-ST001933.txt
cat ./outputs/ST002087.json| jq -r '.keywords.mentioned_metabolites[].name' | sort -uf > outputs/names-ST002087.txt
cat ./outputs/ST002194.json| jq -r '.keywords.mentioned_metabolites[].name' | sort -uf > outputs/names-ST002194.txt
cat ./outputs/ST002829.json| jq -r '.keywords.mentioned_metabolites[].name' | sort -uf > outputs/names-ST002829.txt
cat ./outputs/ST003039.json| jq -r '.keywords.mentioned_metabolites[].name' | sort -uf > outputs/names-ST003039.txt
```

Use the RefMet [name to refmet ID converter tool](https://www.metabolomicsworkbench.org/databases/refmet/name_to_refmetID_form.php) to convert the metabolite names to RefMet IDs and standardized names. This tool does a best-effort matching given a name. For each text file generated above, feed it into the online form and download the results to `./outputs/refmet_XXXXX.txt`.

## Comparing RefMet output to the metabolites study protocol

We can now compare the RefMet-standardized extracted metabolite names with the metabolites listed in the study.

```
$ uv run ../../bin/compare_refmet_to_study.py outputs/refmet_ST001933.txt COVID-19\ papers/ST001933\ metabolites.xlsx
The RefMet results have 47 valid RefMet names out of 83 names.
Found 46 out of 182 (25.27%) metabolites listed in the study protocol.
In the study protocol, there are 4 metabolites that do not list a standardized RefMet name, out of 187 rows.

$ uv run ../../bin/compare_refmet_to_study.py outputs/refmet_ST002087.txt COVID-19\ papers/ST002087\ metabolites.xlsx
The RefMet results have 29 valid RefMet names out of 78 names.
Found 25 out of 25 (100.00%) metabolites listed in the study protocol.
In the study protocol, there are 114 metabolites that do not list a standardized RefMet name, out of 139 rows.

$ uv run ../../bin/compare_refmet_to_study.py outputs/refmet_ST002194.txt COVID-19\ papers/ST002194\ metabolites.xlsx
The RefMet results have 108 valid RefMet names out of 154 names.
Found 46 out of 50 (92.00%) metabolites listed in the study protocol.
In the study protocol, there are 16 metabolites that do not list a standardized RefMet name, out of 67 rows.

$ uv run ../../bin/compare_refmet_to_study.py outputs/refmet_ST002829.txt COVID-19\ papers/ST002829\ metabolites.xlsx
The RefMet results have 34 valid RefMet names out of 81 names.
Found 33 out of 745 (4.43%) metabolites listed in the study protocol.
In the study protocol, there are 342 metabolites that do not list a standardized RefMet name, out of 1108 rows.

$ uv run ../../bin/compare_refmet_to_study.py outputs/refmet_ST003039.txt COVID-19\ papers/ST003039\ metabolites.xlsx
The RefMet results have 71 valid RefMet names out of 77 names.
Found 53 out of 116 (45.69%) metabolites listed in the study protocol.
In the study protocol, there are 0 metabolites that do not list a standardized RefMet name, out of 116 rows.
```

## Matching metabolite names to ChEBI IDs

To build `chebi/db.tsv`, run `uv run chebi/merge_db.py chebi/compounds.tsv chebi/names.tsv > chebi/db.tsv`. See `chebi/README.md` for more details.

To fuzzy-match metabolite names with names in the ChEBI ID, we evaluated two string-distance metrics: Dice and Jaro-Winkler. The following commands outputs the top scoring candidates using Dice and Jaro, respectively.

```bash
for ID in 1933 2087 2194 2829 3039; do
    uv run ../../bin/convert_ids.py name-to-chebi --measure jaro ./outputs/names-ST00$ID.txt ../../chebi/db.tsv --top-k 1 --id-only > outputs/chebi-ids-jaro-ST00$ID.tsv
    uv run ../../bin/convert_ids.py name-to-chebi --measure dice ./outputs/names-ST00$ID.txt ../../chebi/db.tsv --top-k 1 --id-only > outputs/chebi-ids-dice-ST00$ID.tsv
done
```