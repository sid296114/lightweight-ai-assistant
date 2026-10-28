"""大模型流式对话服务。

- 多服务商：任意 OpenAI 兼容接口（云端各厂商 + 本地 Ollama/vLLM 等）
- 真实模式：调用所选服务商 /chat/completions（stream=True），逐块转发
- Mock 模式：未配置任何服务商 Key 且未选择服务商时，输出模拟流式回复便于联调
API Key 仅存后端，前端不可见。
"""
import asyncio
from typing import AsyncIterator

import httpx

from app.config import get_settings
from app.services.providers import is_local_url

settings = get_settings()

SYSTEM_PROMPT = (
    "你是一个轻量、专业的中文 AI 助手，面向学生、开发者与办公人群。"
    "回答要准确、简洁、有条理，代码示例可直接运行。"
    "若用户基于上传文档提问，请优先依据文档内容回答，并指出依据的文档片段。"
)


def build_messages(user_content: str, history: list[dict], file_text: str | None) -> list[dict]:
    """构造发送给模型的 messages。file_text 作为上下文注入。"""
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if file_text:
        messages.append(
            {
                "role": "system",
                "content": f"以下是用户上传文档的解析内容（仅作参考）：\n\n{file_text}",
            }
        )
    messages.extend(history)
    messages.append({"role": "user", "content": user_content})
    return messages


async def _mock_stream(user_content: str) -> AsyncIterator[str]:
    """模拟流式输出：先回应用户输入结构，再给出一段示例回答。"""
    chunks = [
        f"收到你的问题：「{user_content[:40]}{'…' if len(user_content) > 40 else ''}」\n\n",
        "当前处于 Mock 联调模式：后端未配置大模型 API Key。\n\n",
        "接入真实模型的方式：在 backend/.env 中填写 LLM_API_KEY，并将 MOCK_LLM 改为 false。\n\n",
        "以下是示例回复的结构：\n\n",
        "1. **要点一**：流式接口已打通，前端逐字渲染正常工作。\n\n",
        "2. **要点二**：会话已持久化到 MySQL，刷新页面不丢失。\n\n",
        "3. **要点三**：上传 PDF / TXT / Markdown 后，可基于文档内容提问。\n\n",
        "配置真实模型后，本段文字将由模型真实输出替换。",
    ]
    for chunk in chunks:
        yield chunk
        await asyncio.sleep(0.03)


async def stream_chat(
    messages: list[dict],
    *,
    provider: dict | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> AsyncIterator[str]:
    """按 OpenAI 兼容协议流式调用大模型，逐块产出文本。

    provider：完整服务商配置（含 base_url / api_key / models / default_model）；
    为 None 时回退到 .env 全局配置（LLM_BASE_URL / LLM_API_KEY / LLM_MODEL）。
    """
    if provider is None:
        # 回退全局配置：无 Key 且开启 Mock 时输出模拟回复
        base_url = settings.LLM_BASE_URL
        api_key = settings.LLM_API_KEY
        model = model or settings.LLM_MODEL
        if settings.MOCK_LLM or not api_key:
            async for chunk in _mock_stream(messages[-1]["content"]):
                yield chunk
            return
    else:
        base_url = provider.get("base_url") or settings.LLM_BASE_URL
        api_key = provider.get("api_key", "")
        model = model or provider.get("default_model") or (provider.get("models") or [""])[0]
        # 本地服务（Ollama/vLLM 等）与"无需 API Key"的自部署服务无需鉴权
        needs_key = not is_local_url(base_url) and not provider.get("no_auth", False)
        if not api_key and needs_key:
            raise RuntimeError(
                f"服务商「{provider.get('name', '未命名')}」尚未配置 API Key，请到设置中添加后再试"
            )

    url = base_url.rstrip("/") + "/chat/completions"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    body: dict = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
    }
    if max_tokens:
        body["max_tokens"] = max_tokens

    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10, read=300, write=30, pool=10)) as client:
        async with client.stream("POST", url, headers=headers, json=body) as resp:
            if resp.status_code != 200:
                detail = (await resp.aread())[:500].decode("utf-8", errors="ignore")
                raise RuntimeError(f"模型接口返回 {resp.status_code}: {detail}")
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                payload = line[len("data:"):].strip()
                if payload == "[DONE]":
                    break
                try:
                    import json

                    data = json.loads(payload)
                    delta = data["choices"][0]["delta"].get("content", "")
                except Exception:
                    continue
                if delta:
                    yield delta
