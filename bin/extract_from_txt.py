import logging
import sys
from argparse import ArgumentParser, Namespace
from logging import getLogger
from pathlib import Path
import json
from typing import Iterator

import dotenv
import tomllib
from langchain_openai import ChatOpenAI
from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents.base import Document

sys.path.append(str(Path(__file__).parent / ".."))

from viime_extract.pdf_extract import extract_article_from_document_loader
from viime_extract.config import Config

logging.basicConfig(level=logging.INFO)
logger = getLogger(Path(__file__).name)


class UserInputError(RuntimeError): ...


class TextFileDocumentLoader(BaseLoader):
    """Document loader for a specific kind of formatted text file.

    The text file is the following two structures, repeated:

        { "page": int, "source": str }
        <content>
    """

    _file: Path | str

    def __init__(self, file: Path | str):
        super().__init__()
        self._file = file

    def _read_page_meta(self, line: str) -> bool:
        try:
            data = json.loads(line.replace("'", '"'))
            if isinstance(data, dict) and "page" in data and "source" in data:
                return data
            return None
        except json.decoder.JSONDecodeError:
            return None

    def lazy_load(self) -> Iterator[Document]:
        contents = Path(self._file).read_text(encoding="utf-8")
        linegen = iter(contents.strip().split("\n"))

        # skip lines until we get to the first page marker
        for line in linegen:
            page_meta = self._read_page_meta(line)
            if page_meta:
                break

        cur_page_meta = page_meta
        page = []
        for line in linegen:
            if not line.strip():
                continue

            page_meta = self._read_page_meta(line)
            if page_meta:
                yield Document("\n".join(page), metadata=cur_page_meta)
                cur_page_meta = page_meta
                page = []
            else:
                page.append(line)

        if page:
            yield Document("\n".join(page), metadata=cur_page_meta)


class ProgArgs(Namespace):
    file: Path
    config: Path
    output: str | None


def parse_args() -> ProgArgs:
    parser = ArgumentParser(
        description="Extract important information from a journal article PDF."
    )
    parser.add_argument(
        "file",
        type=Path,
        default=Path(__file__).parent.parent / "data/MolGenetMetab_136_306_2022.txt",
        help="The text file to parse.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        help="The TOML config file to use. NOTE: the pdf_loader section does not apply to this command.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output results to a file",
    )

    return parser.parse_args()


def main(args: ProgArgs):
    if not args.file.exists():
        raise UserInputError(f'"{args.pdf_file}" does not exist')
    if not args.file.is_file():
        raise UserInputError(f'"{args.pdf_file}" is not a file')

    config = Config()

    if args.config:
        with open(args.config, "rb") as fp:
            config = Config.model_validate(tomllib.load(fp))

    logger.info('Extracting structured information from "%s"', args.file)

    model = ChatOpenAI(model=config.model_name, temperature=config.temperature)
    article = extract_article_from_document_loader(
        doc_loader=TextFileDocumentLoader(args.file),
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
