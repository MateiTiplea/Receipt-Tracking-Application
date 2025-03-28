from Backend.firebase_config import db


class UserRepository:
    def add_user(self, name: str):
        doc_ref = db.collection("users").document()
        doc_ref.set({
            "name": name
        })
        return doc_ref.id

    def get_user(self, user_id: str):
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    def update_user(self, user_id: str, name: str):
        doc_ref = db.collection("users").document(user_id)
        doc_ref.update({"name": name})
        return user_id

    def delete_user(self, user_id: str):
        doc_ref = db.collection("users").document(user_id)
        doc_ref.delete()
        return user_id
