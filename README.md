# viime-extract

## Notebook setup

Install the required dependencies for running the notebook. If you don't have Jupyter installed, also install `jupyter`.

```
pip install python-dotenv pydantic openai
```

Run the notebook either with `jupyter notebook` or Jupyter Lab with `jupyter lab`.

You will need to have an OpenAI API key in order to use the notebooks and query OpenAI. Add that to a `.env` file at the root of the `viime-extract` project as follows:

```
OPENAI_API_KEY=<YOUR OPENAI API KEY>
```

## Experiment Running

Here is an example of running the extraction pipeline for all PDF files, using `run2.toml` configuration.

```bash
for f in data/PubMed\ LongCovid\ and\ Metabolomics\ Results/*.pdf;
do
    python3 ./bin/extract_from_pdf.py --config ./experiments/run2.toml "$f" -o "./experiments/run2results/$(basename "$f").json"
done
```

## Repo Overview

```
bin
├── compare_refmet_to_study.py  : used to generate the report 7 tables on comparing refmet metabolites to study metabolites
├── convert_ids.py              : used to convert metabolite names to ChEBI names
├── extract_from_pdf.py         : extracts metabolite names from PDFs
└── extract_from_txt.py         : extracts metabolite names from ./data/MolGenetMetab...txt

chebi
├── db.tsv                      : the chebi database
├── merge_db.py                 : creates the database. Read the README in this folder!
└── README.md

examples                        : Jeff added this folder. I haven't gone through the stuff yet.
├── pubmed-search
│   └── search.py
└── streamlit
    ├── main.py
    └── viime-extract-config.toml

experiments                     : TOML files outlining the experiments. The drive/reports likely reference these.
...

notebooks
├── chunked_extraction.ipynb    : chunked extraction experiments. Superceded by the langchain notebook.
├── fuzzy_chebi_db.ipynb        : fuzzy chebi matching experiments
├── langchain_exploration.ipynb : the langchain experiments. Precursor to the viime_extract python package.
└── schema.ipynb                : the first notebook containing experiments querying OpenAI's LLM.

viime_extract                   : the viime_extract package backing the scripts in bin/
├── config.py
├── extract.py
├── references.py
└── schema.py
```
