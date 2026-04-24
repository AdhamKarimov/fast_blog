from fastapi import FastAPI
from user.router import router as user_router
from articl.router import router as post_router
from user.models import User
from articl.models import Post
from comments.models import Comment
from fovorite.models import Fovorite
from like.models import Like

from fastapi_jwt_auth2 import AuthJWT
from user.schema import Settings


app = FastAPI()
app.include_router(user_router)
app.include_router(post_router)

@AuthJWT.load_config
def get_config():
    return Settings()
app.include_router(user_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}