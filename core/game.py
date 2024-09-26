import requests
import time

from smart_airdrop_claimer import base
from core.headers import headers
from core.info import get_info
from core.comb import get_game_data


def start_game(token, proxies=None):
    url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/start"
    payload = {"resourceId": 2056}

    try:
        response = requests.post(
            url=url,
            headers=headers(token=token),
            json=payload,
            proxies=proxies,
            timeout=20,
        )
        data = response.json()
        return data
    except:
        return None


def complete_game(token, payload, point, proxies=None):
    url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/complete"
    payload = {
        "resourceId": 2056,
        "payload": payload,
        "log": point,
    }

    try:
        response = requests.post(
            url=url,
            headers=headers(token=token),
            json=payload,
            proxies=proxies,
            timeout=20,
        )
        data = response.json()
        status = data["success"]
        return status
    except:
        return None


def process_play_game(token, proxies=None):
    while True:
        start_game_data = start_game(token=token, proxies=proxies)
        start_game_code = start_game_data["code"]

        if start_game_code == "000000":
            payload, point = get_game_data(game_response=start_game_data)
            if payload:
                base.log(f"{base.yellow}Playing for 45 seconds...")
                time.sleep(45)
                complete_game_status = complete_game(
                    token=token, payload=payload, point=point, proxies=proxies
                )
                if complete_game_status:
                    base.log(f"{base.white}Auto Play Game: {base.green}Success")
                    get_info(token=token, proxies=proxies)
                    time.sleep(1)
                else:
                    base.log(f"{base.white}Auto Play Game: {base.red}Fail")
                    break
            else:
                base.log(f"{base.white}Auto Play Game: {base.red}Fail")
                break
        elif start_game_code == "116002":
            base.log(f"{base.white}Auto Play Game: {base.red}No attempt to play")
            break
        else:
            error_message = start_game_data["messageDetail"]
            base.log(f"{base.white}Auto Play Game: {base.red}Error - {error_message}")
            break
