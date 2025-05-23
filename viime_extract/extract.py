from logging import getLogger
from concurrent.futures import Executor, ThreadPoolExecutor, as_completed

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


def extract_article_metadata_with_executor(
    pages: list[Document], model: BaseChatModel, prompt: Prompt, executor: Executor
):
    return executor.submit(extract_article_metadata, pages, model, prompt).result()


def extract_article_keywords_from_doc(
    doc: Document, model: BaseChatModel, prompt: Prompt
):
    template = prompt.get_template()
    llm_input = template.invoke({"article_contents": doc.page_content})
    return model.with_structured_output(ArticleKeyWords).invoke(llm_input)


def extract_article_keywords(
    pages: list[Document], model: BaseChatModel, splitter: TextSplitter, prompt: Prompt
):
    keywords = ArticleKeyWords()
    for text_chunk in splitter.split_documents(pages):
        response = extract_article_keywords_from_doc(text_chunk, model, prompt)
        keywords = keywords.merge(response)

    # TODO duplicate removal
    return keywords


def extract_article_keywords_with_executor(
    pages: list[Document],
    model: BaseChatModel,
    splitter: TextSplitter,
    prompt: Prompt,
    executor: Executor,
):
    keywords = ArticleKeyWords()
    futures = [
        executor.submit(extract_article_keywords_from_doc, text_chunk, model, prompt)
        for text_chunk in splitter.split_documents(pages)
    ]

    for future in as_completed(futures):
        keywords = keywords.merge(future.result())

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
    with ThreadPoolExecutor(max_workers=4) as executor:
        pages = list(doc_loader.lazy_load())
        if without_references:
            limit = get_start_of_references_idx(pages, model, detect_references_prompt)
            logging.info("Ignoring pages starting with index %d", limit)
        else:
            limit = len(pages)

        if limit == 0:
            limit = len(pages)

        meta_future = executor.submit(
            extract_article_metadata, pages[:limit], model, article_metadata_prompt
        )
        keywords = extract_article_keywords_with_executor(
            pages[:limit], model, splitter, article_keywords_prompt, executor
        )
        return Article(meta=meta_future.result(), keywords=keywords)
