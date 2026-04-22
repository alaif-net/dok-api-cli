from __future__ import annotations

from typing import Annotated, Optional

import typer

from dok import output
from dok.context import get_client, output_callback

app = typer.Typer(help="通知設定・通知エンドポイント管理", no_args_is_help=True)

endpoint_app = typer.Typer(help="通知エンドポイント管理", no_args_is_help=True)
setting_app = typer.Typer(help="通知設定管理", no_args_is_help=True)

app.add_typer(endpoint_app, name="endpoint")
app.add_typer(setting_app, name="setting")


@app.callback()
def _callback(
    ctx: typer.Context,
    fmt: "Optional[str]" = typer.Option(None, "--output", "-o", help="出力形式 (table / json)"),
) -> None:
    output_callback(ctx, fmt)


@endpoint_app.callback()
def _endpoint_callback(
    ctx: typer.Context,
    fmt: "Optional[str]" = typer.Option(None, "--output", "-o", help="出力形式 (table / json)"),
) -> None:
    output_callback(ctx, fmt)


@setting_app.callback()
def _setting_callback(
    ctx: typer.Context,
    fmt: "Optional[str]" = typer.Option(None, "--output", "-o", help="出力形式 (table / json)"),
) -> None:
    output_callback(ctx, fmt)


# --- エンドポイント ---

@endpoint_app.command("list")
def endpoint_list(ctx: typer.Context) -> None:
    """通知エンドポイントの一覧を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.get("/notification/endpoints/")
    if fmt == "json":
        output.print_json(data)
    else:
        rows = [
            [r["id"], r["endpoint_type"], r["address"], str(r["is_verified"]), r["created_at"]]
            for r in data.get("results", [])
        ]
        output.print_table(
            ["ID", "種別", "アドレス", "検証済み", "作成日時"],
            rows,
            title="通知エンドポイント一覧",
        )


@endpoint_app.command("show")
def endpoint_show(
    ctx: typer.Context,
    endpoint_id: Annotated[str, typer.Argument(help="エンドポイントID")],
) -> None:
    """通知エンドポイントを表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.get(f"/notification/endpoints/{endpoint_id}/")
    if fmt == "json":
        output.print_json(data)
    else:
        rows = [
            ["ID", data["id"]],
            ["種別", data["endpoint_type"]],
            ["アドレス", data["address"]],
            ["検証済み", str(data["is_verified"])],
            ["作成日時", data["created_at"]],
            ["更新日時", data["updated_at"]],
        ]
        output.print_table(["項目", "値"], rows, title="通知エンドポイント詳細")


@endpoint_app.command("create")
def endpoint_create(
    ctx: typer.Context,
    address: Annotated[str, typer.Option("--address", help="Webhook URL")],
    endpoint_type: Annotated[str, typer.Option("--type", help="エンドポイント種別 (webhook)")] = "webhook",
) -> None:
    """通知エンドポイントを登録する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.post(
        "/notification/endpoints/",
        json={"endpoint_type": endpoint_type, "address": address},
    )
    if fmt == "json":
        output.print_json(data)
    else:
        typer.echo(f"登録しました: {data['id']}")


@endpoint_app.command("update")
def endpoint_update(
    ctx: typer.Context,
    endpoint_id: Annotated[str, typer.Argument(help="エンドポイントID")],
    endpoint_type: Annotated[Optional[str], typer.Option("--type", help="エンドポイント種別 (webhook)")] = None,
    address: Annotated[Optional[str], typer.Option("--address", help="Webhook URL")] = None,
) -> None:
    """通知エンドポイントを更新する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    body: dict = {}
    if endpoint_type is not None:
        body["endpoint_type"] = endpoint_type
    if address is not None:
        body["address"] = address
    data = client.put(f"/notification/endpoints/{endpoint_id}/", json=body)
    if fmt == "json":
        output.print_json(data)
    else:
        typer.echo(f"更新しました: {data['id']}")


@endpoint_app.command("delete")
def endpoint_delete(
    ctx: typer.Context,
    endpoint_id: Annotated[str, typer.Argument(help="エンドポイントID")],
    yes: Annotated[bool, typer.Option("--yes", "-y", help="確認をスキップ")] = False,
) -> None:
    """通知エンドポイントを削除する。"""
    client = get_client(ctx)
    if not yes:
        typer.confirm(f"エンドポイント {endpoint_id} を削除しますか？", abort=True)
    client.delete(f"/notification/endpoints/{endpoint_id}/")
    typer.echo(f"削除しました: {endpoint_id}")


# --- 通知設定 ---

@setting_app.command("list")
def setting_list(ctx: typer.Context) -> None:
    """通知設定の一覧を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.get("/notification/settings/")
    if fmt == "json":
        output.print_json(data)
    else:
        rows = [
            [
                r["id"],
                r["event_type"],
                str(r["is_enabled"]),
                str(len(r.get("endpoints", []))),
                r["created_at"],
            ]
            for r in data.get("results", [])
        ]
        output.print_table(
            ["ID", "イベント種別", "有効", "エンドポイント数", "作成日時"],
            rows,
            title="通知設定一覧",
        )


@setting_app.command("show")
def setting_show(
    ctx: typer.Context,
    setting_id: Annotated[str, typer.Argument(help="通知設定ID")],
) -> None:
    """通知設定を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.get(f"/notification/settings/{setting_id}/")
    if fmt == "json":
        output.print_json(data)
    else:
        endpoint_addrs = ", ".join(e["address"] for e in data.get("endpoints", []))
        rows = [
            ["ID", data["id"]],
            ["イベント種別", data["event_type"]],
            ["有効", str(data["is_enabled"])],
            ["エンドポイント", endpoint_addrs or "(なし)"],
            ["作成日時", data["created_at"]],
            ["更新日時", data["updated_at"]],
        ]
        output.print_table(["項目", "値"], rows, title="通知設定詳細")


@setting_app.command("create")
def setting_create(
    ctx: typer.Context,
    event_type: Annotated[str, typer.Option("--event-type", help="通知イベント種別 (例: task_completed)")],
    endpoint_ids: Annotated[Optional[list[str]], typer.Option("--endpoint-id", help="通知先エンドポイントID (複数指定可)")] = None,
    enabled: Annotated[bool, typer.Option("--enabled/--disabled", help="通知設定を有効にするかどうか")] = True,
) -> None:
    """通知設定を登録する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.post(
        "/notification/settings/",
        json={
            "event_type": event_type,
            "is_enabled": enabled,
            "endpoint_ids": endpoint_ids or [],
        },
    )
    if fmt == "json":
        output.print_json(data)
    else:
        typer.echo(f"登録しました: {data['id']}")


@setting_app.command("update")
def setting_update(
    ctx: typer.Context,
    setting_id: Annotated[str, typer.Argument(help="通知設定ID")],
    event_type: Annotated[str, typer.Option("--event-type", help="通知イベント種別")],
    endpoint_ids: Annotated[Optional[list[str]], typer.Option("--endpoint-id", help="通知先エンドポイントID (複数指定可)")] = None,
    enabled: Annotated[bool, typer.Option("--enabled/--disabled", help="通知設定を有効にするかどうか")] = True,
) -> None:
    """通知設定を更新する（全フィールド置換）。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.put(
        f"/notification/settings/{setting_id}/",
        json={
            "event_type": event_type,
            "is_enabled": enabled,
            "endpoint_ids": endpoint_ids or [],
        },
    )
    if fmt == "json":
        output.print_json(data)
    else:
        typer.echo(f"更新しました: {data['id']}")


@setting_app.command("patch")
def setting_patch(
    ctx: typer.Context,
    setting_id: Annotated[str, typer.Argument(help="通知設定ID")],
    event_type: Annotated[Optional[str], typer.Option("--event-type", help="通知イベント種別")] = None,
    endpoint_ids: Annotated[Optional[list[str]], typer.Option("--endpoint-id", help="通知先エンドポイントID (複数指定可)")] = None,
    enabled: Annotated[Optional[bool], typer.Option("--enabled/--disabled", help="通知設定を有効にするかどうか")] = None,
) -> None:
    """通知設定を部分更新する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    body: dict = {}
    if event_type is not None:
        body["event_type"] = event_type
    if enabled is not None:
        body["is_enabled"] = enabled
    if endpoint_ids is not None:
        body["endpoint_ids"] = endpoint_ids
    data = client.patch(f"/notification/settings/{setting_id}/", json=body)
    if fmt == "json":
        output.print_json(data)
    else:
        typer.echo(f"更新しました: {data['id']}")


@setting_app.command("delete")
def setting_delete(
    ctx: typer.Context,
    setting_id: Annotated[str, typer.Argument(help="通知設定ID")],
    yes: Annotated[bool, typer.Option("--yes", "-y", help="確認をスキップ")] = False,
) -> None:
    """通知設定を削除する。"""
    client = get_client(ctx)
    if not yes:
        typer.confirm(f"通知設定 {setting_id} を削除しますか？", abort=True)
    client.delete(f"/notification/settings/{setting_id}/")
    typer.echo(f"削除しました: {setting_id}")


@setting_app.command("test-webhook")
def setting_test_webhook(
    ctx: typer.Context,
    url: Annotated[str, typer.Option("--url", help="テスト送信先のWebhook URL")],
) -> None:
    """Webhook通知設定にテスト送信を行う。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.post("/notification/settings/test-webhook/", json={"url": url})
    if fmt == "json":
        output.print_json(data)
    else:
        ok = data.get("ok", False)
        status = data.get("webhook_status_code", "")
        body = data.get("response_body", "")
        rows = [
            ["結果", "成功" if ok else "失敗"],
            ["HTTPステータス", str(status)],
            ["レスポンスボディ", body or "(なし)"],
        ]
        output.print_table(["項目", "値"], rows, title="Webhookテスト結果")
