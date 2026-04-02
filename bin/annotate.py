"""Annotate definitions"""

from pathlib import Path
import json
from tabulate import tabulate
import click
import pyobo

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve()


@click.command()
def main() -> None:
    rows = []
    grounder = pyobo.get_grounder("doid")
    for path in ROOT.joinpath("definitions", "v1").glob("**/*.json"):
        data = json.loads(path.read_text())
        title = data["title"]
        match = grounder.get_best_match(title)
        if match:
            rows.append((path.name, title, match.curie, match.name))
        else:
            rows.append((path.name, title, "", ""))
    click.echo(tabulate(rows, headers=['path', 'title', 'doid-curie', 'doid-name'], tablefmt="github"))


if __name__ == '__main__':
    main()
