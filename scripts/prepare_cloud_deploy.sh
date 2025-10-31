#!/bin/bash

# クラウドデプロイ用の環境変数を準備するスクリプト

set -e

echo "===================================="
echo "クラウドデプロイ準備スクリプト"
echo "===================================="
echo ""

# credentials.jsonの確認
if [ ! -f "credentials.json" ]; then
    echo "❌ credentials.json が見つかりません"
    echo "   Google Cloud Consoleから認証情報をダウンロードして配置してください"
    exit 1
fi

# token.pickleの確認
if [ ! -f "token.pickle" ]; then
    echo "⚠️  token.pickle が見つかりません"
    echo "   ローカルで一度実行して認証を完了してください:"
    echo "   python main.py"
    echo ""
    read -p "認証が完了している場合は 'y' を入力: " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "📦 認証情報をbase64エンコード中..."
echo ""

# credentials.jsonをエンコード
CREDENTIALS_BASE64=$(cat credentials.json | base64 | tr -d '\n')
echo "✅ GOOGLE_CREDENTIALS_BASE64:"
echo ""
echo "$CREDENTIALS_BASE64"
echo ""
echo "---"
echo ""

# token.pickleをエンコード
if [ -f "token.pickle" ]; then
    TOKEN_BASE64=$(cat token.pickle | base64 | tr -d '\n')
    echo "✅ GOOGLE_TOKEN_BASE64:"
    echo ""
    echo "$TOKEN_BASE64"
    echo ""
    echo "---"
    echo ""
fi

# 環境変数ファイルを生成
OUTPUT_FILE="cloud_env_vars.txt"
cat > "$OUTPUT_FILE" <<EOF
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
EOF

if [ -f "token.pickle" ]; then
    echo "GOOGLE_TOKEN_BASE64=$TOKEN_BASE64" >> "$OUTPUT_FILE"
fi

echo "✅ 環境変数ファイルを生成しました: $OUTPUT_FILE"
echo ""
echo "📋 次のステップ:"
echo "1. $OUTPUT_FILE を開いて、APIキーなどの値を入力"
echo "2. クラウドプラットフォーム（Railway、Render等）の環境変数設定にコピー&ペースト"
echo "3. デプロイを実行"
echo ""
echo "詳細は DEPLOY.md を参照してください"
