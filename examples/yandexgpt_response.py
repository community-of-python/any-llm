import asyncio  # noqa: INP001
import os

import httpx

import any_llm


config = any_llm.YandexGPTConfig(
    auth_header=os.environ["YANDEX_AUTH_HEADER"],
    folder_id=os.environ["YANDEX_FOLDER_ID"],
    model_name="yandexgpt",
)


async def main() -> None:
    async with httpx.AsyncClient() as httpx_client:
        response = await any_llm.get_model(config, httpx_client=httpx_client).request_llm_response(
            messages=[
                any_llm.Message(role="system", text="Ты — опытный ассистент"),
                any_llm.Message(role="user", text="Привет!"),
            ],
            temperature=0.1,
        )
        print(response)  # noqa: T201


asyncio.run(main())
