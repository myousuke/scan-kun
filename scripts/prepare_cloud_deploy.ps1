# クラウドデプロイ用の環境変数を準備するスクリプト (Windows PowerShell)

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "クラウドデプロイ準備スクリプト" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# credentials.jsonの確認
if (-Not (Test-Path "credentials.json")) {
    Write-Host "❌ credentials.json が見つかりません" -ForegroundColor Red
    Write-Host "   Google Cloud Consoleから認証情報をダウンロードして配置してください"
    exit 1
}

# token.pickleの確認
if (-Not (Test-Path "token.pickle")) {
    Write-Host "⚠️  token.pickle が見つかりません" -ForegroundColor Yellow
    Write-Host "   ローカルで一度実行して認証を完了してください:"
    Write-Host "   python main.py"
    Write-Host ""
    $response = Read-Host "認証が完了している場合は 'y' を入力"
    if ($response -ne 'y' -and $response -ne 'Y') {
        exit 1
    }
}

Write-Host ""
Write-Host "📦 認証情報をbase64エンコード中..." -ForegroundColor Green
Write-Host ""

# credentials.jsonをエンコード
$credentialsBytes = [System.IO.File]::ReadAllBytes("credentials.json")
$CREDENTIALS_BASE64 = [System.Convert]::ToBase64String($credentialsBytes)

Write-Host "✅ GOOGLE_CREDENTIALS_BASE64:" -ForegroundColor Green
Write-Host ""
Write-Host $CREDENTIALS_BASE64
Write-Host ""
Write-Host "---"
Write-Host ""

# token.pickleをエンコード
$TOKEN_BASE64 = ""
if (Test-Path "token.pickle") {
    $tokenBytes = [System.IO.File]::ReadAllBytes("token.pickle")
    $TOKEN_BASE64 = [System.Convert]::ToBase64String($tokenBytes)

    Write-Host "✅ GOOGLE_TOKEN_BASE64:" -ForegroundColor Green
    Write-Host ""
    Write-Host $TOKEN_BASE64
    Write-Host ""
    Write-Host "---"
    Write-Host ""
}

# 環境変数ファイルを生成
$OUTPUT_FILE = "cloud_env_vars.txt"
$content = @"
# クラウド環境用の環境変数
# Railway、Render等のクラウドプラットフォームの環境変数設定画面にコピー&ペーストしてください

# 必須の環境変数
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here
LINE_USER_ID=your_line_user_id_here

# オプション（必要に応じて設定）
DRIVE_FOLDER_ID=
POLL_INTERVAL=300
MAX_FILE_SIZE=10485760
SUMMARY_MAX_LENGTH=5000

# Google Drive認証情報（base64エンコード済み）
GOOGLE_CREDENTIALS_BASE64=$CREDENTIALS_BASE64
"@

if (Test-Path "token.pickle") {
    $content += "`nGOOGLE_TOKEN_BASE64=$TOKEN_BASE64"
}

Set-Content -Path $OUTPUT_FILE -Value $content

Write-Host "✅ 環境変数ファイルを生成しました: $OUTPUT_FILE" -ForegroundColor Green
Write-Host ""
Write-Host "📋 次のステップ:" -ForegroundColor Yellow
Write-Host "1. $OUTPUT_FILE を開いて、APIキーなどの値を入力"
Write-Host "2. クラウドプラットフォーム（Railway、Render等）の環境変数設定にコピー&ペースト"
Write-Host "3. デプロイを実行"
Write-Host ""
Write-Host "詳細は DEPLOY.md を参照してください"
