from chembl_webresource_client.new_client import new_client
import sys


def main():
    molecule = new_client.molecule

    mols = molecule.filter(pref_name__icontains="aspirin").only("pref_name")
    for m in mols:
        print(m["pref_name"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
