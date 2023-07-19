import requests
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding
from lxml import etree
import base64
'''
向auth.nju.edu.cn发起post请求时，body中的dllt设为mobileLogin

'''

def do_captcha(img_data):
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

def login(username,password,captcha_callback=do_captcha):
    headers={
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
        'origin': 'https://authserver.nju.edu.cn',
        'referer': 'https://authserver.nju.edu.cn/authserver/login'
    }
    get_cookie_response=requests.get("https://authserver.nju.edu.cn/authserver/login",headers=headers)
    cookies={
        'route':get_cookie_response.cookies['route'],
        'JSESSIONID':get_cookie_response.cookies['JSESSIONID'],
        'org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE':'zh_CN'
    }

    login_page_response=requests.get("https://authserver.nju.edu.cn/authserver/login",headers=headers,cookies=cookies)
    login_page=etree.HTML(login_page_response.text)
    lt=str(login_page.xpath('//*[@id="casLoginForm"]/input[@name="lt"]//@value')[0])
    dllt="mobileLogin"
    execution=str(login_page.xpath('//*[@id="casLoginForm"]/input[@name="execution"]//@value')[0])
    eventid=str(login_page.xpath('//*[@id="casLoginForm"]/input[@name="_eventId"]//@value')[0])
    rmshown=str(login_page.xpath('//*[@id="casLoginForm"]/input[@name="rmShown"]//@value')[0])
    salt=str(login_page.xpath('//*[@id="pwdDefaultEncryptSalt"]//@value')[0])

    need_captcha_response=requests.get(f"https://authserver.nju.edu.cn/authserver/needCaptcha.html?username={username}&pwdEncrypt2=pwdEncryptSalt",cookies=cookies,headers=headers)

    captcha_content=requests.get("https://authserver.nju.edu.cn/authserver/captcha.html",cookies=cookies,headers=headers).content
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
    login_response=requests.post("https://authserver.nju.edu.cn/authserver/login",cookies=cookies,data=data,allow_redirects=False,headers=headers)
    return login_response


