"""账号模块：注册 / 登录 / 当前用户 / 修改密码 / 退出登录。

- 密码 bcrypt 哈希入库，不存明文
- JWT 下发，默认有效期 7 天
- 登录接口带简易频率限制（防暴力破解）
"""
import threading
import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User
from app.schemas import ChangePassword, TokenOut, UserLogin, UserOut, UserRegister
from app.security import create_access_token, hash_password, verify_password
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["账号"])

# 简易登录失败频率限制（进程内）：{email: [fail_count, lock_until]}
_login_guard: dict[str, list] = {}
_guard_lock = threading.Lock()


def _check_login_allowed(email: str) -> None:
    with _guard_lock:
        record = _login_guard.get(email)
        if record and record[1] > time.time():
            remain = int(record[1] - time.time())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"尝试过于频繁，请 {remain} 秒后再试",
            )


def _record_login_fail(email: str) -> None:
    with _guard_lock:
        record = _login_guard.get(email)
        now = time.time()
        if record is None or now > record[1]:
            _login_guard[email] = [1, 0]
        else:
            record[0] += 1
            if record[0] >= settings.LOGIN_FAIL_LIMIT:
                record[1] = now + settings.LOGIN_FAIL_WINDOW_SECONDS
                record[0] = 0


def _record_login_ok(email: str) -> None:
    with _guard_lock:
        _login_guard.pop(email, None)


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where((User.username == payload.username) | (User.email == payload.email)))
    if exists:
        if exists.username == payload.username:
            raise HTTPException(status_code=400, detail="用户名已被使用")
        raise HTTPException(status_code=400, detail="该邮箱已注册")
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenOut(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenOut)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    email = payload.email.lower()
    _check_login_allowed(email)
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(payload.password, user.password_hash):
        _record_login_fail(email)
        raise HTTPException(status_code=400, detail="邮箱或密码错误")
    if user.status != 1:
        raise HTTPException(status_code=403, detail="账号已被禁用，请联系管理员")
    _record_login_ok(email)
    return TokenOut(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/change-password")
def change_password(payload: ChangePassword, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码不正确")
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "密码修改成功"}


@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    # JWT 为无状态方案，由前端清除本地 token
    return {"message": "已退出登录"}
