## COVID-19 experiments

Data overview:
- Data in [COVID-19.zip](https://drive.google.com/file/d/1LaMoBEkPFNVXJ5FOa1EFKMx8rksxdMAZ/view?usp=drive_link) archive
- 5 papers with 5 xlsx files detailing the metabolites in the associated studies

Goals:
- extract metabolites from the 5 papers with LLMs, then map them to RefMet and ChEBI IDs and compare with the metabolites in the xlsx files.

The `outputs/` folder contains the workspace and results from extracting the metabolites.
- `ST*.json` files are the LLM-extracted JSONs containing metabolite names
- `name-*.txt` files are cleaned and deduplicated metabolite names from LLM-based extraction
- `refmet_*.txt` files are results from feeding in `names-*.txt` to the RefMet Name to ID online converter tool
- `chebi-candidates-*.tsv` are the candidate lists from dice and jaro fuzzy metrics, respectively

## Table of Contents

- [viime-extract: processing Tom’s 5 PDFs](#viime-extract-processing-toms-5-pdfs)
  - [Extracting the metabolites into JSON](#extracting-the-metabolites-into-json)
  - [Metabolite names to refmet, pubchem and chebi IDs](#metabolite-names-to-refmet-pubchem-and-chebi-ids)
  - [Metabolite IDs to pubchem/chebi IDs](#metabolite-ids-to-pubchemchebi-ids)
  - [pubchem IDs to chebi IDs](#pubchem-ids-to-chebi-ids)
  - [Comparing RefMet output to the metabolites study protocol](#comparing-refmet-output-to-the-metabolites-study-protocol)


<a id="orge443f64"></a>

# viime-extract: processing Tom&rsquo;s 5 PDFs


<a id="org37782ee"></a>

## Extracting the metabolites into JSON

    uv run ./bin/extract_from_pdf.py -c ./experiments/refine-only_metabolites.toml ./COVID-19/ST001933\ Plasma\ metabolome\ and\ cytokine\ panel\ profile\ reveals\ glcylproline\ modulating\ antibody\ fading\ in\ convalescent\ COVID-19\ patients.pdf -o ST001933.json
    uv run ./bin/extract_from_pdf.py -c ./experiments/refine-only_metabolites.toml ./COVID-19/ST002087\ PLoSPathogens\ Profiling\ metabolites\ and\ lipoproteins\ in\ COMETA\ an\ Italian\ cohort\ of\ COVID-19\ patients.pdf -o ST002087.json
    uv run ./bin/extract_from_pdf.py -c ./experiments/refine-only_metabolites.toml ./COVID-19/ST001933\ Plasma\ metabolome\ and\ cytokine\ panel\ profile\ reveals\ glcylproline\ modulating\ antibody\ fading\ in\ convalescent\ COVID-19\ patients.pdf -o ST001933.json
    uv run ./bin/extract_from_pdf.py -c ./experiments/refine-only_metabolites.toml ./COVID-19/ST002194\ Metabolic\ profiling\ at\ COVID-19\ onset\ shows\ disease\ severity\ and\ sex-specific\ dysregulation.pdf -o workspace/ST002194.json
    uv run ./bin/extract_from_pdf.py -c ./experiments/refine-only_metabolites.toml ./COVID-19/ST002829\ Nucleotide,\ Phospholipid,\ and\ Kynurenine\ Metabolites.PDF -o workspace/ST002829.json


<a id="org18bc338"></a>

## Metabolite names to refmet, pubchem and chebi IDs

Idea: run names through metaboanalyst, then fuzzy-search against chEBI for the remainder

-   <https://www.metaboanalyst.ca/MetaboAnalyst/upload/ConvertView.xhtml>

```
# extract the unique sorted names from the study JSONs. -u keeps unique, and -f ignores case
cat ./workspace/ST001933.json| jq -r '.keywords.mentioned_metabolites[].name' | sort -uf > workspace/names-ST001933.txt
cat ./workspace/ST002087.json| jq -r '.keywords.mentioned_metabolites[].name' | sort -uf > workspace/names-ST002087.txt
cat ./workspace/ST002194.json| jq -r '.keywords.mentioned_metabolites[].name' | sort -uf > workspace/names-ST002194.txt
cat ./workspace/ST002829.json| jq -r '.keywords.mentioned_metabolites[].name' | sort -uf > workspace/names-ST002829.txt
cat ./workspace/ST003039.json| jq -r '.keywords.mentioned_metabolites[].name' | sort -uf > workspace/names-ST003039.txt
```

I can use the metabolomics workbench [name to refmet ID converter tool online](https://www.metabolomicsworkbench.org/databases/refmet/name_to_refmetID_form.php).

To fuzzy-search ChEBI:

    uv run ./bin/convert_ids.py name-to-chebi --measure dice ./workspace/names-ST003039.txt ./chebi/db.tsv > workspace/chebi-candidates-dice-ST003039.tsv


<a id="org591ec96"></a>

## Metabolite IDs to pubchem/chebi IDs

    https://www.metabolomicsworkbench.org/rest/study/metabolite_id/<Metabolite ID, e.g. ME442714>/available/


<a id="org216e791"></a>

## pubchem IDs to chebi IDs

    https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/<PubChem Compound ID>/xrefs/SBURL/XML
    - search for ChEBI identifier in the list


<a id="orga6bfe7b"></a>

## Comparing RefMet output to the metabolites study protocol

    uv run ./bin/compare_refmet_to_study.py workspace/refmet_ST001933.txt COVID-19/ST001933\ metabolites.xlsx
    uv run ./bin/compare_refmet_to_study.py workspace/refmet_ST002087.txt COVID-19/ST002087\ metabolites.xlsx
    uv run ./bin/compare_refmet_to_study.py workspace/refmet_ST002194.txt COVID-19/ST002194\ metabolites.xlsx
    uv run ./bin/compare_refmet_to_study.py workspace/refmet_ST002829.txt COVID-19/ST002829\ metabolites.xlsx
    uv run ./bin/compare_refmet_to_study.py workspace/refmet_ST003039.txt COVID-19/ST003039\ metabolites.xlsx
