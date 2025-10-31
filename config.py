"""Configuration settings for the Google Drive monitor."""
import os
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()


class Config:
    """設定クラス"""

    # Google Drive設定
    DRIVE_CREDENTIALS_FILE = os.getenv('DRIVE_CREDENTIALS_FILE', 'credentials.json')
    DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID', None)  # Noneの場合は全体を監視

    # Anthropic Claude API設定
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    # LINE Messaging API設定
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    LINE_USER_ID = os.getenv('LINE_USER_ID')

    # 監視設定
    POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '300'))  # 5分（秒単位）
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10MB（バイト単位）

    # LLMサマリー設定
    SUMMARY_MAX_LENGTH = int(os.getenv('SUMMARY_MAX_LENGTH', '5000'))  # サマリー対象の最大文字数

    @classmethod
    def validate(cls):
        """設定の妥当性をチェック"""
        errors = []

        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY が設定されていません")

        if not cls.LINE_CHANNEL_ACCESS_TOKEN:
            errors.append("LINE_CHANNEL_ACCESS_TOKEN が設定されていません")

        if not cls.LINE_USER_ID:
            errors.append("LINE_USER_ID が設定されていません")

        if not os.path.exists(cls.DRIVE_CREDENTIALS_FILE):
            errors.append(f"Google Drive認証情報ファイル '{cls.DRIVE_CREDENTIALS_FILE}' が見つかりません")

        if errors:
            raise ValueError("設定エラー:\n" + "\n".join(f"  - {error}" for error in errors))

        return True
