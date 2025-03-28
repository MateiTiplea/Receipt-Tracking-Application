from fastapi import APIRouter, HTTPException, UploadFile, File
from Backend.models.user import UserBase
from Backend.services.user_service import UserService

user_router = APIRouter()

user_service = UserService()

@user_router.post("/api/v1/users/")
async def add_user(user: UserBase):
    user_id = user_service.add_user(user.name)
    return {"user_id": user_id}

@user_router.get("/users/{user_id}")
async def get_user(user_id: str):
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.put("/users/{user_id}")
async def update_user(user_id: str, user: UserBase):
    updated_user_id = user_service.update_user(user_id, user.name)
    if not updated_user_id:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": updated_user_id, "name": user.name}

@user_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    deleted_user_id = user_service.delete_user(user_id)
    if not deleted_user_id:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": deleted_user_id}


