import email
from fastapi import APIRouter, Depends, Body, Response

from utils.auth import auth, AccessUser

from .auth import verifyCredentials, disableUser

from models.users import UserModel
from typing import Optional

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me")
def get_current_user(current_user: AccessUser = Depends(auth.claim(AccessUser))):
    user = UserModel.get(current_user.sub)
    return user.attribute_values


@router.put("/me")
def update_current_user(
    body=Body(),
    current_user: AccessUser = Depends(auth.claim(AccessUser)),
):
    try:
        email = body.get("email")
        username = body.get("username")

        actions = []

        if email != None:
            actions.append(UserModel.email.set(email))
        if username != None:
            actions.append(UserModel.username.set(username))

        if len(actions) > 0:
            UserModel(userId=current_user.sub).update(actions)

        return Response(status_code=204)
    except:
        return Response(status_code=500)


@router.delete("/me")
def update_current_user(
    body=Body(),
    current_user: AccessUser = Depends(auth.claim(AccessUser)),
):
    try:
        user = UserModel.get(current_user.sub)

        password = body.get("password")

        if password == None:
            return Response(status_code=400)

        verifyResult = verifyCredentials(user.email, password)

        print("verify result", verifyResult)

        if verifyResult != True:
            return Response(status_code=403)

        disableResult = disableUser(email=user.email)

        print("disable result", disableResult)

        if disableResult != True:
            return Response(status_code=500)

        UserModel(userId=current_user.sub).update(actions=[UserModel.deleted.set(True)])

        return Response(status_code=204)
    except:
        return Response(status_code=500)


@router.get("/moderators")
def list_all_moderators(current_user: AccessUser = Depends(auth.scope(["Admin"]))):
    # TODO query all moderators from database and return
    return []


@router.get("/admins")
def list_all_admins(current_user: AccessUser = Depends(auth.scope(["Admin"]))):
    # TODO query all admins from database and return
    return []
