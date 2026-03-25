from __future__ import annotations

import typer

from dok import output
from dok.client import DokClient
from dok.context import get_client

app = typer.Typer(help="GPUプラン")


@app.command("list")
def list_plans(ctx: typer.Context) -> None:
    """利用可能なGPUプランの一覧を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.get("/plans/")
    if fmt == "json":
        output.print_json(data)
    else:
        rows = [
            [p.get("id", ""), p.get("name", ""), str(p.get("minimum_execution_seconds", ""))]
            for p in data.get("results", [])
        ]
        output.print_table(["ID", "名前", "最低実行時間(秒)"], rows, title="GPUプラン一覧")
