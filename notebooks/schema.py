from pydantic import BaseModel, Field
from typing import List, Optional

class Person(BaseModel):
    """
    Represents a person.
    """
    firstname: str = Field(..., title="First name", description="The first name of the person.")
    middle_initial: Optional[str] = Field(None, title="Middle initial", description="The middle initial of the person if present.")
    surname: str = Field(..., title="Surname", description="The surname of the person.")
    affiliation: str = Field(..., title="Affiliation", description="The affiliation of the person.")

class Metabolite(BaseModel):
    """
    Represents a metabolite.
    """
    name: str = Field(..., title="Name", description="The name of the metabolite.")
    chebi_id: str = Field(..., title="ChEBI ID", description="The ChEBI ID of the metabolite.")

class Protein(BaseModel):
    """
    Represents a protein.
    """
    name: str = Field(..., title="Name", description="The name of the protein.")
    uniprot_id: str = Field(..., title="UniProt ID", description="The UniProt ID of the protein.")

class Gene(BaseModel):
    """
    Represents a gene.
    """
    name: str = Field(..., title="Name", description="The name of the gene.")
    entrez_id: str = Field(..., title="Entrez ID", description="The Entrez ID of the gene.")

class Pathway(BaseModel):
    """
    Represents a pathway.
    """
    name: str = Field(..., title="Name", description="The name of the pathway.")
    kegg_id: str = Field(..., title="KEGG ID", description="The KEGG ID of the pathway.")

class Drug(BaseModel):
    """
    Represents a drug.
    """
    name: str = Field(..., title="Name", description="The name of the drug.")
    guide_to_pharmacology_id: str = Field(..., title="Guide to Pharmacology ID", description="The Guide to Pharmacology ID of the drug.")

class Disease(BaseModel):
    """
    Represents a disease.
    """
    name: str = Field(..., title="Name", description="The name of the disease.")
    doid_id: str = Field(..., title="DOID ID", description="The DOID ID of the disease.")
    inhibiting_drugs: List[Drug] = Field(..., title="Inhibiting drugs", description="The drugs inhibiting the disease.")
    associated_genes: List[Gene] = Field(..., title="Associated genes", description="The genes associated with the disease.")
    associated_proteins: List[Protein] = Field(..., title="Associated proteins", description="The proteins associated with the disease.")
    associated_metabolites: List[Metabolite] = Field(..., title="Associated metabolites", description="The metabolites associated with the disease.")
    associated_pathways: List[Pathway] = Field(..., title="Associated pathways", description="The pathways associated with the disease.")

# class Regulation(BaseModel):
#     """
#     Represents a regulation.
#     """
#     regulator: str = Field(..., title="Regulator", description="The regulator of the regulation.")
#     target: str = Field(..., title="Target", description="The target of the regulation.")
#     type: str = Field(..., title="Type", description="The type of the regulation.")
#     evidence: str = Field(..., title="Evidence", description="The evidence of the regulation.")

class Drug(BaseModel):
    """
    Represents a drug.
    """
    name: str = Field(..., title="Name", description="The name of the drug.")
    pubchem_id: str = Field(..., title="PubChem ID", description="The PubChem ID of the drug.")

class ArticleFragment(BaseModel):
    """
    Represents information from a fragment of an article.
    """
    mentioned_metabolites: List[Metabolite] = Field(..., title="Mentioned metabolites", description="The metabolites mentioned in the article.")
    mentioned_proteins: List[Protein] = Field(..., title="Mentioned proteins", description="The proteins mentioned in the article.")
    mentioned_genes: List[Gene] = Field(..., title="Mentioned genes", description="The genes mentioned in the article.")
    mentioned_pathways: List[Pathway] = Field(..., title="Mentioned pathways", description="The pathways mentioned in the article.")
    mentioned_drugs: List[Drug] = Field(..., title="Mentioned drugs", description="The drugs mentioned in the article.")
    mentioned_diseases: List[Disease] = Field(..., title="Mentioned diseases", description="The diseases mentioned in the article.")

class Article(ArticleFragment):
    """
    Represents an article.
    """
    title: str = Field(..., title="Title", description="The title of the article.")
    journal: str = Field(..., title="Journal", description="The journal of the article.")
    year: int = Field(..., title="Year", description="The year of the article.")
    volume: str = Field(..., title="Volume", description="The volume of the article.")
    pubmed_id: str = Field(..., title="PubMed ID", description="The PubMed ID of the article.")
    authors: List[Person] = Field(..., title="Authors", description="The authors of the article.")
