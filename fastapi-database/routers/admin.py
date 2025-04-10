from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path, HTTPException
from models import Todos
from database import SessionLocal
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


### Dependecy injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# https://fastapi.tiangolo.com/tutorial/dependencies/#declare-the-dependency-in-the-dependant
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
### Dependecy injection


@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "admin":
        print(user.get("role"))
        raise HTTPException(status_code=401, detail="auth failed")

    return db.query(Todos).all()
