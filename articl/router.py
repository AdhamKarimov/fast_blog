from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File,Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_db
from articl.models import Post
from articl.schema import PostCreate, PostDetail, PostListResponse,PostUpdate
from fastapi_jwt_auth2 import AuthJWT
from user.models import User
import shutil, os, uuid
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/posts", tags=["posts"])

UPLOAD_DIR = "media/post_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/create", response_model=PostDetail, status_code=status.HTTP_201_CREATED)
async def create_post(title:str= Form(),content:str=Form(),db: AsyncSession = Depends(get_db),Authorize: AuthJWT = Depends(),image: UploadFile = File(None)):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()

        result = await db.execute(select(User).filter(User.username == current_user))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

        image_path = None
        if image:
            ext = image.filename.split(".")[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            image_path = f"{UPLOAD_DIR}/{filename}"
            with open(image_path, "wb") as f:
                shutil.copyfileobj(image.file, f)

        new_post = Post(
            title=title,
            content=content,
            image=image_path,
            author_id=user.id
        )
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)

        result = await db.execute(select(Post).options(joinedload(Post.author)).filter(Post.id == new_post.id))
        post = result.scalars().first()

        return post

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/list", response_model=List[PostListResponse])
async def post_list(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).options(joinedload(Post.author)).filter(Post.is_deleted == False))
    posts = result.scalars().all()

    return posts


@router.get("/detail/{post_id}", response_model=PostDetail)
async def detail(post_id: int, db: AsyncSession = Depends(get_db),Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()

        result = await db.execute(select(User).filter(User.username == current_user))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

        posts = await db.execute(select(Post).options(joinedload(Post.author)).filter(Post.id == post_id))

        post = posts.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post topilmadi")

        return post

    except HTTPException as e :
        return e


@router.patch("/update/{post_id}", response_model=PostDetail)
async def update(post_id: int,new_data:PostUpdate, db: AsyncSession = Depends(get_db),Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()

        result = await db.execute(select(User).filter(User.username == current_user))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

        posts = await db.execute(select(Post).options(joinedload(Post.author)).filter(Post.id == post_id))

        post = posts.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post topilmadi")

        if post.author_id!=user.id:
            raise HTTPException(status_code=403, detail="sizda ruxsat yo'q")

        if new_data.title:
            post.title = new_data.title
        if new_data.content:
            post.content = new_data.content

        await db.commit()
        await db.refresh(post)

        result = await db.execute(select(Post).filter(Post.id == post_id))
        post = result.scalars().first()

        return post
    except HTTPException as e :
        raise e


@router.delete("/delete/{post_id}")
async def delete(post_id:int,db: AsyncSession = Depends(get_db),Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()

        result = await db.execute(select(User).filter(User.username == current_user))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

        posts = await db.execute(select(Post).options(joinedload(Post.author)).filter(Post.id == post_id))

        post = posts.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post topilmadi")

        if post.author_id!=user.id:
            raise HTTPException(status_code=403, detail="sizda ruxsat yo'q")

        await db.delete(post)
        await db.commit()

        return {'message':"post o'chirildi"}

    except HTTPException as e :
        raise e

