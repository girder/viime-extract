import csv
import json
from pathlib import Path

import click


@click.group()
def cli(): ...


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--output-file", "-o", required=True, type=click.Path())
def as_csv(files: list[click.Path], output_file: click.Path):
    output = []

    for file in files:
        with open(file, "rb") as fp:
            data = json.load(fp)

        paper_fname = Path(file).stem
        title = data["meta"]["title"]
        doi = data["meta"]["doi_id"]
        metabolites = data["keywords"]["mentioned_metabolites"]
        proteins = data["keywords"]["mentioned_proteins"]
        genes = data["keywords"]["mentioned_genes"]
        pathways = data["keywords"]["mentioned_pathways"]
        drugs = data["keywords"]["mentioned_drugs"]
        diseases = data["keywords"]["mentioned_diseases"]

        assert title

        if not doi:
            if paper_fname == "001-012.pdf":
                doi = "10.26355/eurrev_202312_34684"
            else:
                raise Exception(f"no doi for paper {paper_fname}")

        for m in metabolites:
            output.append(
                {
                    "Title": title,
                    "DOI": doi,
                    "keyword": m["name"],
                    "keyword_type": "metabolite",
                }
            )

        for p in proteins:
            output.append(
                {
                    "Title": title,
                    "DOI": doi,
                    "keyword": p["name"],
                    "keyword_type": "protein",
                }
            )

        for g in genes:
            output.append(
                {
                    "Title": title,
                    "DOI": doi,
                    "keyword": g["name"],
                    "keyword_type": "gene",
                }
            )

        for p in pathways:
            output.append(
                {
                    "Title": title,
                    "DOI": doi,
                    "keyword": p["name"],
                    "keyword_type": "pathway",
                }
            )

        for d in drugs:
            output.append(
                {
                    "Title": title,
                    "DOI": doi,
                    "keyword": d["name"],
                    "keyword_type": "drug",
                }
            )

        for d in diseases:
            output.append(
                {
                    "Title": title,
                    "DOI": doi,
                    "keyword": d["name"],
                    "keyword_type": "disease",
                }
            )

    with open(output_file, "w", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp, fieldnames=["Title", "DOI", "keyword", "keyword_type"]
        )
        writer.writeheader()
        for row in output:
            writer.writerow(row)


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--output-file", "-o", required=True, type=click.Path())
def as_layoutr(files: list[click.Path], output_file: click.Path):
    nodes = []
    seen_nodes = set()
    edges = []

    for file in files:
        with open(file, "rb") as fp:
            data = json.load(fp)

        title = data["meta"]["title"]
        metabolites = data["keywords"]["mentioned_metabolites"]
        proteins = data["keywords"]["mentioned_proteins"]
        genes = data["keywords"]["mentioned_genes"]
        pathways = data["keywords"]["mentioned_pathways"]
        drugs = data["keywords"]["mentioned_drugs"]
        diseases = data["keywords"]["mentioned_diseases"]

        assert title

        nodes.append(
            {
                "id": title,
                "type": "paper",
                "x": 0,
                "y": 0,
            }
        )

        for m in metabolites:
            name = m["name"]
            key = f"{name}:metabolite"
            if key in seen_nodes:
                continue
            seen_nodes.add(key)
            nodes.append(
                {
                    "id": name,
                    "type": "metabolite",
                    "x": 0,
                    "y": 0,
                }
            )
            edges.append([title, name, 1])

        for p in proteins:
            name = p["name"]
            key = f"{name}:protein"
            if key in seen_nodes:
                continue
            seen_nodes.add(key)
            nodes.append(
                {
                    "id": name,
                    "type": "protein",
                    "x": 0,
                    "y": 0,
                }
            )
            edges.append([title, name, 1])

        for g in genes:
            name = g["name"]
            key = f"{name}:gene"
            if key in seen_nodes:
                continue
            seen_nodes.add(key)
            nodes.append(
                {
                    "id": name,
                    "type": "gene",
                    "x": 0,
                    "y": 0,
                }
            )
            edges.append([title, name, 1])

        for p in pathways:
            name = p["name"]
            key = f"{name}:pathway"
            if key in seen_nodes:
                continue
            seen_nodes.add(key)
            nodes.append(
                {
                    "id": name,
                    "type": "pathway",
                    "x": 0,
                    "y": 0,
                }
            )
            edges.append([title, name, 1])

        for d in drugs:
            name = d["name"]
            key = f"{name}:drug"
            if key in seen_nodes:
                continue
            seen_nodes.add(key)
            nodes.append(
                {
                    "id": name,
                    "type": "drug",
                    "x": 0,
                    "y": 0,
                }
            )
            edges.append([title, name, 1])

        for d in diseases:
            name = d["name"]
            key = f"{name}:disease"
            if key in seen_nodes:
                continue
            seen_nodes.add(key)
            nodes.append(
                {
                    "id": name,
                    "type": "disease",
                    "x": 0,
                    "y": 0,
                }
            )
            edges.append([title, name, 1])

    with open(output_file, "w", encoding="utf-8") as fp:
        json.dump(
            {
                "nodes": nodes,
                "links": edges,
            },
            fp,
        )


if __name__ == "__main__":
    cli()
