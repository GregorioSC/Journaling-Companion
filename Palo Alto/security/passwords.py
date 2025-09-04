# security/passwords.py
import bcrypt


def hash_password(plain: str) -> str:
    if not isinstance(plain, str) or not plain:
        raise ValueError("password required")
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # hashed is not a valid bcrypt string -> treat as mismatch
        return False
