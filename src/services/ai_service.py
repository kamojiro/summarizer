import datetime
import os
from typing import Literal
from weakref import ref

from dotenv import load_dotenv
from google import genai
from google.genai.types import (
    GenerateContentConfig,
    GenerateContentResponse,
    GoogleSearch,
    HttpOptions,
    Tool,
    UrlContext,
)
from pydantic import BaseModel

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")


SYSTEM_PROMPT = """あなたは有能なアシスタントです。
与えられた指示及び情報に基づいて、正確で簡潔な回答を提供してください。
必要に応じて、提供されたツールを使用して情報を検索し、回答を補完してください。
回答は日本語で行ってください。

- 指示が与えられればその指示に従ってください
- 指示ではなく情報が与えられた場合は、その情報について調査し、回答を生成してください
- URL が含まれている場合は、URLの内容を要約してください
- URL が含まれていない場合は、検索ツールを使用して情報を取得し、回答を生成してください
- 分からなければとりあえず検索してください

[参考情報]
"""


class URLAccessError(Exception):
    pass


class Reference(BaseModel):
    title: str
    uri: str


class AIService:
    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=REGION,
            http_options=HttpOptions(api_version="v1"),
        )
        self.model = "gemini-2.5-flash"

    def _get_tools(self, tool: Literal["search", "url"]) -> list[Tool]:
        if tool == "url":
            url_context_tool = Tool(url_context=UrlContext())
            return [url_context_tool]
        else:
            search_tool = Tool(google_search=GoogleSearch())
            return [search_tool]

    def _generate_system_prompt(self) -> str:
        today = datetime.date.today()
        return (
            SYSTEM_PROMPT + f"\n今日は{today.year}年{today.month}月{today.day}日です。"
        )

    def _get_config(self, tool: Literal["search", "url"]) -> GenerateContentConfig:
        tools = self._get_tools(tool)
        system_prompt = self._generate_system_prompt()
        return GenerateContentConfig(
            system_instruction=system_prompt,
            tools=tools,
            response_modalities=["TEXT"],
        )

    def _get_references(self, response: GenerateContentResponse) -> list[Reference]:
        if response.candidates is None:
            return []
        references = []
        for candidate in response.candidates:
            if candidate.grounding_metadata is None:
                continue
            if candidate.grounding_metadata.grounding_chunks is None:
                continue
            for chunk in candidate.grounding_metadata.grounding_chunks:
                if chunk.web is None:
                    continue
                if chunk.web.title is None or chunk.web.uri is None:
                    continue
                references.append(Reference(title=chunk.web.title, uri=chunk.web.uri))
        return references

    def _success_grounding(self, response: GenerateContentResponse) -> bool:
        if response.candidates is None:
            return False
        for candidate in response.candidates:
            if candidate.grounding_metadata is None:
                continue
            if candidate.grounding_metadata.grounding_chunks is None:
                return False
        return True

    def _generate_message(self, response: GenerateContentResponse) -> str:
        if not response.text:
            raise ValueError("Response text is empty")
        text = response.text
        references = self._get_references(response)
        reference = "\n".join([f"- [{ref.title}]({ref.uri})" for ref in references])
        if reference:
            text += "\n\n[References]\n" + reference
        return text

    def generate_content(self, prompt: str, tool: Literal["search", "url"]) -> str:
        config = self._get_config(tool)
        response: GenerateContentResponse = self.client.models.generate_content(
            model=self.model, contents=prompt, config=config
        )
        if tool == "url" and not self._success_grounding(response):
            raise URLAccessError(
                f"Failed to access the URL or no relevant information found. prompt: {prompt}"
            )
        return self._generate_message(response)

    def generate_content_if(self, prompt) -> str:
        tool: Literal["search", "url"] = "search"
        if "https://" in prompt:
            tool = "url"
        try:
            return self.generate_content(prompt, tool)
        except URLAccessError:
            print("URL access failed, switching to search tool.")
            return self.generate_content(prompt, "search")
