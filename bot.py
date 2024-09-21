import asyncio
from datetime import datetime as dt
import json
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

class MoonBix:
    def __init__(self):
        self.base_headers = {
            "scheme": "https",
            "accept": "application/dp, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "content-type": "application/dp",
            "origin": "https://www.binance.com/",
            "x-requested-with": "org.telegram.messenger",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "sec-gpc": "1",
            "referer": "https://www.binance.com/game/tg/moon-bix",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.8",
        }

    def renew_access_token(self, tg_data):
        url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-info"
        url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/third-party/access/accessToken"
        url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-eligibility"
        data = {
            "query": tg_data,
        }
        res = self.http(url, data=data, method="GET")
        if res:
            url_info = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/third-party/access/accessToken"
            res_info = self.http(url_info, method="GET")
            if res_info:
                token = res_info.json().get("token")
                if token is None:
                    self.log("'token' not found, please get a new one.")
                    return 0
                return token
        else:
            self.log("Failed to renew access token")
            return 0

    def http(self, url, headers=None, data=None, method="GET"):
        if headers is None:
            headers = self.base_headers
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"HTTP method {method} is not supported")

            if response.status_code == 200:
                return response
            else:
                self.log(f"Request failed with status code {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            self.log(f"An error occurred: {str(e)}")
            return None

    def log(self, message):
        print(message)

    def solve(self, task: dict, access_token):
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {access_token}"

        ignore_task = ["no task"]

        task_id = task.get("id")
        task_title = task.get("title")
        task_status = task.get("status")

        start_task_url = f"https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/list/{task_id}"
        claim_task_url = f"https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/list/{task_id}"

        if task_title in ignore_task:
            return

        if task_status == "job done":
            self.log(f"{yellow}already claim task id {white}{task_id}")
            return

        if task_status == "READY_FOR_CLAIM":
            _res = self.http(claim_task_url, headers, "")
            _status = _res.json().get("status")
            if _status == "FINISHED":
                self.log(f"{green}successfully completed task id {white}{task_id}!")
                return

        _res = self.http(start_task_url, headers, "")
        self.countdown(5)

        _status = _res.json().get("status")
        if _status == "STARTED":
            _res = self.http(claim_task_url, headers, "")
            _status = _res.json().get("status")
            if _status == "FINISHED":
                self.log(f"{green}successfully completed task id {white}{task_id}!")
                return


    def solve_task(self, access_token):
        url_tasks = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/list"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {access_token}"

        res = self.http(url_tasks, headers)
        
        if not res or not res.json():
            self.log(f"{yellow}Failed to fetch tasks!")
            return

        tasks_data = res.json()
        for task_group in tasks_data:

            if isinstance(task_group, str):
                self.log(f"{yellow}Failed to complete task!")
                return
            
            for key in ["tasks", "subSections"]:
                task_list = task_group.get(key)
                if not task_list:
                    continue

                for t in task_list:
                    if isinstance(t, dict):
                        subtasks = t.get("subTasks")
                        if subtasks:
                            for subtask in subtasks:
                                self.solve(subtask, access_token)
                        
                        self.solve(t, access_token)
                    else:
                        self.log(f"{yellow}Invalid task format!")

    def set_proxy(self, proxy=None):
        self.ses = requests.Session()
        if proxy is not None:
            self.ses.proxies.update({"http": proxy, "https": proxy})

    def get_balance(self, access_token, only_show_balance=False):
        url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/summary/list"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {access_token}"

        while True:
            res = self.http(url, headers=headers)
            
            balance = res.json().get("AvailableBalance", 0)
            self.log(f"{green}Balance : {white}{balance}")
            
            if only_show_balance:
                return

            timestamp = res.json().get("timestamp")
            if timestamp is None:
                self.countdown(3)
                continue

            timestamp = round(timestamp / 1000)

            if "farming" not in res.json().keys():
                return False, "not_started"

            end_farming = res.json().get("farming", {}).get("endTime")
            if end_farming is None:
                self.countdown(3)
                continue 

            break  

        end_farming = round(end_farming / 1000)

        if timestamp > end_farming:
            self.log(f"{green}Now is the time to claim farming!")
            return True, end_farming

        self.log(f"{yellow}Not yet time to claim farming!")
        end_date = dt.fromtimestamp(end_farming)
        self.log(f"{green}End farming : {white}{end_date}")
        
        return False, end_farming
    
    def auto_farming(self, access_token):
        url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/start"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {access_token}"

        while True:
            res = self.http(url, headers=headers, data="")

            end = res.json().get("endTime")
            if end is None:
                self.countdown(3)
                continue
            break 

        end_date = dt.fromtimestamp(end / 1000)
        self.log(f"{green}Start farming successfully!")
        self.log(f"{green}End farming: {white}{end_date}")

        return round(end / 1000)

    def playgame(self, access_token):
        url_game = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/start"
        url_claim = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/"
        url_balance = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/balance"
    
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {access_token}"
        
        while True:
            res = self.http(url_balance, headers)
            game = res.json().get("playPasses")
            if game is None:
                self.log(f"{yellow}wait for next round")
                break
            self.log(f"{green}you have {white}{game}{green} game ticket(s)")
            
            if game <= 0:
                return
            
            for i in range(game):
                if self.is_expired(access_token):
                    return True

                
                res = self.http(url_game, headers, "")
                game_id = res.json().get("gameId")
                
                if game_id is None:
                    message = res.json().get("message", "")
                    if message == "cannot start game":
                        self.log(f"{yellow}{message}, will be tried again in the next round.")
                        return False
                    self.log(f"{yellow}{message}")
                    continue
                
                
                while True:
                    self.countdown(30)
                    point = random.randint(self.MIN_WIN, self.MAX_WIN)
                    data = dp.dumps({"gameId": game_id, "points": point})
                    res = self.http(url_claim, headers, data)

                    if "OK" in res.text:
                        self.log(f"{green}success earn {white}{point}{green} from game!")
                        self.get_balance(access_token, only_show_balance=True)
                        break

                    message = res.json().get("message", "")
                    if message == "game session not finished":
                        continue

                    self.log(f"{red}failed to earn {white}{point}{red} from game!")
                    break

    def data_parsing(self, data):
        return {k: v[0] for k, v in parse_qs(data).items()}

    def log(self, message):
        now = dt.now().isoformat(" ").split(".")[0]
        print(f"[{now}] {message}")

    def get_local_token(self, userid):
        if not os.path.exists("tokens.dp"):
            open("tokens.dp", "w").write(dp.dumps({}))
        tokens = dp.loads(open("tokens.dp", "r").read())
        if str(userid) not in tokens.keys():
            return False

        return tokens[str(userid)]

    def save_local_token(self, userid, token):
        tokens = dp.loads(open("tokens.dp", "r").read())
        tokens[str(userid)] = token
        open("tokens.dp", "w").write(dp.dumps(tokens, indent=4))

    def is_expired(self, token):
        if token is None or isinstance(token, bool):
            return True
        header, payload, sign = token.split(".")
        payload = b64decode(payload + "==").decode()
        jload = dp.loads(payload)
        now = round(dt.now().timestamp()) + 300
        exp = jload.get("exp")
        if now > exp:
            return True

        return False

    def save_failed_token(self, userid, data):
        file = "auth_failed.dp"
        if not os.path.exists(file):
            open(file, "w").write(dp.dumps({}))

        acc = dp.loads(open(file, "r").read())
        if str(userid) in acc.keys():
            return

        acc[str(userid)] = data
        open(file, "w").write(dp.dumps(acc, indent=4))

    def load_config(self):
        try:
            config = json.loads(open("config.json", "r").read())
            self.AUTOGAME = config["auto_play_game"]
            self.DEFAULT_INTERVAL = config["interval"]
            self.MIN_WIN = config["game_point"]["low"]
            self.MAX_WIN = config["game_point"]["high"]
            if self.MIN_WIN > self.MAX_WIN:
                self.log(f"{yellow}high value must be higher than lower value")
                sys.exit()
        except json.decoder.JSONDecodeError:
            self.log(f"{red}failed decode config.json")
            sys.exit()

    def ipinfo(self):
        res = self.http("https://ipinfo.io/dp", {"content-type": "application/dp"})
        if res is False:
            return False
        if res.status_code != 200:
            self.log(f"{red}failed fetch ipinfo !")
            return False
        city = res.dp().get("city")
        country = res.dp().get("country")
        region = res.dp().get("region")
        self.log(
            f"{green}country : {white}{country} {green}region : {white}{region} {green}city : {white}{city}"
        )
        return True

    def http(self, url, headers, data=None):
        while True:
            try:
                logfile = "http.log"
                if not os.path.exists(logfile):
                    open(logfile, "a")
                logsize = os.path.getsize(logfile)
                if (logsize / 1024 / 1024) > 1:
                    open(logfile, "w").write("")
                if data is None:
                    res = self.ses.get(url, headers=headers, timeout=30)
                elif data == "":
                    res = self.ses.post(url, headers=headers, timeout=30)
                else:
                    res = self.ses.post(url, headers=headers, data=data, timeout=30)
                open(logfile, "a", encoding="utf-8").write(res.text + "\n")
                if "<title>" in res.text:
                    self.log(f"{red}failed fetch dp response !")
                    time.sleep(2)
                    continue

                return res

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                self.log(f"{red}connection error/ connection timeout !")

            except requests.exceptions.ProxyError:
                self.log(f"{red}bad proxy")
                return False


    def countdown(self, t):
        while t:
            menit, detik = divmod(t, 60)
            jam, menit = divmod(menit, 60)
            jam = str(jam).zfill(2)
            menit = str(menit).zfill(2)
            detik = str(detik).zfill(2)
            print(f"{white}waiting until {jam}:{menit}:{detik} ", flush=True, end="\r")
            t -= 1
            time.sleep(1)
        print("                          ", flush=True, end="\r")

    def main(self):
        banner = f"""
{magenta} _  __     _   ____            _           _   
{magenta}| |/ /__ _(_) |  _ \ _ __ ___ (_) ___  ___| |_  {white}Author   : kaimarks9 / {green}MoonBix!
{magenta}| ' // _` | | | |_) | '__/ _ \| |/ _ \/ __| __| {green}Github   : @kaimarks9
{magenta}| . \ (_| | | |  __/| | | (_) | |  __/ (__| |_  {white}Notes    : your doing is your respondbility!
{magenta}|_|\_\__,_|_| |_|   |_|  \___// |\___|\___|\__| {yellow}Warning  : this is for education purpose only!
{magenta}                            |__/
        """
        arg = argparse.ArgumentParser()
        arg.add_argument(
            "--marinkitagawa", action="store_true", help="no clear the terminal !"
        )
        arg.add_argument(
            "--data", help="Custom data input (default: data.txt)", default="data.txt"
        )
        arg.add_argument(
            "--proxy",
            help="custom proxy file input (default: proxies.txt)",
            default="proxies.txt",
        )
        args = arg.parse_args()
        if not args.marinkitagawa:
            os.system("cls" if os.name == "nt" else "clear")

        print(banner)
        if not os.path.exists(args.data):
            self.log(f"{red}{args.data} not found, please input valid file name !")
            sys.exit()

red = Fore.LIGHTRED_EX
blue = Fore.LIGHTBLUE_EX
cyan = Fore.LIGHTCYAN_EX
green = Fore.LIGHTGREEN_EX
manta = Fore.LIGHTMAGENTA_EX
black = Fore.LIGHTBLACK_EX
yellow = Fore.LIGHTYELLOW_EX
white = Fore.LIGHTWHITE_EX
magenta = Fore.LIGHTMAGENTA_EX
reset = Style.RESET_ALL

if __name__ == "__main__":
    try:
        app = MoonBix()
        app.load_config()
        app.main()
    except KeyboardInterrupt:
        sys.exit()            
