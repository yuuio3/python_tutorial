from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Depends, Path
import models
from models import Todos
from starlette import status

from database import engine, SessionLocal

# from routers import auth, todos, admin, users

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# app.include_router(auth.router)
# app.include_router(todos.router)
# app.include_router(admin.router)
# app.include_router(users.router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="not found")


@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def post_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()
