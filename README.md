# Google Drive Monitor with LLM Summary and LINE Notification

Google Driveを監視し、新しいファイルが追加されたらLLMでサマリーを生成してLINEで通知するシステムです。

## 機能

- Google Driveの指定フォルダを定期的に監視
- 新しいファイルが追加されたら自動検出
- Claude APIを使用してファイル内容のサマリーを生成
- LINE Messaging APIでサマリーを送信

## クイックスタート

### オプション1: Docker Compose（推奨）

```bash
# 環境変数を設定
cp .env.example .env
# .envを編集

# credentials.jsonを配置
cp /path/to/your/credentials.json ./credentials.json

# 起動
docker-compose up -d

# ログを確認
docker-compose logs -f
```

### オプション2: Python直接実行

詳細は [SETUP.md](SETUP.md) を参照してください。

## デプロイ

本番環境へのデプロイ方法は [DEPLOY.md](DEPLOY.md) を参照してください。

以下のデプロイオプションに対応しています：

- **Vercel**（サーバーレス、完全無料）
- **Docker + Docker Compose**（推奨、ローカル/サーバー）
- **Railway**（クラウド、無料枠あり）
- **Render**（クラウド、無料枠あり）
- **systemd**（Linuxサーバー）

## セットアップ

### 1. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. Google Drive API の設定

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Google Drive APIを有効化
3. 認証情報を作成（OAuth 2.0クライアントID）
4. `credentials.json`をプロジェクトルートに配置

### 3. Anthropic Claude API の設定

1. [Anthropic Console](https://console.anthropic.com/)でAPIキーを取得
2. `.env`ファイルに`ANTHROPIC_API_KEY`を設定

### 4. LINE Messaging API の設定

1. [LINE Developers Console](https://developers.line.biz/)でMessaging APIチャネルを作成
2. チャネルアクセストークンを取得
3. `.env`ファイルに`LINE_CHANNEL_ACCESS_TOKEN`と`LINE_USER_ID`を設定

### 5. 環境変数の設定

`.env.example`をコピーして`.env`を作成し、必要な値を設定してください。

```bash
cp .env.example .env
```

## 使用方法

```bash
python main.py
```

監視を開始すると、設定された間隔でGoogle Driveをチェックし、新しいファイルが追加されたら自動的にサマリーをLINEに送信します。

## 設定

`config.py`で以下の設定を変更できます：

- `POLL_INTERVAL`: 監視間隔（秒）
- `DRIVE_FOLDER_ID`: 監視するGoogle DriveフォルダのID
- `MAX_FILE_SIZE`: 処理する最大ファイルサイズ

## サポートされるファイル形式

- テキストファイル (.txt)
- PDF (.pdf)
- Word文書 (.docx)
- Excel (.xlsx)
- その他のテキストベースファイル

## 注意事項

- Google Drive APIには利用制限があります
- Claude APIの使用量に応じて課金されます
- LINE Messaging APIの無料枠に注意してください
