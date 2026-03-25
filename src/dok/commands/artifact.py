from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import httpx
import typer

from dok import output
from dok.client import DokClient
from dok.context import get_client

app = typer.Typer(help="アーティファクト")


@app.command("list")
def list_artifacts(
    ctx: typer.Context,
    task: Annotated[Optional[str], typer.Option("--task", help="タスクIDで絞り込み")] = None,
) -> None:
    """アーティファクトの一覧を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    params = {}
    if task:
        params["task"] = task
    data = client.get("/artifacts/", params=params)
    if fmt == "json":
        output.print_json(data)
    else:
        rows = [
            [a["id"], a["task"], a["filename"], str(a["size_bytes"]), a["created_at"]]
            for a in data.get("results", [])
        ]
        output.print_table(["ID", "タスクID", "ファイル名", "サイズ(bytes)", "作成日時"], rows, title="アーティファクト一覧")


@app.command("show")
def show(
    ctx: typer.Context,
    artifact_id: Annotated[str, typer.Argument(help="アーティファクトID")],
) -> None:
    """アーティファクト情報を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.get(f"/artifacts/{artifact_id}/")
    if fmt == "json":
        output.print_json(data)
    else:
        rows = [[data["id"], data["task"], data["filename"], str(data["size_bytes"]), data["created_at"]]]
        output.print_table(["ID", "タスクID", "ファイル名", "サイズ(bytes)", "作成日時"], rows)


@app.command("download")
def download(
    ctx: typer.Context,
    artifact_id: Annotated[str, typer.Argument(help="アーティファクトID")],
    out: Annotated[Optional[Path], typer.Option("--out", "-o", help="保存先パス")] = None,
) -> None:
    """アーティファクトをダウンロードする。"""
    client = get_client(ctx)
    data = client.get(f"/artifacts/{artifact_id}/download/")
    url = data.get("url") or data.get("download_url")
    if not url:
        output.exit_with_error("ダウンロードURLを取得できませんでした。")
        return

    with httpx.stream("GET", url) as response:
        response.raise_for_status()
        filename = out or Path(artifact_id + ".tar.gz")
        with open(filename, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
    typer.echo(f"ダウンロード完了: {filename}")
