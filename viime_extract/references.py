from pydantic import BaseModel, Field
from typing import Optional

from langchain_core.documents.base import Document
from langchain_core.language_models.chat_models import BaseChatModel

from viime_extract.config import Prompt


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
        return (
            []
            if self.references is None
            else [r for r in self.references if not r.incomplete]
        )


def extract_references(page: Document, model: BaseChatModel, prompt: Prompt):
    template = prompt.get_template()
    llm_input = template.invoke({"article_contents": page})
    return model.with_structured_output(References).invoke(llm_input)


def get_start_of_references_idx(
    pages: list[Document], model: BaseChatModel, prompt: Prompt
):
    for ridx, page in enumerate(pages[::-1]):
        refs = extract_references(page, model, prompt)
        if len(refs.complete_references) == 0:
            # pick the page index after the current page
            return len(pages) - ridx
    return 0
