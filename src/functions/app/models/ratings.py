import os
from typing import Optional

from pydantic import BaseModel
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, NumberAttribute

from .dbmodel import DBModel

table_name = os.getenv("ratings_table_name")
region = os.getenv("region")


class RatingDTO:
    def __init__(self, ean: Optional[str], rating: int, comment: Optional[str],
                 username: Optional[str],
                 created_at: Optional[int], updated_at: Optional[int]) -> None:
        self.ean = ean
        self.rating = rating
        self.comment = comment
        self.username = username
        self.created_at = created_at
        self.updated_at = updated_at


class RatingModel(DBModel):
    """
    A DynamoDB Ratings
    """

    class Meta:
        table_name = table_name
        region = region

    ean = UnicodeAttribute(hash_key=True)
    userId = UnicodeAttribute(range_key=True)
    username = UnicodeAttribute(null=True)
    rating = NumberAttribute()
    comment = UnicodeAttribute(null=True)
    created_at = NumberAttribute(null=True)
    updated_at = NumberAttribute(null=True)


class Rating(BaseModel):
    ean: Optional[str]
    userId: Optional[str]
    username: Optional[str]
    rating: int
    comment: Optional[str]
    created_at: Optional[int]
    updated_at: Optional[int]


class RatingAmountDTO:
    def __init__(self, rating: int, amount: int) -> None:
        self.amount = amount
        self.rating = rating
