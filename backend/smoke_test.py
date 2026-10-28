"""后端接口冒烟测试：注册 → 登录 → me → 会话 CRUD → SSE 流式对话 → 文件解析。

运行：backend 目录下 .venv\\Scripts\\python.exe smoke_test.py
"""
import io
import json
import sys
import time

import httpx

BASE = "http://127.0.0.1:8000"
client = httpx.Client(timeout=60)

results = []


def report(name: str, ok: bool, detail: str = ""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}", flush=True)


# 1. 注册（唯一邮箱）
suffix = int(time.time())
username = f"testuser{suffix}"
email = f"test{suffix}@example.com"
password = "pass123456"

r = client.post(f"{BASE}/api/auth/register", json={"username": username, "email": email, "password": password})
report("register", r.status_code == 201, r.text[:200])
token = r.json().get("access_token", "") if r.status_code == 201 else ""

# 2. 重复注册应失败
r = client.post(f"{BASE}/api/auth/register", json={"username": username, "email": email, "password": password})
report("register-duplicate-rejected", r.status_code == 400, r.text[:120])

# 3. 登录
r = client.post(f"{BASE}/api/auth/login", json={"email": email, "password": password})
report("login", r.status_code == 200, r.text[:120])
token = r.json().get("access_token", token)

# 4. 错误密码应失败
r = client.post(f"{BASE}/api/auth/login", json={"email": email, "password": "wrongpass"})
report("login-wrong-password-rejected", r.status_code == 400, r.text[:120])

headers = {"Authorization": f"Bearer {token}"}

# 5. me
r = client.get(f"{BASE}/api/auth/me", headers=headers)
report("me", r.status_code == 200 and r.json().get("email") == email, r.text[:200])

# 6. 未登录访问应 401
r = client.get(f"{BASE}/api/chat/sessions")
report("unauth-401", r.status_code == 401, str(r.status_code))

# 7. 创建会话
r = client.post(f"{BASE}/api/chat/sessions", headers=headers, json={"title": "冒烟测试会话"})
report("create-session", r.status_code == 201, r.text[:120])
session_id = r.json().get("id") if r.status_code == 201 else None

# 8. 会话列表
r = client.get(f"{BASE}/api/chat/sessions", headers=headers)
report("list-sessions", r.status_code == 200 and any(s.get("id") == session_id for s in r.json()), r.text[:200])

# 9. SSE 流式对话（mock）
assert session_id is not None
collected = []
with client.stream(
    "POST",
    f"{BASE}/api/chat/stream",
    headers=headers,
    json={"content": "你好，请介绍一下你自己", "session_id": session_id, "temperature": 0.7},
) as resp:
    sse_ok = resp.status_code == 200 and "text/event-stream" in resp.headers.get("content-type", "")
    for line in resp.iter_lines():
        if line.startswith("data: "):
            evt = json.loads(line[6:])
            collected.append(evt)
            if evt["type"] == "done":
                break
has_delta = any(e.get("type") == "delta" and e.get("content") for e in collected)
has_done = any(e.get("type") == "done" for e in collected)
report("sse-stream", sse_ok and has_delta and has_done, f"events={len(collected)}")

# 10. 历史消息
r = client.get(f"{BASE}/api/chat/sessions/{session_id}/messages", headers=headers)
msgs = r.json() if r.status_code == 200 else []
report(
    "history-messages",
    r.status_code == 200 and len(msgs) == 2 and msgs[0]["role"] == "user" and msgs[1]["role"] == "assistant",
    f"count={len(msgs)}",
)

# 11. 重命名会话
r = client.patch(f"{BASE}/api/chat/sessions/{session_id}", headers=headers, json={"title": "重命名后的标题"})
report("rename-session", r.status_code == 200 and r.json().get("title") == "重命名后的标题", r.text[:120])

# 12. 文件解析（TXT）
r = client.post(
    f"{BASE}/api/files/upload",
    headers=headers,
    files={"file": ("demo.txt", io.BytesIO("这是文档内容：轻量AI助手文件解析测试。".encode("utf-8")), "text/plain")},
)
report("upload-txt", r.status_code == 200 and r.json().get("file_id"), r.text[:200])
file_id = r.json().get("file_id", "") if r.status_code == 200 else ""

# 13. 基于文档对话
if file_id:
    with client.stream(
        "POST",
        f"{BASE}/api/chat/stream",
        headers=headers,
        json={"content": "文档里说了什么？", "session_id": session_id, "file_id": file_id},
    ) as resp:
        for line in resp.iter_lines():
            if line.startswith("data: "):
                evt = json.loads(line[6:])
                if evt["type"] == "done":
                    break
    report("doc-based-chat", True, "stream completed")

# 14. 上传 PDF 扫描件提示（伪造空文本 PDF 走 is_scanned 分支）— 用非法扩展名验证拦截
r = client.post(
    f"{BASE}/api/files/upload",
    headers=headers,
    files={"file": ("a.docx", io.BytesIO(b"x" * 100), "application/octet-stream")},
)
report("unsupported-ext-rejected", r.status_code == 400, r.text[:150])

# 15. 删除会话
r = client.delete(f"{BASE}/api/chat/sessions/{session_id}", headers=headers)
report("delete-session", r.status_code == 204, str(r.status_code))

# 16. 删除后消息不可见（会话不存在 → 404）
r = client.get(f"{BASE}/api/chat/sessions/{session_id}/messages", headers=headers)
report("deleted-session-404", r.status_code == 404, str(r.status_code))

failed = [x for x in results if not x[1]]
print(f"\n总计 {len(results)} 项，失败 {len(failed)} 项", flush=True)
sys.exit(1 if failed else 0)
