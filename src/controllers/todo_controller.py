from fastapi import HTTPException, status
from typing import Optional
from pydantic import BaseModel
from src.models.todo_model import TodoModel

class CreateTodoRequest(BaseModel):
    title: str
    completed: Optional[bool] = False

class UpdateTodoRequest(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None

class TodoController:
    @staticmethod
    def get_todos(q: Optional[str] = None, completed: Optional[str] = None):
        return TodoModel.get_all(q, completed)

    @staticmethod
    def get_todo_by_id(id: int):
        todo = TodoModel.get_by_id(id)
        if not todo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
        return todo

    @staticmethod
    def create_todo(body: CreateTodoRequest):
        if not body.title:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title is required")
        return TodoModel.create(body.title, body.completed)

    @staticmethod
    def update_todo(id: int, body: UpdateTodoRequest):
        updated = TodoModel.update(id, body.title, body.completed)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
        return updated

    @staticmethod
    def delete_todo(id: int):
        deleted = TodoModel.delete(id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
        return {"message": "Todo deleted successfully", "deletedTodo": deleted}
