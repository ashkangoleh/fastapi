from typing import Any, List, Optional, Dict
from fastapi import APIRouter, status, Depends
import json
import asyncio
from fastapi import Request, Body, Query
from fastapi.exceptions import HTTPException
from fastapi import WebSocket
from fastapi_jwt_auth import AuthJWT
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocketClose, WebSocketDisconnect
from fastapi_jwt_auth.exceptions import AuthJWTException
from .coin_api import (
    coinAPI,
    COIN_URL,
    COIN_PASSWORD,
    TIME_FRAME_LIST
)
from utils.cbv import ClassBased

ws = APIRouter()
wrapper = ClassBased(ws)


@ws.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """websocket to get coin pairs

    Args:
        websocket (WebSocket): websocket.receive_json =>{
                                                            "start":boolean,  // if true means start connection , false stop connection
                                                            "time_frame":int, // time frame 5 15 30 4h ...
                                                            "data":{
                                                                "exchange":str  // exchange name
                                                            }

                                                        }
    """
    await websocket.accept()
    while 1:
        message= await websocket.receive_json()
        if message['start']:
            if message['time_frame'] in TIME_FRAME_LIST:
                try:
                    await asyncio.sleep(message['time_frame']*60)
                    payload = coinAPI(
                        url=COIN_URL, password=COIN_PASSWORD, time_frame=message['time_frame'], exchange=message['data']['exchange'])
                    await websocket.send_json(payload)

                except WebSocketDisconnect:
                    await websocket.send_json({
                        'status': 'fail',
                        'message': 'websocket disconnected'
                    })
            else:
                await websocket.send_json({
                    'status': 'fail',
                    'message': 'time_frame incorrect'
                })
        else:
            await websocket.send_json({
                'status': 'fail',
                'message': 'websocket closed'
            })
    

@ws.get('/redirect',response_class=RedirectResponse,status_code=302)
async def redirect_url():
    return "https://devsteam.ir/"

# class based (1 route multiple methods)
@wrapper('/item')
class Item:
    def get():
        return {"item_id": "q"}

    def post():
        return {"item_name":1}
# get cookie by default
# @ws.get('/get-cookie')
# def get_cookie(Authorize: AuthJWT = Depends()):
#     access_token = Authorize.create_access_token(subject='a',fresh=True)
#     refresh_token = Authorize.create_refresh_token(subject='a')

#     Authorize.set_access_cookies(access_token)
#     Authorize.set_refresh_cookies(refresh_token)
#     return {"msg":"Successfully login"}
