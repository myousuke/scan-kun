# GitHub Actions セットアップガイド

Vercelの無料プランで定期実行を行うために、GitHub Actionsを使用します。

## セットアップ手順

### 1. GitHub Actionsワークフローファイルの作成

GitHubのWebインターフェースで直接ファイルを作成します：

1. GitHubリポジトリページを開く
2. **Actions** タブをクリック
3. "set up a workflow yourself" をクリック（または "New workflow" → "set up a workflow yourself"）
4. ファイル名を `.github/workflows/cron-check-drive.yml` に変更
5. 以下の内容をコピー&ペースト：

```yaml
name: Check Google Drive (Cron)

on:
  schedule:
    # 10分ごとに実行（UTC時間）
    - cron: '*/10 * * * *'
  workflow_dispatch:  # 手動実行も可能

jobs:
  check-drive:
    runs-on: ubuntu-latest
    steps:
      - name: Call Vercel Serverless Function
        run: |
          curl -X GET "${{ secrets.VERCEL_FUNCTION_URL }}/api/check-drive" \
            -H "Content-Type: application/json" \
            -w "\nHTTP Status: %{http_code}\n"
```

6. "Commit changes" をクリック

### 2. GitHubシークレットの設定

1. リポジトリの **Settings** タブを開く
2. 左メニューから **Secrets and variables** → **Actions** を選択
3. "New repository secret" をクリック
4. 以下のシークレットを追加：

   - **Name**: `VERCEL_FUNCTION_URL`
   - **Secret**: `https://your-project.vercel.app`（VercelプロジェクトのURL）

5. "Add secret" をクリック

### 3. GitHub Actionsの有効化確認

1. リポジトリの **Settings** → **Actions** → **General** を開く
2. "Actions permissions" セクションで以下が選択されていることを確認：
   - "Allow all actions and reusable workflows" または
   - "Allow [organization] and select non-[organization], actions and reusable workflows"

3. "Workflow permissions" セクションで以下が選択されていることを確認：
   - "Read and write permissions" または
   - 最低限 "Read repository contents and packages permissions"

4. "Save" をクリック（変更した場合）

### 4. 動作確認

#### 手動実行でテスト

1. リポジトリの **Actions** タブを開く
2. 左サイドバーから "Check Google Drive (Cron)" を選択
3. "Run workflow" ドロップダウンをクリック
4. "Run workflow" ボタンをクリック
5. 実行が完了したらログを確認

#### 自動実行の確認

- ワークフローは10分ごとに自動実行されます
- **Actions** タブで実行履歴を確認できます
- LINEに通知が届くことを確認してください

### 5. トラブルシューティング

#### ワークフローが実行されない

**原因**: リポジトリがプライベートで、GitHub Actionsの実行時間を使い果たした可能性

**解決策**:
- パブリックリポジトリに変更（無制限）
- または GitHub Actionsの実行時間を確認（Settings → Billing）

#### "secret not found" エラー

**原因**: `VERCEL_FUNCTION_URL` シークレットが設定されていない

**解決策**:
- 上記の手順2を確認して、シークレットを追加

#### cURLコマンドが失敗する

**原因**: VercelのURLが間違っている、または関数がデプロイされていない

**解決策**:
- Vercel Dashboardでプロジェクトのデプロイ状況を確認
- URLが正しいか確認（`https://`で始まり、末尾に`/`は不要）

#### 403 Forbidden エラー

**原因**: Vercel関数へのアクセスが制限されている可能性

**解決策**:
- Vercel Dashboardで関数のアクセス設定を確認
- 必要に応じて認証を追加（より高度な設定）

## スケジュール変更

実行頻度を変更したい場合、cron式を編集します：

```yaml
schedule:
  - cron: '*/5 * * * *'   # 5分ごと
  - cron: '*/15 * * * *'  # 15分ごと
  - cron: '0 * * * *'     # 毎時0分
  - cron: '0 */6 * * *'   # 6時間ごと
```

**注意**: GitHub Actionsのcronは最短で5分間隔です。

## 代替案: Uptime Robot

GitHub Actionsの代わりに、外部のcronサービスも使用できます：

1. [Uptime Robot](https://uptimerobot.com/)に登録（無料）
2. "Add New Monitor" をクリック
3. Monitor Type: "HTTP(s)"
4. Friendly Name: "Google Drive Monitor"
5. URL: `https://your-project.vercel.app/api/check-drive`
6. Monitoring Interval: 5 minutes（無料プランの最短）
7. "Create Monitor" をクリック

これにより、GitHub Actionsを使わずに定期実行が可能です。

## コスト

- **GitHub Actions無料枠**:
  - パブリックリポジトリ: 無制限
  - プライベートリポジトリ: 2,000分/月

- 10分ごとの実行で月間約4,320回（実行時間は1回あたり数秒）
- ほとんどの場合、無料枠内で十分です

## 参考リンク

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron syntax](https://crontab.guru/)
- [Vercel Serverless Functions](https://vercel.com/docs/functions)
