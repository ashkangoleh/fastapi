from datetime import datetime
from fastapi import APIRouter, Request,Header,Response
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import os
from pathlib import Path
from fastapi.templating import Jinja2Templates
import threading   
app_view = APIRouter()

TEMPLATES = Jinja2Templates(directory="templates")
CHUNK_SIZE = 1024*1024
video_path = Path(os.path.dirname(os.path.dirname(__file__))+'/static/video.mp4')

@app_view.get("/")
async def read_index(request: Request):
    context = {
        "request":request,
        "title":"None Api route",
        "overview": "this is jinja2 test for fastapi",
    }
    return TEMPLATES.TemplateResponse("index.html", context=context)

@app_view.get("/video")
async def video_endpoint(range: str = Header(None)):
    start, end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else start + CHUNK_SIZE
    with open(video_path, "rb") as video:
        video.seek(start)
        data = video.read(end - start)
        filesize = str(video_path.stat().st_size)
        headers = {
            'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
            'Accept-Ranges': 'bytes'
        }
        return Response(data, status_code=206, headers=headers, media_type="video/mp4")
    
    
import datetime
counter = 0
lock = threading.Lock()
_2min = datetime.datetime.now()+datetime.timedelta(seconds=3)
@app_view.get("/test")
def do_something():
    global counter
    global _2min
    now = datetime.datetime.now()
    try:
        with lock:
            counter += 1
            if counter >= 3:
                raise HTTPException(
                    status_code=400,
                    detail="stop spam"
                )
    except Exception as e:
        if now > _2min:
             counter = 0
        raise HTTPException(
            status_code=400
        )
    return {"message": "Hello World"}