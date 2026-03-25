from __future__ import annotations

import typer

from dok import config as cfg
from dok import output
from dok.client import DokClient
from dok.exceptions import ConfigError


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
