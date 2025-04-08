from typing import Optional

import discord
import fastapi
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel


# --- モデル定義 ---
class Message(BaseModel):
    id: int
    content: str
    author_name: str
    author_id: int
    created_at: str


class ErrorResponse(BaseModel):
    detail: str


# ルーターの作成
router = APIRouter(
    prefix="/channel",
    tags=["discord"],
)


@router.get(
    "/{channel_id}/messages",
    response_model=list[Message],
    responses={
        400: {"model": ErrorResponse, "description": "不正なリクエスト"},
        403: {"model": ErrorResponse, "description": "権限がありません"},
        404: {"model": ErrorResponse, "description": "チャンネルが見つかりません"},
        503: {"model": ErrorResponse, "description": "Discord Botが準備できていません"},
    },
)
async def get_channel_messages(
    request: Request, channel_id: int, limit: int | None = 100
):
    """指定されたチャンネルIDのメッセージ履歴を取得するAPIエンドポイント"""
    discord_client: discord.Client = request.app.state.discord_client
    if (
        not discord_client or discord_client.is_closed()
    ):  # Bot準備完了かつクローズされていないか確認
        # 起動直後やBotが何らかの理由で停止した場合
        raise HTTPException(
            status_code=503, detail="Discord Bot is not ready or closed."
        )

    channel = discord_client.get_channel(channel_id)

    if not channel:
        raise HTTPException(
            status_code=404, detail=f"Channel with ID {channel_id} not found."
        )

    if not isinstance(channel, discord.TextChannel):
        raise HTTPException(
            status_code=400, detail=f"Channel ID {channel_id} is not a text channel."
        )

    print(f'チャンネル "{channel.name}" のメッセージを取得します (上限: {limit})...')
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
        raise fastapi.HTTPException(
            status_code=500, detail=f"An error occurred while fetching messages: {e}"
        ) from e
