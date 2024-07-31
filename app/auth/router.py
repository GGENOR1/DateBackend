from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.MailServices.servis import generate_confirmation_code, send_confirmation_email
from app.Redis.servise import get_from_cache, set_in_cache
from app.Users.dependecies import get_current_user
from app.Users.models import Users
from app.Users.schema import UserAddSchema
from app.Users.servis import UsersDAO
from app.Users.utils import get_async_session
from app.auth.auth import authenticate_user, create_access_token, get_password_hash, verify_confirmation_code
from app.auth.servis import RegisterDAO
from app.auth.shemas import SUserAuth, SUserAuthWithCode, SUserRegistration, SUserConfirmCode, SUserRegistrationWithCode
from sqlalchemy.ext.asyncio import AsyncSession

from app.exception import *
from app.successfulResponse import SuccessfulСodeSubmission, SuccessfulReceiptToken, SuccessfulUserAdd, \
    CorrectСonfirmationСode

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


# Ручка для проверки наличия почты при создании аккаунта
# @router.post("/check_email/signUp")
# async def check_sign_up(user_data: SUserAuth, session: AsyncSession = Depends(get_async_session)):
#     existing_user = await RegisterDAO.check_email(session, email=user_data.email)
#     if existing_user:
#         print(f"existing_user:{existing_user}")
#         raise UserAlreadyExistsException
#
#     return HTTPException(status_code=status.HTTP_200_OK)

# Ручка для проверки наличия почты при создании аккаунта
# @router.post("/check_email/signIn")
# async def check_sign_in(user_data: SUserAuth, session: AsyncSession = Depends(get_async_session)):
#     existing_user = await RegisterDAO.check_email(session, email=user_data.email)
#     if not existing_user:
#         print(f"existing_user:{existing_user}")
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
#     return  HTTPException(status_code=status.HTTP_200_OK)

# Ручка для добавления пользователя (!!! ВЫПОЛНЯТЬ ТОЛЬКО ПОСЛЕ РУЧКИ ПРОВЕРКИ ПОЧТЫ)

# @router.post("/register" )
# async def add_user(new_user: UserAddSchema , session: AsyncSession = Depends(get_async_session)):
#     # Еще раз проверяем наличие почты 
#     existing_user = await RegisterDAO.check_email(session, email=new_user.email)
#     if existing_user:
#         raise UserAlreadyExistsException
#     hashed_password = get_password_hash(new_user.password)
#     # Создание пользователя с хэшированным паролем
#     user_data = new_user.dict()
#     user_data['password'] = hashed_password
#     result = await UsersDAO.add_user(user_data, session)
#     if result is None:
#         raise HTTPException(status_code=404, detail="Exception")
#     return result

# Ручка для отправки сообщения пользователя при регистрации (!!! ВЫПОЛНЯТЬ ТОЛЬКО ПОСЛЕ РУЧКИ ПРОВЕРКИ ПОЧТЫ)

@router.post("/send_verify-email_to_registr")
async def send_verify_email_to_registr(new_user: SUserRegistration, session: AsyncSession = Depends(get_async_session)):
    # Проверка наличия почты в базе данных
    existing_user = await RegisterDAO.check_email(session, email=new_user.email)
    if existing_user:
        raise UserAlreadyExistsException

    confirmation_code = await generate_confirmation_code()
    # confirmation_code = 111
    print(f"confirmation_code {confirmation_code}")
    status_key_redis = await set_in_cache(f"SignUp:{new_user.email}", confirmation_code, 600)
    if not status_key_redis:
        raise InternalErrorRedisServer()
    status = await send_confirmation_email(new_user.email, confirmation_code)
    print(status)
    if not status:
        raise InvalidSendingConfirmation
    return SuccessfulСodeSubmission()


@router.post("/check_verify-code_to_registr")
async def check_verify_code_to_registr(new_user: SUserConfirmCode, session: AsyncSession = Depends(get_async_session)):
    existing_user = await RegisterDAO.check_email(session, email=new_user.email)
    if existing_user:
        raise UserAlreadyExistsException
    check_code = await verify_confirmation_code(f"SignUp:{new_user.email}", new_user.code)
    print(f"Статус проверке при регистрации: {check_code}")
    if (check_code == False) or (not check_code):
        raise InvalidСonfirmationСode

    return CorrectСonfirmationСode()


# Ручка для проверки кода и регистрации пользователя (!!! ВЫПОЛНЯТЬ ТОЛЬКО ПОСЛЕ РУЧКИ ПРОВЕРКИ ПОЧТЫ)
@router.post("/verify-email_to_registr")
async def verify_email_and_add_user(new_user: SUserRegistrationWithCode,
                                    session: AsyncSession = Depends(get_async_session)):
    existing_user = await RegisterDAO.check_email(session, email=new_user.email)
    if existing_user:
        raise UserAlreadyExistsException
    check_code = await verify_confirmation_code(f"SignUp:{new_user.email}", new_user.code)
    # check_code = 111
    print(f"Статус проверке при регистрации: {check_code}")
    if (check_code == False) or (not check_code):
        raise InvalidСonfirmationСode
    hashed_password = get_password_hash(new_user.password)
    user_data = new_user.dict()
    user_data['password'] = hashed_password
    user_data["registered_at"] = datetime.utcnow()
    user_data.pop('code', None)
    user_data['role_id'] = 1
    print(user_data)
    result = await UsersDAO.add_user(user_data, session)
    if result is None:
        raise InternalErrorAdded
    return SuccessfulUserAdd()



# Ручка для отправки сообщения пользователя при входе (!!! ВЫПОЛНЯТЬ ТОЛЬКО ПОСЛЕ РУЧКИ ПРОВЕРКИ ПОЧТЫ)

@router.post("/send_verify-email_to_login")
async def send_verify_email_to_login(user: SUserAuth, session: AsyncSession = Depends(get_async_session)):
    # Проверка наличия почты в базе данных
    existing_user = await RegisterDAO.check_email(session, email=user.email)
    if not existing_user:
        raise InvalidUserVailabilityUser
    user = await authenticate_user(user.email, user.password, session)
    if not user:
        raise IncorrectEmailOrPassException
    # Отправка кода подтверждения на почту
    confirmation_code = await generate_confirmation_code()
    # confirmation_code = 111
    print(f"confirmation_code {confirmation_code}")
    status_key_redis = await set_in_cache(f"SignIn:{user.email}", confirmation_code, 600)
    if not status_key_redis:
        raise InternalErrorRedisServer()
    status_send_mail = await send_confirmation_email(user.email, confirmation_code)  # тут отправляем сообщение на почту
    print(f"Статус при отправке сообщения на почту при входе: {status_send_mail}")
    if status_send_mail == False:
        raise InvalidSendingConfirmation
        ##отправить ошибку об отправке соединения
    ##если все ок, реализовать добавления кода в редис на n минут   
    return SuccessfulСodeSubmission()


# Ручка для проверки кода и входа пользователя (!!! ВЫПОЛНЯТЬ ТОЛЬКО ПОСЛЕ РУЧКИ ПРОВЕРКИ ПОЧТЫ)
@router.post("/verify-email_to_login")
async def verify_email_and_login_user(response: Response, user: SUserAuthWithCode,
                                      session: AsyncSession = Depends(get_async_session)):
    existing_user = await RegisterDAO.check_email(session, email=user.email)
    if not existing_user:
        raise InvalidUserVailabilityUser
    check_code = await verify_confirmation_code(f"SignIn:{user.email}", user.code)
    check_code = True
    print(f"Статус проверке при авторизации: {check_code}")
    # if ((check_code == False) or (not check_code)) or (check_code != 111):
    #
    #     raise HTTPException(status_code=404, detail="Error with check confirmation code")
    user = await authenticate_user(user.email, user.password, session)
    if not user:
        raise IncorrectEmailOrPassException
    access_token = create_access_token(user)
    print(access_token)
    response.set_cookie("user_access_token", access_token, httponly=True)
    return SuccessfulReceiptToken(access_token)


# # Ручка для авторизации пользователя (!!! ВЫПОЛНЯТЬ ТОЛЬКО ПОСЛЕ РУЧКИ ПРОВЕРКИ ПОЧТЫ)
# @router.post("/login" )
# async def login_user(response: Response, user: SUserAuth , session: AsyncSession = Depends(get_async_session)):
#     user = await authenticate_user(user.email, user.password, session)
#     if not user:
#          raise IncorrectEmailOrPassException
#     access_token = create_access_token({"sub": int(user.id)})
#     print(access_token)
#     response.set_cookie("user_access_token", access_token, httponly=True)
#     return access_token


# Ручка которая поможет вернуть все поля и данные по токену пользователя (т.е. выводить его данные)
@router.get("/test")
async def geasat_users(user: Users = Depends(get_current_user)):
    print(user, type(user), user.id)
    return user


# Ручка которая поможет вернуть все поля и данные по токену пользователя (т.е. выводить его данные)
@router.get("/TEST")
async def testFunctions():
    return "Hellow"
# # Ручка для удаления куки
# @router.get("/logout")
# async def logout_user(response: Response):
#     response.delete_cookie("user_access_token")
#     return HTTPException(status_code=status.HTTP_202_ACCEPTED)
