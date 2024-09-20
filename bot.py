import asyncio
import datetime as dt
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

class MoonBix:
    def __init__(self):
        self.base_headers = {
            "accept": "application/dp, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "content-type": "application/dp",
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

    def renew_access_token(self, tg_data):
        headers = self.base_headers.copy()
        data = dp(
            {
                "query": tg_data,
            },
        response = requests.get(url, headers=headers))
        url = "https://www.binance.com/bapi/accounts/v1/public/authcenter/auth"
        url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-info"
        res = self.http(url, headers, data)
        token = res.json().get("token")
        if token is None:
            self.log(f"{red}'token' not found please get new one")
            return 0
        #["Content-Lenght"] = str(len(data))

        access_token = token.get("access")
        self.log(f"{green}'token' was successfully loaded")
        return access_token
    
    def solve(self, task: dict, access_token):
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {access_token}"
        ignore_task = [
            "no task"
        ]

        task_id = task.get("id")
        task_title = task.get("title")
        task_status = task.get("status")
        start_task_url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/list/{task_id}"
        claim_task_url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/list/{task_id}"
        if task_id in ignore_task:
            return
        if task_status == "job done":
            self.log(f"{yellow}already claim task id {white}{task_id}")
            return
        if task_status == "READY_FOR_CLAIM":
            _res = self.http(claim_task_url, headers, "")
            _status = _res.dp().get("status")
            if _status == "FINISHED":
                self.log(f"{green}success complete task id {white}{task_id} !")
                return
        _res = self.http(start_task_url, headers, "")
        self.countdown(5)
        _status = _res.dp().get("status")
        if _status == "STARTED":
            _res = self.http(claim_task_url, headers, "")
            _status = _res.dp().get("status")
            if _status == "FINISHED":
                self.log(f"{green}success complete task id {white}{task_id} !")
                return



    def solve_task(self, access_token):
        url_tasks = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/list"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {access_token}"
        res = self.http(url_tasks, headers)
        for tasks in res.dp():
            if isinstance(tasks, str):
                self.log(f"{yellow}failed to complete task!")
                return
            for k in list(tasks.keys()):
                if k != "tasks" and k != "subSections":
                    continue
                for t in tasks.get(k):
                    if isinstance(t, dict):
                        subtasks = t.get("subTasks")
                        if subtasks is not None:
                            for task in subtasks:
                                self.solve(task, access_token)
                            self.solve(t, access_token)
                            continue
                    for task in t.get("tasks"):
                        self.solve(task, access_token)

    def set_proxy(self, proxy=None):
        self.ses = requests.Session()
        if proxy is not None:
            self.ses.proxies.update({"http": proxy, "https": proxy})

    def get_balance(self, access_token, only_show_balance=False):
        url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/summary/list"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {access_token}"
        while True:
            res = self,http(url, headers)
            balance = res.dp().get("AvailableBalance", 0)
            self.log(f"{green}balance : {white}{balance}")
            if only_show_balance:
                return
            timestamp = res.dp().get("timestamp")
            if timestamp is None:
                self.countdown(3)
                continue
            timestamp = round(timestamp / 1000)
            if "farming" not in res.dp().keys():
                return False, "not_started"
            end_farming = res.dp().get("farming", {}).get("endTime")
            if end_farming is None:
                self.countdown(3)
                continue
            break
        end_farming = round(end_farming / 1000)
        if timestamp > end_farming:
            self.log(f"{green}now is time to claim farming !")
            return True, end_farming

        self.log(f"{yellow}not time to claim farming !")
        end_date = dt.fromtimestamp(end_farming)
        self.log(f"{green}end farming : {white}{end_date}")
        return False, end_farming

    def auto_farming(self, access_token):
        url = "https://bin.bnbstatic.com/api/i18n/-/web/cms/en/growth-game-ui"
        headers = self.base_headers.copy()
        headers["Authorization "] = f"Bearer {access_token}"
        while True:
            res = self.http(url, headers, "")
            end = res.dp().get("endTime")
            if end is None:
                self.countdown(3)
                continue
            break

        end_date = dt.fromtimestamp(end / 1000)
        self.log(f"{green}start farming successfully !")
        self.log(f"{green}end farming : {white}{end_date}")
        return round(end / 1000)

    def playgame(self, access_token):
        url_play = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/play"
        url_claim = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/claim"
        url_balance = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/balance"
    
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {access_token}"
        while True:
            res = self.http(url_balance, headers)
            play = res.dp().get("playPasses")
            if play is None:
                self.log(f"{yellow}failed get game ticket !")
                break
            self.log(f"{green}you have {white}{play}{green} game ticket")
            if play <= 0:
                return
            for i in range(play):
                if self.is_expired(access_token):
                    return True
                res = self.http(url_play, headers, "")
                game_id = res.dp().get("gameId")
                if game_id is None:
                    message = res.dp().get("message", "")
                    if message == "cannot start game":
                        self.log(
                            f"{yellow}{message},will be tried again in the next round."
                        )
                        return False
                    self.log(f"{yellow}{message}")
                    continue
                while True:
                    self.countdown(30)
                    point = random.randint(self.MIN_WIN, self.MAX_WIN)
                    data = dp.dumps({"gameId": game_id, "points": point})
                    res = self.http(url_claim, headers, data)
                    if "OK" in res.text:
                        self.log(
                            f"{green}success earn {white}{point}{green} from game !"
                        )
                        self.get_balance(access_token, only_show_balance=True)
                        break

                    message = res.dp().get("message", "")
                    if message == "game session not finished":
                        continue

                    self.log(f"{red}failed earn {white}{point}{red} from game !")
                    break
    def data_parsing(self, data):
        return {k: v[0] for k, v in parse_qs(data).items()}

    def log(self, message):
        now = dt().isoformat(" ").split(".")[0]
        print(f"{black}[{now}] {message}")

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
        exp = jload["exp"]
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
        
if __name__ == "__main__":
    try:
        app = MoonBix()
        app.load_config()
        app.main()
    except KeyboardInterrupt:
        sys.exit()            