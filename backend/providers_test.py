"""大模型服务商接口冒烟测试：CRUD + API Key + 对话 provider 选择。"""
import json
import sys

import httpx

BASE = "http://127.0.0.1:8000"
client = httpx.Client(timeout=60)
results = []


def report(name, ok, detail=""):
    results.append((name, ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}", flush=True)


# 登录
r = client.post(f"{BASE}/api/auth/login", json={"email": "test1793154273@example.com", "password": "pass123456"})
token = r.json().get("access_token", "")
headers = {"Authorization": f"Bearer {token}"}
report("login", bool(token), r.text[:100])

# 1. 预置服务商列表
r = client.get(f"{BASE}/api/providers", headers=headers)
providers = r.json() if r.status_code == 200 else []
report("providers-list", r.status_code == 200 and len(providers) >= 2, r.text[:200])
names = {p["name"] for p in providers}
report("preset-deepseek+ollama", "DeepSeek" in names and "本地 Ollama" in names, str(names))
# 脱敏检查：不返回 api_key 字段
has_key_field = any("api_key" in p for p in providers)
report("api-key-hidden", not has_key_field)

# 2. 新增服务商
r = client.post(f"{BASE}/api/providers", headers=headers, json={
    "name": "测试服务商", "base_url": "https://api.test.com/v1",
    "models": ["m1", "m2"], "default_model": "m1",
})
pid = r.json().get("id", "") if r.status_code == 201 else ""
report("create-provider", r.status_code == 201 and pid, r.text[:150])

# 3. 设置 API Key
r = client.post(f"{BASE}/api/providers/{pid}/api-key", headers=headers, json={"api_key": "sk-test-123"})
report("set-api-key", r.status_code == 200 and r.json().get("api_key_configured") is True, r.text[:150])
# 明文不可见
r = client.get(f"{BASE}/api/providers", headers=headers)
t = r.text
report("key-not-in-response", "sk-test-123" not in t)

# 4. 更新
r = client.patch(f"{BASE}/api/providers/{pid}", headers=headers, json={"models": ["m3"], "default_model": "m3"})
report("update-provider", r.status_code == 200 and r.json().get("models") == ["m3"], r.text[:150])

# 5. 对话：指定有 key 的服务商（真实调用会失败于网络，但应走到 httpx 层而不是 400）
with client.stream(
    "POST", f"{BASE}/api/chat/stream", headers=headers,
    json={"content": "hi", "provider_id": pid, "model_name": "m3"},
) as resp:
    evts = []
    for line in resp.iter_lines():
        if line.startswith("data: "):
            evts.append(json.loads(line[6:]))
report("chat-with-provider-sse", resp.status_code == 200 and len(evts) > 0, f"events={len(evts)} first={evts[0] if evts else None}")

# 6. 对话：指定无 Key 云端服务商 → SSE error 提示配置
with client.stream(
    "POST", f"{BASE}/api/chat/stream", headers=headers,
    json={"content": "hi", "provider_id": "deepseek", "model_name": "deepseek-chat"},
) as resp:
    evts = []
    for line in resp.iter_lines():
        if line.startswith("data: "):
            evts.append(json.loads(line[6:]))
    is_err = evts and evts[0].get("type") == "error" and "API Key" in evts[0].get("message", "")
report("chat-no-key-errors", is_err, str(evts[:1]))

# 7. 对话：不指定服务商 → 回退全局 Mock 流式
with client.stream(
    "POST", f"{BASE}/api/chat/stream", headers=headers,
    json={"content": "你好"},
) as resp:
    evts = []
    for line in resp.iter_lines():
        if line.startswith("data: "):
            evts.append(json.loads(line[6:]))
    has_delta = any(e.get("type") == "delta" and e.get("content") for e in evts)
    has_done = any(e.get("type") == "done" for e in evts)
report("chat-fallback-mock", has_delta and has_done, f"events={len(evts)}")

# 8. 删除服务商
r = client.delete(f"{BASE}/api/providers/{pid}", headers=headers)
report("delete-provider", r.status_code == 204, str(r.status_code))
r = client.get(f"{BASE}/api/providers", headers=headers)
report("deleted-gone", pid not in [p["id"] for p in r.json()])

failed = [x for x in results if not x[1]]
print(f"\n总计 {len(results)} 项，失败 {len(failed)} 项", flush=True)
sys.exit(1 if failed else 0)
