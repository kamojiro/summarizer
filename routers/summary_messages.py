import os

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from services.discord_service import DiscordClass, Message
from services.missky_service import MisskyService

load_dotenv()

MISSKY_HOST = os.getenv("MISSKY_HOST")
MISSKY_TOKEN = os.getenv("MISSKY_TOKEN")


class ErrorResponse(BaseModel):
    detail: str


# ルーターの作成
router = APIRouter(
    prefix="/missky",
    tags=["discord"],
)


@router.get(
    "/summary",
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
    discord_service: DiscordClass = Depends(DiscordClass()),
    missky_service: MisskyService = Depends(MisskyService),
):
    messages = await discord_service.get_discord_defined_channel_messages()
    print(messages)
    headers = {"Content-Type": "application/json"}
    url = f"https://{MISSKY_HOST}/api"

    text = "Hello, World!"
    body = {
        "i": MISSKY_TOKEN,
        "visibility": "home",
        "text": text,
    }
    print("💠")
    r = requests.post(f"{url}/notes/create", headers=headers, json=body, timeout=5)
    return {"text": text}
