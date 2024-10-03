import requests

from smart_airdrop_claimer import base
from core.headers import headers


def get_info(token, proxies=None):
    url = "https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-info"
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
        total_grade = data["data"]["metaInfo"]["totalGrade"]
        total_ref_grade = data["data"]["metaInfo"]["referralTotalGrade"]
        if total_ref_grade:
            balance = total_grade + total_ref_grade
        else:
            balance = total_grade
        total_attempts = data["data"]["metaInfo"]["totalAttempts"]
        consumed_attempts = data["data"]["metaInfo"]["consumedAttempts"]
        attempts_left = total_attempts - consumed_attempts
        is_countdown = data["data"]["metaInfo"]["attemptRefreshCountDownTime"]

        base.log(
            f"{base.green}Balance: {base.white}{balance:,} - {base.green}Attempts Left: {base.white}{attempts_left}"
        )

        return attempts_left, is_countdown
    except:
        return None, None
