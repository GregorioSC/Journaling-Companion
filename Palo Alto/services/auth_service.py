# services/auth_service.py
from typing import Optional
from dao.interfaces import IUserDAO
from models.user import User
from security.passwords import hash_password, verify_password
from security.tokens import make_access_token
from dao.exceptions import DAOError


class AuthService:
    def __init__(self, user_dao: IUserDAO):
        self.user_dao = user_dao

    def register(self, user: User) -> User:
        # hash before saving
        user.password = hash_password(user.password)
        return self.user_dao.create(user)

    def login(self, email: str, password: str) -> Optional[str]:
        """Returns a JWT access token if credentials are valid, else None."""
        u = self.user_dao.find_by_email(email)
        if not u:
            return None
        if not verify_password(password, u.password):
            return None
        # issue access token (1h)
        return make_access_token(
            sub=u.id, expires_in=3600, extra={"username": u.username}
        )
