import os
from pathlib import Path

import requests
from Bio import Entrez
from tqdm import tqdm

Entrez.email = "jeff.baumes@kitware.com"
# ENTREZ_API_KEY = "9201c5ba986bf916829ca1002df834dc5808"
query = '"covid" AND metabolomics NOT review[Publication Type] AND English[Language]'
downloads_folder = "pubmed_articles"


def get_pubmed_article_count(query):
    handle = Entrez.esearch(db="pubmed", term=query, retmax=1000)
    record = Entrez.read(handle)
    handle.close()
    return int(record["Count"]), record.get(
        "IdList", []
    )  # Returns count and list of PubMed IDs


count, pubmed_ids = get_pubmed_article_count(query)
print(f"\nQuery: {query}")
print(f"Articles Available in PubMed: {count}")

os.makedirs(downloads_folder, exist_ok=True)


def get_pmc_articles(pubmed_ids):
    if not pubmed_ids:
        return []

    query_pmc = " OR ".join(pubmed_ids)

    handle = Entrez.esearch(db="pmc", term=query_pmc, retmax=1000)
    pmc_record = Entrez.read(handle)
    pmc_id_set = pmc_record.get("IdList", [])  # Only return PMC IDs that exist
    handle.close()

    return pmc_id_set


pmc_ids = get_pmc_articles(pubmed_ids)


def get_pmc_pdf_url(pmc_id):
    pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/pdf/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(pdf_url, headers=headers, allow_redirects=True)
    if response.status_code == 200 and "pdf" in response.headers.get(
        "Content-Type", ""
    ):
        return pdf_url
    return None


def download_pdf(pmc_id, pdf_url, category_folder):
    os.makedirs(category_folder, exist_ok=True)
    pdf_path = os.path.join(category_folder, f"PMC{pmc_id}.pdf")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(pdf_url, headers=headers, stream=True, timeout=30)

    content_type = response.headers.get("Content-Type", "")
    if "pdf" not in content_type:
        print(f"Skipping PMC{pmc_id} - Invalid file format.")
        return

    total_size = int(response.headers.get("content-length", 0))
    with open(pdf_path, "wb") as file, tqdm(
        desc=f"Downloading PMC{pmc_id}",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
            bar.update(len(chunk))

    if (
        os.path.getsize(pdf_path) < 1000
    ):  # If file size is too small, assume it's corrupted
        print(f"Deleting incomplete file: PMC{pmc_id}.pdf")
        os.remove(pdf_path)


count = len(pmc_ids)
print(f"\nSearching for {count} matching PMC articles for query: {query}")

if count == 0:
    print(f"No full-text articles available in PMC for '{query}'.")

for pmc_id in pmc_ids:
    pdf_url = get_pmc_pdf_url(pmc_id)
    if pdf_url:
        download_pdf(pmc_id, pdf_url, downloads_folder)
    else:
        print(f"No PDF available for PMC{pmc_id}.")

print("\nDownload Complete! Articles are saved in 'Downloads/PubMed Articles/'.")
