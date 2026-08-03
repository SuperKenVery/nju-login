from .captcha import do_captcha
from .utils import extract_page_context, encrypt, getSafeSecure
import base64
from typing import Callable

import requests
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding
from lxml import etree
import json

"""
向auth.nju.edu.cn发起post请求时，body中的dllt设为mobileLogin

"""


def login(
    username: str,
    password: str,
) -> requests.Response:
    session = requests.Session()
    session.headers.update(
        {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15",
            "origin": "https://authserver.nju.edu.cn",
            "referer": "https://authserver.nju.edu.cn/authserver/login",
        }
    )

    # Get some neccessary cookie
    session.get("https://authserver.nju.edu.cn/authserver/login")

    login_page_response = session.get("https://authserver.nju.edu.cn/authserver/login")
    context = extract_page_context(login_page_response.text)

    _ = session.get("https://authserver.nju.edu.cn/authserver/common/toSliderCaptcha.htl")
    captchas = session.get("https://authserver.nju.edu.cn/authserver/common/openSliderCaptcha.htl").json()

    big_image=base64.b64decode(captchas['bigImage'])
    small_image=base64.b64decode(captchas['smallImage'])
    captcha_data = do_captcha(big_image, small_image)
    captcha_result = session.post(
        "https://authserver.nju.edu.cn/authserver/common/verifySliderCaptcha.htl",
        data={
            "sign": encrypt(json.dumps(captcha_data), getSafeSecure(small_image))
        }
    )
    print(captcha_result.text)

    return login_response
