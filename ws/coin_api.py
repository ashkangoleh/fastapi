import requests
from decouple import config as env

COIN_URL = env("COIN_API")
COIN_PASSWORD = env("COIN_API_PWD")
TIME_FRAME_LIST= [5,15,30,60,120,240,360,720,1440,10080]


def coinAPI(url, password, time_frame, exchange):
    params = {
        "password": password,
        "time_frame": time_frame,
        "exchange": exchange,
        "marketType": "spot"
    }
    res = requests.get(url, params=params)
    response = res.json()
    pairs = {}
    for i in response:
        pairs[i['symbol']] = i['buy']
    return pairs
