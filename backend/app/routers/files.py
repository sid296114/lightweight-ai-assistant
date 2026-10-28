"""文件解析模块：上传 TXT / Markdown / PDF，解析文本并生成可引用 file_id。"""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import get_settings
from app.deps import get_current_user
from app.models import User
from app.schemas import FileParseOut
from app.services.file_parser import parse_file, save_parsed

settings = get_settings()
router = APIRouter(prefix="/api/files", tags=["文件解析"])

ALLOWED_EXTENSIONS = {"txt", "md", "markdown", "text", "pdf"}


@router.post("/upload", response_model=FileParseOut)
async def upload_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"暂不支持 {ext or '未知'} 格式，首期支持 TXT / Markdown / PDF",
        )
    data = await file.read()
    if len(data) > settings.FILE_MAX_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件超过 {settings.FILE_MAX_MB}MB 上限",
        )
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="文件内容为空")

    result = parse_file(file.filename or "unnamed", data)
    if result.error:
        raise HTTPException(status_code=400, detail=result.error)
    result = save_parsed(result)

    return FileParseOut(
        file_id=result.file_id,
        filename=result.filename,
        size_bytes=result.size_bytes,
        pages=result.pages,
        chars=result.chars,
        preview=result.text[:300],
        truncated=result.truncated,
    )
