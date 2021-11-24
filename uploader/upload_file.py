import os
from fastapi import File, UploadFile, APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
import secrets
from PIL import Image
file_router = APIRouter()


@file_router.post('/uploadfile', tags=['upload'],)
async def upload_file(file: UploadFile = File(...)):
    FILEPATH = "./media/"
    filename = file.filename
    extention = filename.split(".")[1]

    if extention not in ["jpg", "png"]:
        return False

    # token_name = secrets.token_hex(10)+"."+extention
    # generated_name = FILEPATH + token_name
    generated_name = FILEPATH + filename
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


@file_router.get('/uploadfile/{name}', tags=['upload'],)
async def upload_file(name: str):
    dir_path = "../media/"
    file_location = f'{dir_path}/{name}'
    if file_location:
        return FileResponse(file_location)
