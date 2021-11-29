from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse

from fastapi.templating import Jinja2Templates
app_view = APIRouter()

TEMPLATES = Jinja2Templates(directory="templates")


@app_view.get("/")
async def read_index(request: Request):
    context = {
        "request":request,
        "title":"None Api route",
        "overview": "this is jinja2 test for fastapi",
    }
    return TEMPLATES.TemplateResponse("index.html", context=context)
