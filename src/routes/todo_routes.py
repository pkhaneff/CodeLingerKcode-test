from fastapi import APIRouter, Path, Query
from typing import Optional
from src.controllers.todo_controller import TodoController, CreateTodoRequest, UpdateTodoRequest

router = APIRouter()

@router.get("/todos")
def get_todos(q: Optional[str] = Query(None), completed: Optional[str] = Query(None)):
    return TodoController.get_todos(q, completed)

@router.get("/todos/{id}")
def get_todo_by_id(id: int = Path(...)):
    return TodoController.get_todo_by_id(id)

@router.post("/todos", status_code=201)
def create_todo(body: CreateTodoRequest):
    return TodoController.create_todo(body)

@router.put("/todos/{id}")
def update_todo(id: int = Path(...), body: Optional[UpdateTodoRequest] = None):
    return TodoController.update_todo(id, body or UpdateTodoRequest())

@router.delete("/todos/{id}")
def delete_todo(id: int = Path(...)):
    return TodoController.delete_todo(id)
