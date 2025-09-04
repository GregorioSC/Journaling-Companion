# security/tokens.py
import time
import jwt  # PyJWT
from typing import Optional, Dict, Any

# change this to a strong secret (env var in real app)
JWT_SECRET = "change-me-in-env"
JWT_ALG = "HS256"


def make_access_token(
    sub: int, expires_in: int = 3600, extra: Optional[Dict[str, Any]] = None
) -> str:
    now = int(time.time())
    payload = {"sub": str(sub), "iat": now, "exp": now + expires_in}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
