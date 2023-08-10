import os

stage = os.environ.get("STAGE", None)
public_content_bucket_name = os.environ.get("public_content_bucket_name", None)
user_pool_id = os.environ.get("user_pool_id", None)
user_pool_client_id = os.environ.get("user_pool_client_id", None)
region = os.environ.get("region", None)
