from typing import Union

from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette import status

class SuccessResponse(BaseModel):
    detail: str
    additional_info: Union[str, None] = None

def SuccessfulReceiptToken(token: str):
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"detail": token}
    )


def SuccessfulСodeSubmission():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "Check confirmation code"}
    )


def CorrectСonfirmationСode():
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"detail": "Correct confirmation Сode"}
    )

def SuccessfulUserAdd():
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"detail": "User created"}
    )




