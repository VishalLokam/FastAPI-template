from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from .auth import get_current_user, UserRequest
from .todos import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from models import Users
from passlib.context import CryptContext

router = APIRouter(prefix="/user", tags=["user"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# https://fastapi.tiangolo.com/tutorial/dependencies/#declare-the-dependency-in-the-dependant
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
### Dependecy injection


@router.get("/get_user", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="auth failed")
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_user_password(
    user: user_dependency, db: db_dependency, user_request: UserRequest
):
    if user is None:
        raise HTTPException(status_code=401, detail="auth failed")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    user_model.hashed_password = bcrypt_context.hash(user_request.password)

    user_model.email = user_model.email
    user_model.username = user_model.username
    user_model.first_name = user_model.first_name
    user_model.last_name = user_model.last_name
    user_model.is_active = user_model.is_active
    user_model.role = user_model.role

    db.add(user_model)
    db.commit()
