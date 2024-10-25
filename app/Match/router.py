from typing import List

from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from app.Account.schema import UserAccountReturn, UserAccountReturnToListCard, UserAccountReturnToListMatches
from app.Account.servise import AccountDAO
from app.Chats.Chats.servise import ChatRepository
from app.Match.Models.LikeClass import LikeModel
from app.Match.Models.MatchClass import MatchModel
from app.Match.Repository.LikeRepository import LikeRepository
from app.Connection.kafkaController.controller import kafka_service
from app.Match.Repository.MatchesRepository import MatchesRepository
from app.Users.utils import get_async_session
from app.auth.auth import check_user_role
from app.config import KAFKA_LIKES, KAFKA_MATCHES

router = APIRouter(
    prefix="/Match",
    tags=["Match"],
)

#TODO: при проверке наличия взимного лайка, если имеются а Мэтча нет, надо создавать его и отправлять уведомления
@router.get("/matches")
async def get_all_matches(repository: MatchesRepository = Depends(MatchesRepository.get_instance)) -> list[MatchModel]:
    return await repository.find_all()


@router.post("/matches", dependencies=[Depends(check_user_role(["admin", "user"]))])
async def add_match(match_user_id: int,
                   request: Request,
                   repository: MatchesRepository = Depends(MatchesRepository.get_instance),
                   session: AsyncSession = Depends(get_async_session)):
    user = request.state.user
    other_account = await AccountDAO.find_by_ids(user.id, match_user_id, session)
    print(f"{other_account=}")
    if not other_account:
        raise HTTPException(status_code=404, detail="Users accounts not found")
        # Проверяем наличие мэтча у текущего пользователя и того который есть
    check_match_1, check_match_2 = await repository.find_by_user_and_match_user(user.id, match_user_id)
    if check_match_1 or check_match_2 :
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": "There is a match"})
    post_id = await repository.create_post(current_id_user=user.id, liked_user_id=match_user_id)
    return post_id


@router.get("/matches/{id}")
async def get_match_by_id_(id: int,
                          repository: MatchesRepository = Depends(MatchesRepository.get_instance)) -> MatchModel:
    return await repository.find_by_id(id)

@router.get("/match", dependencies=[Depends(check_user_role(["admin", "user"]))])
async def check_match_from_user(match_user_id: int,
                         request: Request,
                         repository: MatchesRepository = Depends(MatchesRepository.get_instance),
                         session: AsyncSession = Depends(get_async_session)):
    user = request.state.user
    other_account = await AccountDAO.find_by_ids(user.id, match_user_id, session)
    print(f"{other_account=}")
    if not other_account:
        raise HTTPException(status_code=404, detail="Users accounts not found")
    # Проверяем наличие лайка у текущего пользователя и того который есть
    check_match_1, check_match_2 = await repository.find_by_user_and_match_user(user.id, match_user_id)
    print(f"{check_match_1=} or {check_match_2=}")
    if check_match_1 or check_match_2:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": "There is a match"})

    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "There is no match"})

@router.get("/matches/{id}")
async def get_match_by_id(id: int,
                          repository: MatchesRepository = Depends(MatchesRepository.get_instance)) -> MatchModel:
    return await repository.find_by_id(id)

@router.get("/find_by_match_users", dependencies=[Depends(check_user_role(["admin", "user"]))],
            response_model=List[UserAccountReturnToListMatches])
async def find_by_match_users(
                         request: Request,
                         repository: MatchesRepository = Depends(MatchesRepository.get_instance),
                         session: AsyncSession = Depends(get_async_session)):
    user = request.state.user
    # print(f"{user}")
    # account = await AccountDAO.find_by_id(user.id, session)
    # print(f"{account.id=}")
    # print(f"{account.geolocation=}")
    # if not account:
    #     raise HTTPException(status_code=404, detail="Users accounts not found")
    # Проверяем наличие лайка у текущего пользователя и того который есть
    # print(f"{account=}")
    matches = await repository.find_by_match_user(user.id)
    print(f"{matches=}")
    if not matches:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Match not found"})
    accounts = await AccountDAO.find_by_ids_in_list(user.id, matches, session)
    # print(f"{accounts=}")
    return accounts

@router.get("/likes")
async def get_all_likes(repository: LikeRepository = Depends(LikeRepository.get_instance)) -> list[LikeModel]:
    return await repository.find_all()



@router.get("/like", dependencies=[Depends(check_user_role(["admin", "user"]))])
async def check_like_from_user(liked_user_id: int,
                         request: Request,
                         repository: LikeRepository = Depends(LikeRepository.get_instance),
                         session: AsyncSession = Depends(get_async_session)):
    user = request.state.user
    other_account = await AccountDAO.find_by_ids(user.id, liked_user_id, session)
    print(f"{other_account=}")
    if not other_account:
        raise HTTPException(status_code=404, detail="Users accounts not found")
    # Проверяем наличие лайка у текущего пользователя и того который есть
    check_likes = await repository.find_by_user_and_liked_user(user.id, liked_user_id)
    if check_likes:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": "There is a like"})

    return JSONResponse(status_code=status.HTTP_200_OK, content={
        "detail": "There is no like"})


@router.post("/likes", dependencies=[Depends(check_user_role(["admin", "user"]))])
async def add_like(liked_user_id: int,
                   request: Request,
                   repositoryLike: LikeRepository = Depends(LikeRepository.get_instance),
                   repositoryMatches: MatchesRepository = Depends(MatchesRepository.get_instance),
                   repositoryChats: ChatRepository = Depends(ChatRepository.get_instance),
                   session: AsyncSession = Depends(get_async_session)):
    user = request.state.user
    other_account = await AccountDAO.find_by_ids(user.id, liked_user_id, session)
    print(f"{other_account=}")
    if not other_account:
        raise HTTPException(status_code=404, detail="Users accounts not found")
    # Проверяем наличие лайка от текущего пользователя к партнеру
    check_likes = await repositoryLike.find_by_user_and_liked_user(user.id, liked_user_id)
    if check_likes:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": "There is a like"})
    post_id = await repositoryLike.create_post(current_id_user=user.id, liked_user_id=liked_user_id)
    print(f"{post_id=}")
    #проверяем на наличие взаимных лайков
    checking_mutual_likes = await repositoryLike.find_by_user_and_liked_user(user_id=liked_user_id, liked_user_id=user.id)
    print(f"{checking_mutual_likes=}")
    if checking_mutual_likes:
        # если есть то создаем мэтч
        create_match = await repositoryMatches.create_post(current_id_user=user.id, liked_user_id=liked_user_id)
        create_chats = await repositoryChats.create(user.id, liked_user_id)
        print(f"{create_match=}")
        # TODO: Добавить запись в KAFKA уведомления о мэтче
        # await send_kafka_message(producer,KAFKA_MATCHES,str(user.id), 
        #                    {"match_id": 12, "user_id":12, "liked_user_id": 12, "status": "match_created"})
    # Отправляем уведомление о мэтче
        # await send_push_notification("ExponentPushToken[oWADAWFAXFWADAWFAXFWADAWFAXFWADAWFAXCW]",
        #   
        #                               "test","test?")

        await kafka_service.send_message (
            KAFKA_MATCHES, str(post_id),
            {
                "user_id": user.id,
                "liked_user_id": liked_user_id,
                "status": "created"
            }
        )
    
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": f"Match {create_match} is created"})
    # await send_push_notification("ExponentPushToken[oWADAWFAXFWADAWFAXFWADAWFAXFWADAWFAXCW]",
    #                                     "test","test1?")
    await kafka_service.send_message(
        KAFKA_LIKES, str(post_id),
        {
            "user_id": user.id,
            "liked_user_id": liked_user_id,
            "status": "created"
        }
    )
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": f"Like {post_id} is created"})


@router.get("/likes/{id}")
async def get_like_by_id(id: int, repository: LikeRepository = Depends(LikeRepository.get_instance)) -> LikeModel:
    return await repository.find_by_id(id)
