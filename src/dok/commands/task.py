from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Annotated, Optional

import typer

from dok import output
from dok.client import DokClient
from dok.context import get_client, output_callback

app = typer.Typer(help="タスク管理")


@app.callback()
def _callback(
    ctx: typer.Context,
    fmt: Annotated[Optional[str], typer.Option("--output", "-o", help="出力形式 (table / json)")] = None,
) -> None:
    output_callback(ctx, fmt)

_STATUS_COLORS = {
    "waiting": "yellow",
    "running": "blue",
    "error": "red",
    "done": "green",
    "aborted": "red",
    "canceled": "grey50",
}


def _status_str(status: str) -> str:
    color = _STATUS_COLORS.get(status, "white")
    return f"[{color}]{status}[/{color}]"


@app.command("list")
def list_tasks(
    ctx: typer.Context,
    status: Annotated[Optional[str], typer.Option("--status", help="ステータスで絞り込み (カンマ区切り)")] = None,
    tag: Annotated[Optional[str], typer.Option("--tag", help="タグで絞り込み")] = None,
    page: Annotated[int, typer.Option("--page", help="ページ番号")] = 1,
    page_size: Annotated[int, typer.Option("--page-size", help="1ページのサイズ")] = 100,
) -> None:
    """タスクの一覧を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    params: dict = {"page": page, "page_size": page_size}
    if status:
        params["status"] = status
    if tag:
        params["tag"] = tag
    data = client.get("/tasks/", params=params)
    if fmt == "json":
        output.print_json(data)
    else:
        rows = [
            [t["id"], t["name"], t["status"], ",".join(t.get("tags", [])), t["created_at"]]
            for t in data.get("results", [])
        ]
        output.print_table(["ID", "名前", "ステータス", "タグ", "作成日時"], rows, title="タスク一覧")


@app.command("show")
def show(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="タスクID")],
) -> None:
    """タスクの詳細を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.get(f"/tasks/{task_id}/")
    if fmt == "json":
        output.print_json(data)
    else:
        output.print_table(
            ["フィールド", "値"],
            [
                ["ID", data["id"]],
                ["名前", data["name"]],
                ["ステータス", data["status"]],
                ["タグ", ",".join(data.get("tags", []))],
                ["作成日時", data["created_at"]],
                ["更新日時", data["updated_at"]],
                ["HTTP URI", data.get("http_uri") or ""],
                ["エラー", data.get("error_message") or ""],
            ],
        )
        for c in data.get("containers", []):
            output.print_table(
                ["フィールド", "値"],
                [
                    ["コンテナ index", str(c["index"])],
                    ["イメージ", c["image"]],
                    ["プラン", c["plan"]],
                    ["終了コード", str(c.get("exit_code", ""))],
                    ["実行時間(秒)", str(c.get("execution_seconds", ""))],
                ],
                title=f"コンテナ {c['index']}",
            )


@app.command("create")
def create(
    ctx: typer.Context,
    file: Annotated[Optional[Path], typer.Option("--file", "-f", help="タスク定義JSONファイル")] = None,
    name: Annotated[Optional[str], typer.Option("--name", help="タスク名")] = None,
    image: Annotated[Optional[str], typer.Option("--image", help="コンテナイメージ")] = None,
    plan: Annotated[Optional[str], typer.Option("--plan", help="GPUプラン (v100-32gb / h100-80gb)")] = None,
    command: Annotated[Optional[str], typer.Option("--command", help='実行コマンド (JSON配列 例: \'["python","train.py"]\')')] = None,
    entrypoint: Annotated[Optional[str], typer.Option("--entrypoint", help="エントリポイント (JSON配列)")] = None,
    env: Annotated[Optional[list[str]], typer.Option("--env", "-e", help="環境変数 KEY=VALUE (複数指定可)")] = None,
    tag: Annotated[Optional[list[str]], typer.Option("--tag", help="タグ (複数指定可)")] = None,
    registry: Annotated[Optional[str], typer.Option("--registry", help="レジストリ認証情報ID")] = None,
    ssh_shell: Annotated[Optional[str], typer.Option("--ssh-shell", help="SSHシェル (/bin/sh, /bin/bash, /bin/zsh)")] = None,
    ssh_port: Annotated[Optional[int], typer.Option("--ssh-port", help="SSHポート番号")] = None,
    http_port: Annotated[Optional[int], typer.Option("--http-port", help="HTTPポート番号")] = None,
    http_path: Annotated[Optional[str], typer.Option("--http-path", help="HTTPパス")] = None,
    execution_time_limit: Annotated[Optional[int], typer.Option("--execution-time-limit", help="実行時間制限(秒)")] = None,
) -> None:
    """タスクを作成する。-f でJSONファイルを指定するか、オプションで指定する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]

    if file:
        body = json.loads(file.read_text())
    else:
        if not name:
            output.exit_with_error("--name を指定してください。")
            return
        if not image or not plan:
            output.exit_with_error("--image と --plan を指定してください。")
            return

        environment: dict[str, str] = {}
        for e in (env or []):
            if "=" not in e:
                output.exit_with_error(f"環境変数の形式が不正です: {e}  (KEY=VALUE 形式で指定してください)")
                return
            k, v = e.split("=", 1)
            environment[k] = v

        ssh_def = None
        if ssh_shell and ssh_port:
            ssh_def = {"shell": ssh_shell, "port": ssh_port}

        http_def = None
        if http_port:
            http_def = {"port": http_port, "path": http_path or "/"}

        container: dict = {
            "image": image,
            "plan": plan,
            "command": json.loads(command) if command else [],
            "entrypoint": json.loads(entrypoint) if entrypoint else [],
        }
        if environment:
            container["environment"] = environment
        if registry:
            container["registry"] = registry
        if ssh_def:
            container["ssh"] = ssh_def
        if http_def:
            container["http"] = http_def

        body = {
            "name": name,
            "containers": [container],
            "tags": tag or [],
        }
        if execution_time_limit is not None:
            body["execution_time_limit_sec"] = execution_time_limit

    data = client.post("/tasks/", json=body)
    if fmt == "json":
        output.print_json(data)
    else:
        typer.echo(f"タスクを作成しました: {data['id']}")
        typer.echo(f"ステータス: {data['status']}")


@app.command("delete")
def delete(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="タスクID")],
    yes: Annotated[bool, typer.Option("--yes", "-y", help="確認をスキップ")] = False,
) -> None:
    """タスクを削除する。"""
    client = get_client(ctx)
    if not yes:
        typer.confirm(f"タスク {task_id} を削除しますか？", abort=True)
    client.delete(f"/tasks/{task_id}/")
    typer.echo(f"削除しました: {task_id}")


@app.command("cancel")
def cancel(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="タスクID")],
    yes: Annotated[bool, typer.Option("--yes", "-y", help="確認をスキップ")] = False,
) -> None:
    """実行中のタスクをキャンセルする。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    if not yes:
        typer.confirm(f"タスク {task_id} をキャンセルしますか？", abort=True)
    data = client.post(f"/tasks/{task_id}/cancel/")
    if fmt == "json":
        output.print_json(data)
    else:
        typer.echo(f"キャンセルしました: {task_id} (ステータス: {data['status']})")


@app.command("download")
def download_url(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="タスクID")],
    target: Annotated[str, typer.Argument(help="ダウンロード対象 (output)")] = "output",
    filename: Annotated[Optional[str], typer.Option("--filename", help="ダウンロード時のファイル名")] = None,
) -> None:
    """タスク関連ファイルのダウンロードURLを取得する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    params = {}
    if filename:
        params["filename"] = filename
    data = client.get(f"/tasks/{task_id}/download/{target}/", params=params)
    if fmt == "json":
        output.print_json(data)
    else:
        typer.echo(data.get("url", ""))


@app.command("logs")
def logs(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="タスクID")],
    container_index: Annotated[int, typer.Argument(help="コンテナインデックス")] = 0,
) -> None:
    """タスクのログをストリーミング表示する。"""
    from dok.exceptions import AuthError
    client = get_client(ctx)
    try:
        info = client.get_stream_info(task_id, container_index)
    except AuthError as e:
        if "not running" in str(e).lower() or "task is not running" in str(e).lower():
            output.exit_with_error("タスクが実行中ではありません。ログストリームは実行中のタスクのみ利用できます。")
        raise
    ws_url: str = info["url"]
    token: str = info["token"]

    async def _stream() -> None:
        import websockets

        async with websockets.connect(
            ws_url,
            additional_headers={"Authorization": f"Bearer {token}"},
        ) as ws:
            async for message in ws:
                typer.echo(message, nl=False)

    asyncio.run(_stream())


@app.command("notify")
def notify(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="タスクID")],
    enabled: Annotated[Optional[bool], typer.Option("--enabled/--disabled", help="通知を有効にするかどうか")] = None,
    endpoint_id: Annotated[Optional[list[str]], typer.Option("--endpoint-id", help="通知先エンドポイントID (複数指定可)")] = None,
) -> None:
    """タスク完了時の通知設定を行う。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    body: dict = {}
    if enabled is not None:
        body["is_enabled"] = enabled
    if endpoint_id is not None:
        body["endpoint_ids"] = endpoint_id
    data = client.put(f"/tasks/{task_id}/notification-preference/", json=body)
    if fmt == "json":
        output.print_json(data)
    else:
        ok = data.get("ok", False)
        typer.echo(f"通知設定を更新しました: {'成功' if ok else '失敗'}")
