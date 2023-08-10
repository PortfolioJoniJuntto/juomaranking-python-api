import os
from typing import Optional, List

from pydantic import BaseModel
from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute,
    NumberAttribute,
    MapAttribute,
    ListAttribute,
)

from .dbmodel import DBModel
from .ratings import RatingDTO, RatingAmountDTO

table_name = os.getenv("products_table_name")
region = os.getenv("region")


class PriceDataDTO:
    def __init__(self, price: int, updated_at: Optional[int], store: str) -> None:
        self.price = price
        self.updated_at = updated_at
        self.store = store


class PriceData(BaseModel):
    price: int
    updated_at: Optional[int]
    store: str


class PriceDataModel(MapAttribute):
    price = NumberAttribute()
    updated_at = NumberAttribute(null=True)
    store = UnicodeAttribute()


class Nutrients(BaseModel):
    name: Optional[str]
    ri: Optional[str]
    value: Optional[str]


class NutrientsDTO:
    def __init__(self, name: str, ri: str, value: str) -> None:
        self.name = name
        self.ri = ri
        self.value = value


class NutrientsModel(MapAttribute):
    name = UnicodeAttribute(null=True)
    ri = UnicodeAttribute(null=True)
    value = UnicodeAttribute(null=True)


class Stars(BaseModel):
    one: int
    two: int
    three: int
    four: int
    five: int


class StarsModel(MapAttribute):
    one = NumberAttribute()
    two = NumberAttribute()
    three = NumberAttribute()
    four = NumberAttribute()
    five = NumberAttribute()


class StarsDTO:
    def __init__(self, one: int, two: int, three: int, four: int, five: int) -> None:
        self.one = one
        self.two = two
        self.three = three
        self.four = four
        self.five = five


class ProductModel(DBModel):
    """
    A DynamoDB Products
    """

    class Meta:
        table_name = table_name
        region = region

    ean = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute(null=True)
    stars = StarsModel(null=True)
    photo = UnicodeAttribute(null=True)
    price = NumberAttribute(null=True)
    category = UnicodeAttribute(null=True)
    created_at = NumberAttribute(null=True)
    updated_at = NumberAttribute(null=True)
    store = ListAttribute(of=UnicodeAttribute, null=True)
    price_data = ListAttribute(of=PriceDataModel, null=True)
    main_product_ean = UnicodeAttribute(null=True)
    name_fi = UnicodeAttribute(null=True)
    name_sv = UnicodeAttribute(null=True)
    name_en = UnicodeAttribute(null=True)
    description_fi = UnicodeAttribute(null=True)
    description_sv = UnicodeAttribute(null=True)
    description_en = UnicodeAttribute(null=True)
    ingredients_fi = UnicodeAttribute(null=True)
    ingredients_sv = UnicodeAttribute(null=True)
    ingredients_en = UnicodeAttribute(null=True)
    nutrients = ListAttribute(of=NutrientsModel, null=True)
    supplier = UnicodeAttribute(null=True)


class Product(BaseModel):
    ean: str
    name: Optional[str]
    category: Optional[str]
    stars: Optional[Stars]
    photo: Optional[str]
    price: Optional[int]
    created_at: Optional[int]
    updated_at: Optional[int]
    price_data: Optional[List[PriceData]]
    store: Optional[List[str]]
    main_product_ean: Optional[str]
    name_fi: Optional[str]
    name_sv: Optional[str]
    name_en: Optional[str]
    description_fi: Optional[str]
    description_sv: Optional[str]
    description_en: Optional[str]
    ingredients_fi: Optional[str]
    ingredients_sv: Optional[str]
    ingredients_en: Optional[str]
    nutrients: Optional[List[Nutrients]]
    supplier: Optional[str]


class ProductDTO:
    ratings: Optional[List[RatingDTO]]
    rating_amounts: Optional[List[RatingAmountDTO]]

    def __init__(self, product: ProductModel) -> None:
        self.ean = product.ean
        self.name = product.name
        self.category = product.category
        self.stars = StarsDTO(
            one=product.stars.one,
            two=product.stars.two,
            three=product.stars.three,
            four=product.stars.four,
            five=product.stars.five,
        )
        self.photo = product.photo
        self.price = product.price
        self.created_at = product.created_at
        self.updated_at = product.updated_at
        if product.price_data is not None:
            self.price_data = [
                PriceDataDTO(price=pd.price, updated_at=pd.updated_at, store=pd.store)
                for pd in product.price_data
                if pd is not None
            ]

        self.store = product.store
        self.main_product_ean = product.main_product_ean
        self.name_fi = product.name_fi
        self.name_sv = product.name_sv
        self.name_en = product.name_en
        self.description_fi = product.description_fi
        self.description_sv = product.description_sv
        self.description_en = product.description_en
        self.ingredients_fi = product.ingredients_fi
        self.ingredients_sv = product.ingredients_sv
        self.ingredients_en = product.ingredients_en
        if product.nutrients is not None:
            self.nutrients = [
                NutrientsDTO(name=n.name, ri=n.ri, value=n.value)
                for n in product.nutrients
                if n is not None
            ]

        self.supplier = product.supplier
