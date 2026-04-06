from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from dok.config import Config, load, DEFAULT_BASE_URL
from dok.exceptions import ConfigError


def test_load_from_env():
    with patch.dict(os.environ, {
        "DOK_ACCESS_TOKEN": "token123",
        "DOK_ACCESS_TOKEN_SECRET": "secret456",
    }):
        conf = load()
    assert conf.access_token == "token123"
    assert conf.access_token_secret == "secret456"
    assert conf.base_url == DEFAULT_BASE_URL


def test_cli_option_overrides_env():
    with patch.dict(os.environ, {
        "DOK_ACCESS_TOKEN": "env_token",
        "DOK_ACCESS_TOKEN_SECRET": "env_secret",
    }):
        conf = load(token="cli_token", token_secret="cli_secret")
    assert conf.access_token == "cli_token"
    assert conf.access_token_secret == "cli_secret"


def test_missing_token_raises():
    with patch.dict(os.environ, {}, clear=True):
        with patch("dok.config.CONFIG_FILE") as mock_file:
            mock_file.exists.return_value = False
            with pytest.raises(ConfigError):
                load()


def test_custom_base_url():
    with patch.dict(os.environ, {
        "DOK_ACCESS_TOKEN": "t",
        "DOK_ACCESS_TOKEN_SECRET": "s",
    }):
        conf = load(base_url="https://custom.example.com/api/1.0")
    assert conf.base_url == "https://custom.example.com/api/1.0"
