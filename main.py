from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now()

start_date = os.environ.get('START_DATE', '2024-06-06')  # 设置默认值
city = os.environ.get('CITY', '长春')
birthday = os.environ.get('BIRTHDAY', '01-02')

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
    url = f"http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city={city}"
    try:
        res = requests.get(url).json()
        weather = res['data']['list'][0]
        return weather['weather'], math.floor(weather['temp'])
    except (KeyError, IndexError, requests.exceptions.RequestException) as e:
        print(f"Error fetching weather data: {e}")
        return None, None

def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days

def get_birthday():
    next_birthday = datetime.strptime(f"{date.today().year}-{birthday}", "%Y-%m-%d")
    if next_birthday < today:
        next_birthday = next_birthday.replace(year=next_birthday.year + 1)
    return (next_birthday - today).days

def get_words():
    while True:
        words = requests.get("https://api.shadiao.pro/chp")
        if words.status_code == 200:
            return words.json()['data']['text']
        print("Failed to get words, retrying...")

def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)

wea, temperature = get_weather()
data = {
    "weather": {"value": wea},
    "temperature": {"value": temperature},
    "love_days": {"value": get_count()},
    "birthday_left": {"value": get_birthday()},
    "words": {"value": get_words(), "color": get_random_color()}
}

try:
    res = wm.send_template(user_id, template_id, data)
    print(res)
except Exception as e:
    print(f"Error sending template message: {e}")
