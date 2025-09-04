from fastapi import APIRouter, Depends
from api.deps import get_current_user
from api.schemas.user import UserOut

router = APIRouter()


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
