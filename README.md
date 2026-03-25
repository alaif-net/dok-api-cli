# dok

さくらのクラウドの GPU コンテナ実行プラットフォーム「[高火力 DOK](https://www.sakura.ad.jp/koukaryoku-dok)」を操作する CLI ツール。

## インストール

```bash
# リポジトリをクローンして uv でセットアップ
git clone https://github.com/yourname/dok-api-cli.git
cd dok-api-cli
uv sync

# または uvx で直接実行（インストール不要）
uvx --from . dok
```

## 設定

### 対話的に設定

```bash
uv run dok configure
```

`~/.config/dok/config.toml` に認証情報を保存します。

### 環境変数で設定（CI/CD・コンテナ向け）

```bash
export DOK_ACCESS_TOKEN=your-access-token
export DOK_ACCESS_TOKEN_SECRET=your-access-token-secret
```

### コマンドラインオプションで指定

```bash
dok --token YOUR_TOKEN --token-secret YOUR_SECRET task list
```

### 設定の優先順位

CLIオプション > 環境変数 > `~/.config/dok/config.toml`

設定ファイルが存在しなくても、環境変数またはCLIオプションのみで動作します。

### config.toml の形式

```toml
[default]
access_token = "your-access-token"
access_token_secret = "your-access-token-secret"

[staging]
access_token = "staging-token"
access_token_secret = "staging-secret"
base_url = "https://custom.example.com/api/1.0"
```

## 使い方

### グローバルオプション

| オプション | 環境変数 | 説明 |
|---|---|---|
| `--token` | `DOK_ACCESS_TOKEN` | アクセストークン |
| `--token-secret` | `DOK_ACCESS_TOKEN_SECRET` | アクセストークンシークレット |
| `--base-url` | `DOK_BASE_URL` | API Base URL |
| `--profile / -p` | | 使用するプロファイル名（デフォルト: `default`） |
| `--output / -o` | | 出力形式 `table`（デフォルト）または `json` |

### タスク

```bash
# 一覧表示
dok task list
dok task list --status running
dok task list --tag my-tag

# 詳細表示
dok task show <task-id>

# 作成（JSONファイルから）
dok task create -f task.json

# 作成（オプション指定）
dok task create \
  --name my-task \
  --image ghcr.io/example/myapp:latest \
  --plan v100-32gb \
  --command '["python", "train.py"]' \
  --env BATCH_SIZE=32 \
  --env MODEL_PATH=/data/model.pt \
  --tag experiment

# キャンセル・削除
dok task cancel <task-id>
dok task delete <task-id>

# ダウンロードURL取得
dok task download <task-id> output

# ログのストリーミング表示
dok task logs <task-id>
dok task logs <task-id> 1  # コンテナインデックス指定
```

#### タスク定義ファイル（task.json）

```json
{
  "name": "my-task",
  "tags": ["experiment"],
  "execution_time_limit_sec": 3600,
  "containers": [
    {
      "image": "ghcr.io/example/myapp:latest",
      "plan": "v100-32gb",
      "command": ["python", "train.py"],
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

### レジストリ

```bash
dok registry list
dok registry show <registry-id>
dok registry create --hostname ghcr.io --username myuser --password mypass
dok registry update <registry-id> --hostname ghcr.io --username myuser --password newpass
dok registry delete <registry-id>
```

### アーティファクト

```bash
dok artifact list
dok artifact list --task <task-id>
dok artifact show <artifact-id>
dok artifact download <artifact-id> --out ./output.tar.gz
```

### GPUプラン

```bash
dok plan list
```

### SSH公開鍵

```bash
dok ssh list
dok ssh show <key-id>
dok ssh create --name my-key --key-file ~/.ssh/id_rsa.pub
dok ssh update <key-id> --name new-name
dok ssh delete <key-id>
```

### 認証・料金

```bash
dok auth show
dok auth agree

dok billing show
dok billing prices
```

## 開発

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy src/
```
