Parameters:
- PyPDF
- gpt-4o-2024-08-06, temperature=0
- RecursiveCharacterTextSplitter.from_tiktoken_encoder(model_name=gpt-4o-2024-08-06, chunk_size=1024, chunk_overlap=128)

ArticleMeta system message:
> You are an expert in extracting structured information from medical journal articles.
> Present the extracted information in a clear, structured format. Be comprehensive and extract every single
> mentioned entity. You will be evaluated on the quality and completeness of the extracted information.

ArticleMeta user message:
> Please extract the title, authors, journal title, publication year, journal volume, DOI ID, and pubmed ID from the following journal article:\n\n{article_contents}

ArticleKeyWords system message:
> You are an expert in extracting structured information from medical journal articles.
> Present the extracted information in a clear, structured format. Be comprehensive and extract every single
> mentioned entity. You will be evaluated on the quality and completeness of the extracted information.
>
> If you are not confident in the identifier for an entity, you can specify it as "unknown". It is better
> to include an entity with an "unknown" identified than to omit it entirely.

ArticleKeyWords user message:
> Please extract the metabolites, proteins, genes, pathways, drugs, and diseases mentioned in the following journal article:\n\n{article_contents}