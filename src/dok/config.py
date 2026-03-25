from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import tomllib
import tomli_w

from dok.exceptions import ConfigError

CONFIG_DIR = Path.home() / ".config" / "dok"
CONFIG_FILE = CONFIG_DIR / "config.toml"
DEFAULT_BASE_URL = "https://secure.sakura.ad.jp/cloud/zone/is1a/api/managed-container/1.0"


class Config:
    def __init__(
        self,
        access_token: str,
        access_token_secret: str,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.base_url = base_url


def load(
    profile: str = "default",
    token: Optional[str] = None,
    token_secret: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Config:
    """CLIオプション > 環境変数 > 設定ファイルの優先順位で設定を解決する。"""
    file_data: dict[str, str] = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "rb") as f:
            all_profiles = tomllib.load(f)
        file_data = all_profiles.get(profile, {})

    resolved_token = (
        token
        or os.environ.get("DOK_ACCESS_TOKEN")
        or file_data.get("access_token")
    )
    resolved_secret = (
        token_secret
        or os.environ.get("DOK_ACCESS_TOKEN_SECRET")
        or file_data.get("access_token_secret")
    )
    resolved_base_url = (
        base_url
        or os.environ.get("DOK_BASE_URL")
        or file_data.get("base_url")
        or DEFAULT_BASE_URL
    )

    if not resolved_token:
        raise ConfigError(
            "アクセストークンが設定されていません。"
            " --token オプション、DOK_ACCESS_TOKEN 環境変数、または `dok configure` で設定してください。"
        )
    if not resolved_secret:
        raise ConfigError(
            "アクセストークンシークレットが設定されていません。"
            " --token-secret オプション、DOK_ACCESS_TOKEN_SECRET 環境変数、または `dok configure` で設定してください。"
        )

    return Config(
        access_token=resolved_token,
        access_token_secret=resolved_secret,
        base_url=resolved_base_url,
    )


def save(
    access_token: str,
    access_token_secret: str,
    base_url: Optional[str] = None,
    profile: str = "default",
) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    existing: dict[str, dict[str, str]] = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "rb") as f:
            existing = tomllib.load(f)

    existing[profile] = {
        "access_token": access_token,
        "access_token_secret": access_token_secret,
    }
    if base_url:
        existing[profile]["base_url"] = base_url

    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(existing, f)
