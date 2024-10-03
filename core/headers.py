from fake_useragent import UserAgent

def headers(token=None):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.binance.info",
        "Referer": "https://www.binance.info/en/game/tg/moon-bix",
        "User-Agent": UserAgent().random
    }
    if token:
        headers["X-Growth-Token"] = token
    return headers
