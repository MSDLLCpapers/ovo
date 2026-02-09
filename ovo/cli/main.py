import typer
from rich.panel import Panel
from ovo import console
from ovo.cli import init
from ovo.cli import module
from ovo.cli import app as app_cli
from ovo.cli import scheduler_cli
from ovo.cli.common import OVOCliError, print_ovo_logo


app = typer.Typer(
    pretty_exceptions_enable=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

app.add_typer(init.app, name="init")
app.add_typer(module.app, name="")
app.add_typer(app_cli.app, name="")
app.add_typer(scheduler_cli.app, name="scheduler")


def main():
    print_ovo_logo()

    try:
        app()
    except OVOCliError as e:
        console.print(Panel.fit(str(e), title="CLI Error", border_style="red"))


if __name__ == "__main__":
    main()
