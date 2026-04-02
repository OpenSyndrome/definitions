"""Annotate definitions"""

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
    grounder: ssslm.Grounder = pyobo.get_grounder("doid")
    for path in ROOT.joinpath("definitions", "v1").glob("**/*.json"):
        data = json.loads(path.read_text())
        title = data["title"]
        match = grounder.get_best_match(title)
        if not match and "(" in title:
            match = grounder.get_best_match(title.split("(")[0])

        if match:
            rows.append((title, match.curie, match.name))
        else:
            rows.append((title, "", ""))

        for inclusion_criteria in data.get("inclusion_criteria", []):
            _work_criteria(title, inclusion_criteria, grounder)

    click.echo(tabulate(rows, headers=['title', 'doid-curie', 'doid-name'], tablefmt="github"))


def _work_criteria(title, data, grounder: ssslm.Grounder):
    match data['type']:
        case 'criterion':
            for value in data['values']:
                _work_criteria(title, value, grounder)
        case 'symptom' | "syndrome":
            name = data['name']
            match = grounder.get_best_match(name)
            if match:
                print(title, data['type'], match.curie, match.name)
        case "diagnosis":
            name = data['name']
            match = grounder.get_best_match(name)
            # TODO 'code': {'system': 'ICD-10', 'code': 'A92.9'}}
            if match:
                print(title, data['type'], match.curie, match.name)
        case "professional_judgment" | "diagnostic_test":
            name = data['name']
            for annotation in grounder.annotate(name):
                print(title, data['type'], annotation.curie, annotation.name)
        case "demographic_criteria" | "epidemiological_history":
            pass
        case _ as e:
            raise NotImplementedError(e, data)


if __name__ == '__main__':
    main()
