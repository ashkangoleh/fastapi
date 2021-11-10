from fastapi import APIRouter, status, Depends
import json
import asyncio
from fastapi import Request
from fastapi import WebSocket


ws = APIRouter()

@ws.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await asyncio.sleep(1)
        payload = "this is test"
        await websocket.send_json(payload)
    await websocket.close()