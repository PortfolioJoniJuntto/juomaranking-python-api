from typing import List
from fastapi import APIRouter, HTTPException

from models.pricehistory import PriceHistoryModel, PriceHistoryDTO

router = APIRouter(
    prefix="/ratings",
    tags=["Ratings"],
)


@router.get("/price-history/{ean}")
def get_product_price_history(ean: str) -> List[PriceHistoryDTO]:
    try:
        phms = PriceHistoryModel.query(ean)
    except PriceHistoryModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="PriceHistoryModel not found")

    return [PriceHistoryDTO(price_history=phm) for phm in phms]
