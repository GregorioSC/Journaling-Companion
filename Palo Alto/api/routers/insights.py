from fastapi import APIRouter, Depends, HTTPException
from api.deps import get_current_user
from api.schemas.insight import InsightPatch, InsightOut
from services.insight_service import InsightService
from dao.insight_dao import InsightDAO

router = APIRouter()


def get_insight_service():
    return InsightService(InsightDAO())


@router.get("/by-entry/{entry_id}", response_model=InsightOut)
def get_insight(
    entry_id: int,
    svc: InsightService = Depends(get_insight_service),
    current=Depends(get_current_user),
):
    ins = svc.get_for_entry(entry_id)
    if not ins:
        raise HTTPException(status_code=404, detail="insight not found")
    return InsightOut(
        id=ins.id,
        entry_id=ins.entry_id,
        sentiment=ins.sentiment,
        themes=ins.themes,
        embedding=ins.embedding,
        created_at=str(ins.created_at),
    )


@router.patch("/by-entry/{entry_id}", response_model=InsightOut)
def patch_insight(
    entry_id: int,
    patch: InsightPatch,
    svc: InsightService = Depends(get_insight_service),
    current=Depends(get_current_user),
):
    updated = svc.update_partial(
        entry_id, **{k: v for k, v in patch.dict().items() if v is not None}
    )
    if not updated:
        raise HTTPException(status_code=404, detail="insight not found")
    return InsightOut(
        id=updated.id,
        entry_id=updated.entry_id,
        sentiment=updated.sentiment,
        themes=updated.themes,
        embedding=updated.embedding,
        created_at=str(updated.created_at),
    )
