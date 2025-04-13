import os

import requests
import vertexai
from dotenv import load_dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import WebBaseLoader
from vertexai.generative_models import GenerativeModel

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")

if not PROJECT_ID or not REGION:
    raise ValueError(
        "Environment variables PROJECT_ID and REGION must be set for Vertex AI."
    )

load_dotenv()


class MisskeyService:
    def __init__(self):
        self.missky_host = os.getenv("MISSKY_HOST")
        self.missky_token = os.getenv("MISSKY_TOKEN")

    async def message_summaries(self, messages):
        for message in messages:
            await self.message_summary(message.content.strip())
        return messages

    async def message_summary(self, url):
        title, summary = await self.get_summary_from_url(url)
        text = f"[{title}]({url})\n\n{summary}"
        headers = {"Content-Type": "application/json"}
        kamomai_url = f"https://{self.missky_host}/api"
        body = {
            "i": self.missky_token,
            "visibility": "followers",
            "text": text,
        }
        requests.post(
            f"{kamomai_url}/notes/create", headers=headers, json=body, timeout=5
        )

    async def get_summary_from_url(self, url):
        loader = WebBaseLoader(url)
        docs = loader.load()
        vertexai.init(project=PROJECT_ID, location=REGION)
        model_name = "gemini-1.5-flash-002"
        # model_name = "gemini-2.0-flash-001"
        model = GenerativeModel(model_name)
        prompt = f"""
        以下の内容を日本語で要約してください。
        要約結果のみを出力してください。

        {docs[0].page_content}
        """
        response = model.generate_content(prompt)
        split_text = response.text.split("。")
        summary = "。\n".join([text.strip() for text in split_text])
        return docs[0].metadata["title"].strip(), summary
