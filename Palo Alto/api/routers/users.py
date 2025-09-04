from fastapi import APIRouter, Depends, HTTPException
from api.deps import get_current_user
from api.schemas.user import UserOut, UserUpdate
from dao.user_dao import UserDAO

router = APIRouter()
_users = UserDAO()


@router.get("/me", response_model=UserOut)
def me(current=Depends(get_current_user)):
    return UserOut(
        id=current.id,
        username=current.username,
        email=current.email,
        age=current.age,
        gender=current.gender,
        last_entry_date=current.last_entry_date,
        current_streak=current.current_streak,
        longest_streak=current.longest_streak,
    )


@router.get("/me/streak")
def my_streak(current=Depends(get_current_user)):
    return {
        "last_entry_date": current.last_entry_date,
        "current_streak": current.current_streak,
        "longest_streak": current.longest_streak,
    }


@router.patch("/me", response_model=UserOut)
def patch_me(payload: UserUpdate, current=Depends(get_current_user)):
    fields = {}

    if payload.username is not None:
        if not payload.username.strip():
            raise HTTPException(status_code=422, detail="Username cannot be empty.")
        fields["username"] = payload.username.strip()

    if payload.age is not None:
        # pydantic already validated range; just coerce to int
        fields["age"] = int(payload.age)

    if payload.gender is not None:
        # allow empty -> NULL to “clear” gender
        fields["gender"] = payload.gender.strip() or None

    # If nothing to change, just return current
    if not fields:
        return UserOut(
            id=current.id,
            username=current.username,
            email=current.email,
            age=current.age,
            gender=current.gender,
            last_entry_date=current.last_entry_date,
            current_streak=current.current_streak,
            longest_streak=current.longest_streak,
        )

    updated = _users.update_partial(current.id, **fields)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    return UserOut(
        id=updated.id,
        username=updated.username,
        email=updated.email,
        age=updated.age,
        gender=updated.gender,
        last_entry_date=updated.last_entry_date,
        current_streak=updated.current_streak,
        longest_streak=updated.longest_streak,
    )
