import os

from pydantic import BaseModel
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, NumberAttribute

from .dbmodel import DBModel

table_name = os.getenv("pricehistory_table_name")
region = os.getenv("region")


class PriceHistory(BaseModel):
    ean: str
    sk: str
    price: int
    created_at: int
    store: str


class PriceHistoryModel(DBModel):
    """
    A DynamoDB Pricehistory
    """

    class Meta:
        table_name = table_name
        region = region

    ean = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True)
    price = NumberAttribute()
    created_at = NumberAttribute()
    store = UnicodeAttribute()


class PriceHistoryDTO:
    def __init__(self, price_history: PriceHistoryModel) -> None:
        self.ean = price_history.ean
        self.price = price_history.price
        self.created_at = price_history.created_at
        self.store = price_history.store
