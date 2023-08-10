from time import time
from fastapi import APIRouter, Depends, HTTPException, Response

from utils.auth import auth, AccessUser

from models.products import (
    ProductModel,
)
from models.ratings import Rating, RatingDTO, RatingModel
from models.users import UserModel
from utils.utils import RatingToString

router = APIRouter(
    prefix="/ratings",
    tags=["Ratings"],
)


@router.post("/{ean}")
def rate_product(
    ean: str,
    new_rating: Rating,
    current_user: AccessUser = Depends(auth.claim(AccessUser)),
):
    user = UserModel.get(current_user.sub)

    if new_rating.rating < 1 or new_rating.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1-5")

    try:
        old_rating = RatingModel.get(ean, current_user.sub)
        old_num = RatingToString(old_rating.rating)
    except:
        old_num = None
        print("Old rating not found")

    num = RatingToString(new_rating.rating)

    rating_model = RatingModel(ean=ean, userId=current_user.sub)

    update_actions = [
        RatingModel.rating.set(new_rating.rating),
        RatingModel.comment.set(new_rating.comment),
        RatingModel.updated_at.set(int(time())),
        RatingModel.username.set(user.username),
    ]

    if num != old_num:
        if old_num is None:
            update_actions.append(RatingModel.created_at.set(int(time())))
        else:
            ProductModel(ean=ean).update(
                actions=[
                    ProductModel.stars[old_num].set(ProductModel.stars[old_num] - 1)
                ]
            )

        ProductModel(ean=ean).update(
            actions=[ProductModel.stars[num].set(ProductModel.stars[num] + 1)]
        )

    try:
        rating_model.update(actions=update_actions)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500)

    return Response(status_code=204)


@router.get("/{ean}")
def get_product_ratings(
    ean: str,
):
    results_iter = RatingModel.query(ean, limit=10)
    results = list(results_iter)
    return [RatingDTO(pm) for pm in results]
