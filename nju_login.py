import requests
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding
from lxml import etree
import base64
from typing import Callable
'''
向auth.nju.edu.cn发起post请求时，body中的dllt设为mobileLogin

'''

def do_captcha(img_data: bytes) -> str:
    print("Loading ddddocr...",end='')
    import ddddocr
    print("\r"*18,end='')
    ocr=ddddocr.DdddOcr()
    return ocr.classification(img_data)

def web_page(url,headers={}):
    response=requests.get(url,headers=headers)
    text=response.text
    document=etree.HTML(text)
    return document

def encrypt(password,salt):
    cipher=AES.new(salt.encode('utf-8'),AES.MODE_CBC,iv=('a'*16).encode('utf-8'))
    encrypted_password_bytes=cipher.encrypt(Padding.pad(('a'*64+password).encode('utf-8'),16,'pkcs7'))
    encrypted_password=base64.b64encode(encrypted_password_bytes).decode('utf-8')
    return encrypted_password

def login(
    username: str,
    password: str,
    captcha_callback: Callable[[bytes], str] = do_captcha,
) -> requests.Response:
    session = requests.Session()
    session.headers.update({
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
        'origin': 'https://authserver.nju.edu.cn',
        'referer': 'https://authserver.nju.edu.cn/authserver/login'
    })

    # Get some neccessary cookie
    session.get("https://authserver.nju.edu.cn/authserver/login")

    login_page_response=session.get("https://authserver.nju.edu.cn/authserver/login")
    login_page=etree.HTML(login_page_response.text)
    lt=str(login_page.xpath('//*[@id="casLoginForm"]/input[@name="lt"]//@value')[0])
    dllt="mobileLogin"
    execution=str(login_page.xpath('//*[@id="casLoginForm"]/input[@name="execution"]//@value')[0])
    eventid=str(login_page.xpath('//*[@id="casLoginForm"]/input[@name="_eventId"]//@value')[0])
    rmshown=str(login_page.xpath('//*[@id="casLoginForm"]/input[@name="rmShown"]//@value')[0])
    salt=str(login_page.xpath('//*[@id="pwdDefaultEncryptSalt"]//@value')[0])

    need_captcha=session.get(f"https://authserver.nju.edu.cn/authserver/needCaptcha.html?username={username}&pwdEncrypt2=pwdEncryptSalt")

    captcha_content=session.get("https://authserver.nju.edu.cn/authserver/captcha.html").content
    captcha_result=captcha_callback(captcha_content)

    encrypted_password=encrypt(password,salt)

    data={
        "username":username,
        "password":encrypted_password,
        "captchaResponse":captcha_result,
        "lt":lt,
        "dllt":dllt,
        "execution":execution,
        "_eventId":eventid,
        "rmShown":rmshown
    }
    login_response=session.post("https://authserver.nju.edu.cn/authserver/login",data=data,allow_redirects=False)
    return login_response
