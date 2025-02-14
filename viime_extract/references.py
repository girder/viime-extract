from pydantic import BaseModel, Field
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents.base import Document
from langchain_core.language_models.chat_models import BaseChatModel


class Reference(BaseModel):
    refnum: Optional[int] = Field(
        title="Reference Number", description="The reference number", default=None
    )
    authors: Optional[list[str]] = Field(
        title="Authors", description="List of authors in a reference", default=None
    )
    title: Optional[str] = Field(
        title="Paper title", description="The reference paper title", default=None
    )
    journal: Optional[str] = Field(
        title="Journal",
        description="The journal in which the reference was published",
        default=None,
    )
    year: Optional[int] = Field(
        title="Paper year",
        description="The reference paper year of publication",
        default=None,
    )

    @property
    def incomplete(self):
        return any(
            getattr(self, prop) is None
            for prop in ["refnum", "authors", "title", "year", "journal"]
        )


class References(BaseModel):
    references: Optional[list[Reference]] = Field(
        title="Bibliographic reference",
        description="A bibliographic reference in an academic paper",
        default=None,
    )

    @property
    def complete_references(self):
        return [r for r in self.references if not r.incomplete]


def extract_references(page: Document, model: BaseChatModel):
    template = ChatPromptTemplate(
        [
            (
                "system",
                """You are an expert in extracting structured information from medical journal articles.
Present the extracted information in a clear, structured format. Be comprehensive and extract every single reference. You will be evaluated on the quality and completeness of the extracted information. If you are unsure if an entry is a reference, then do not include it.""",
            ),
            (
                "user",
                "Please list any references in this journal article, if there are any present:\n\n{article_contents}",
            ),
        ]
    )
    prompt = template.invoke({"article_contents": page})
    return model.with_structured_output(References).invoke(prompt)


def get_start_of_references_idx(pages: list[Document], model: BaseChatModel):
    for ridx, page in enumerate(pages[::-1]):
        refs = extract_references(page, model)
        if len(refs.complete_references) == 0:
            # pick the page index after the current page
            return len(pages) - ridx
    return 0
