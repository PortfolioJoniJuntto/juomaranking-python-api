import os

from pydantic import BaseModel
from fastapi_cloudauth.cognito import Cognito, CognitoCurrentUser

class AccessUser(BaseModel):
    sub: str

auth = Cognito(
    region=os.environ["region"], 
    userPoolId=os.environ["user_pool_id"],
    client_id=os.environ["user_pool_client_id"]
)

get_current_user = CognitoCurrentUser(
    region=os.environ["region"], 
    userPoolId=os.environ["user_pool_id"],
    client_id=os.environ["user_pool_client_id"]
)
