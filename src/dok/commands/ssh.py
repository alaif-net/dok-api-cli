from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from dok import output
from dok.client import DokClient
from dok.context import get_client, output_callback

app = typer.Typer(help="SSH公開鍵管理")

@app.callback()
def _callback(
    ctx: typer.Context,
    fmt: "Optional[str]" = typer.Option(None, "--output", "-o", help="出力形式 (table / json)"),
) -> None:
    output_callback(ctx, fmt)




@app.command("list")
def list_keys(ctx: typer.Context) -> None:
    """SSH公開鍵の一覧を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.get("/ssh/keys/")
    if fmt == "json":
        output.print_json(data)
    else:
        rows = [
            [k["id"], k["name"], "有効" if k["is_active"] else "無効", k["pub_key"][:40] + "..."]
            for k in data.get("results", [])
        ]
        output.print_table(["ID", "名前", "状態", "公開鍵(先頭)"], rows, title="SSH公開鍵一覧")


@app.command("show")
def show(
    ctx: typer.Context,
    key_id: Annotated[str, typer.Argument(help="鍵ID")],
) -> None:
    """SSH公開鍵を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.get(f"/ssh/keys/{key_id}/")
    if fmt == "json":
        output.print_json(data)
    else:
        rows = [[data["id"], data["name"], "有効" if data["is_active"] else "無効"]]
        output.print_table(["ID", "名前", "状態"], rows)
        typer.echo(data["pub_key"])


@app.command("create")
def create(
    ctx: typer.Context,
    name: Annotated[str, typer.Option("--name", help="鍵の名前")],
    key: Annotated[Optional[str], typer.Option("--key", help="公開鍵文字列")] = None,
    key_file: Annotated[Optional[Path], typer.Option("--key-file", help="公開鍵ファイルのパス")] = None,
    active: Annotated[bool, typer.Option("--active/--inactive", help="有効/無効")] = True,
) -> None:
    """SSH公開鍵を登録する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]

    if key_file:
        pub_key = key_file.read_text().strip()
    elif key:
        pub_key = key
    else:
        output.exit_with_error("--key または --key-file を指定してください。")
        return

    data = client.post("/ssh/keys/", json={"name": name, "pub_key": pub_key, "is_active": active})
    if fmt == "json":
        output.print_json(data)
    else:
        typer.echo(f"登録しました: {data['id']}")


@app.command("update")
def update(
    ctx: typer.Context,
    key_id: Annotated[str, typer.Argument(help="鍵ID")],
    name: Annotated[str, typer.Option("--name", help="鍵の名前")],
    active: Annotated[bool, typer.Option("--active/--inactive", help="有効/無効")] = True,
) -> None:
    """SSH公開鍵情報を更新する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.put(f"/ssh/keys/{key_id}/", json={"name": name, "is_active": active})
    if fmt == "json":
        output.print_json(data)
    else:
        typer.echo(f"更新しました: {data['id']}")


@app.command("delete")
def delete(
    ctx: typer.Context,
    key_id: Annotated[str, typer.Argument(help="鍵ID")],
    yes: Annotated[bool, typer.Option("--yes", "-y", help="確認をスキップ")] = False,
) -> None:
    """SSH公開鍵を削除する。"""
    client = get_client(ctx)
    if not yes:
        typer.confirm(f"SSH鍵 {key_id} を削除しますか？", abort=True)
    client.delete(f"/ssh/keys/{key_id}/")
    typer.echo(f"削除しました: {key_id}")
