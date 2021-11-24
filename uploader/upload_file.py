from fastapi import File, UploadFile, APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from utils import AuthHandler
from PIL import Image
import os
file_router = APIRouter()


@file_router.post('/profile_image', tags=['upload'])
async def upload_file(file: UploadFile = File(...), _user=Depends(AuthHandler.Token_requirement)):
    FILEPATH = "./media/profile_image/"
    filename = file.filename
    extention = filename.split(".")[1]

    if extention not in ["jpg", "png"]:
        return False

    user_id = _user.get_raw_jwt()['detail']['id']
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


