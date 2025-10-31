# デプロイヘルパースクリプト

このディレクトリには、クラウドデプロイを簡単にするためのスクリプトが含まれています。

## prepare_cloud_deploy.sh / prepare_cloud_deploy.ps1

Google Drive認証情報（`credentials.json` と `token.pickle`）をbase64エンコードして、クラウド環境の環境変数として設定できる形式で出力します。

### 使用方法

#### Linux/Mac

```bash
# スクリプトに実行権限を付与（初回のみ）
chmod +x scripts/prepare_cloud_deploy.sh

# スクリプトを実行
./scripts/prepare_cloud_deploy.sh
```

#### Windows (PowerShell)

```powershell
# スクリプトを実行
.\scripts\prepare_cloud_deploy.ps1
```

### 前提条件

1. `credentials.json` がプロジェクトルートに配置されていること
2. ローカルで一度 `python main.py` を実行して `token.pickle` が生成されていること

### 出力

スクリプトを実行すると、`cloud_env_vars.txt` ファイルが生成されます。このファイルには以下が含まれます：

- `GOOGLE_CREDENTIALS_BASE64`: base64エンコードされた `credentials.json`
- `GOOGLE_TOKEN_BASE64`: base64エンコードされた `token.pickle`
- その他の必要な環境変数のテンプレート

### 次のステップ

1. `cloud_env_vars.txt` を開く
2. APIキー（`ANTHROPIC_API_KEY`、`LINE_CHANNEL_ACCESS_TOKEN`等）を入力
3. クラウドプラットフォーム（Railway、Render等）の環境変数設定画面に内容をコピー&ペースト
4. デプロイを実行

詳細は [DEPLOY.md](../DEPLOY.md) を参照してください。

## セキュリティ上の注意

- `cloud_env_vars.txt` には機密情報が含まれます
- このファイルは `.gitignore` に追加されていますが、誤ってコミットしないよう注意してください
- デプロイ後は `cloud_env_vars.txt` を安全に削除することを推奨します
