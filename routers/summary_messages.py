import os

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from services.discord_service import DiscordClass, Message

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
):
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
    print(r.status_code)
    print(r.json())
    return r.json()
