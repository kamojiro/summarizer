import asyncio
import os
from contextlib import asynccontextmanager  # lifespanで使用
from typing import List, Optional

import discord
import fastapi
import uvicorn
from fastapi import Request, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel

# --- Discord Bot 設定 ---
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 必要なインテントを設定
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # 特権インテント
intents.guilds = True

# Discordクライアントを作成
client = discord.Client(intents=intents)
discord_ready = False  # Bot の準備完了フラグ
discord_task = None  # Discord Botのタスクを保持する変数


@client.event
async def on_ready():
    """BotがDiscordに接続し準備が完了したときに呼ばれる"""
    print(f"{client.user} としてログインしました")


async def run_discord_bot():
    """Discord Botを起動するコルーチン"""
    try:
        await client.start(BOT_TOKEN)
    except Exception as e:
        print(f"Discord Bot Error: {e}")
    finally:
        if not client.is_closed():
            await client.close()


# --- FastAPI アプリケーション設定 ---


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    """FastAPIのライフサイクル管理 (推奨される方法)"""
    print("FastAPI起動、Discord Botをバックグラウンドで起動します...")
    app.state.discord_client = client
    # Discord Botをバックグラウンドタスクとして起動
    app.state.discord_task = asyncio.create_task(run_discord_bot())

    # --- アプリケーションが実行されるフェーズ ---
    yield
    # --- アプリケーション終了時の処理 ---
    print("FastAPI終了、Discord Botを停止します...")
    discord_task = app.state.discord_task
    discord_client = app.state.discord_client
    if client and not client.is_closed():
        # Botを閉じる,run_discord_botのfinallyでも処理されるが念のため
        await client.close()
    if discord_task and not discord_task.done():
        # タスクがまだ実行中の場合、キャンセルを試みる
        discord_task.cancel()
        try:
            await discord_task  # キャンセルが完了するのを待つ
        except asyncio.CancelledError:
            print("Discord Botタスクのキャンセルを確認しました。")


# lifespanを指定してFastAPIアプリを作成
app = fastapi.FastAPI(lifespan=lifespan)


# --- API エンドポイント定義 ---


class Message(BaseModel):
    id: int
    content: str
    author_name: str
    author_id: int
    created_at: str


class ErrorResponse(BaseModel):
    detail: str


@app.get(
    "/channel/{channel_id}/messages",
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
    print(f"💠{discord_client=}, {discord_client.is_closed()=}")
    if (
        not discord_client or client.is_closed()
    ):  # Bot準備完了かつクローズされていないか確認
        # 起動直後やBotが何らかの理由で停止した場合
        raise HTTPException(
            status_code=503, detail="Discord Bot is not ready or closed."
        )

    channel = client.get_channel(channel_id)

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


@app.get("/")
async def read_root():
    return {"message": "Discord Data Fetcher API is running!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
