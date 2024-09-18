import asyncio
import datetime as dt
import random
import http
import argparse
import requests
import requests_html
from json import dump as dp, loads as ld
from colorama import *
from base64 import b64decode
import os
import time
import sys
from urllib.parse import unquote, parse_qs

init(autoreset=True)

red = Fore.LIGHTRED_EX
blue = Fore.LIGHTBLUE_EX
cyan = Fore.LIGHTCYAN_EX
green = Fore.LIGHTGREEN_EX
manta = Fore.LIGHTMAGENTA_EX
black = Fore.LIGHTBLACK_EX
yellow = Fore.LIGHTYELLOW_EX
white = Fore.LIGHTWHITE_EX

class MoonBix:
    def __init__(self):
        self.base_headers = {
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            "content-type": "application/json",
            "origin": "https://www.binance.com/game/tg/moon-bix",
            "x-requested-with": "org.telegram.messenger",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.binance.com/game/tg/moon-bix",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en,en-US;q=0.9",
        }
        self.line = white + "~" * 50

    def renew_access_token(self,tg_data):
        headers = self.base_headers.copy()
        data = dp(
            {
                "query": tg_data,
            },
        )
        headers["Content-Lenght"] = str(len(data))
        url = "https://www.binance.com/game/tg/moon-bix"
        res = self.http(url, headers, data)
        token = res.json().get("token")
        if token is None:
            self.log(f"{red}'token' not found please get new one")
            return 0
        
        access_token = token.get("access")
        self.log(f"{green}'token' was successfully loaded")
        return access_token
    
    def solve(self, task: dict, access_token):
        headers = self.base_headers.copy()
        headers["authorization"] = f"Bearer {access_token}"
        ignore_task = [
            "no task"
        ]
