#!/usr/bin/env python3
"""
Google Drive Monitor with LLM Summary and LINE Notification

Google Driveを監視し、新しいファイルが追加されたらLLMでサマリーを生成してLINEで通知します。
"""
import time
import sys
from datetime import datetime
from typing import Dict
from config import Config
from google_drive import GoogleDriveMonitor
from llm_summarizer import LLMSummarizer
from line_notifier import LINENotifier


def get_file_type(mime_type: str) -> str:
    """
    MIMEタイプから読みやすいファイルタイプ名を取得

    Args:
        mime_type: MIMEタイプ

    Returns:
        ファイルタイプ名
    """
    type_map = {
        'application/pdf': 'PDF',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word文書',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel',
        'application/vnd.google-apps.document': 'Google Docs',
        'application/vnd.google-apps.spreadsheet': 'Google Sheets',
        'application/vnd.google-apps.presentation': 'Google Slides',
        'text/plain': 'テキスト',
        'text/csv': 'CSV',
        'application/json': 'JSON',
    }

    for key, value in type_map.items():
        if key in mime_type:
            return value

    if 'text/' in mime_type:
        return 'テキスト'
    elif 'image/' in mime_type:
        return '画像'
    elif 'video/' in mime_type:
        return '動画'
    elif 'audio/' in mime_type:
        return '音声'
    else:
        return 'その他'


def format_file_size(size_bytes: int) -> str:
    """
    ファイルサイズを読みやすい形式に変換

    Args:
        size_bytes: バイト単位のサイズ

    Returns:
        フォーマットされたサイズ文字列
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"


def process_new_file(file_info: Dict, drive_monitor: GoogleDriveMonitor,
                    llm_summarizer: LLMSummarizer, line_notifier: LINENotifier) -> bool:
    """
    新しいファイルを処理

    Args:
        file_info: ファイル情報
        drive_monitor: Google Driveモニター
        llm_summarizer: LLMサマリー生成器
        line_notifier: LINE通知送信者

    Returns:
        処理成功の場合True
    """
    try:
        file_id = file_info['id']
        filename = file_info['name']
        mime_type = file_info.get('mimeType', 'unknown')
        file_size = int(file_info.get('size', 0))

        print(f"\n新しいファイルを検出: {filename} ({mime_type})")

        # ファイルサイズチェック
        if file_size > Config.MAX_FILE_SIZE:
            size_str = format_file_size(file_size)
            max_size_str = format_file_size(Config.MAX_FILE_SIZE)
            message = f"""📄 ファイル名: {filename}
📝 種類: {get_file_type(mime_type)}
⚠️ ファイルサイズ ({size_str}) が上限 ({max_size_str}) を超えているため、サマリーをスキップしました。"""
            line_notifier.send_message(f"🆕 新しいファイルが追加されました\n\n{message}")
            return True

        # ファイル内容をダウンロード
        print("ファイルをダウンロード中...")
        content = drive_monitor.download_file_content(file_id, mime_type)

        if content is None:
            line_notifier.send_error(f"ファイルのダウンロードに失敗しました: {filename}")
            return False

        # テキストを抽出
        print("テキストを抽出中...")
        text_content = drive_monitor.extract_text_from_content(content, mime_type, filename)

        # サマリーを生成
        print("LLMでサマリーを生成中...")
        file_type = get_file_type(mime_type)
        summary = llm_summarizer.summarize_with_context(
            filename=filename,
            content=text_content,
            file_type=file_type,
            max_length=Config.SUMMARY_MAX_LENGTH
        )

        # LINEで通知
        print("LINEに送信中...")
        file_url = f"https://drive.google.com/file/d/{file_id}/view"
        success = line_notifier.send_file_summary(
            filename=filename,
            summary=summary,
            file_url=file_url
        )

        if success:
            print(f"✓ 処理完了: {filename}")
        else:
            print(f"✗ LINE送信失敗: {filename}")

        return success

    except Exception as e:
        print(f"ファイル処理エラー: {e}")
        line_notifier.send_error(f"ファイル処理エラー ({filename}): {str(e)}")
        return False


def main():
    """メイン処理"""
    print("=" * 60)
    print("Google Drive Monitor with LLM Summary")
    print("=" * 60)
    print()

    # 設定の検証
    try:
        Config.validate()
        print("✓ 設定の検証完了")
    except ValueError as e:
        print(f"✗ {e}")
        sys.exit(1)

    # 各コンポーネントを初期化
    try:
        print("\n初期化中...")
        drive_monitor = GoogleDriveMonitor(Config.DRIVE_CREDENTIALS_FILE)
        llm_summarizer = LLMSummarizer(Config.ANTHROPIC_API_KEY)
        line_notifier = LINENotifier(
            Config.LINE_CHANNEL_ACCESS_TOKEN,
            Config.LINE_USER_ID
        )
        print("✓ 初期化完了")
    except Exception as e:
        print(f"✗ 初期化エラー: {e}")
        sys.exit(1)

    # 起動通知を送信
    start_message = f"""🚀 Google Drive監視を開始しました

⏰ 監視間隔: {Config.POLL_INTERVAL}秒
📁 監視フォルダ: {"全体" if not Config.DRIVE_FOLDER_ID else Config.DRIVE_FOLDER_ID[:20] + "..."}
📊 最大ファイルサイズ: {format_file_size(Config.MAX_FILE_SIZE)}
"""
    line_notifier.send_notification("監視開始", start_message.strip())

    print(f"\n監視を開始します...")
    print(f"監視間隔: {Config.POLL_INTERVAL}秒")
    if Config.DRIVE_FOLDER_ID:
        print(f"監視フォルダID: {Config.DRIVE_FOLDER_ID}")
    else:
        print("監視フォルダ: 全体")
    print("\nCtrl+C で終了")
    print("-" * 60)

    # 監視ループ
    try:
        while True:
            try:
                # 新しいファイルをチェック
                new_files = drive_monitor.check_new_files(Config.DRIVE_FOLDER_ID)

                if new_files:
                    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {len(new_files)}件の新しいファイルを検出")

                    for file_info in new_files:
                        process_new_file(
                            file_info,
                            drive_monitor,
                            llm_summarizer,
                            line_notifier
                        )
                        # 連続処理の間に少し待機
                        time.sleep(2)
                else:
                    # 定期的な生存確認ログ（1時間ごと）
                    current_time = datetime.now()
                    if current_time.minute == 0:
                        print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] 監視中... (新しいファイルなし)")

            except Exception as e:
                print(f"\n監視エラー: {e}")
                line_notifier.send_error(f"監視エラー: {str(e)}")

            # 次のチェックまで待機
            time.sleep(Config.POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n監視を終了します...")
        line_notifier.send_notification("監視終了", "Google Drive監視を終了しました")
        sys.exit(0)


if __name__ == '__main__':
    main()
