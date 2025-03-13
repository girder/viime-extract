from logging import getLogger

from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents.base import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_text_splitters.base import TextSplitter

from viime_extract.schema import Article, ArticleKeyWords, ArticleMeta
from viime_extract.config import (
    Prompt,
    DetectReferencesPrompt,
    ArticleKeywordsPrompt,
    ArticleMetadataPrompt,
)
from viime_extract.references import get_start_of_references_idx

logging = getLogger(__name__)


def extract_article_metadata(
    pages: list[Document], model: BaseChatModel, prompt: Prompt
):
    # assumption: first page contains all of the metadata
    first_page = pages[0].page_content

    template = prompt.get_template()
    llm_input = template.invoke({"article_contents": first_page})
    return model.with_structured_output(ArticleMeta).invoke(llm_input)


def extract_article_keywords(
    pages: list[Document], model: BaseChatModel, splitter: TextSplitter, prompt: Prompt
):
    template = prompt.get_template()
    keywords = ArticleKeyWords()
    for text_chunk in splitter.split_documents(pages):
        llm_input = template.invoke({"article_contents": text_chunk.page_content})
        response = model.with_structured_output(ArticleKeyWords).invoke(llm_input)
        keywords = keywords.merge(response)

    # TODO duplicate removal
    return keywords


def extract_article_from_document_loader(
    *,
    model: BaseChatModel,
    splitter: TextSplitter,
    doc_loader: BaseLoader,
    detect_references_prompt: DetectReferencesPrompt,
    article_metadata_prompt: ArticleMetadataPrompt,
    article_keywords_prompt: ArticleKeywordsPrompt,
    without_references=False,
):
    pages = list(doc_loader.lazy_load())
    if without_references:
        limit = get_start_of_references_idx(pages, model, detect_references_prompt)
        logging.info("Ignoring pages starting with index %d", limit)
    else:
        limit = len(pages)
    meta = extract_article_metadata(pages[:limit], model, article_metadata_prompt)
    keywords = extract_article_keywords(
        pages[:limit], model, splitter, article_keywords_prompt
    )
    return Article(meta=meta, keywords=keywords)
