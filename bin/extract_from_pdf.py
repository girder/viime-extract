import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from logging import getLogger

import dotenv

from langchain_openai import ChatOpenAI

sys.path.append(str(Path(__file__).parent / ".."))
from viime_extract.pdf_extract import extract_article_from_pdf

logger = getLogger(__name__)


class UserInputError(RuntimeError): ...


class ProgArgs(Namespace):
    pdf_file: Path
    openai_model: str
    output: str | None


def parse_args() -> ProgArgs:
    parser = ArgumentParser(
        description="Extract important information from a journal article PDF."
    )
    parser.add_argument("pdf_file", type=Path, help="The PDF file to parse")
    parser.add_argument(
        "--openai-model",
        type=str,
        help="The OpenAI model to use",
        default="gpt-4o-2024-08-06",
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

    logger.info('Extracting structured information from "%s"', args.pdf_file)

    model = ChatOpenAI(model=args.openai_model, temperature=0)
    article = extract_article_from_pdf(args.pdf_file, model)
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
