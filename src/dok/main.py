from __future__ import annotations

from typing import Annotated, Optional

import typer

from dok import config as cfg
from dok import output
from dok.commands import auth, artifact, billing, plan, registry, ssh, task
from dok.exceptions import ConfigError

app = typer.Typer(
    name="dok",
    help="さくらのクラウド 高火力 DOK CLI",
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


@app.command("configure")
def configure(
    ctx: typer.Context,
    profile: Annotated[str, typer.Option("--profile", "-p", help="設定するプロファイル名")] = "default",
) -> None:
    """認証情報を対話的に設定する。"""
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
