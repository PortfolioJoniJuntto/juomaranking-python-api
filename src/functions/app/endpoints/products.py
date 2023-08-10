from time import time
from datetime import date
from typing import List

import boto3
import jsons
from fastapi import APIRouter, HTTPException, Depends
from pynamodb.exceptions import PutError, VerboseClientError

from models.pricehistory import PriceHistoryModel
from models.products import (
    ProductModel,
    Product,
    ProductDTO,
    PriceDataModel,
    NutrientsModel,
)
from models.ratings import RatingDTO, RatingModel

from utils.constants import public_content_bucket_name

from utils.auth import auth, AccessUser

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


def update_product_stores(
    product_model: ProductModel, product: Product
) -> ProductModel:
    if product_model.store is None:
        product_model.store = product.store
    else:
        for p in product.store:
            product_model.store.append(p)
    product_model.store = list(set(product_model.store))
    return product_model


def update_product_price_history(product_models: List[ProductModel]):
    date = date.today().strftime("%Y-%m-%d")
    price_histories: List[PriceHistoryModel] = []

    for pm in product_models:
        for pd in pm.price_data:
            sk = "{}-{}".format(date, pd.store)
            price_histories.append(
                PriceHistoryModel(
                    ean=pm.ean,
                    sk=sk,
                    price=pd.price,
                    created_at=int(time()),
                    store=pd.store,
                )
            )

    with PriceHistoryModel.batch_write() as batch:
        for phm in price_histories:
            batch.save(phm)


def update_product_price_data(
    product_model: ProductModel, product: Product
) -> ProductModel:
    if product_model.price_data is None:
        product_model.price_data = []

    if product.price_data is not None:
        for p in product.price_data:
            found = False
            for pd in product_model.price_data:
                if pd.store == p.store and p.price is not None:
                    pd.price = p.price
                    pd.updated_at = int(time())
                    found = True
                    break
            if not found:
                product_model.price_data.append(
                    PriceDataModel(price=p.price, store=p.store, updated_at=int(time()))
                )
    return product_model


def update_product_nutrients(
    product_model: ProductModel, product: Product
) -> ProductModel:
    product_model.nutrients = []

    if product.nutrients is not None:
        for n in product.nutrients:
            product_model.nutrients.append(
                NutrientsModel(name=n.name, value=n.value, ri=n.ri)
            )
    return product_model


@router.get("")
def get_products():
    results_iter = ProductModel.scan(limit=25)
    results = list(results_iter)
    total_count = results_iter.total_count
    last_evaluated_key = results_iter.last_evaluated_key

    return {
        "items": [ProductDTO(pm) for pm in results],
        "total_count": total_count,
        "last_evaluated_key": last_evaluated_key,
    }


@router.post("")
def add_product(
    product: Product, current_user: AccessUser = Depends(auth.scope(["Admin"]))
):
    product_model = None
    try:
        product_model = ProductModel(
            ean=product.ean,
            name=product.name,
            stars={"one": 0, "two": 0, "three": 0, "four": 0, "five": 0},
            photo=product.photo,
            price=product.price,
            created_at=int(time()),
            updated_at=int(time()),
            category=product.category,
            price_data=None,
            store=product.store,
            main_product_ean=product.main_product_ean,
            name_fi=product.name_fi,
            name_sv=product.name_sv,
            name_en=product.name_en,
            description_fi=product.description_fi,
            description_sv=product.description_sv,
            description_en=product.description_en,
            ingredients_fi=product.ingredients_fi,
            ingredients_sv=product.ingredients_sv,
            ingredients_en=product.ingredients_en,
            supplier=product.supplier,
        )
        update_product_price_data(product_model, product)
        update_product_nutrients(product_model, product)
        product_model.save(ProductModel.ean.does_not_exist())
    except PutError as e:
        if isinstance(e.cause, VerboseClientError):
            code = e.cause.response["Error"].get("Code")
            if code == "ConditionalCheckFailedException":
                raise HTTPException(status_code=400, detail="Item already exists.")
        raise HTTPException(status_code=500, detail=jsons.dumps(e))
    try:
        update_product_price_history([product_model])
    except Exception as e:
        print(e)

    return product_model.to_dict()


@router.put("/{ean}")
def update_product(
    ean: str,
    product: Product,
    current_user: AccessUser = Depends(auth.scope(["Admin"])),
):
    try:
        product_model = ProductModel.get(ean)
    except ProductModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        product_model.name = product.name
        product_model.stars = product.stars
        product_model.photo = product.photo
        product_model.price = product.price
        product_model.category = product.category
        product_model.updated_at = int(time())
        product_model.main_product_ean = product.main_product_ean

        product_model.name_fi = product.name_fi
        product_model.name_sv = product.name_sv
        product_model.name_en = product.name_en
        product_model.description_fi = product.description_fi
        product_model.description_sv = product.description_sv
        product_model.description_en = product.description_en
        product_model.ingredients_fi = product.ingredients_fi
        product_model.ingredients_sv = product.ingredients_sv
        product_model.ingredients_en = product.ingredients_en

        product_model.supplier = product.supplier

        product_model = update_product_price_data(product_model, product)
        product_model = update_product_stores(product_model, product)
        product_model = update_product_nutrients(product_model, product)

        product_model.save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

    try:
        update_product_price_history([product_model])
    except Exception as e:
        print(e)

    return product_model.to_dict()


@router.post("/batch")
def batch_products(
    products: List[Product], current_user: AccessUser = Depends(auth.scope(["Admin"]))
):
    eans = list(set(map(lambda product: product.ean, products)))

    db_products = dict()
    for product_model in ProductModel.batch_get(eans):
        if product_model is not None:
            db_products[product_model.ean] = product_model

    product_models = []

    with ProductModel.batch_write() as batch:
        for product in products:
            if product.ean in db_products:
                product_model = db_products[product.ean]
            else:
                product_model = ProductModel(ean=product.ean, name=product.name)

            product_model.name = product.name
            product_model.stars = {"one": 0, "two": 0, "three": 0, "four": 0, "five": 0}
            product_model.photo = product.photo
            product_model.price = product.price
            product_model.category = product.category
            product_model.updated_at = int(time())
            product_model.main_product_ean = product.main_product_ean

            product_model.name_fi = product.name_fi
            product_model.name_sv = product.name_sv
            product_model.name_en = product.name_en
            product_model.description_fi = product.description_fi
            product_model.description_sv = product.description_sv
            product_model.description_en = product.description_en
            product_model.ingredients_fi = product.ingredients_fi
            product_model.ingredients_sv = product.ingredients_sv
            product_model.ingredients_en = product.ingredients_en
            product_model.supplier = product.supplier

            product_model = update_product_price_data(product_model, product)
            product_model = update_product_stores(product_model, product)
            product_model = update_product_nutrients(product_model, product)

            product_models.append(product_model)

            batch.save(product_model)

    try:
        update_product_price_history(
            product_models
        )  # Update price history for all product_models
    except Exception as e:
        print(e)

    return [pm.to_dict() for pm in product_models]


@router.get("/{ean}")
def get_product(ean: str) -> ProductDTO:
    try:
        product_model = ProductModel.get(ean)
    except ProductModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        rating_models = RatingModel.query(ean, limit=5)
    except RatingModel.DoesNotExist:
        pass

    dto = ProductDTO(product_model)

    if rating_models is not None:
        dto.ratings = sorted(
            [
                RatingDTO(
                    ean=ean,
                    rating=sr.rating,
                    comment=sr.comment,
                    username=sr.username,
                    created_at=sr.created_at,
                    updated_at=sr.updated_at,
                )
                for sr in rating_models
                if sr.comment is not None and len(sr.comment) > 0
            ],
            key=lambda sr: sr.created_at,
            reverse=True,
        )  # This python language is so wierd.

    return dto


@router.get("/scan")
def get_products_scan(current_user: AccessUser = Depends(auth.scope(["Admin"]))):
    results_iter = ProductModel.scan(limit=99999)
    results = list(results_iter)
    total_count = results_iter.total_count
    results_iter.last_evaluated_key

    print(total_count, len(results))
    return [ProductDTO(pm) for pm in results]


@router.delete("/delete-all")
def delete_all_products(current_user: AccessUser = Depends(auth.scope(["Admin"]))):
    results_iter = ProductModel.scan(limit=99999)
    results = list(results_iter)

    with ProductModel.batch_write() as batch:
        for pm in results:
            batch.delete(pm)
    return {"ok": len(results)}


@router.post("/export")
def export_to_s3(current_user: AccessUser = Depends(auth.scope(["Admin"]))):
    results_iter = ProductModel.scan(limit=99999)
    results = list(results_iter)
    products = [ProductDTO(pm) for pm in results]
    s3_client = boto3.client("s3")
    s3_client.put_object(
        Bucket=public_content_bucket_name,
        Key="products.json",
        Body=jsons.dumps(products),
    )
    s3_client.close()
    return {"ok": len(products)}
