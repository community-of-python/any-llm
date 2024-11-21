# any-llm-client

A unified and lightweight asynchronous Python API for communicating with LLMs. It supports multiple providers, including OpenAI Chat Completions API (and any OpenAI-compatible API, such as Ollama and vLLM) and YandexGPT API.

## How To Use

Before starting using any-llm-client, make sure you have it installed:

```sh
uv add any-llm-client
poetry add any-llm-client
```

### Response API

Here's a full example that uses Ollama and Qwen2.5-Coder:

```python
import asyncio

import any_llm_client


config = any_llm_client.OpenAIConfig(url="http://127.0.0.1:11434/v1/chat/completions", model_name="qwen2.5-coder:1.5b")


async def main() -> None:
    async with any_llm_client.get_client(config) as client:
        print(await client.request_llm_message("Кек, чо как вообще на нарах?"))


asyncio.run(main())
```

To use `YandexGPT`, replace the config:

```python
config = any_llm_client.YandexGPTConfig(
    auth_header=os.environ["YANDEX_AUTH_HEADER"], folder_id=os.environ["YANDEX_FOLDER_ID"], model_name="yandexgpt"
)
```

### Streaming API

LLMs often take long time to respond fully. Here's an example of streaming API usage:

```python
import asyncio

import any_llm_client


config = any_llm_client.OpenAIConfig(url="http://127.0.0.1:11434/v1/chat/completions", model_name="qwen2.5-coder:1.5b")


async def main() -> None:
    async with (
        any_llm_client.get_client(config) as client,
        client.stream_llm_partial_messages("Кек, чо как вообще на нарах?") as partial_messages,
    ):
        async for message in partial_messages:
            print("\033[2J")  # clear screen
            print(message)


asyncio.run(main())
```

Note that this will yield partial growing message, not message chunks, for example: "Hi", "Hi there!", "Hi there! How can I help you?".

### Passing chat history and temperature

You can pass `list[any_llm_client.Message]` instead of `str` as the first argument, and set `temperature`:

```python
async with (
    any_llm_client.get_client(config) as client,
    client.stream_llm_partial_messages(
        messages=[
            any_llm_client.Message(role="system", text="Ты — опытный ассистент"),
            any_llm_client.Message(role="user", text="Кек, чо как вообще на нарах?"),
        ],
        temperature=1.0,
    ) as partial_messages,
):
    ...
```

### Other

#### Mock client

You can use a mock client for testing:

```python
config = any_llm_client.MockLLMConfig(
    response_message=...,
    stream_messages=["Hi!"],
)
client = any_llm_client.get_client(config, ...)
```

#### Using dynamic LLM config from environment with [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

```python
import os

import pydantic_settings

import any_llm_client


class Settings(pydantic_settings.BaseSettings):
    llm_model: any_llm_client.AnyLLMConfig


os.environ["LLM_MODEL"] = """{
    "api_type": "openai",
    "url": "http://127.0.0.1:11434/v1/chat/completions",
    "model_name": "qwen2.5-coder:1.5b"
}"""
settings = Settings()
client = any_llm_client.get_client(settings.llm_model, ...)
```

#### Using clients directly

The recommended way to get LLM client is to call `any_llm_client.get_client()`. This way you can easily swap LLM models. If you prefer, you can use `any_llm_client.OpenAIClient` or `any_llm_client.YandexGPTClient` directly:

```python
config = any_llm_client.OpenAIConfig(
    url=pydantic.HttpUrl("https://api.openai.com/v1/chat/completions"),
    auth_token=os.environ["OPENAI_API_KEY"],
    model_name="gpt-4o-mini",
)
client = any_llm_client.OpenAIClient(config, ...)
```

#### Errors

`any_llm_client.LLMClient.request_llm_message()` and `any_llm_client.LLMClient.stream_llm_partial_messages()` will raise `any_llm_client.LLMError` or `any_llm_client.OutOfTokensOrSymbolsError` when the LLM API responds with a failed HTTP status.

#### Timeouts, proxy & other HTTP settings

Pass custom [HTTPX](https://www.python-httpx.org) client:

```python
import httpx

import any_llm_client


async with any_llm_client.get_client(
    ...,
    httpx_client=niquests.AsyncSession(
        mounts={"https://api.openai.com": httpx.AsyncHTTPTransport(proxy="http://localhost:8030")},
        timeout=httpx.Timeout(None, connect=5.0),
    ),
) as client:
    ...
```

#### Retries

By default, requests are retried 3 times on HTTP status errors. You can change the retry behaviour by supplying `request_retry` parameter:

```python
client = any_llm_client.get_client(..., request_retry=any_llm_client.RequestRetryConfig(attempts=5, ...))
```
