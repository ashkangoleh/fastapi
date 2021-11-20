import requests

API_KEY = "25fa38601f534479b20317050ebe6f1c"

def GeoIpLocation(ip):
    # url = f"https://api.ipgeolocation.io/ipgeo?apiKey={API_KEY}&ip={ip}"
    url = f"http://ip-api.com/json/{ip}"
    response = requests.get(url).json()
    return response