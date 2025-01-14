import logging
import sys
from argparse import ArgumentParser, Namespace
from logging import getLogger
from pathlib import Path

import dotenv
import langchain_text_splitters
import tomllib
from langchain_community import document_loaders
from langchain_community.document_loaders.base import BaseLoader
from langchain_openai import ChatOpenAI
from langchain_text_splitters.base import TextSplitter
from pydantic import BaseModel, Field, field_validator

sys.path.append(str(Path(__file__).parent / ".."))

from viime_extract.pdf_extract import extract_article_from_document_loader

logging.basicConfig(level=logging.INFO)
logger = getLogger(Path(__file__).name)


class UserInputError(RuntimeError): ...


class ProgArgs(Namespace):
    pdf_file: Path
    config: Path
    output: str | None


class PDFLoaderConfig(BaseModel):
    class_name: str = "PyPDFLoader"

    @field_validator("class_name", mode="after")
    @classmethod
    def is_valid_loader(cls, name: str) -> str:
        if not hasattr(document_loaders, name):
            raise ValueError(
                f"{name} is not a valid langchain_community document loader"
            )
        return name

    def create_loader(self, *args, **kwargs) -> BaseLoader:
        return getattr(document_loaders, self.class_name)(*args, **kwargs)


class TextSplitterConfig(BaseModel):
    class_name: str = "RecursiveCharacterTextSplitter"
    from_tiktoken_encoder: bool = False
    chunk_size: int = 1024
    chunk_overlap: int = 128

    @field_validator("class_name", mode="after")
    @classmethod
    def is_valid_loader(cls, name: str) -> str:
        if not hasattr(langchain_text_splitters, name):
            raise ValueError(
                f"{name} is not a valid langchain_text_splitters text splitter"
            )
        return name

    def create_splitter(self, *args, **kwargs) -> TextSplitter:
        klass: TextSplitter = getattr(langchain_text_splitters, self.class_name)
        if self.from_tiktoken_encoder:
            return klass.from_tiktoken_encoder(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                *args,
                **kwargs,
            )
        return klass(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            *args,
            **kwargs,
        )


class Config(BaseModel):
    model_name: str = "gpt-4o"
    temperature: float = 0
    pdf_loader: PDFLoaderConfig = Field(default_factory=PDFLoaderConfig)
    text_splitter: TextSplitterConfig = Field(default_factory=TextSplitterConfig)


def parse_args() -> ProgArgs:
    parser = ArgumentParser(
        description="Extract important information from a journal article PDF."
    )
    parser.add_argument("pdf_file", type=Path, help="The PDF file to parse")
    parser.add_argument(
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
