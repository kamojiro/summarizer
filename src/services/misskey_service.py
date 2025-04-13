import os

import requests
import vertexai
from dotenv import load_dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import WebBaseLoader
from vertexai.generative_models import GenerationConfig, GenerativeModel, Tool

from utils.url_validator import which_url

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
        vertexai.init(project=PROJECT_ID, location=REGION)
        model_name = "gemini-1.5-flash-002"
        # model_name = "gemini-2.0-flash-001"
        self.model = GenerativeModel(model_name)
        self.generation_config = GenerationConfig(temperature=0.0)

    async def message_summaries(self, messages):
        for message in messages:
            await self.message_summary(message.content.strip())
        return messages

    async def message_summary(self, message):
        match which_url(message):
            case "html":
                title, summary = await self.get_summary_from_url(message)
                text = f"[{title}]({message})\n\n{summary}"
            case None:
                summary = await self.get_explanation_from_message(message)
                text = f"**{message}**\n\n{summary}"

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

        prompt = f"""
        以下の内容を日本語で要約してください。
        要約結果のみを出力してください。

        {docs[0].page_content}
        """
        response = self.model.generate_content(
            prompt, generation_config=self.generation_config
        )
        split_text = response.text.split("。")
        summary = "。\n".join([text.strip() for text in split_text])
        return docs[0].metadata["title"].strip(), summary

    async def get_explanation_from_message(self, message):
        # REVIEW: 検索が効いてないように見える
        prompt = f"""
        以下の内容について検索してください。
        検索結果をまとめてください。

        {message}
        """
        tools = [
            Tool.from_google_search_retrieval(
                google_search_retrieval=vertexai.generative_models.grounding.GoogleSearchRetrieval()
            ),
        ]
        response = self.model.generate_content(
            prompt, tools=tools, generation_config=self.generation_config
        )
        split_text = response.text.split("。")
        explanation = "。\n".join([text.strip() for text in split_text])
        return explanation
