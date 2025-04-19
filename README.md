# Discord & Misskey 連携サマライザー

このプロジェクトは、Discordのチャンネルメッセージを取得し、要約してMisskeyに投稿するAPIサービスです。また、RSSフィードの取得と処理も行います。

## 主な機能

- **Discordメッセージの取得**: 指定したDiscordチャンネルからメッセージを取得
- **メッセージの要約**: Google Cloud VertexAIのGeminiモデルを使用してメッセージやWebコンテンツを要約
- **Misskeyへの投稿**: 要約したコンテンツをMisskeyに投稿
- **RSSフィード処理**: 指定したRSSフィードからエントリーを取得

## 技術スタック

- **バックエンド**: FastAPI, Python 3.11+
- **Discord連携**: discord.py
- **AI/ML**: Google Cloud VertexAI (Gemini)
- **その他**: LangChain, feedparser

## インストール方法

### 前提条件

- Python 3.11以上
- Discord Botトークン
- Misskey APIトークン
- Google Cloud Projectの設定（VertexAI APIの有効化）

### セットアップ

1. リポジトリをクローン

```bash
git clone <repository-url>
cd summarizer
```

2. 仮想環境を作成

```bash
uv init
```

3. 依存パッケージをインストール

```bash
uv sync --frozen
```

4. 環境変数の設定

`.env.example`ファイルを`.env`にコピーして、必要な環境変数を設定します。

## 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| DISCORD_BOT_TOKEN | Discord Botのトークン | 必須 |
| DISCORD_CHANNEL_ID | 監視するDiscordチャンネルのID | 必須 |
| API_BASE_URL | APIのベースURL | http://localhost:8000 |
| MISSKY_HOST | MisskeyのホストURL | 必須 |
| MISSKY_TOKEN | MisskeyのAPIトークン | 必須 |
| PROJECT_ID | Google Cloud ProjectのID | 必須 |
| REGION | Google Cloudのリージョン | 必須 |
| RSS_URLS | RSSフィードのURL（カンマ区切りで複数指定可能） | https://b.hatena.ne.jp/hotentry/it.rss |

## 使用方法

### サーバーの起動

```bash
uv run main.py
```

サーバーはデフォルトで`http://localhost:8080`で起動します。

### APIエンドポイント

| エンドポイント | メソッド | 説明 |
|---------------|---------|------|
| `/` | GET | APIの稼働確認 |
| `/channel/{channel_id}/messages` | GET | 指定したDiscordチャンネルのメッセージを取得 |
| `/misskey/summary` | GET | 過去1時間のDiscordメッセージを要約してMisskeyに投稿 |
| `/rss/entries` | GET | 設定されたRSSフィードのエントリーURLを取得 |

## Docker

Dockerを使用して環境を構築することもできます。

```bash
docker-compose up -d
```

