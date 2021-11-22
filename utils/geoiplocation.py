import requests
from fastapi import APIRouter, status, Depends, Body, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
API_KEY = "25fa38601f534479b20317050ebe6f1c"

async def GeoIpLocation(ip):
    url = f"http://ip-api.com/json/{ip}"
    response = requests.get(url).json()
    if not response:
        return False
    return response
