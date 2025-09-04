from fastapi import APIRouter, Depends, HTTPException
from api.deps import get_current_user
from api.schemas.entry import EntryCreate, EntryPatch, EntryOut
from services.entry_service import EntryService
from dao.entry_dao import EntryDAO
from models.entry import Entry

router = APIRouter()


def get_entry_service():
    return EntryService(EntryDAO())


@router.post("", response_model=EntryOut)
def create_entry(
    payload: EntryCreate,
    svc: EntryService = Depends(get_entry_service),
    current=Depends(get_current_user),
):
    if payload.user_id != current.id:
        raise HTTPException(
            status_code=403, detail="cannot create entry for another user"
        )
    saved = svc.create(
        Entry(
            id=None,
            user_id=payload.user_id,
            title=payload.title,
            text=payload.text,
            created_at=None,
        )
    )
    return EntryOut(
        id=saved.id,
        user_id=saved.user_id,
        title=saved.title,
        text=saved.text,
        created_at=str(saved.created_at),
    )


@router.patch("/{entry_id}", response_model=EntryOut)
def update_entry(
    entry_id: int,
    patch: EntryPatch,
    svc: EntryService = Depends(get_entry_service),
    current=Depends(get_current_user),
):
    updated = svc.update_partial(
        entry_id, **{k: v for k, v in patch.dict().items() if v is not None}
    )
    if not updated:
        raise HTTPException(status_code=404, detail="entry not found")
    if updated.user_id != current.id:
        raise HTTPException(status_code=403, detail="cannot modify this entry")
    return EntryOut(
        id=updated.id,
        user_id=updated.user_id,
        title=updated.title,
        text=updated.text,
        created_at=str(updated.created_at),
    )


@router.get("", response_model=list[EntryOut])
def list_my_entries(
    svc: EntryService = Depends(get_entry_service), current=Depends(get_current_user)
):
    rows = svc.list_for_user(current.id, limit=100)
    return [
        EntryOut(
            id=r.id,
            user_id=r.user_id,
            title=r.title,
            text=r.text,
            created_at=str(r.created_at),
        )
        for r in rows
    ]


@router.get("/{entry_id}", response_model=EntryOut)
def get_entry(
    entry_id: int,
    svc: EntryService = Depends(get_entry_service),
    current=Depends(get_current_user),
):
    e = svc.get(entry_id)
    if not e or e.user_id != current.id:
        raise HTTPException(status_code=404, detail="entry not found")
    return EntryOut(
        id=e.id,
        user_id=e.user_id,
        title=e.title,
        text=e.text,
        created_at=str(e.created_at),
    )


@router.delete("/{entry_id}")
def delete_entry(
    entry_id: int,
    svc: EntryService = Depends(get_entry_service),
    current=Depends(get_current_user),
):
    e = svc.get(entry_id)
    if not e or e.user_id != current.id:
        raise HTTPException(status_code=404, detail="entry not found")
    svc.remove(entry_id)
    return {"ok": True}
