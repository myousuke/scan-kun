"""LINE Messaging API integration module."""
import os
from typing import Optional
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage
)


class LINENotifier:
    """LINEで通知を送信するクラス"""

    def __init__(self, channel_access_token: Optional[str] = None,
                 user_id: Optional[str] = None):
        """
        初期化

        Args:
            channel_access_token: LINEチャネルアクセストークン
            user_id: 送信先のLINEユーザーID
        """
        self.channel_access_token = channel_access_token or os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.user_id = user_id or os.getenv('LINE_USER_ID')

        if not self.channel_access_token:
            raise ValueError("LINE_CHANNEL_ACCESS_TOKENが設定されていません")
        if not self.user_id:
            raise ValueError("LINE_USER_IDが設定されていません")

        # LINE Messaging APIクライアントの設定
        self.configuration = Configuration(access_token=self.channel_access_token)
        self.api_client = ApiClient(self.configuration)
        self.messaging_api = MessagingApi(self.api_client)

    def send_message(self, message: str) -> bool:
        """
        LINEメッセージを送信

        Args:
            message: 送信するメッセージ

        Returns:
            送信成功の場合True
        """
        try:
            # メッセージが長すぎる場合は分割（LINEの制限は5000文字）
            max_length = 4900
            if len(message) > max_length:
                # 分割して送信
                parts = []
                while message:
                    parts.append(message[:max_length])
                    message = message[max_length:]

                for i, part in enumerate(parts):
                    if i > 0:
                        part = f"(続き {i+1}/{len(parts)})\n{part}"
                    self._send_single_message(part)
                return True
            else:
                return self._send_single_message(message)

        except Exception as e:
            print(f"LINEメッセージ送信エラー: {e}")
            return False

    def _send_single_message(self, message: str) -> bool:
        """
        単一のLINEメッセージを送信

        Args:
            message: 送信するメッセージ

        Returns:
            送信成功の場合True
        """
        try:
            push_message_request = PushMessageRequest(
                to=self.user_id,
                messages=[TextMessage(text=message)]
            )

            self.messaging_api.push_message(push_message_request)
            print(f"LINEメッセージ送信成功: {len(message)}文字")
            return True

        except Exception as e:
            print(f"LINEメッセージ送信エラー: {e}")
            return False

    def send_file_summary(self, filename: str, summary: str,
                         file_url: Optional[str] = None) -> bool:
        """
        ファイルサマリーを整形して送信

        Args:
            filename: ファイル名
            summary: サマリー内容
            file_url: ファイルのURL（オプション）

        Returns:
            送信成功の場合True
        """
        message = f"""🆕 新しいファイルが追加されました

{summary}
"""

        if file_url:
            message += f"\n🔗 ファイル: {file_url}"

        return self.send_message(message)

    def send_notification(self, title: str, body: str) -> bool:
        """
        通知メッセージを送信

        Args:
            title: タイトル
            body: 本文

        Returns:
            送信成功の場合True
        """
        message = f"""📢 {title}

{body}
"""
        return self.send_message(message)

    def send_error(self, error_message: str) -> bool:
        """
        エラーメッセージを送信

        Args:
            error_message: エラーメッセージ

        Returns:
            送信成功の場合True
        """
        message = f"""⚠️ エラーが発生しました

{error_message}
"""
        return self.send_message(message)
