from __future__ import annotations

from typing import Annotated, Optional

import typer

from dok import output
from dok.client import DokClient
from dok.context import get_client

app = typer.Typer(help="コンテナレジストリ認証情報")


@app.command("list")
def list_registries(ctx: typer.Context) -> None:
    """コンテナレジストリ認証情報の一覧を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.get("/registries/")
    if fmt == "json":
        output.print_json(data)
    else:
        rows = [
            [r["id"], r["hostname"], r["username"], r["created_at"]]
            for r in data.get("results", [])
        ]
        output.print_table(["ID", "ホスト名", "ユーザー名", "作成日時"], rows, title="レジストリ一覧")


@app.command("show")
def show(
    ctx: typer.Context,
    registry_id: Annotated[str, typer.Argument(help="レジストリID")],
) -> None:
    """コンテナレジストリ認証情報を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.get(f"/registries/{registry_id}/")
    if fmt == "json":
        output.print_json(data)
    else:
        rows = [[data["id"], data["hostname"], data["username"], data["created_at"]]]
        output.print_table(["ID", "ホスト名", "ユーザー名", "作成日時"], rows)


@app.command("create")
def create(
    ctx: typer.Context,
    hostname: Annotated[str, typer.Option("--hostname", help="レジストリのホスト名")],
    username: Annotated[str, typer.Option("--username", help="ユーザー名")],
    password: Annotated[str, typer.Option("--password", help="パスワード", prompt=True, hide_input=True)],
) -> None:
    """コンテナレジストリ認証情報を登録する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.post("/registries/", json={"hostname": hostname, "username": username, "password": password})
    if fmt == "json":
        output.print_json(data)
    else:
        typer.echo(f"登録しました: {data['id']}")


@app.command("update")
def update(
    ctx: typer.Context,
    registry_id: Annotated[str, typer.Argument(help="レジストリID")],
    hostname: Annotated[str, typer.Option("--hostname", help="ホスト名")],
    username: Annotated[str, typer.Option("--username", help="ユーザー名")],
    password: Annotated[str, typer.Option("--password", help="パスワード", prompt=True, hide_input=True)],
) -> None:
    """コンテナレジストリ認証情報を更新する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.put(f"/registries/{registry_id}/", json={"hostname": hostname, "username": username, "password": password})
    if fmt == "json":
        output.print_json(data)
    else:
        typer.echo(f"更新しました: {data['id']}")


@app.command("delete")
def delete(
    ctx: typer.Context,
    registry_id: Annotated[str, typer.Argument(help="レジストリID")],
    yes: Annotated[bool, typer.Option("--yes", "-y", help="確認をスキップ")] = False,
) -> None:
    """コンテナレジストリ認証情報を削除する。"""
    client = get_client(ctx)
    if not yes:
        typer.confirm(f"レジストリ {registry_id} を削除しますか？", abort=True)
    client.delete(f"/registries/{registry_id}/")
    typer.echo(f"削除しました: {registry_id}")
