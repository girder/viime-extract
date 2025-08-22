import logging
import json
import csv
import sys
from logging import getLogger
import tomllib
from pathlib import Path

import dotenv
import click
from langchain_openai import ChatOpenAI
from langchain_core.documents.base import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

sys.path.append("../../")

from viime_extract.schema import ArticleKeyWords

sys.path.append(str(Path(__file__).parent.parent.parent))

from viime_extract.extract import extract_article_keywords_from_doc
from viime_extract.config import Config

logging.basicConfig(level=logging.INFO)
logger = getLogger(Path(__file__).name)


@click.command()
@click.argument("csv_file")
@click.option("-c", "--config-file")
@click.option("-o", "--output-file")
def main(csv_file: str, config_file: str, output_file: str):
    with open(config_file, "rb") as fp:
        config = Config.model_validate(tomllib.load(fp))

    outputs = dict()

    with open(csv_file, "r", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            print("Working on:", row["PMID"], f"(processed {len(outputs)})")
            model = ChatOpenAI(model=config.model_name, temperature=0)
            doc = Document(row["Abstract"])
            splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=0)
            keywords = ArticleKeyWords()
            for chunk in splitter.split_documents([doc]):
                keywords = keywords.merge(
                    extract_article_keywords_from_doc(
                        chunk, model, config.prompts.article_keywords
                    )
                )

            outputs[row["PMID"]] = json.loads(keywords.model_dump_json())

            with open(output_file, "w") as fp:
                fp.write(json.dumps(outputs))


if __name__ == "__main__":
    dotenv.load_dotenv()

    # pylint: disable=no-value-for-parameter
    main()
