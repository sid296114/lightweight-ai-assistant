"""大模型服务商管理：各类 OpenAI 兼容接口 + 本地大模型统一管理。

- 存储：backend/providers.json（本地文件，API Key 仅存后端，前端不可见）
- 预置：DeepSeek（云端，需配置 Key）、本地 Ollama（无需 Key）
- 兼容：任何实现 OpenAI /chat/completions 协议的服务均可接入
"""
import json
import os
import threading
import uuid

from app.config import get_settings

settings = get_settings()

PROVIDERS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "providers.json"
)

DEFAULT_PROVIDERS = [
    {
        "id": "deepseek",
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "api_key": "",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "default_model": "deepseek-chat",
        "system_prompt": "",
    },
    {
        "id": "local-minimind",
        "name": "本地微调模型（MiniMind-768）",
        "base_url": "http://127.0.0.1:8001/v1",
        "api_key": "",
        "models": ["minimind-768-fengyixuan"],
        "default_model": "minimind-768-fengyixuan",
        "system_prompt": "你是冯毅轩，一个欢乐幽默的聊天伙伴。你24小时电量满格的乐天派，喜欢用网络热梗、谐音梗和表情包表达情绪。即使吐槽也充满幽默感，绝不传递负能量。偶尔会装傻卖萌，但关键时刻能说出让人会心一笑的哲理。每句话不超过3行，常用颜文字和网络流行语。",
    },
    {
        "id": "local-ollama",
        "name": "本地 Ollama",
        "base_url": "http://127.0.0.1:11434/v1",
        "api_key": "",
        "models": ["qwen2.5:7b", "llama3.2:latest"],
        "default_model": "",
        "system_prompt": "",
    },
]

_lock = threading.Lock()


def _ensure_file() -> None:
    if not os.path.isfile(PROVIDERS_FILE):
        with open(PROVIDERS_FILE, "w", encoding="utf-8") as f:
            json.dump({"providers": DEFAULT_PROVIDERS}, f, ensure_ascii=False, indent=2)


def _load() -> list[dict]:
    _ensure_file()
    with open(PROVIDERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("providers", [])


def _save(providers: list[dict]) -> None:
    _ensure_file()
    with open(PROVIDERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"providers": providers}, f, ensure_ascii=False, indent=2)


def is_local_url(base_url: str) -> bool:
    return "127.0.0.1" in base_url or "localhost" in base_url


def _public(provider: dict) -> dict:
    """脱敏：不返回 API Key，只给是否已配置。"""
    return {
        "id": provider["id"],
        "name": provider["name"],
        "base_url": provider["base_url"],
        "models": provider.get("models", []),
        "default_model": provider.get("default_model", ""),
        "system_prompt": provider.get("system_prompt", ""),
        "api_key_configured": bool(provider.get("api_key", "")),
        "is_local": is_local_url(provider["base_url"]),
        "no_auth": bool(provider.get("no_auth", False)),
    }


def list_providers() -> list[dict]:
    with _lock:
        return [_public(p) for p in _load()]


def get_provider(provider_id: str) -> dict | None:
    with _lock:
        for p in _load():
            if p["id"] == provider_id:
                return p
        return None


def get_provider_public(provider_id: str) -> dict | None:
    p = get_provider(provider_id)
    return _public(p) if p else None


def create_provider(
    name: str,
    base_url: str,
    models: list[str],
    default_model: str = "",
    no_auth: bool = False,
    system_prompt: str = "",
) -> dict:
    with _lock:
        providers = _load()
        provider = {
            "id": "p-" + uuid.uuid4().hex[:10],
            "name": name.strip(),
            "base_url": base_url.strip().rstrip("/"),
            "api_key": "",
            "models": [m.strip() for m in models if m.strip()],
            "default_model": default_model.strip(),
            "no_auth": bool(no_auth),
            "system_prompt": system_prompt.strip(),
        }
        providers.append(provider)
        _save(providers)
        return _public(provider)


def update_provider(
    provider_id: str,
    name: str | None = None,
    base_url: str | None = None,
    models: list[str] | None = None,
    default_model: str | None = None,
    no_auth: bool | None = None,
    system_prompt: str | None = None,
) -> dict | None:
    with _lock:
        providers = _load()
        for p in providers:
            if p["id"] != provider_id:
                continue
            if name is not None:
                p["name"] = name.strip()
            if base_url is not None:
                p["base_url"] = base_url.strip().rstrip("/")
            if models is not None:
                p["models"] = [m.strip() for m in models if m.strip()]
            if default_model is not None:
                p["default_model"] = default_model.strip()
            if no_auth is not None:
                p["no_auth"] = bool(no_auth)
            if system_prompt is not None:
                p["system_prompt"] = system_prompt.strip()
            _save(providers)
            return _public(p)
        return None


def delete_provider(provider_id: str) -> bool:
    with _lock:
        providers = _load()
        remaining = [p for p in providers if p["id"] != provider_id]
        if len(remaining) == len(providers):
            return False
        _save(remaining)
        return True


def set_api_key(provider_id: str, api_key: str) -> dict | None:
    """保存（或清空）API Key，不返回明文。"""
    with _lock:
        providers = _load()
        for p in providers:
            if p["id"] != provider_id:
                continue
            p["api_key"] = api_key.strip()
            _save(providers)
            return _public(p)
        return None
