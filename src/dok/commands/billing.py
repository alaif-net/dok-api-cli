from __future__ import annotations

import datetime

import typer

from dok import output
from dok.client import DokClient
from dok.context import get_client

app = typer.Typer(help="料金・請求情報")


@app.command("show")
def show(ctx: typer.Context) -> None:
    """請求情報を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    data = client.get("/billing_infos/")
    if fmt == "json":
        output.print_json(data)
    else:
        info = data if isinstance(data, dict) else {}
        typer.echo(f"アカウント: {info.get('account', '')}")
        typer.echo(f"締め日: {info.get('bill_close_at', '')}")
        typer.echo(f"最終更新: {info.get('last_upload_at', '')}")
        details = info.get("details", [])
        if details:
            rows = [
                [str(d["sequence_no"]), d["plan"], str(d["usage"]), str(d["amount"]), d["description"]]
                for d in details
            ]
            output.print_table(["No", "プラン", "使用量", "金額", "説明"], rows, title="請求明細")


@app.command("prices")
def prices(
    ctx: typer.Context,
    year: int = typer.Option(None, help="取得対象の年 (デフォルト: 今年)"),
    month: int = typer.Option(None, help="取得対象の月 (デフォルト: 今月)"),
    day: int = typer.Option(None, help="取得対象の日 (デフォルト: 今日)"),
) -> None:
    """プラン別単価を表示する。"""
    client = get_client(ctx)
    fmt: str = ctx.obj["output"]
    today = datetime.date.today()
    params = {
        "year": year or today.year,
        "month": month or today.month,
        "day": day or today.day,
    }
    data = client.get("/unit_prices/", params=params)
    if fmt == "json":
        output.print_json(data)
    else:
        results = data.get("results", data) if isinstance(data, dict) else data
        rows = [
            [p["plan"], p["price"], p["begin_at"], p["end_at"], "上書き" if p.get("is_overridden") else ""]
            for p in results
        ]
        output.print_table(["プラン", "単価", "開始日", "終了日", "備考"], rows, title="プラン別単価")
