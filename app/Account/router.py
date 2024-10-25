# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# from multiprocessing import Pool
# from typing import Any
# from bson import ObjectId
# from fastapi import APIRouter, Depends, HTTPException, status
# from pymongo import MongoClient
# from starlette.responses import JSONResponse
#
# from app.Account.schema import UserAccountSchema
# from app.Account.servise import UserRepository, UpdateAccountUser
# from app.Users.servis import UsersDAO
# from app.Users.utils import get_async_session
#
# from sqlalchemy.ext.asyncio import AsyncSession
#
#
#
# router = APIRouter(
#     prefix="/Account",
#     tags=["Account"],
# )
#
# # Новый эндпоинт для заполнения дополнительных настроек пользователя
# @router.post("/complete-profile")
# async def complete_profile(user_id: int, profile_data: UserAccountSchema, session: AsyncSession = Depends(get_async_session)):
#     user = await UsersDAO.get_user_by_id(user_id, session)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
#
#     # Сохранение дополнительных настроек пользователя
#     user.details = profile_data.dict()
#     session.add(user)
#     await session.commit()
#
#     return {"message": "User profile updated successfully."}
from typing import List, Optional

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.Account.schema import UserAccountCreate, UserAccountUpdate, UserAccountReturn, Location, Geolocation, \
    UserAccountReturnToListCard
from app.Account.servise import AccountDAO
from app.Users.utils import get_async_session
from app.auth.auth import check_user_role

## Новый эндпоинт для заполнения дополнительных настроек пользователя

# Получение Информации о пользователе (т.е. информации об ПОЛЬЗОВАТЕЛЕ)


router = APIRouter(
    prefix="/Account",
    tags=["Account"],
)


@router.get("/getInfoUser", dependencies=[Depends(check_user_role(["admin", "user"]))], response_model=UserAccountReturn)
async def getInfoUser(request: Request, session: AsyncSession = Depends(get_async_session)):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_account = await AccountDAO.find_by_id(user.id, session)
    if not user_account:
        raise HTTPException(status_code=404, detail="User account not found")
    print(f"{user_account=}")
    return user_account


@router.get("/getAccountUser/{id}", dependencies=[Depends(check_user_role(["admin", "user"]))], response_model=UserAccountReturn)
async def getAccountUser(id: int, request: Request, session: AsyncSession = Depends(get_async_session)):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_account = await AccountDAO.find_by_id(id, session)
    if not user_account:
        raise HTTPException(status_code=404, detail="User account not found")
    print(f"{user_account=}")
    return user_account

@router.get("/get_id_account", dependencies=[Depends(check_user_role(["admin", "user"]))] )
async def get_account_id(request: Request, session: AsyncSession = Depends(get_async_session)) -> int:
    user = request.state.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id


@router.post("/createUser", dependencies=[Depends(check_user_role(["admin", "user"]))],
             response_model=UserAccountReturn)
async def create_user(request: Request, user_account: UserAccountCreate,
                      session: AsyncSession = Depends(get_async_session)):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        new_account = await AccountDAO.create_user(user.id, user_account.dict(), session)
        return new_account
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/updateUser", dependencies=[Depends(check_user_role(["admin", "user"]))], response_model=UserAccountReturn)
async def update_user(request: Request, user_account: UserAccountUpdate,
                      session: AsyncSession = Depends(get_async_session)):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        updated_user = await AccountDAO.update_user(user.id, user_account.dict(exclude_unset=True), session)
        return updated_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/updateUserGeolocation", dependencies=[Depends(check_user_role(["admin", "user"]))],
            response_model=UserAccountUpdate)
async def update_geolocation(request: Request, user_account: Geolocation,
                             session: AsyncSession = Depends(get_async_session)):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        updated_user = await AccountDAO.update_user_geolocation(user.id, user_account.latitude, user_account.longitude,
                                                                session)
        return updated_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getUsersWithinRadius", dependencies=[Depends(check_user_role(["admin", "user"]))],
            response_model=List[UserAccountReturnToListCard])
async def get_users_within_radius(request: Request,
                                  session: AsyncSession = Depends(get_async_session)):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        users = await AccountDAO.get_users_within_radius(user.id, session)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/getUsersWithinRadius2", dependencies=[Depends(check_user_role(["admin", "user"]))],
            response_model=List[UserAccountReturnToListCard])
async def get_users_within_radius2(    request: Request,
    tags: Optional[List[str]] = Query(None),  # Добавьте параметр для тегов
    session: AsyncSession = Depends(get_async_session)
):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        users = await AccountDAO.get_users_within_radius_with_tags(user.id, tags, session)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.get("/getUsers", dependencies=[Depends(check_user_role(["admin", "user"]))])
# async def getUserAbout(request: Request, session: AsyncSession = Depends(get_async_session)):
#     user = request.state.user
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     user_account = await AccountDAO.find_by_id(user.id, session)
#     if not user_account:
#         raise HTTPException(status_code=404, detail="User account not found")
#     latitude = user_account.location['latitude']
#     longitude = user_account.location['longitude']
#
#     print(f"latitude: {latitude},longitude: {longitude} ")
#     try:
#         user_accounts = await AccountDAO.find_nearby_accounts(float(latitude), float(longitude), session)
#         if not user_accounts:
#             raise HTTPException(status_code=404, detail="User accounts not found within 2 km radius")
#         return user_accounts
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch nearby user accounts: {str(e)}")
