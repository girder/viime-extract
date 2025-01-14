from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents.base import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters.base import TextSplitter

from viime_extract.schema import Article, ArticleKeyWords, ArticleMeta


def extract_article_metadata(pages: list[Document], model: BaseChatModel):
    # assumption: first page contains all of the metadata
    first_page = pages[0].page_content

    template = ChatPromptTemplate(
        [
            (
                "system",
                """You are an expert in extracting structured information from medical journal articles.
Present the extracted information in a clear, structured format. Be comprehensive and extract every single
mentioned entity. You will be evaluated on the quality and completeness of the extracted information.""",
            ),
            (
                "user",
                "Please extract the title, authors, journal title, publication year, "
                + "journal volume, DOI ID, and pubmed ID from the following journal article:"
                + "\n\n"
                + "{article_contents}",
            ),
        ]
    )
    prompt = template.invoke({"article_contents": first_page})
    return model.with_structured_output(ArticleMeta).invoke(prompt)


def extract_article_keywords(
    pages: list[Document], model: BaseChatModel, splitter: TextSplitter
):
    template = ChatPromptTemplate(
        [
            (
                "system",
                """You are an expert in extracting structured information from medical journal articles.
Present the extracted information in a clear, structured format. Be comprehensive and extract every single
mentioned entity. You will be evaluated on the quality and completeness of the extracted information.

If you are not confident in the identifier for an entity, you can specify it as "unknown". It is better
to include an entity with an "unknown" identified than to omit it entirely.""",
            ),
            (
                "user",
                "Please extract the metabolites, proteins, genes, pathways, drugs, "
                + "and diseases mentioned in the following journal article:"
                + "\n\n"
                + "{article_contents}",
            ),
        ]
    )

    keywords = ArticleKeyWords()
    for text_chunk in splitter.split_documents(pages):
        prompt = template.invoke({"article_contents": text_chunk})
        response = model.with_structured_output(ArticleKeyWords).invoke(prompt)
        keywords = keywords.merge(response)

    # TODO duplicate removal
    return keywords


def extract_article_from_document_loader(
    *,
    model: BaseChatModel,
    splitter: TextSplitter,
    doc_loader: BaseLoader,
):
    pages = list(doc_loader.lazy_load())
    meta = extract_article_metadata(pages, model)
    keywords = extract_article_keywords(pages, model, splitter)
    return Article(meta=meta, keywords=keywords)
