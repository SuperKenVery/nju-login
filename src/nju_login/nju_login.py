from .captcha import do_captcha
from .utils import extract_page_context, encrypt, getSafeSecure, extract_login_error
import base64
from typing import Callable

import requests
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding
from lxml import etree
import json


class NJULoginError(Exception):
    """登陆流程中的所有错误。错误基类，不直接抛出。"""
    pass

class CaptchaFailError(NJULoginError):
    """过验证码失败"""
    pass

class LoginError(NJULoginError):
    """提交用户名密码登录时失败"""
    pass

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

    # 1. 进入登陆页面，获取基础cookies和页面内容
    session.get("https://authserver.nju.edu.cn/authserver/login")

    login_page_response = session.get("https://authserver.nju.edu.cn/authserver/login")
    context = extract_page_context(login_page_response.text)

    # 2. 获取验证码内容
    _ = session.get("https://authserver.nju.edu.cn/authserver/common/toSliderCaptcha.htl")
    captchas = session.get("https://authserver.nju.edu.cn/authserver/common/openSliderCaptcha.htl").json()

    # 3. 过验证码
    big_image=base64.b64decode(captchas['bigImage'])
    small_image=base64.b64decode(captchas['smallImage'])
    captcha_data = do_captcha(big_image, small_image)
    captcha_result = session.post(
        "https://authserver.nju.edu.cn/authserver/common/verifySliderCaptcha.htl",
        data={
            "sign": encrypt(json.dumps(captcha_data), salt=getSafeSecure(small_image))
        }
    ).json()

    if captcha_result["errorMsg"] != "success":
        # Expected: {"errorCode":1,"errorMsg":"success"}
        raise CaptchaFailError(f"Failed to pass captcha: {captcha_result}")

    # 4. 提交用户名和密码，登陆
    login_ctx = context.copy()
    del login_ctx["pwdEncryptSalt"]
    login_ctx["dllt"]="mobileLogin" # 模拟移动端来获取长效cookie
    login_response = session.post(
        "https://authserver.nju.edu.cn/authserver/login",
        data={
            "username": username,
            "password": encrypt(password, salt=context["pwdEncryptSalt"]),
            "captcha": "",
            **login_ctx
        },
        allow_redirects=False
    )

    if not "CASTGC" in login_response.cookies:
        error_msg = extract_login_error(login_response.text)
        raise LoginError(error_msg)

    return login_response
