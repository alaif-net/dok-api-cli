from __future__ import annotations

from typing import Annotated, Optional

import typer

from dok import config as cfg
from dok import output
from dok.commands import auth, artifact, billing, plan, registry, ssh, task
from dok.exceptions import ConfigError

app = typer.Typer(
    name="dok",
    help="高火力 DOK CLI",
    no_args_is_help=True,
)

app.add_typer(auth.app, name="auth")
app.add_typer(task.app, name="task")
app.add_typer(registry.app, name="registry")
app.add_typer(artifact.app, name="artifact")
app.add_typer(plan.app, name="plan")
app.add_typer(ssh.app, name="ssh")
app.add_typer(billing.app, name="billing")



@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    profile: Annotated[str, typer.Option("--profile", "-p", help="使用するプロファイル名")] = "default",
    fmt: Annotated[str, typer.Option("--output", "-o", help="出力形式 (table / json)")] = "table",
    token: Annotated[Optional[str], typer.Option("--token", help="アクセストークン", envvar="DOK_ACCESS_TOKEN")] = None,
    token_secret: Annotated[Optional[str], typer.Option("--token-secret", help="アクセストークンシークレット", envvar="DOK_ACCESS_TOKEN_SECRET")] = None,
    base_url: Annotated[Optional[str], typer.Option("--base-url", help="API Base URL", envvar="DOK_BASE_URL")] = None,
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["output"] = fmt
    ctx.obj["_config_params"] = {
        "profile": profile,
        "token": token,
        "token_secret": token_secret,
        "base_url": base_url,
    }


configure_app = typer.Typer(help="設定を管理する。", no_args_is_help=False)
app.add_typer(configure_app, name="configure")


@configure_app.callback(invoke_without_command=True)
def configure(
    ctx: typer.Context,
    profile: Annotated[str, typer.Option("--profile", "-p", help="設定するプロファイル名")] = "default",
) -> None:
    """認証情報を対話的に設定する。"""
    if ctx.invoked_subcommand is not None:
        return
    typer.echo("高火力 DOK CLI の初期設定")
    access_token = typer.prompt("アクセストークン")
    access_token_secret = typer.prompt("アクセストークンシークレット", hide_input=True)
    base_url = typer.prompt(
        "API Base URL (Enterでデフォルト使用)",
        default="",
        show_default=False,
    )
    try:
        cfg.save(
            access_token=access_token,
            access_token_secret=access_token_secret,
            base_url=base_url or None,
            profile=profile,
        )
        typer.echo(f"設定を保存しました: ~/.config/dok/config.toml [{profile}]")
    except Exception as e:
        output.exit_with_error(str(e))


@configure_app.command("list")
def configure_list(
    ctx: typer.Context,
) -> None:
    """設定済みのプロファイル一覧を表示する。"""
    import tomllib

    if not cfg.CONFIG_FILE.exists():
        typer.echo("設定ファイルが見つかりません。")
        raise typer.Exit(0)

    with open(cfg.CONFIG_FILE, "rb") as f:
        all_profiles: dict[str, dict[str, str]] = tomllib.load(f)

    if not all_profiles:
        typer.echo("設定済みプロファイルはありません。")
        raise typer.Exit(0)

    fmt = ctx.find_root().obj.get("output", "table") if ctx.find_root().obj else "table"

    def _mask(token: str) -> str:
        return token[:4] + "****" + token[-4:] if len(token) >= 8 else "****"

    if fmt == "json":
        import json
        result = []
        for name, data in all_profiles.items():
            result.append({
                "profile": name,
                "access_token": _mask(data.get("access_token", "")),
                "base_url": data.get("base_url", cfg.DEFAULT_BASE_URL),
            })
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        from rich.table import Table
        from rich.console import Console

        table = Table(show_header=True)
        table.add_column("Profile", style="cyan")
        table.add_column("Access Token")
        table.add_column("Base URL")

        for name, data in all_profiles.items():
            table.add_row(
                name,
                _mask(data.get("access_token", "")),
                data.get("base_url", cfg.DEFAULT_BASE_URL),
            )

        Console().print(table)
