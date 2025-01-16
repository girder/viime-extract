import langchain_text_splitters
from langchain_community import document_loaders
from langchain_community.document_loaders.base import BaseLoader
from langchain_text_splitters.base import TextSplitter
from pydantic import BaseModel, Field, field_validator


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
