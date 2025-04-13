from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from services.discord_service import DiscordClass, Message


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
    request: Request,
    channel_id: int,
    limit: int | None = 100,
    discord_service: DiscordClass = Depends(DiscordClass()),
):
    """指定されたチャンネルIDのメッセージ履歴を取得するAPIエンドポイント"""
    return await discord_service.get_discord_channel_messages(channel_id, limit)
