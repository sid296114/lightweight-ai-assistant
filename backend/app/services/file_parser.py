"""文件解析服务：TXT / Markdown 直接读原文，PDF 用 PyMuPDF 提取文本。

限制：单文件 ≤10MB、≤50 页；解析结果超出上限截断；扫描件（图片型 PDF）首期不支持。
"""
import os
import uuid
from dataclasses import dataclass, field

import fitz  # PyMuPDF

from app.config import get_settings

settings = get_settings()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


@dataclass
class ParseResult:
    file_id: str
    filename: str
    size_bytes: int
    text: str
    pages: int | None = None
    chars: int = 0
    truncated: bool = False
    is_scanned: bool = False
    error: str = field(default="")


def _ensure_upload_dir() -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def _decode_text(raw: bytes) -> str:
    for enc in ("utf-8", "gb18030", "latin-1"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="ignore")


def _truncate(text: str) -> tuple[str, bool]:
    if len(text) > settings.FILE_MAX_CHARS:
        return text[: settings.FILE_MAX_CHARS], True
    return text, False


def parse_file(filename: str, data: bytes) -> ParseResult:
    _ensure_upload_dir()
    ext = os.path.splitext(filename)[1].lower().lstrip(".") or "txt"

    if ext in ("txt", "md", "markdown", "text"):
        text = _decode_text(data)
        text, truncated = _truncate(text)
        return ParseResult(
            file_id="", filename=filename, size_bytes=len(data),
            text=text, chars=len(text), truncated=truncated,
        )

    if ext == "pdf":
        try:
            doc = fitz.open(stream=data, filetype="pdf")
        except Exception:
            return ParseResult(
                file_id="", filename=filename, size_bytes=len(data),
                text="", error="PDF 文件无法打开，可能已损坏",
            )
        page_count = doc.page_count
        if page_count > settings.FILE_MAX_PAGES:
            doc.close()
            return ParseResult(
                file_id="", filename=filename, size_bytes=len(data),
                text="", pages=page_count, error=f"PDF 共 {page_count} 页，超出 {settings.FILE_MAX_PAGES} 页上限",
            )
        parts = []
        for page in doc:
            parts.append(page.get_text("text"))
        doc.close()
        text = "\n".join(parts).strip()
        # 扫描件（图片型 PDF）提取不到文本
        if len(text) < 20:
            return ParseResult(
                file_id="", filename=filename, size_bytes=len(data),
                text="", pages=page_count, is_scanned=True,
                error="暂不支持扫描件（图片型 PDF），请提供可复制的文本版 PDF",
            )
        text, truncated = _truncate(text)
        return ParseResult(
            file_id="", filename=filename, size_bytes=len(data),
            text=text, pages=page_count, chars=len(text), truncated=truncated,
        )

    return ParseResult(
        file_id="", filename=filename, size_bytes=len(data),
        text="", error=f"暂不支持 {ext} 格式，首期支持 TXT / Markdown / PDF",
    )


def save_parsed(result: ParseResult) -> ParseResult:
    """将解析后的文本落盘，返回带 file_id 的结果，供后续对话引用。"""
    _ensure_upload_dir()
    file_id = uuid.uuid4().hex
    text_path = os.path.join(UPLOAD_DIR, f"{file_id}.txt")
    meta_path = os.path.join(UPLOAD_DIR, f"{file_id}.meta.json")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(result.text)
    import json

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "file_id": file_id,
                "filename": result.filename,
                "size_bytes": result.size_bytes,
                "pages": result.pages,
                "chars": len(result.text),
                "truncated": result.truncated,
            },
            f,
            ensure_ascii=False,
        )
    result.file_id = file_id
    return result


def load_parsed_text(file_id: str) -> str | None:
    """按 file_id 读取已解析文本；不存在返回 None。"""
    text_path = os.path.join(UPLOAD_DIR, f"{file_id}.txt")
    if not os.path.isfile(text_path):
        return None
    with open(text_path, "r", encoding="utf-8") as f:
        return f.read()
