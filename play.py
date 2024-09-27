from datetime import datetime
import os, requests, time, crayons, json, threading
import urllib.parse
from banner import *


def is_url_encoded(url):
    decoded_url = urllib.parse.unquote(url)
    reencoded_url = urllib.parse.quote(decoded_url)
    return reencoded_url == url



def url_decode(encoded_url):
    return urllib.parse.unquote(encoded_url)


def log(message, level="INFO"):
    levels = {
        "INFO": crayons.cyan,
        "ERROR": crayons.red,
        "SUCCESS": crayons.green,
        "WARNING": crayons.yellow
    }
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{crayons.white(current_time)} | {levels.get(level, crayons.cyan)(level)} | {message}")

class MoonBix:
    def __init__(self, token, proxy=None):
        self.session = requests.session()
        self.session.headers.update({
            'authority': 'www.binance.info',
            'accept': '*/*',
            'accept-language': 'en-EG,en;q=0.9,ar-EG;q=0.8,ar;q=0.7,en-GB;q=0.6,en-US;q=0.5',
            'clienttype': 'web',
            'content-type': 'application/json',
            'lang': 'en',
            'origin': 'https://www.binance.info',
            'referer': 'https://www.binance.info/en/game/tg/moon-bix',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        })
        
        if proxy:
            self.session.proxies.update({'http': proxy, 'https': proxy})

        self.token = token
        self.game_response = None
        self.task = None

    def login(self):
        try:
            response = self.session.post(
                'https://www.binance.info/bapi/growth/v1/friendly/growth-paas/third-party/access/accessToken',
                json={'queryString': self.token, 'socialType': 'telegram'},
            )
            if response.status_code == 200:
                self.session.headers['x-growth-token'] = response.json()['data']['accessToken']
                log("Logged in successfully!", level="SUCCESS")
                return True
            else:
                log("Failed to login", level="ERROR")
                return False
        except Exception as e:
            log(f"Error during login: {e}", level="ERROR")

    def user_info(self):
        try:
            response = self.session.post(
                'https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-info',
                json={'resourceId': 2056},
            )
            return response.json()
        
        except Exception as e:
            log(f"Error during get info: {e}", level="ERROR")

    def game_data(self):
        try:
            while True:
                responses = requests.post('https://app.winsnip.xyz/play', json=self.game_response).text
                try:
                    response = json.loads(responses)
                except json.JSONDecodeError:
                    continue
                if response['message'] == 'success' and response['game']['log'] >= 100:
                    self.game = response['game']
                    return True
        except Exception as e:
            log(f"Error getting game data: {e}", level="ERROR")

            
    def solve_task(self):
        try:
            res = self.session.post("https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/list",json={"resourceId": 2056})
            if not res or not res.json():
                log(f"Failed to fetch tasks!", level="ERROR")
                return
            tasks_datas = res.json()
            tasks_data = tasks_datas["data"]["data"][0]["taskList"]["data"]
            resource_ids = [entry['resourceId'] for entry in tasks_data
                    if entry['status'] != 'COMPLETED' and entry['type'] != 'THIRD_PARTY_BIND']
            for idx, resource_id in enumerate(resource_ids, start=1):
                ress = self.session.post("https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/complete", json={"resourceIdList": [resource_id], "referralCode": None}).json()
                if(ress["code"] == "000000"):
                    log(f"Succes complete task id {resource_id}", level="SUCCESS")
                else:
                    log(f"Failed complete task id {resource_id}", level="ERROR")
            return True
        except Exception as e:
            log(f"Error completing tasks: {e}", level="ERROR")



    def set_proxy(self, proxy=None):
        self.ses = requests.Session()
        if proxy is not None:
            self.ses.proxies.update({"http": proxy, "https": proxy})


    def complete_game(self):
        try:
            response = self.session.post(
                'https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/complete',
                json={'resourceId': 2056, 'payload': self.game['payload'], 'log': self.game['log']},
            )
            if response.json()['success']:
                log(f"Game completed! Earned + {self.game['log']}", level="SUCCESS")
            return response.json()['success']
        except Exception as e:
            log(f"Error during complete game: {e}", level="ERROR")

    def start_game(self):
        try:
            while True:
                response = self.session.post(
                    'https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/start',
                    json={'resourceId': 2056},
                )
                self.game_response = response.json()
                if self.game_response['code'] == '000000':
                    log("Game started successfully!", level="INFO")
                    return True
                elif self.game_response['code'] == '116002':
                    log('Attempts not enough! Switching to the next account.', level="WARNING")
                    return False
                log("ERROR! Cannot start game.", level="ERROR")
                return False
        except Exception as e:
            log(f"Error during start game: {e}", level="ERROR")

    def start(self):
        if not self.login():
            log("Login failed.", level="ERROR")
            return
        if not self.user_info():
            log("Failed to get user data.", level="ERROR")
            return
        if not self.solve_task():
            log("Failed to solve task.", level="ERROR")
            return
        while self.start_game():
            if not self.game_data():
                log("Failed to generate game data!", level="ERROR")
                return
            sleep(45)
            if not self.complete_game():
                log("Failed to complete game", level="ERROR")
            sleep(15)

def sleep(seconds):
    while seconds > 0:
        time_str = time.strftime('%H:%M:%S', time.gmtime(seconds))
        time.sleep(1)
        seconds -= 1
        print(f'\rWaiting {time_str}', end='', flush=True)
    print()

def run_account(index, token, proxy=None):
    if(is_url_encoded(token)):
        tokens = url_decode(token)
    else:
        tokens = token
    log(f"=== Account {index} ===", level="INFO")
    x = MoonBix(tokens, proxy)
    x.start()
    log(f"=== Account {index} Done ===", level="SUCCESS")
    sleep(10)

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    print(banner)
    
    proxies = [line.strip() for line in open('proxy.txt') if line.strip()]
    tokens = [line.strip() for line in open('data.txt')]

    threads = []
    
    log("==== Starting ===", level="INFO")
    while True:
        for index, token in enumerate(tokens, start=1):
            proxy = proxies[(index - 1) % len(proxies)] if proxies else None
            t = threading.Thread(target=run_account, args=(index, token, proxy))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        log("All accounts have been completed.", level="SUCCESS")
        sleep(2000)
