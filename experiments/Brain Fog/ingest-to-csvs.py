import csv
import json
from collections import defaultdict
from pathlib import Path

import click


@click.command()
@click.option("-i", "--input-json", type=click.Path(exists=True))
@click.option("-o", "--output-dir")
def main(input_json: click.Path, output_dir: click.Path):
    input_json = Path(input_json)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_metabolites = defaultdict(list)
    all_proteins = defaultdict(list)
    all_genes = defaultdict(list)
    all_pathways = defaultdict(list)
    all_drugs = defaultdict(list)
    all_diseases = defaultdict(list)

    input_data = json.loads(input_json.read_bytes())
    for pmid, entities in input_data.items():
        metabolites = entities["mentioned_metabolites"] or []
        proteins = entities["mentioned_proteins"] or []
        genes = entities["mentioned_genes"] or []
        pathways = entities["mentioned_pathways"] or []
        drugs = entities["mentioned_drugs"] or []
        diseases = entities["mentioned_diseases"] or []

        for m in metabolites:
            name = m["name"].lower()
            all_metabolites[name].append(pmid)

        for p in proteins:
            name = p["name"].lower()
            all_proteins[name].append(pmid)

        for g in genes:
            name = g["name"].lower()
            all_genes[name].append(pmid)

        for p in pathways:
            name = p["name"].lower()
            all_pathways[name].append(pmid)

        for d in drugs:
            name = d["name"].lower()
            all_drugs[name].append(pmid)

        for d in diseases:
            name = d["name"].lower()
            all_diseases[name].append(pmid)

    with open(output_dir / "metabolites.csv", "w", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["metabolite", "paper_dois"])
        writer.writeheader()
        for metabolite in sorted(all_metabolites.items(), key=lambda a: a[0]):
            writer.writerow(
                {"metabolite": metabolite[0], "paper_dois": ";".join(metabolite[1])}
            )

    with open(output_dir / "proteins.csv", "w", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["protein", "paper_dois"])
        writer.writeheader()
        for protein in sorted(all_proteins.items(), key=lambda a: a[0]):
            writer.writerow({"protein": protein[0], "paper_dois": ";".join(protein[1])})

    with open(output_dir / "genes.csv", "w", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["gene", "paper_dois"])
        writer.writeheader()
        for gene in sorted(all_genes.items(), key=lambda a: a[0]):
            writer.writerow({"gene": gene[0], "paper_dois": ";".join(gene[1])})

    with open(output_dir / "pathways.csv", "w", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["pathway", "paper_dois"])
        writer.writeheader()
        for pathway in sorted(all_pathways.items(), key=lambda a: a[0]):
            writer.writerow({"pathway": pathway[0], "paper_dois": ";".join(pathway[1])})

    with open(output_dir / "drugs.csv", "w", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["drug", "paper_dois"])
        writer.writeheader()
        for drug in sorted(all_drugs.items(), key=lambda a: a[0]):
            writer.writerow({"drug": drug[0], "paper_dois": ";".join(drug[1])})

    with open(output_dir / "diseases.csv", "w", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["disease", "paper_dois"])
        writer.writeheader()
        for disease in sorted(all_diseases.items(), key=lambda a: a[0]):
            writer.writerow({"disease": disease[0], "paper_dois": ";".join(disease[1])})


if __name__ == "__main__":
    main()
