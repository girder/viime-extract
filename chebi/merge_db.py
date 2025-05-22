import click
import io
import csv


@click.command()
@click.argument("compounds_tsv")
@click.argument("names_tsv")
def merge_db(compounds_tsv, names_tsv):
    db = {}
    with open(compounds_tsv, "r", encoding="latin-1") as fp:
        reader = csv.DictReader(fp, delimiter="\t")
        for row in reader:
            if row["NAME"] == "null":
                continue
            db[int(row["ID"])] = [row["NAME"]]

    with open(names_tsv, "r", encoding="latin-1") as fp:
        reader = csv.DictReader(fp, delimiter="\t")
        for row in reader:
            db[int(row["COMPOUND_ID"])].append(row["NAME"])

    for key, names in db.items():
        print(f'{key}\t{"\t".join(names)}')


if __name__ == "__main__":
    merge_db()
