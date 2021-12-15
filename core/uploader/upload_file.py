from fastapi import File, UploadFile, APIRouter, Depends, Security
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from db import AuthHandler
from db.schema.auth_schema import get_current_user
from PIL import Image
import os
file_router = APIRouter()


@file_router.post('/profile_image', tags=['upload'])
async def upload_file(file: UploadFile = File(...), current_user:Security=Depends(get_current_user)):
    FILEPATH = "./media/profile_image/"
    filename = file.filename
    extention = filename.split(".")[1]

    if extention not in ["jpg", "png"]:
        return False

    user_id = current_user['id']
    generated_name = FILEPATH + f"{user_id}.{extention}"
    file_content = await file.read()
    if not os.path.exists(generated_name):
        with open(generated_name, "wb") as file_object:
            file_object.write(file_content)

        img = Image.open(generated_name)
        img = img.resize(size=(200, 200))
        img.save(generated_name)

        file_object.close()
        return FileResponse(generated_name)
    else:
        raise HTTPException(
            status_code=404,
            detail="file already exists"
        )


