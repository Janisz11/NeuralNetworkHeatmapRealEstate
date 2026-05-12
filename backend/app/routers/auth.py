from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from jose import jwt, JWTError
import httpx

from ..database import get_db
from ..models.user import User
from ..config import get_settings
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def _create_jwt(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


@router.get("/google")
async def google_login(request: Request):
    redirect_uri = f"{settings.frontend_url.rstrip('/')}/auth/google/callback"
    redirect_uri = str(request.url_for("google_callback"))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo") or {}

    email = userinfo.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google did not return an email address")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            name=userinfo.get("name"),
            picture=userinfo.get("picture"),
            provider="google",
            provider_id=userinfo.get("sub", ""),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = _create_jwt(user.id, user.email)
    return RedirectResponse(
        url=f"{settings.frontend_url}/admin?token={access_token}"
    )


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "role": current_user.role,
    }
