import asyncio
import os
from contextlib import asynccontextmanager  # lifespanで使用

import discord
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

# routersからインポート
from routers import discord_messages, summary_messages

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
async def lifespan(app: FastAPI):
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
app = FastAPI(lifespan=lifespan)


# ルーターの登録
app.include_router(discord_messages.router)
app.include_router(summary_messages.router)


@app.get("/")
async def read_root():
    return {"message": "Discord Data Fetcher API is running!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, log_level="info")  # noqa: S104
