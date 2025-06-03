from pathlib import Path
import csv
import heapq
import httpx
import click
import re
import jaro


def bigrams(s: str):
    return [s[i : i + 2] for i in range(len(s) - 1)]


def dice(a: str, b: str):
    a = set(bigrams(a.lower()))
    b = set(bigrams(b.lower()))
    return 2 * len(a & b) / (len(a) + len(b))


@click.group()
def cli():
    pass


def get_chebi_id(data):
    for line in data["InformationList"]["Information"][0]["SBURL"]:
        if "chebiId=CHEBI:" in line:
            return line.rsplit(":", 1)[1]


@cli.command()
@click.argument("pubchem_ids_file")
def pubchem_to_chebi(pubchem_ids_file: str):
    pubchem_ids_file: Path = Path(pubchem_ids_file)

    client = httpx.Client()

    lines = pubchem_ids_file.read_text(encoding="utf-8").splitlines()
    for pc_id in lines:
        if not re.fullmatch(r"\d+", pc_id):
            continue
        r = client.get(
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{pc_id}/xrefs/SBURL/JSON"
        )
        resp = r.json()
        chebi_id = get_chebi_id(resp)
        print(pc_id, chebi_id)


def load_chebi_database(file: Path):
    db = []
    with open(file, "r", encoding="utf-8") as fp:
        for line in fp:
            chebi_id, *names = line.split("\t")
            db.append({"ID": chebi_id, "NAMES": names})
    return db


@cli.command()
@click.argument("metabolite_names_txt")
@click.argument("chebi_database")
@click.option("--measure", default="dice", show_default=True)
@click.option("--top-k", default=3, type=int, show_default=True)
@click.option("--id-only", is_flag=True)
def name_to_chebi(
    metabolite_names_txt, chebi_database, measure="dice", top_k=3, id_only=False
):
    metabolite_names_txt = Path(metabolite_names_txt)
    chebi_database = Path(chebi_database)

    db = load_chebi_database(chebi_database)
    for name in metabolite_names_txt.read_text(encoding="utf-8").splitlines():
        heap = []
        for entry in db:
            for entry_name in entry["NAMES"]:
                entry_name = entry_name.strip()
                if measure == "dice":
                    dist = dice(name, entry_name)
                elif measure == "jaro":
                    dist = jaro.jaro_winkler_metric(name.lower(), entry_name.lower())
                else:
                    raise Exception("Invalid measure: " + measure)
                heapq.heappush(heap, (dist, entry_name, entry["ID"]))
                if len(heap) > 10:
                    heapq.heappop(heap)

        candidates = [heapq.heappop(heap) for _ in range(len(heap))][::-1]
        if len(candidates) == 0:
            print(f"{name}\t-")
            continue
        else:
            if id_only:
                top_k_str = "\t".join(
                    f"{chebi_id}" for score, chebi_name, chebi_id in candidates[:top_k]
                )
            else:
                top_k_str = "\t".join(
                    f"{chebi_name} {chebi_id}"
                    for score, chebi_name, chebi_id in candidates[:top_k]
                )

        print(f"{name}\t{top_k_str}")


@cli.command()
@click.argument("refmet_output_txt")
@click.option("--just-ids", is_flag=True, help="If set, only output ChEBI IDs")
def extract_refmet_chebi_ids(refmet_output_txt, just_ids=False):
    refmet_output_txt = Path(refmet_output_txt)

    for idx, line in enumerate(
        refmet_output_txt.read_text(encoding="utf-8").splitlines()
    ):
        if idx == 0:
            continue
        input_name, refmet_name, _, _, _, _, _, pubchem_id, chebi_id, *_ = line.split(
            "\t"
        )
        if just_ids:
            if re.fullmatch(r"\d+", chebi_id):
                print(chebi_id)
        else:
            print(f"{input_name}\t{chebi_id}")


# def load_refmet_db(file: Path):
#     data = json.loads(file.read_bytes())
#     db = []
#     for _, value in data.items():
#         db.append(value)

#     db.sort(key=lambda v: v["name"])
#     return db


# @cli.command()
# @click.argument("refmet_ids_file")
# @click.argument(
#     "refmet_db"
# )  # fetched via https://www.metabolomicsworkbench.org/rest/refmet/all_ids
# def refmet_to_chebi(refmet_ids_file, refmet_db):
#     refmet_ids_file: Path = Path(refmet_ids_file)
#     refmet_db: Path = Path(refmet_db)

#     db = load_refmet_db(refmet_db)

#     for refmet_id in refmet_ids_file.read_text(encoding="utf-8").splitlines():
#         bisect.bisect(db)


if __name__ == "__main__":
    cli()
