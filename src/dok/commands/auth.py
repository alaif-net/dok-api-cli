from __future__ import annotations

from typing import Annotated

import typer

from dok import output
from dok.client import DokClient
from dok.context import get_client

app = typer.Typer(help="認証・アカウント情報")


@app.command("show")
def show(ctx: typer.Context) -> None:
    """クラウドアカウント情報を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.get("/auth/")
    if fmt == "json":
        output.print_json(data)
    else:
        rows = [[str(v) for v in data.values()]]
        output.print_table(list(data.keys()), rows, title="アカウント情報")


@app.command("agree")
def agree(
    ctx: typer.Context,
    version: Annotated[str, typer.Option(help="同意する利用規約バージョン")] = "",
) -> None:
    """利用規約に同意する。"""
    client = get_client(ctx)
    params = {"version": version} if version else {}
    client.post("/auth/agree/", params=params)
    typer.echo("利用規約に同意しました。")
