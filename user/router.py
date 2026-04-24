from user.models import User
from user.schema import SignUp, Login, Updateprofil, PasswordResert
from fastapi import APIRouter, HTTPException, Depends, status
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth2 import AuthJWT
import datetime

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up(user: SignUp, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.username == user.username))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu Username band")

    result = await db.execute(select(User).filter(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu Email band")

    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        'status': status.HTTP_201_CREATED,
        'first_name': new_user.first_name,
        'last_name': new_user.last_name,
        'username': new_user.username,
        'email': new_user.email,
    }


@router.post("/login")
async def login(data: Login, db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    result = await db.execute(select(User).filter(User.username == data.username))
    db_user = result.scalars().first()

    if not db_user or not check_password_hash(db_user.password, data.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username yoki password xato")

    access_token = Authorize.create_access_token(
        subject=db_user.username,
        expires_time=datetime.timedelta(minutes=30)
    )
    refresh_token = Authorize.create_refresh_token(
        subject=db_user.username,
        expires_time=datetime.timedelta(days=7)
    )

    return {
        'status': status.HTTP_200_OK,
        'access_token': access_token,
        'refresh_token': refresh_token,
    }


@router.get("/profile")
async def profile(db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()

        result = await db.execute(select(User).filter(User.username == current_user))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.put("/update")
async def update_profile(
    user_data: Updateprofil,
    db: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()

        result = await db.execute(select(User).filter(User.username == current_user))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

        if user_data.first_name:
            user.first_name = user_data.first_name
        if user_data.last_name:
            user.last_name = user_data.last_name
        if user_data.username:
            res = await db.execute(select(User).filter(User.username == user_data.username))
            existing = res.scalars().first()
            if existing and existing.id != user.id:
                raise HTTPException(status_code=400, detail="Bu username band")
            user.username = user_data.username
        if user_data.email:
            res = await db.execute(select(User).filter(User.email == user_data.email))
            existing = res.scalars().first()
            if existing and existing.id != user.id:
                raise HTTPException(status_code=400, detail="Bu email band")
            user.email = user_data.email

        await db.commit()
        await db.refresh(user)

        return {
            'status': status.HTTP_200_OK,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.put("/password-reset")
async def password_reset(
    data: PasswordResert,
    db: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()

        result = await db.execute(select(User).filter(User.username == current_user))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

        if not check_password_hash(user.password, data.old_password):
            raise HTTPException(status_code=400, detail="Eski password xato")

        if data.new_password != data.confirm_password:
            raise HTTPException(status_code=400, detail="Yangi passwordlar mos kelmadi")

        if check_password_hash(user.password, data.new_password):
            raise HTTPException(status_code=400, detail="Yangi password eski bilan bir xil bo'lmasligi kerak")

        user.password = generate_password_hash(data.new_password)
        await db.commit()

        return {
            'status': status.HTTP_200_OK,
            'detail': "Password muvaffaqiyatli yangilandi"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))