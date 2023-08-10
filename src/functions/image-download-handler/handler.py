import io
import os

import boto3
import requests
from PIL import Image
from pydantic import BaseModel

stage = os.environ.get('STAGE', None)
public_content_bucket = os.environ.get('public_content_bucket_name', None)


class ImageRequest(BaseModel):
    image_url: str
    ean: str


def image_download(image_request: ImageRequest) -> bool:
    r = requests.get(url=image_request.image_url, stream=True, timeout=30)
    if r.status_code == 200:
        obj_name = "products/{}.webp".format(image_request.ean)
        thumbnail_name = "products/{}_thumbnail.webp".format(image_request.ean)
        try:
            image = Image.open(r.raw)
            thumbnail = image.copy()

            fixed_height = 1080
            if fixed_height > image.height:
                fixed_height = image.height
            height_percent = (fixed_height / float(image.size[1]))
            width_size = int(float(image.size[0]) * float(height_percent))
            image = image.resize((width_size, fixed_height), Image.LANCZOS)

            save_image(image, obj_name, False)

            MAX_THUMBNAIL_SIZE = (500, 500)
            thumbnail.thumbnail(MAX_THUMBNAIL_SIZE)

            save_image(thumbnail, thumbnail_name, True)
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            return False
    else:
        print(f"Error downloading image: {r.status_code}")
        print(f"Error removing bg from image: {image_request.image_url}")
        return False


def save_image(image: Image, obj_name: str, thumbnail: bool) -> bool:
    print(f"Uploading to S3: {obj_name}")
    in_mem_file = io.BytesIO()

    image.save(in_mem_file, format="webp", optimize=True, quality=85)
    in_mem_file.seek(0)

    s3 = boto3.client("s3")
    s3.upload_fileobj(in_mem_file, public_content_bucket, obj_name)
    print(f"Uploaded to S3: {obj_name}")
    s3.close()


def handler(event, context):
    print(event)
    for record in event["Records"]:
        if record["eventName"] != "INSERT":
            continue
        photo_url = record["dynamodb"]["NewImage"]["photo"]["S"]
        ean = record["dynamodb"]["NewImage"]["ean"]["S"]

        image_download(ImageRequest(image_url=photo_url, ean=ean))