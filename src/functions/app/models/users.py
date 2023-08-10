import os

from pydantic import BaseModel
from pynamodb.attributes import NumberAttribute, UnicodeAttribute, BooleanAttribute

from .dbmodel import DBModel

table_name = os.getenv("users_table_name")
region = os.getenv("region")


class User(BaseModel):
    userId: str
    username: str
    email: str
    createdAt: int
    profileImgUrl: str
    type: str
    deleted: bool


class UserModel(DBModel):
    """
    A DynamoDB User
    """

    class Meta:
        table_name = table_name
        region = region

    userId = UnicodeAttribute(hash_key=True)
    username = UnicodeAttribute()
    email = UnicodeAttribute()
    createdAt = NumberAttribute(null=True)
    profileImgUrl = UnicodeAttribute()
    type = UnicodeAttribute(null=True)
    deleted = BooleanAttribute(null=True)


class UserDTO:
    def __init__(self, user: UserModel) -> None:
        self.userId = user.userId
        self.username = user.username
        self.email = user.email
        self.createdAt = user.createdAt
        self.profileImgUrl = user.profileImgUrl
        self.type = user.type
