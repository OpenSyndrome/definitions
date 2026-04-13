# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "click>=8.3.1",
#     "pyobo[gilda-slim]>=0.12.18",
#     "ssslm[gilda-slim]>=0.1.3",
#     "tabulate>=0.10.0",
# ]
# ///

"""
This script will use various natural language processing (NLP)
methods to annotate various aspects of the OpenSyndromes
definitions using ontologies and databases exposed through
PyOBO.

Run using ``uv`` with ``uv run annotate.py``. This will
automatically download and cache relevant ontologies
and databases on first run, so be patient.
"""

from pathlib import Path
import json
from tabulate import tabulate
import click
import pyobo
import ssslm

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve()


@click.command()
def main() -> None:
    rows = []
    organization_grounder = pyobo.get_grounder("ror")
    location_grounder = pyobo.get_grounder("geonames")
    disease_symptom_grounder: ssslm.Grounder = pyobo.get_grounder(["doid", "hpo"])
    for path in ROOT.joinpath("definitions", "v1").glob("**/*.json"):
        click.echo(f"\n==== Processing {path.name}")
        data = json.loads(path.read_text())
        title = data["title"]
        match = disease_symptom_grounder.get_best_match(title)
        if not match and "(" in title:
            match = disease_symptom_grounder.get_best_match(title.split("(")[0])
        if match:
            print(f"matched title: {match}")
            rows.append((title, match.curie, match.name))
        else:
            rows.append((title, "", ""))

        if organization_matches := organization_grounder.get_matches(
            data["organization"]
        ):
            if len(organization_matches) == 1:
                click.echo(f"matched unique organization: {organization_matches[0]}")
            else:
                click.echo(f"matched {len(organization_matches)} organizations")

        if location_match := location_grounder.get_matches(data["location"]):
            click.echo(f"matched location: {location_match}")

        for inclusion_criteria in data.get("inclusion_criteria", []):
            _recurse_over_criteria(inclusion_criteria, disease_symptom_grounder)
        for exclusion_criteria in data.get("exclusion_criteria", []):
            _recurse_over_criteria(exclusion_criteria, disease_symptom_grounder)

        for threat in data.get("target_public_health_threats", []):
            if threat_match := disease_symptom_grounder.get_best_match(threat):
                click.echo(f"matched threat: {threat_match}")

    click.echo("\nSummary table of all title matches:\n\n")
    click.echo(
        tabulate(rows, headers=["title", "doid-curie", "doid-name"], tablefmt="github")
    )


def _recurse_over_criteria(record, grounder: ssslm.Grounder):
    match record["type"]:
        case "criterion":
            for value_record in record["values"]:
                _recurse_over_criteria(value_record, grounder)
        case "symptom" | "syndrome":
            name = record["name"]
            match = grounder.get_best_match(name)
            if match:
                print("matched", record["type"], match.curie, match.name)
        case "diagnosis":
            name = record["name"]
            match = grounder.get_best_match(name)
            # TODO 'code': {'system': 'ICD-10', 'code': 'A92.9'}}
            if match:
                print("matched", record["type"], match.curie, match.name)
        case "professional_judgment" | "diagnostic_test":
            name = record["name"]
            for annotation in grounder.annotate(name):
                print("matched", record["type"], annotation.curie, annotation.name)
        case "demographic_criteria" | "epidemiological_history":
            pass
        case _ as e:
            raise NotImplementedError(e, record)


if __name__ == "__main__":
    main()
