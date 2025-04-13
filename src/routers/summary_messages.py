import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from services.discord_service import DiscordService
from services.misskey_service import MisskeyService
from utils.url_validator import which_url

load_dotenv()

MISSKY_HOST = os.getenv("MISSKY_HOST")
MISSKY_TOKEN = os.getenv("MISSKY_TOKEN")


class ErrorResponse(BaseModel):
    detail: str


# ルーターの作成
router = APIRouter(
    prefix="/misskey",
    tags=["misskey"],
)


@router.get(
    "/summary",
    responses={
        400: {"model": ErrorResponse, "description": "不正なリクエスト"},
        403: {"model": ErrorResponse, "description": "権限がありません"},
        404: {"model": ErrorResponse, "description": "チャンネルが見つかりません"},
        503: {"model": ErrorResponse, "description": "Discord Botが準備できていません"},
    },
)
async def get_channel_messages(
    request: Request,
    discord_service: DiscordService = Depends(DiscordService()),
    misskey_service: MisskeyService = Depends(MisskeyService),
):
    after = datetime.now() - timedelta(hours=1)
    messages = await discord_service.get_discord_defined_channel_messages(after=after)
    return await misskey_service.message_summaries(messages)
