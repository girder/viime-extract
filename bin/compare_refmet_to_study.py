import click
import pandas as pd


@click.command()
@click.argument("refmet_results")
@click.argument("study_xlsx")
def compare_refmet_to_study(refmet_results, study_xlsx):
    refmet_results = pd.read_csv(refmet_results, delimiter="\t")
    study = pd.read_excel(study_xlsx)

    study_names = study["RefMet Name"]
    study_metabolite_names = set(study_names[study_names != "-"])

    found_names = []
    valid_refmet_name_count = 0
    for name in refmet_results["Standardized name"]:
        if name == "-":
            continue
        valid_refmet_name_count += 1
        if name in study_metabolite_names:
            found_names.append(name)

    print(
        f"""
The RefMet results have {valid_refmet_name_count} valid RefMet names out of {len(refmet_results)} names.
Found {len(found_names)} out of {len(study_metabolite_names)} ({100 * len(found_names) / len(study_metabolite_names):.2f}%) metabolites listed in the study protocol.
In the study protocol, there are {study["RefMet Name"].eq("-").sum()} metabolites that do not list a standardized RefMet name, out of {len(study['RefMet Name'])} rows.

"""
    )


if __name__ == "__main__":
    compare_refmet_to_study()
