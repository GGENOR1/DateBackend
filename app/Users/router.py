from typing import List
from sqlalchemy import select
from fastapi import APIRouter, Depends
from app.Users.dependecies import get_current_user
from app.Users.models import Users
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from fastapi import HTTPException

from app.Users.schema import UserAddSchema, UserSchema, UserUpdateSchema
from app.Users.servis import UsersDAO
from app.Users.utils import get_async_session
from app.auth.auth import CustomHTTPBearer, check_user_role

router = APIRouter(
    prefix="/Admin",
    tags=["Admin"],
)



@router.get("/admin_only", dependencies=[Depends(check_user_role("admin"))])
async def admin_only_endpoint(
    authorized: bool = Depends(check_user_role("admin"))
):
    print("Тут начинается")

    # return authorized

# Ручка для получения всех пользователей из БД
@router.get("", response_model=List[UserSchema], dependencies=[Depends(check_user_role("admin"))])
async def get_users(session: AsyncSession = Depends(get_async_session)) -> List[UserSchema]:
    return await UsersDAO.find_all(session)


# Ручка для получения пользователя по id
@router.get("/{user_id}", response_model=UserSchema, dependencies=[Depends(check_user_role("admin"))])
async def get_user(user_id: int, session: AsyncSession = Depends(get_async_session)) -> UserSchema:
    result = await UsersDAO.find_by_id(user_id, session)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result


# # Ручка для добавления пользователя
# @router.post("" )
# async def add_user(new_user: UserAddSchema , session:AsyncSession = Depends(get_async_session)):
#     result = await UsersDAO.add_user(new_user.dict(), session)
#     if result is None:
#         raise HTTPException(status_code=404, detail="Exception")
#     return result

# Ручка для добавления пользователя
@router.post("", dependencies=[Depends(check_user_role("admin"))])
async def add_user(new_user: UserAddSchema, session: AsyncSession = Depends(get_async_session)):
    result = await UsersDAO.add_user(new_user.dict(), session)
    if result is None:
        raise HTTPException(status_code=404, detail="Exception")
    return result


# Ручка для удаления пользователя
@router.delete("/{id}", dependencies=[Depends(check_user_role("admin"))])
async def delete_user(id: int, session: AsyncSession = Depends(get_async_session)):
    result = await UsersDAO.delete_user(id, session)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {id} deleted successfully"}


# Ручка для обновления пользователя
@router.put("/{user_id}", dependencies=[Depends(check_user_role("admin"))])
async def update_user(user_id: int, update_data: UserUpdateSchema, session: AsyncSession = Depends(get_async_session)):
    user_data = update_data.dict(exclude_unset=True)  # Исключаем незаданные значения из словаря
    result = await UsersDAO.update_user(user_id, user_data, session)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}


@router.get("/test2", dependencies=[Depends(check_user_role("admin"))])
async def geasat_userwwws():
    print("user")

