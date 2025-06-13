import click
import json
from pathlib import Path
import csv


@click.group()
def cli(): ...


@cli.command()
@click.option("--abstracts-csv", "-a", type=click.Path(exists=True), required=True)
@click.option("--results-json", "-r", type=click.Path(exists=True), required=True)
@click.option("--output-csv", "-o", type=click.Path(), required=True)
def as_csv(abstracts_csv: click.Path, results_json: click.Path, output_csv: click.Path):
    results_json = json.loads(Path(results_json).read_bytes())
    output = []
    with open(abstracts_csv, "r", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            pmid = row["PMID"]
            abstract_result = results_json[pmid]

            for m in abstract_result["mentioned_metabolites"] or []:
                output.append(
                    {
                        **row,
                        "keyword": m["name"],
                        "keyword_type": "metabolite",
                    }
                )

            for g in abstract_result.get("mentioned_genes", []) or []:
                output.append(
                    {
                        **row,
                        "keyword": g["name"],
                        "keyword_type": "gene",
                    }
                )

            for p in abstract_result.get("mentioned_pathways", []) or []:
                output.append(
                    {
                        **row,
                        "keyword": p["name"],
                        "keyword_type": "pathway",
                    }
                )

            for d in abstract_result.get("mentioned_drugs", []) or []:
                output.append(
                    {
                        **row,
                        "keyword": d["name"],
                        "keyword_type": "drug",
                    }
                )

            for ds in abstract_result.get("mentioned_diseases", []) or []:
                output.append(
                    {
                        **row,
                        "keyword": ds["name"],
                        "keyword_type": "disease",
                    }
                )

            for pr in abstract_result.get("mentioned_proteins", []) or []:
                output.append(
                    {
                        **row,
                        "keyword": pr["name"],
                        "keyword_type": "protein",
                    }
                )

        with open(output_csv, "w", encoding="utf-8", newline="") as out_fp:
            fieldnames = reader.fieldnames + ["keyword", "keyword_type"]
            writer = csv.DictWriter(out_fp, fieldnames=fieldnames)
            writer.writeheader()
            for row in output:
                writer.writerow(row)


@cli.command()
@click.option("--abstracts-csv", "-a", type=click.Path(exists=True), required=True)
@click.option("--results-json", "-r", type=click.Path(exists=True), required=True)
@click.option("--output-json", "-o", type=click.Path(), required=True)
def as_layoutr(
    abstracts_csv: click.Path, results_json: click.Path, output_json: click.Path
):
    results_json = json.loads(Path(results_json).read_bytes())
    pmid_to_title = {}
    with open(abstracts_csv, "r", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            pmid = row["PMID"]
            pmid_to_title[pmid] = row["Title"]

    nodes = [
        {
            "id": title,
            "type": "paper",
            "x": 0,
            "y": 0,
        }
        for title in pmid_to_title.values()
    ]
    seen_nodes = set(f"{e['id']}:{e['type']}" for e in nodes)
    edges = []

    for pmid, abstract_result in results_json.items():
        title = pmid_to_title[pmid]

        for m in abstract_result["mentioned_metabolites"] or []:
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

        for pr in abstract_result.get("mentioned_proteins", []) or []:
            name = pr["name"]
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

        for g in abstract_result.get("mentioned_genes", []) or []:
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

        for p in abstract_result.get("mentioned_pathways", []) or []:
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

        for ds in abstract_result.get("mentioned_diseases", []) or []:
            name = ds["name"]
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

        for d in abstract_result.get("mentioned_drugs", []) or []:
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

    with open(output_json, "w", encoding="utf-8", newline="") as out_fp:
        json.dump(
            {
                "nodes": nodes,
                "links": edges,
            },
            out_fp,
        )


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    cli()
