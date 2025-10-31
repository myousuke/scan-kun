"""LLM integration module for summarizing file contents."""
import os
from typing import Optional
from anthropic import Anthropic


class LLMSummarizer:
    """Claude APIを使用してファイル内容をサマリーするクラス"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: Anthropic API key（Noneの場合は環境変数から取得）
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API keyが設定されていません")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def summarize_file(self, filename: str, content: str,
                      max_length: int = 5000) -> str:
        """
        ファイル内容をサマリー

        Args:
            filename: ファイル名
            content: ファイルの内容
            max_length: サマリー対象の最大文字数

        Returns:
            サマリー文
        """
        # 内容が長すぎる場合は切り詰める
        if len(content) > max_length:
            content = content[:max_length] + "\n...(以降省略)"

        prompt = f"""以下のファイルの内容を日本語で簡潔にサマリーしてください。

ファイル名: {filename}

内容:
{content}

サマリーには以下を含めてください：
1. ファイルの種類や目的
2. 主な内容のポイント（3-5点）
3. 重要な情報や注目すべき点

サマリーは200文字以内で、箇条書きで見やすくまとめてください。"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            summary = message.content[0].text
            return summary

        except Exception as e:
            print(f"LLMサマリー生成エラー: {e}")
            return f"[サマリー生成失敗: {filename}]\nエラー: {str(e)}"

    def summarize_with_context(self, filename: str, content: str,
                              file_type: str, max_length: int = 5000) -> str:
        """
        ファイルタイプを考慮したサマリー生成

        Args:
            filename: ファイル名
            content: ファイルの内容
            file_type: ファイルタイプ（例: "PDF", "Word文書", "テキスト"）
            max_length: サマリー対象の最大文字数

        Returns:
            サマリー文
        """
        # 内容が長すぎる場合は切り詰める
        if len(content) > max_length:
            content = content[:max_length] + "\n...(以降省略)"

        # ファイルタイプに応じたプロンプト調整
        type_specific_instructions = {
            "PDF": "PDFドキュメントとして、章立てや構成も考慮してサマリーしてください。",
            "Word文書": "文書として、主要なセクションや見出しを踏まえてサマリーしてください。",
            "Excel": "スプレッドシートとして、データの種類や構造を説明してください。",
            "テキスト": "テキストファイルとして、内容の要点をまとめてください。",
            "Google Docs": "Google Docsドキュメントとして、文書の構成と主要な内容をまとめてください。",
            "Google Sheets": "Google Sheetsとして、データの概要と主要な項目を説明してください。",
        }

        type_instruction = type_specific_instructions.get(
            file_type,
            "ファイルの内容を分析してサマリーしてください。"
        )

        prompt = f"""以下のファイルの内容を日本語で簡潔にサマリーしてください。

ファイル名: {filename}
ファイルタイプ: {file_type}

{type_instruction}

内容:
{content}

サマリー形式:
📄 ファイル名: {filename}
📝 種類: [ファイルの種類や目的を一言で]

🔍 主な内容:
• [ポイント1]
• [ポイント2]
• [ポイント3]

💡 注目ポイント:
[重要な情報や特記事項]

全体で250文字以内にまとめてください。"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            summary = message.content[0].text
            return summary

        except Exception as e:
            print(f"LLMサマリー生成エラー: {e}")
            return f"📄 {filename}\n❌ サマリー生成に失敗しました\nエラー: {str(e)}"
