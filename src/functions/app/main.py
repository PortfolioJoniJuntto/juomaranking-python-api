from fastapi import FastAPI
from mangum import Mangum

from endpoints import auth, products, users, ratings

app = FastAPI(title="Juoma Ranking", root_path="/")

app.include_router(products.router)
app.include_router(users.router)
app.include_router(ratings.router)
app.include_router(auth.router)

handler = Mangum(app)
