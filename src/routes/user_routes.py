from fastapi import APIRouter, Path
from src.controllers.user_controller import UserController, CreateUserRequest, LoginRequest

router = APIRouter()

@router.post("/users", status_code=201)
def create_user(body: CreateUserRequest):
    return UserController.create_user(body)

@router.get("/users/{username}")
def get_user(username: str = Path(...)):
    return UserController.get_user(username)

@router.post("/users/login")
def login(body: LoginRequest):
    return UserController.login(body)

@router.put("/users/{username}")
def update_user(username: str = Path(...)):
    return UserController.update_user(username)
