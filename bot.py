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
black = Fore,