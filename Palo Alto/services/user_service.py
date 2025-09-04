# services/user_service.py
from typing import Optional, List
from dao.interfaces import IUserDAO
from models.user import User
from dao.exceptions import DAOError, NotFoundError, UniqueConstraintError


class UserService:
    def __init__(self, user_dao: IUserDAO):
        self.user_dao = user_dao

    # Create
    def register(self, user: User) -> User:
        self._validate_user(user)

        try:
            return self.user_dao.create(user)
        except DAOError as e:

            raise e

    # Read
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.user_dao.find_by_id(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.user_dao.find_by_email(email)

    def list_recent(self, limit: int = 50, offset: int = 0) -> List[User]:
        return self.user_dao.list_recent(limit=limit, offset=offset)

    # Update
    def update_full(self, user: User) -> User:
        self._validate_user(user)
        return self.user_dao.update(user)

    def update_partial(self, user_id: int, **fields) -> Optional[User]:
        self._validate_user_patch(fields)
        return self.user_dao.update_partial(user_id, **fields)

    # Delete
    def remove(self, user_id: int) -> None:
        self.user_dao.delete(user_id)

    # --- simple validations ---
    def _validate_user(self, user: User):
        if not user.username or not user.email:
            raise ValueError("username and email are required")
        if not isinstance(user.age, int) or user.age < 0 or user.age > 150:
            raise ValueError("age must be between 0 and 150")
        if not user.password or len(user.password) < 3:
            # replace with password policy later
            raise ValueError("password too short")

    def _validate_user_patch(self, fields: dict):
        if "age" in fields:
            a = fields["age"]
            if not isinstance(a, int) or a < 0 or a > 150:
                raise ValueError("age must be between 0 and 150")
