# デプロイガイド

このガイドでは、Google Drive監視システムを様々な環境にデプロイする方法を説明します。

## 目次

1. [Vercel（サーバーレス、無料枠あり）](#1-vercelサーバーレス無料枠あり)
2. [Docker + Docker Compose（推奨）](#2-docker--docker-compose推奨)
3. [Railway（クラウド、無料枠あり）](#3-railwayクラウド無料枠あり)
4. [Render（クラウド、無料枠あり）](#4-renderクラウド無料枠あり)
5. [systemd（Linuxサーバー）](#5-systemdlinuxサーバー)

---

## 1. Vercel（サーバーレス、無料枠あり）

Vercelはサーバーレス関数として実行します。Cron Jobsまたは外部サービスから定期的に呼び出されます。

### 特徴

- 完全無料で利用可能（無料枠内）
- サーバー不要、メンテナンスフリー
- GitHubと連携した自動デプロイ
- 定期実行はVercel Cron Jobs（Proプラン）またはGitHub Actions（無料）で実現

### 前提条件

- [Vercel](https://vercel.com/)アカウント
- GitHubリポジトリ
- ローカルで `credentials.json` と `token.pickle` を取得済み

### 手順

#### 1.1 認証情報の準備

ローカルで認証情報をbase64エンコードします：

```bash
# Linux/Mac
./scripts/prepare_cloud_deploy.sh

# Windows
.\scripts\prepare_cloud_deploy.ps1
```

生成された `cloud_env_vars.txt` の内容を控えておきます。

#### 1.2 Vercelプロジェクトの作成

1. [Vercel Dashboard](https://vercel.com/dashboard)にログイン
2. "Add New..." → "Project" をクリック
3. GitHubリポジトリをインポート
4. このリポジトリを選択

#### 1.3 環境変数の設定

Vercelのプロジェクト設定で以下の環境変数を追加：

**Settings** → **Environment Variables** から以下を設定：

```
ANTHROPIC_API_KEY=sk-ant-xxxxx
LINE_CHANNEL_ACCESS_TOKEN=xxxxx
LINE_USER_ID=Uxxxxx
DRIVE_FOLDER_ID=xxxxx（オプション）
GOOGLE_CREDENTIALS_BASE64=[cloud_env_vars.txtから取得]
GOOGLE_TOKEN_BASE64=[cloud_env_vars.txtから取得]
CHECK_INTERVAL_MINUTES=10
```

#### 1.4 デプロイ

"Deploy" をクリックしてデプロイを開始します。数分でデプロイが完了します。

#### 1.5 定期実行の設定

**オプションA: Vercel Cron Jobs（Proプランのみ）**

`vercel.json` にCron設定が含まれているため、自動的に10分ごとに実行されます。

**オプションB: GitHub Actions（無料プラン推奨）**

1. GitHubリポジトリの **Settings** → **Secrets and variables** → **Actions** を開く

2. 新しいシークレットを追加：
   - Name: `VERCEL_FUNCTION_URL`
   - Value: `https://your-project.vercel.app`（VercelのプロジェクトURL）

3. `.github/workflows/cron-check-drive.yml` が自動的に10分ごとに実行されます

4. 手動実行も可能：
   - GitHubリポジトリの **Actions** タブを開く
   - "Check Google Drive (Cron)" を選択
   - "Run workflow" をクリック

#### 1.6 動作確認

1. GitHub Actionsの実行ログを確認
2. LINEに通知が届くことを確認
3. Vercelのログを確認：
   - Vercel Dashboard → プロジェクト → **Functions** タブ
   - `/api/check-drive` のログを確認

### トラブルシューティング

#### 関数タイムアウト

```
Error: Function execution timed out
```

→ `vercel.json` の `maxDuration` を増やす（Proプランでは最大300秒）

#### 認証エラー

```
Error: Failed to authenticate with Google Drive API
```

→ `GOOGLE_CREDENTIALS_BASE64` と `GOOGLE_TOKEN_BASE64` が正しく設定されているか確認

#### GitHub Actionsが実行されない

→ リポジトリの **Settings** → **Actions** → **General** で "Allow all actions and reusable workflows" が有効になっているか確認

### コスト

- **Vercel無料枠**:
  - サーバーレス関数実行: 100GB-時間/月
  - デプロイ: 100回/日
  - 帯域幅: 100GB/月

- **GitHub Actions無料枠**:
  - 2,000分/月（パブリックリポジトリは無制限）

10分ごとに実行する場合、月間約4,320回の実行で、完全に無料枠内で運用可能です。

---

## 2. Docker + Docker Compose（推奨）

Dockerを使用した最もシンプルで移植性の高いデプロイ方法です。

### 前提条件

- Docker と Docker Compose がインストールされていること
- `SETUP.md` に従って環境変数とAPI設定が完了していること

### 手順

#### 1.1 credentials.json の配置

Google Drive APIの認証情報ファイルをプロジェクトルートに配置：

```bash
# credentials.json をプロジェクトルートにコピー
cp /path/to/your/credentials.json ./credentials.json
```

#### 1.2 .env ファイルの設定

```bash
cp .env.example .env
# .env を編集して実際の値を設定
```

#### 1.3 初回Google認証の実行

Dockerコンテナ内で初回認証を行う必要があります：

```bash
# 一時的にインタラクティブモードで起動して認証
docker-compose run --rm drive-monitor python main.py
```

ブラウザが開かない場合は、表示されたURLをコピーしてブラウザで開き、認証を完了してください。
`token.pickle` が作成されたら `Ctrl+C` で終了します。

#### 1.4 バックグラウンドで起動

```bash
# バックグラウンドで起動
docker-compose up -d

# ログを確認
docker-compose logs -f

# 停止
docker-compose down

# 再起動
docker-compose restart
```

### トラブルシューティング

#### 認証がうまくいかない場合

```bash
# コンテナに入って手動で認証
docker-compose run --rm drive-monitor /bin/bash
python main.py
```

#### ログの確認

```bash
# リアルタイムでログを表示
docker-compose logs -f drive-monitor

# 最後の100行を表示
docker-compose logs --tail=100 drive-monitor
```

---

## 3. Railway（クラウド、無料枠あり）

Railwayは簡単にアプリケーションをデプロイできるクラウドプラットフォームです。

### 前提条件

- [Railway](https://railway.app/)アカウント
- Railway CLI（オプション）

### 手順

#### 2.1 Railwayプロジェクトの作成

1. [Railway](https://railway.app/)にログイン
2. "New Project" をクリック
3. "Deploy from GitHub repo" を選択
4. このリポジトリを選択

#### 2.2 環境変数の設定

Railwayのダッシュボードで以下の環境変数を設定：

```
ANTHROPIC_API_KEY=your_api_key
LINE_CHANNEL_ACCESS_TOKEN=your_token
LINE_USER_ID=your_user_id
DRIVE_FOLDER_ID=your_folder_id
POLL_INTERVAL=300
MAX_FILE_SIZE=10485760
SUMMARY_MAX_LENGTH=5000
```

#### 2.3 Google Drive認証情報の設定

Railwayでは `credentials.json` をファイルとしてアップロードできないため、環境変数として設定します：

```bash
# credentials.jsonの内容をbase64エンコード
cat credentials.json | base64 > credentials.txt
```

Railwayの環境変数に追加：

```
GOOGLE_CREDENTIALS_BASE64=[credentials.txtの内容をペースト]
```

そして、`google_drive.py` を修正して環境変数から読み込むようにする必要があります（後述）。

#### 2.4 デプロイ

Railwayは自動的にデプロイを開始します。ログを確認して正常に起動したことを確認してください。

### 注意事項

- Railwayの無料枠では月$5相当のリソースが利用可能
- Google Drive認証（OAuth）が初回に必要だが、Railwayではブラウザが開けないため、ローカルで `token.pickle` を生成してからアップロードする方法が必要
- **推奨**: ローカルで認証後、`token.pickle` を環境変数としてbase64エンコードして設定

### Railway用のcredentials対応

`config.py` に以下を追加：

```python
import base64
import json

# Google認証情報を環境変数から取得（Railway用）
credentials_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
if credentials_base64:
    credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
    with open('credentials.json', 'w') as f:
        f.write(credentials_json)
```

---

## 4. Render（クラウド、無料枠あり）

Renderは無料枠が充実したクラウドプラットフォームです。

### 前提条件

- [Render](https://render.com/)アカウント

### 手順

#### 3.1 Renderプロジェクトの作成

1. [Render Dashboard](https://dashboard.render.com/)にログイン
2. "New +" → "Background Worker" を選択
3. GitHubリポジトリを接続
4. このリポジトリを選択

#### 3.2 設定

- **Name**: `google-drive-monitor`
- **Environment**: `Docker`
- **Docker Command**: `python -u main.py` （自動検出されるはず）
- **Instance Type**: `Free`

#### 3.3 環境変数の設定

Renderのダッシュボードで環境変数を追加：

```
ANTHROPIC_API_KEY
LINE_CHANNEL_ACCESS_TOKEN
LINE_USER_ID
DRIVE_FOLDER_ID
POLL_INTERVAL=300
MAX_FILE_SIZE=10485760
SUMMARY_MAX_LENGTH=5000
```

#### 3.4 Google Drive認証

Railwayと同様に、`credentials.json` と `token.pickle` を環境変数として設定する必要があります。

```bash
# credentials.jsonをbase64エンコード
cat credentials.json | base64

# token.pickleをbase64エンコード（ローカルで認証後）
cat token.pickle | base64
```

環境変数に追加：

```
GOOGLE_CREDENTIALS_BASE64=[base64エンコードされたcredentials.json]
GOOGLE_TOKEN_BASE64=[base64エンコードされたtoken.pickle]
```

#### 3.5 デプロイ

"Create Background Worker" をクリックしてデプロイを開始します。

### 注意事項

- Renderの無料枠では750時間/月のコンピュート時間が利用可能
- 無料インスタンスは15分間アクティビティがないとスリープするため、Worker（バックグラウンドプロセス）として設定することが重要

---

## 5. systemd（Linuxサーバー）

既存のLinuxサーバーがある場合、systemdサービスとして実行できます。

### 前提条件

- Linux サーバー（Ubuntu、Debian、CentOS等）
- Python 3.8以上
- systemd

### 手順

#### 4.1 プロジェクトのセットアップ

```bash
# プロジェクトをクローン
cd /opt
sudo git clone https://github.com/yourusername/scan-kun.git
cd scan-kun

# 仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# パッケージをインストール
pip install -r requirements.txt
```

#### 4.2 認証情報の設定

```bash
# credentials.jsonを配置
sudo cp /path/to/credentials.json /opt/scan-kun/credentials.json

# .envファイルを作成
sudo cp .env.example .env
sudo nano .env  # 編集
```

#### 4.3 初回認証

```bash
# 仮想環境を有効化
source venv/bin/activate

# 初回起動して認証
python main.py
# ブラウザで認証を完了
# Ctrl+C で終了
```

#### 4.4 systemdサービスの設定

```bash
# サービスファイルを編集
sudo nano drive-monitor.service

# 以下を適切に変更：
# - YOUR_USERNAME → 実際のユーザー名
# - /path/to/scan-kun → /opt/scan-kun

# サービスファイルをコピー
sudo cp drive-monitor.service /etc/systemd/system/

# systemdをリロード
sudo systemctl daemon-reload

# サービスを有効化
sudo systemctl enable drive-monitor

# サービスを起動
sudo systemctl start drive-monitor

# ステータスを確認
sudo systemctl status drive-monitor
```

#### 4.5 ログの確認

```bash
# リアルタイムでログを表示
sudo journalctl -u drive-monitor -f

# 最近のログを表示
sudo journalctl -u drive-monitor -n 100

# 特定の期間のログを表示
sudo journalctl -u drive-monitor --since "1 hour ago"
```

#### 4.6 サービスの管理

```bash
# 停止
sudo systemctl stop drive-monitor

# 再起動
sudo systemctl restart drive-monitor

# 無効化
sudo systemctl disable drive-monitor

# ステータス確認
sudo systemctl status drive-monitor
```

### セキュリティ設定

より安全に実行するため、専用ユーザーを作成することを推奨します：

```bash
# 専用ユーザーを作成
sudo useradd -r -s /bin/false drive-monitor

# プロジェクトディレクトリの所有者を変更
sudo chown -R drive-monitor:drive-monitor /opt/scan-kun

# サービスファイルのUserとGroupを変更
sudo nano /etc/systemd/system/drive-monitor.service
# User=drive-monitor
# Group=drive-monitor

# サービスを再起動
sudo systemctl daemon-reload
sudo systemctl restart drive-monitor
```

---

## Google Drive OAuth認証の課題

クラウド環境（Railway、Render等）では、初回のGoogle OAuth認証がブラウザを必要とするため、以下の方法で対応します：

### 方法1: ローカルで認証してtoken.pickleをアップロード

1. ローカル環境で一度実行して `token.pickle` を生成
2. `token.pickle` をbase64エンコードして環境変数として設定

```bash
# token.pickleを生成（ローカル）
python main.py
# 認証完了後Ctrl+Cで終了

# base64エンコード
cat token.pickle | base64 > token.txt
```

3. `google_drive.py` を修正して環境変数から読み込むように変更：

```python
# google_drive.py の _authenticate メソッドに追加
token_base64 = os.getenv('GOOGLE_TOKEN_BASE64')
if token_base64 and not os.path.exists('token.pickle'):
    import base64
    token_data = base64.b64decode(token_base64)
    with open('token.pickle', 'wb') as token:
        token.write(token_data)
```

### 方法2: サービスアカウントを使用

より本格的な運用では、Google Cloud のサービスアカウントを使用することを推奨します。
これにより、OAuthフローなしで認証できます。

詳細は [Google Cloudドキュメント](https://cloud.google.com/iam/docs/service-accounts) を参照してください。

---

## 推奨デプロイ方法の選び方

| 環境 | 推奨度 | メリット | デメリット |
|------|--------|----------|------------|
| Vercel | ⭐⭐⭐⭐⭐ | 完全無料、サーバー不要、メンテナンスフリー | サーバーレスなので継続的プロセスには向かない（Cron必要） |
| Docker Compose | ⭐⭐⭐⭐⭐ | 簡単、移植性高い、ローカルでもクラウドでも動く | Dockerの知識が必要 |
| systemd | ⭐⭐⭐⭐ | 既存サーバーを活用、フルコントロール | サーバー管理の知識が必要 |
| Railway | ⭐⭐⭐ | 簡単、自動デプロイ、無料枠あり | OAuth認証の対応が必要 |
| Render | ⭐⭐⭐ | 無料枠が充実、信頼性高い | OAuth認証の対応が必要 |

### 初心者向け
- **完全無料でクラウド**: **Vercel + GitHub Actions**
- **ローカルで試す**: **Docker Compose**

### 本番運用向け
- **コスト重視**: **Vercel**（完全無料）
- **フルコントロール**: **systemd（VPS）**
- **簡単運用**: **Docker Compose（クラウドVM）**

---

## トラブルシューティング

### Google Drive API エラー

```
Error: invalid_grant
```

→ `token.pickle` を削除して再認証

### LINE送信エラー

```
LINE Messaging API error
```

→ トークンとユーザーIDを確認

### メモリ不足

→ `MAX_FILE_SIZE` を減らす、または `SUMMARY_MAX_LENGTH` を減らす

### 頻繁な再起動

→ ログを確認して原因を特定。API制限に引っかかっている可能性がある場合は `POLL_INTERVAL` を増やす

---

## 本番運用の推奨設定

### 環境変数

```env
POLL_INTERVAL=300          # 5分ごと（APIクォータを節約）
MAX_FILE_SIZE=10485760     # 10MB（大きいファイルは除外）
SUMMARY_MAX_LENGTH=5000    # サマリー対象を制限してAPI使用量を削減
```

### モニタリング

- ログを定期的に確認
- LINEの起動通知で正常動作を確認
- Google Drive API、Claude API、LINE APIの使用量を監視

### バックアップ

- `token.pickle` のバックアップを取る
- `.env` ファイルのバックアップを取る（セキュアな場所に）

---

## サポート

問題が発生した場合は、以下を確認してください：

1. ログの確認
2. 環境変数の設定
3. API認証情報の有効性
4. ネットワーク接続

それでも解決しない場合は、GitHubのIssueで報告してください。
