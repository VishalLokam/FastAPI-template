from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path, HTTPException
from models import Todos
from database import SessionLocal
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user

router = APIRouter()


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


class TodosRequest(BaseModel):
    title: str = Field(min_length=3, max_length=20)
    description: str = Field(min_length=0, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="auth failed")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/todod/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="auth failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is not None and todo_model.owner_id == user.get("id"):
        return todo_model

    raise HTTPException(status_code=404, detail="todo not found.")


@router.post("/todo/create", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: user_dependency, db: db_dependency, todo_request: TodosRequest
):
    if user is None:
        raise HTTPException(status_code=401, detail="auth failed")

    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))

    db.add(todo_model)
    db.commit()


@router.put("/todo/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodosRequest,
    todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="auth failed")

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )

    if todo_model is not None:
        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.complete = todo_request.complete

        db.add(todo_model)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Todo not found")


@router.delete("/todo/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="auth failed")

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )

    if todo_model is not None:
        db.query(Todos).filter(Todos.id == todo_id).delete()
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
