# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

さくらインターネットの GPU コンテナ実行プラットフォーム「高火力 DOK」を操作する Python CLI ツール。

- API仕様: https://manual.sakura.ad.jp/koukaryoku-dok-api/spec.html
- API Base URL: `https://secure.sakura.ad.jp/cloud/zone/is1a/api/managed-container/1.0`
- 認証: Basic認証（アクセストークン=ユーザーID、アクセストークンシークレット=パスワード）

## コマンド

```bash
# 開発環境セットアップ
uv sync

# CLI実行
uv run dok

# テスト実行
uv run pytest

# 単一テスト実行
uv run pytest tests/test_client.py::test_name -v

# リント・フォーマット
uv run ruff check .
uv run ruff format .

# 型チェック
uv run mypy src/
```

## アーキテクチャ

```
src/dok/
├── main.py          # CLIルートコマンド、グローバルオプション、サブコマンド登録
├── config.py        # 設定ファイル管理 (~/.config/dok/config.toml)
├── client.py        # httpx ベース API クライアント (DokClient)
├── exceptions.py    # カスタム例外 (DokError, AuthError, NotFoundError, ApiError)
├── context.py       # get_client() ヘルパー（クライアント遅延初期化）
├── output.py        # rich を使ったテーブル/JSON出力ユーティリティ
├── commands/        # サブコマンド (typer.Typer インスタンスを export)
│   ├── auth.py         # dok auth show / agree
│   ├── task.py         # dok task list/show/create/delete/cancel/download/logs/notify
│   ├── registry.py     # dok registry list/show/create/update/delete
│   ├── artifact.py     # dok artifact list/show/download
│   ├── plan.py         # dok plan list
│   ├── ssh.py          # dok ssh list/show/create/update/delete
│   ├── billing.py      # dok billing show / prices
│   └── notification.py # dok notification endpoint .../setting ...
└── models/          # Pydantic v2 モデル (APIレスポンスの型定義)
    └── notification.py # NotificationEndpoint, NotificationSetting など
```

### 主要な設計方針

**レイヤー構成**: `commands/` → `client.py` → HTTP → API。コマンドは `DokClient` を通じてのみ API を呼ぶ。

**設定解決の優先順位**: CLIオプション > 環境変数 > `~/.config/dok/config.toml` の指定プロファイル（デフォルト: `default`）。設定ファイルが存在しなくても環境変数・CLIオプションのみで動作する。

| 設定項目 | CLIオプション | 環境変数 | 設定ファイルキー |
|---|---|---|---|
| アクセストークン | `--token` | `DOK_ACCESS_TOKEN` | `access_token` |
| トークンシークレット | `--token-secret` | `DOK_ACCESS_TOKEN_SECRET` | `access_token_secret` |
| Base URL | `--base-url` | `DOK_BASE_URL` | `base_url` |

**出力**: 全コマンドで `--output table|json` をサポート。テーブルは `rich`、JSON は `json.dumps` でそのまま出力。エラーは `stderr` に出力して exit code 1。

**破壊的操作**: `delete` 系コマンドは `typer.confirm()` で確認を挟む。`--yes / -y` で省略可能。

**ログストリーミング**: `dok task logs` は `/tasks/{taskId}/containers/{containerIndex}/stream/` から WebSocket URL と token を取得し、`websockets` ライブラリで接続してログを stdout に出力する。

**HTTP メソッド**: `DokClient` は `get / post / put / patch / delete` をサポート。`patch` は通知設定の部分更新 (`PATCH /notification/settings/{id}/`) で使用。

## CLIコマンド体系

```
dok configure                              # 初期設定ウィザード
dok auth show / agree
dok task list / show / create / delete / cancel / download / logs / notify
dok registry list / show / create / update / delete
dok artifact list / show / download
dok plan list
dok ssh list / show / create / update / delete
dok billing show / prices
dok notification endpoint list / show / create / update / delete
dok notification setting list / show / create / update / patch / delete / test-webhook
```

グローバルオプション: `--profile/-p`, `--output/-o`, `--token`, `--token-secret`, `--base-url`

## API スキーマ（仕様準拠）

### タスク作成リクエスト (`CreateTaskRequest`)

必須フィールド: `name`, `containers`, `tags`

```json
{
  "name": "my-task",
  "tags": ["tag1", "tag2"],
  "execution_time_limit_sec": 3600,
  "containers": [
    {
      "image": "nginx:latest",
      "plan": "v100-32gb",
      "command": ["/bin/sh", "-c", "python train.py"],
      "entrypoint": [],
      "registry": null,
      "environment": {
        "BATCH_SIZE": "32"
      },
      "ssh": {
        "shell": "/bin/bash",
        "port": 22
      },
      "http": null
    }
  ]
}
```

### `ContainerDefinition` フィールド

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `image` | string | ✓ | コンテナイメージ URI |
| `command` | string[] | ✓ | 実行コマンド配列 |
| `entrypoint` | string[] | ✓ | エントリポイント配列 |
| `plan` | PlanID | ✓ | `"v100-32gb"`, `"h100-80gb"`, `"h100-8gpu-80gb"` |
| `registry` | UUID \| null | - | コンテナレジストリ認証情報 ID |
| `environment` | object | - | 環境変数 (key-value) |
| `ssh` | ContainerSshDefinition \| null | - | SSH 接続設定 |
| `http` | ContainerHttpDefinition \| null | - | HTTP 公開設定 |

### `ContainerSshDefinition`

| フィールド | 型 | 値 |
|---|---|---|
| `shell` | enum | `/bin/sh`, `/bin/bash`, `/bin/zsh` |
| `port` | integer | ポート番号 |
| `host_name` | string \| null | ホスト名 |

### `ContainerHttpDefinition`

| フィールド | 型 |
|---|---|
| `port` | integer |
| `path` | string |

### タスクステータス (`TaskStatus`)

`waiting` / `running` / `error` / `done` / `aborted` / `canceled`

### 通知エンドポイント (`NotificationEndpoint`)

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | integer | エンドポイントID |
| `endpoint_type` | enum | `"webhook"` |
| `address` | string | Webhook URL |
| `is_verified` | boolean | 検証済みかどうか |
| `created_at` | DateTime | 作成日時 |
| `updated_at` | DateTime | 更新日時 |

### 通知設定 (`NotificationSetting`)

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | UUID | 設定ID |
| `event_type` | string | イベント種別（例: `task_completed`） |
| `is_enabled` | boolean | 有効/無効 |
| `endpoints` | NotificationEndpoint[] | 通知先エンドポイント一覧 |
| `created_at` | DateTime | 作成日時 |
| `updated_at` | DateTime | 更新日時 |

### タスク完了通知設定 (`TaskNotificationPreferenceRequest`)

`PUT /tasks/{taskId}/notification-preference/` で使用。

| フィールド | 型 | 説明 |
|---|---|---|
| `is_enabled` | boolean \| null | 通知を有効にするかどうか |
| `endpoint_ids` | integer[] \| null | 通知先エンドポイントIDのリスト |

## タスク定義ファイル（`-f` オプション）

`dok task create -f task.json` で読み込む JSON ファイル（`CreateTaskRequest` と同一構造）:

```json
{
  "name": "my-task",
  "tags": ["tag1", "tag2"],
  "execution_time_limit_sec": 3600,
  "containers": [
    {
      "image": "ghcr.io/example/myapp:latest",
      "plan": "v100-32gb",
      "command": ["python", "train.py"],
      "entrypoint": [],
      "registry": null,
      "environment": {
        "BATCH_SIZE": "32",
        "MODEL_PATH": "/data/model.pt"
      },
      "ssh": {
        "shell": "/bin/bash",
        "port": 22
      },
      "http": null
    }
  ]
}
```
