import os
from typing import Optional

import discord
from dotenv import load_dotenv
from fastapi import HTTPException, Request
from pydantic import BaseModel

load_dotenv()


# --- モデル定義 ---
class Message(BaseModel):
    id: int
    content: str
    author_name: str
    author_id: int
    created_at: str


class DiscordClass:
    """Discordサービスを提供するクラス"""

    def __init__(self):
        """初期化"""
        self.discord_client = None

    def __call__(self, request: Request) -> "DiscordClass":
        """依存性注入のためのコールメソッド"""
        self.discord_client = request.app.state.discord_client
        return self

    async def get_discord_channel_messages(
        self, channel_id: int, limit: int | None = 100
    ) -> list[Message]:
        """指定されたチャンネルIDのメッセージ履歴を取得する"""
        if (
            not self.discord_client or self.discord_client.is_closed()
        ):  # Bot準備完了かつクローズされていないか確認
            # 起動直後やBotが何らかの理由で停止した場合
            raise HTTPException(
                status_code=503, detail="Discord Bot is not ready or closed."
            )

        channel = self.discord_client.get_channel(channel_id)

        if not channel:
            raise HTTPException(
                status_code=404, detail=f"Channel with ID {channel_id} not found."
            )

        if not isinstance(channel, discord.TextChannel):
            raise HTTPException(
                status_code=400,
                detail=f"Channel ID {channel_id} is not a text channel.",
            )

        print(
            f'チャンネル "{channel.name}" のメッセージを取得します (上限: {limit})...'
        )
        messages_data: list[Message] = []
        try:
            async for message in channel.history(limit=limit):
                messages_data.extend(
                    [
                        Message(
                            id=message.id,
                            content=message.content,
                            author_name=message.author.name,
                            author_id=message.author.id,
                            created_at=message.created_at.isoformat(),
                        )
                    ]
                )
            print(
                f"--- {len(messages_data)} 件のメッセージをAPIレスポンスとして返します ---"
            )
            return messages_data

        except discord.errors.Forbidden:
            print(
                f'エラー: チャンネル "{channel.name}" のメッセージ履歴を読む権限がありません。'
            )
            raise HTTPException(
                status_code=403,
                detail=f"Missing permissions to read history in channel {channel_id}.",
            ) from discord.errors.Forbidden
        except Exception as e:
            print(f"メッセージ取得中にエラーが発生しました: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while fetching messages: {e}",
            ) from e

    async def get_discord_defined_channel_messages(self):
        channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))
        print(f"チャンネルID: {channel_id}")
        try:
            return await self.get_discord_channel_messages(channel_id=channel_id)
        except HTTPException as e:
            print(f"チャンネルID: {channel_id}")
            raise e
