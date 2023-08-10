import os
import boto3
from time import time
from fastapi import APIRouter
import random
import string
import re
from fastapi import HTTPException

from typing import Optional
from pydantic import BaseModel
from models.users import UserModel

user_pool_id = os.environ.get("user_pool_id", None)
user_pool_client_id = os.environ.get("user_pool_client_id", None)
region = os.environ.get("region", None)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

cognito = boto3.client("cognito-idp", region_name=region)

regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"


def disableUser(email: str):
    try:
        cognito.admin_disable_user(UserPoolId=user_pool_id, Username=email)
        return True
    except:
        return False


def verifyCredentials(email: str, password: str):
    try:
        cognito.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=user_pool_client_id,
            AuthFlow="ADMIN_USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": email, "PASSWORD": password},
        )
        return True
    except:
        return False


def isValidEmail(email):
    if re.fullmatch(regex, email):
        return True

    return False


class Body(BaseModel):
    email: Optional[str]
    password: Optional[str]
    refresh_token: Optional[str]


@router.post("/login")
def login(body: Body):
    try:
        response = cognito.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=user_pool_client_id,
            AuthFlow="ADMIN_USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": body.email, "PASSWORD": body.password},
        )
    except cognito.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    except cognito.exceptions.UserNotFoundException:
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    return response["AuthenticationResult"]


@router.post("/register")
def register(body: Body):
    if isValidEmail(body.email) != True:
        raise HTTPException(status_code=400, detail="Invalid email.")

    try:
        user = cognito.admin_create_user(UserPoolId=user_pool_id, Username=body.email)
    except cognito.exceptions.UsernameExistsException:
        raise HTTPException(status_code=400, detail="This email is already in use.")

    sub = None

    for x in user["User"]["Attributes"]:
        if x["Name"] == "sub":
            sub = x["Value"]
            break

    cognito.admin_set_user_password(
        Username=body.email,
        Password=body.password,
        UserPoolId=user_pool_id,
        Permanent=True,
    )

    user_model = UserModel(
        userId=sub,
        username="user_" + "".join(random.choices(string.ascii_lowercase, k=12)),
        createdAt=int(time()),
        email=body.email,
        profileImgUrl="",
    )

    user_model.save(UserModel.userId.does_not_exist())

    response = cognito.admin_initiate_auth(
        UserPoolId=user_pool_id,
        ClientId=user_pool_client_id,
        AuthFlow="ADMIN_USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": body.email, "PASSWORD": body.password},
    )
    return response["AuthenticationResult"]


@router.post("/refresh")
def refresh_access_token(body: Body):
    response = cognito.admin_initiate_auth(
        UserPoolId=user_pool_id,
        ClientId=user_pool_client_id,
        AuthFlow="REFRESH_TOKEN_AUTH",
        AuthParameters={"REFRESH_TOKEN": body.refresh_token},
    )

    return response["AuthenticationResult"]
