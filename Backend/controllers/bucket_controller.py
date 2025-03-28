from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import timedelta
import os
from Backend.firebase_config import storage_client

bucket_router = APIRouter(prefix="/api/v1/bucket", tags=["Bucket"])



BUCKET_NAME = "receipt-photos-for-receipt-tracking-application"

@bucket_router.post("/upload_image/",tags=["bucket"])
async def upload_image(file: UploadFile = File(...), folder: str = None):
    try:
        if not folder:
            raise HTTPException(status_code=400, detail="Folder name is required.")

        if not folder.endswith("/"):
            folder += "/"

        file_location = f"temp_{file.filename}"

        with open(file_location, "wb") as f:
            f.write(await file.read())

        bucket = storage_client.bucket(BUCKET_NAME)

        # calea catre fisierul din bucket
        blob = bucket.blob(folder + file.filename)
        blob.upload_from_filename(file_location)

        public_url = blob.public_url

        os.remove(file_location)

        return {"filename": file.filename, "url": public_url}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to upload image: {e}")


@bucket_router.post("/create_folder_with_name/",tags=["bucket"])
async def create_folder_with_name(folder_name: str):
    try:
        if not folder_name.endswith("/"):
            folder_name += "/"

        bucket = storage_client.bucket(BUCKET_NAME)

        existing_blobs = list(bucket.list_blobs(prefix=folder_name, max_results=1))

        if existing_blobs:
            return {"message": f"Folder '{folder_name}' already exists."}

        blob = bucket.blob(folder_name)
        blob.upload_from_string("")  # Zero-byte pentru a simula folderul

        return {"message": f"Folder '{folder_name}' created successfully."}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create folder: {e}")


@bucket_router.get("/get_content_by_folder_name/",tags=["bucket"])
async def get_content_by_folder_name(folder_name: str):
    try:
        if not folder_name.endswith("/"):
            folder_name += "/"

        bucket = storage_client.bucket(BUCKET_NAME)
        blobs = bucket.list_blobs(prefix=folder_name)

        content_list = []

        for blob in blobs:
            if blob.name.endswith("/"):
                continue

            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=15),
                method="GET"
            )

            content_list.append({
                "file_name": blob.name.split("/")[-1],
                "url": url
            })

        return {"content": content_list}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get content: {e}")