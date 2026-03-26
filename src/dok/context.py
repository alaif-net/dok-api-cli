from __future__ import annotations

import typer

from dok import config as cfg
from dok import output
from dok.client import DokClient
from dok.exceptions import ConfigError


def output_callback(ctx: typer.Context, output_fmt: str | None) -> None:
    """サブコマンドグループの --output/-o オプションを ctx.obj に反映する。"""
    if output_fmt and ctx.obj is not None:
        ctx.obj["output"] = output_fmt


def get_client(ctx: typer.Context) -> DokClient:
    """ctx.obj からクライアントを取得する。未初期化なら設定を読み込んで初期化する。"""
    if "client" not in ctx.obj:
        try:
            params = ctx.obj.get("_config_params", {})
            conf = cfg.load(**params)
            ctx.obj["client"] = DokClient(conf)
        except ConfigError as e:
            output.exit_with_error(str(e))
            raise typer.Exit(1)
    return ctx.obj["client"]  # type: ignore[return-value]
