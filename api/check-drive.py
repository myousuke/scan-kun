"""
Vercel Serverless Function for Google Drive monitoring
"""
import os
import sys
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_drive import GoogleDriveMonitor
from llm_summarizer import LLMSummarizer
from line_notifier import LINENotifier
from config import Config


def handler(request):
    """
    Vercel Serverless Function ハンドラー

    この関数はVercel Cron Jobsまたは外部のcronサービスから定期的に呼び出されます。
    """
    try:
        print(f"[{datetime.now()}] Google Drive チェック開始")

        # 環境変数から設定を読み込む
        check_interval_minutes = int(os.getenv('CHECK_INTERVAL_MINUTES', '10'))

        # 各コンポーネントを初期化
        drive_monitor = GoogleDriveMonitor(Config.DRIVE_CREDENTIALS_FILE)
        llm_summarizer = LLMSummarizer(Config.ANTHROPIC_API_KEY)
        line_notifier = LINENotifier(
            Config.LINE_CHANNEL_ACCESS_TOKEN,
            Config.LINE_USER_ID
        )

        # 過去N分間のファイルをチェック
        since_time = datetime.utcnow() - timedelta(minutes=check_interval_minutes)
        new_files = drive_monitor.get_recent_files(
            folder_id=Config.DRIVE_FOLDER_ID,
            since=since_time
        )

        if not new_files:
            print(f"新しいファイルはありません（過去{check_interval_minutes}分）")
            return {
                'statusCode': 200,
                'body': {
                    'message': 'No new files',
                    'checked_since': since_time.isoformat(),
                    'file_count': 0
                }
            }

        print(f"{len(new_files)}件の新しいファイルを検出")
        processed_count = 0

        # 各ファイルを処理
        for file_info in new_files:
            try:
                file_id = file_info['id']
                filename = file_info['name']
                mime_type = file_info.get('mimeType', 'unknown')
                file_size = int(file_info.get('size', 0))

                print(f"処理中: {filename}")

                # ファイルサイズチェック
                if file_size > Config.MAX_FILE_SIZE:
                    print(f"スキップ（ファイルサイズ超過）: {filename}")
                    continue

                # ファイル内容をダウンロード
                content = drive_monitor.download_file_content(file_id, mime_type)
                if content is None:
                    continue

                # テキストを抽出
                text_content = drive_monitor.extract_text_from_content(
                    content, mime_type, filename
                )

                # サマリーを生成
                from main import get_file_type
                file_type = get_file_type(mime_type)
                summary = llm_summarizer.summarize_with_context(
                    filename=filename,
                    content=text_content,
                    file_type=file_type,
                    max_length=Config.SUMMARY_MAX_LENGTH
                )

                # LINEで通知
                file_url = f"https://drive.google.com/file/d/{file_id}/view"
                success = line_notifier.send_file_summary(
                    filename=filename,
                    summary=summary,
                    file_url=file_url
                )

                if success:
                    processed_count += 1
                    print(f"✓ 完了: {filename}")

            except Exception as e:
                print(f"ファイル処理エラー ({filename}): {e}")
                continue

        return {
            'statusCode': 200,
            'body': {
                'message': 'Success',
                'checked_since': since_time.isoformat(),
                'files_found': len(new_files),
                'files_processed': processed_count
            }
        }

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()

        return {
            'statusCode': 500,
            'body': {
                'error': str(e)
            }
        }
