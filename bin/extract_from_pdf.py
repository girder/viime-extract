import logging
import sys
from argparse import ArgumentParser, Namespace
from logging import getLogger
from pathlib import Path

import dotenv
import tomllib
from langchain_openai import ChatOpenAI

sys.path.append(str(Path(__file__).parent / ".."))

from viime_extract.pdf_extract import extract_article_from_document_loader
from viime_extract.config import Config

logging.basicConfig(level=logging.INFO)
logger = getLogger(Path(__file__).name)


class UserInputError(RuntimeError): ...


class ProgArgs(Namespace):
    pdf_file: Path
    config: Path
    output: str | None


def parse_args() -> ProgArgs:
    parser = ArgumentParser(
        description="Extract important information from a journal article PDF."
    )
    parser.add_argument("pdf_file", type=Path, help="The PDF file to parse")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        help="The TOML config file to use",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output results to a file",
    )

    return parser.parse_args()


def main(args: ProgArgs):
    if not args.pdf_file.exists():
        raise UserInputError(f'"{args.pdf_file}" does not exist')
    if not args.pdf_file.is_file():
        raise UserInputError(f'"{args.pdf_file}" is not a file')

    config = Config()

    if args.config:
        with open(args.config, "rb") as fp:
            config = Config.model_validate(tomllib.load(fp))

    logger.info('Extracting structured information from "%s"', args.pdf_file)

    model = ChatOpenAI(model=config.model_name, temperature=config.temperature)
    article = extract_article_from_document_loader(
        doc_loader=config.pdf_loader.create_loader(args.pdf_file),
        model=model,
        splitter=config.text_splitter.create_splitter(),
        without_references=config.extractor.without_references,
    )
    article_json = article.model_dump_json(indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fp:
            fp.write(article_json)
    else:
        print(article_json)


if __name__ == "__main__":
    dotenv.load_dotenv()

    try:
        main(parse_args())
    except UserInputError as exc:
        print("Usage error:", " ".join(exc.args), file=sys.stderr)
        sys.exit(1)
