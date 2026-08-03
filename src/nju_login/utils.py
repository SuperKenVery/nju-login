from lxml import etree
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding
import base64

def extract_page_context(page_text: str) -> dict[str, str]:
    page = etree.HTML(page_text)
    ctx = {}

    for elem in page.xpath('//*[@id="pwdFromId"]/input'):
        name = elem.get("id")
        value = elem.get("value")
        ctx[name]=value

    return ctx

def extract_login_error(page_text: str) -> str:
    page = etree.HTML(page_text)
    error_msg = page.xpath('//div[@id="pwdLoginDiv"]//span[@id="showErrorTip"]//text()')[0]
    return error_msg

def encrypt(password, salt):
    cipher = AES.new(salt.encode("utf-8"), AES.MODE_CBC, iv=("a" * 16).encode("utf-8"))
    encrypted_password_bytes = cipher.encrypt(
        Padding.pad(("a" * 64 + password).encode("utf-8"), 16, "pkcs7")
    )
    encrypted_password = base64.b64encode(encrypted_password_bytes).decode("utf-8")
    return encrypted_password

def getSafeSecure(small_image: bytes) -> str:
    assert len(small_image) >= 16

    safe_secure=""
    for c in small_image[-16:]:
        safe_secure += chr(c)
    return safe_secure

if __name__=="__main__":
    import requests
    session = requests.Session()

    login_page = session.get("https://authserver.nju.edu.cn/authserver/login")
    context = extract_page_context(login_page.text)
    print(context)
