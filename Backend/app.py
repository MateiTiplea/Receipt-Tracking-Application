from fastapi import FastAPI
from Backend.controllers.user_controller import user_router
from Backend.controllers.bucket_controller import bucket_router
from Backend.controllers.receipt_controller import receipt_router


app = FastAPI()

print("Inregistrarea routerelor...")
app.include_router(user_router)
app.include_router(bucket_router)
app.include_router(receipt_router)
print("Routerele au fost înregistrate!")

