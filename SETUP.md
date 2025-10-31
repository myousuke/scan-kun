# セットアップガイド

このガイドでは、Google Drive監視システムのセットアップ手順を詳しく説明します。

## 前提条件

- Python 3.8以上がインストールされていること
- Google アカウント
- LINE アカウント
- Anthropic アカウント（Claude API利用のため）

## 1. リポジトリのクローン

```bash
git clone <repository-url>
cd scan-kun
```

## 2. Python仮想環境のセットアップ

```bash
# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化（Linux/Mac）
source venv/bin/activate

# 仮想環境の有効化（Windows）
venv\Scripts\activate

# パッケージのインストール
pip install -r requirements.txt
```

## 3. Google Drive APIの設定

### 3.1 Google Cloud Projectの作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成（または既存のプロジェクトを選択）
3. プロジェクト名を入力して「作成」をクリック

### 3.2 Google Drive APIの有効化

1. 左側のメニューから「APIとサービス」→「ライブラリ」を選択
2. 「Google Drive API」を検索
3. 「Google Drive API」をクリックして「有効にする」

### 3.3 OAuth 2.0認証情報の作成

1. 左側のメニューから「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「OAuth クライアント ID」を選択
3. 同意画面の設定を求められた場合:
   - 「外部」を選択（個人使用の場合）
   - アプリ名、ユーザーサポートメール、デベロッパーの連絡先情報を入力
   - スコープは設定不要（次へ）
   - テストユーザーに自分のGoogleアカウントを追加
4. OAuth クライアント IDの作成:
   - アプリケーションの種類: 「デスクトップアプリ」を選択
   - 名前を入力（例: "Google Drive Monitor"）
   - 「作成」をクリック
5. JSONファイルをダウンロード
6. ダウンロードしたファイルを `credentials.json` にリネームしてプロジェクトルートに配置

### 3.4 監視するフォルダIDの取得（オプション）

特定のフォルダのみを監視する場合:

1. Google Driveで監視したいフォルダを開く
2. URLを確認: `https://drive.google.com/drive/folders/FOLDER_ID`
3. `FOLDER_ID` の部分をコピー（後で `.env` に設定）

## 4. Anthropic Claude APIの設定

1. [Anthropic Console](https://console.anthropic.com/)にアクセス
2. アカウントを作成（まだの場合）
3. 「API Keys」から新しいAPIキーを作成
4. APIキーをコピー（後で `.env` に設定）

## 5. LINE Messaging APIの設定

### 5.1 LINE Developersコンソールでチャネルを作成

1. [LINE Developers Console](https://developers.line.biz/console/)にアクセス
2. ログインして「新規プロバイダー」を作成（既存のものを使用してもOK）
3. プロバイダー内で「新規チャネル作成」→「Messaging API」を選択
4. チャネル情報を入力:
   - チャネル名: 適当な名前（例: "Drive Monitor Bot"）
   - チャネル説明: 適当な説明
   - カテゴリ: 任意
   - サブカテゴリ: 任意
5. 利用規約に同意して「作成」

### 5.2 チャネルアクセストークンの取得

1. 作成したチャネルの「Messaging API設定」タブを開く
2. 「チャネルアクセストークン」セクションで「発行」をクリック
3. 表示されたトークンをコピー（後で `.env` に設定）

### 5.3 LINE ユーザーIDの取得

方法1: LINE Official Account Managerで確認
1. [LINE Official Account Manager](https://manager.line.biz/)にアクセス
2. 作成したアカウントを選択
3. 「設定」→「応答設定」で、Webhookを有効にする
4. LINEで自分のアカウントを友だち追加
5. 何かメッセージを送信

方法2: 簡易的な方法（推奨）
1. LINEアプリで作成したBotを友だち追加
2. 一時的にこのスクリプトを実行して取得:

```python
# get_user_id.py
import os
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi

access_token = "YOUR_CHANNEL_ACCESS_TOKEN"
configuration = Configuration(access_token=access_token)

with ApiClient(configuration) as api_client:
    line_bot_api = MessagingApi(api_client)
    # プロファイル取得などの方法でユーザーIDを取得
    # 詳細はLINE Bot SDKのドキュメントを参照
```

または、Bot設定で「Webhook URL」を一時的に設定し、RequestBinなどのサービスでリクエストを受け取ってユーザーIDを確認することもできます。

## 6. 環境変数の設定

1. `.env.example` をコピーして `.env` を作成:

```bash
cp .env.example .env
```

2. `.env` を編集して実際の値を設定:

```env
DRIVE_CREDENTIALS_FILE=credentials.json
DRIVE_FOLDER_ID=your_folder_id_here  # 全体を監視する場合は空欄
ANTHROPIC_API_KEY=sk-ant-xxxxx
LINE_CHANNEL_ACCESS_TOKEN=xxxxx
LINE_USER_ID=Uxxxxx
POLL_INTERVAL=300
MAX_FILE_SIZE=10485760
SUMMARY_MAX_LENGTH=5000
```

## 7. 初回認証

初回実行時にGoogle Driveの認証が必要です:

```bash
python main.py
```

ブラウザが開いて認証画面が表示されます:
1. Googleアカウントでログイン
2. 「このアプリはGoogleで確認されていません」と表示されたら「詳細」→「（アプリ名）に移動」をクリック
3. 権限を確認して「許可」をクリック
4. 認証が完了すると `token.pickle` ファイルが作成されます

## 8. 動作確認

1. プログラムが正常に起動したことを確認
2. LINEに起動通知が届くことを確認
3. Google Driveにテストファイルをアップロード
4. 数分後（POLL_INTERVAL秒後）にLINEにサマリーが届くことを確認

## トラブルシューティング

### Google Drive API認証エラー

- `credentials.json` が正しい場所にあるか確認
- Google Cloud Consoleで「Google Drive API」が有効になっているか確認
- `token.pickle` を削除して再認証を試す

### LINE送信エラー

- `LINE_CHANNEL_ACCESS_TOKEN` が正しいか確認
- `LINE_USER_ID` が正しいか確認（"U"で始まる文字列）
- LINEでBotを友だち追加しているか確認

### LLMサマリー生成エラー

- `ANTHROPIC_API_KEY` が正しいか確認
- APIの利用制限に達していないか確認
- インターネット接続を確認

## バックグラウンド実行

### Linux/Mac (systemd)

1. サービスファイルを作成: `/etc/systemd/system/drive-monitor.service`

```ini
[Unit]
Description=Google Drive Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/scan-kun
Environment="PATH=/path/to/scan-kun/venv/bin"
ExecStart=/path/to/scan-kun/venv/bin/python /path/to/scan-kun/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

2. サービスを有効化:

```bash
sudo systemctl daemon-reload
sudo systemctl enable drive-monitor
sudo systemctl start drive-monitor
sudo systemctl status drive-monitor
```

### Linux/Mac (screen/tmux)

```bash
# screenを使用
screen -S drive-monitor
python main.py
# Ctrl+A, D でデタッチ

# tmuxを使用
tmux new -s drive-monitor
python main.py
# Ctrl+B, D でデタッチ
```

### Docker

Dockerfileを作成して実行することも可能です（別途設定が必要）。

## 注意事項

- Google Drive APIには1日あたりのクエリ制限があります
- Claude APIは使用量に応じて課金されます
- LINE Messaging APIの無料プランには月間メッセージ数の制限があります
- `credentials.json`、`.env`、`token.pickle` は絶対にGitにコミットしないでください
