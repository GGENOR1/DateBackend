from fastapi import HTTPException, status

UserAlreadyExistsException = HTTPException (
    status_code=status.HTTP_409_CONFLICT,
    detail="The user already exists"
)

IncorrectEmailOrPassException = HTTPException (
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid email or password"
)

InvalidСonfirmationСode = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail="Invalid Сonfirmation Сode"
)

InvalidUserVailabilityUser = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The user not exists"
)

InvalidSendingConfirmation = HTTPException(
    status_code=status.HTTP_412_PRECONDITION_FAILED,
    detail="Error in sending the confirmation code"
)
#Ошибки на стороне сервера

InternalErrorRedisServer = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal error of the Redis server when sending the code"
)
InternalErrorSendingConfirmation = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal error in sending the confirmation code"
)
InternalErrorAdded = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal error adding a user"
)

