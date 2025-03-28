from Backend.repositories.user_repository import UserRepository

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def add_user(self, name: str):
        user_id = self.user_repository.add_user(name)
        return user_id

    def get_user(self, user_id: str):
        return self.user_repository.get_user(user_id)

    def update_user(self, user_id: str, name: str):
        return self.user_repository.update_user(user_id, name)

    def delete_user(self, user_id: str):
        return self.user_repository.delete_user(user_id)
