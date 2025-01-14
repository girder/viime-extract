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