from fastapi import (
    APIRouter,
    Depends,
    Query,
    Header,
    WebSocket
    )
import asyncio
from fastapi_jwt_auth import AuthJWT
from starlette import websockets
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocketClose, WebSocketDisconnect
from starlette import websockets
from fastapi_jwt_auth.exceptions import AuthJWTException
from .coin_api import (
    coinAPI,
    COIN_URL,
    COIN_PASSWORD,
    TIME_FRAME_LIST
)
from utils import CBV

ws = APIRouter(
    tags=['Websocket']
)
wrapper = CBV(ws)


@ws.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Header(...) ,Authorize: AuthJWT = Depends()):
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
    try:
        Authorize.jwt_required("websocket", token=token)
    except AuthJWTException as err:
        await websocket.send_json({
            'status': 'fail',
            'detail': err.message,
            'message': 'invalid token',

        })
        await websocket.close()
    while websocket.application_state == websockets.WebSocketState.CONNECTED:
        message = await websocket.receive_json()
        if message['start']:
            if message['time_frame'] in TIME_FRAME_LIST:
                try:
                    # await asyncio.sleep(message['time_frame']*60)
                    await asyncio.sleep(1)
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
            await websocket.close()
        


@ws.get('/redirect', response_class=RedirectResponse, status_code=302)
async def redirect_url():
    return "https://devsteam.ir/"

# class based (1 route multiple methods)


@wrapper('/item')
class Item:
    def get():
        return {"item_id": "q"}

    def post():
        return {"item_name": 1}
# get cookie by default
# @ws.get('/get-cookie')
# def get_cookie(Authorize: AuthJWT = Depends()):
#     access_token = Authorize.create_access_token(subject='a',fresh=True)
#     refresh_token = Authorize.create_refresh_token(subject='a')

#     Authorize.set_access_cookies(access_token)
#     Authorize.set_refresh_cookies(refresh_token)
#     return {"msg":"Successfully login"}
