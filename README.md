# 南京大学统一认证登陆

从账号密码拿到 `CASTGC` cookie

```python3
import nju_login
response = nju_login.login('学号', '统一认证密码')
```

## 自定义验证码识别

```python3
response = nju_login.login(
  '学号',
  '统一认证密码',
  # 验证码识别回调，不传则使用ddddocr识别
  lambda x: "45cx"
)
```

# 登陆南大网站

南大SSO的登陆流程一般是：

1. 你去访问目标网站，比如课表 <https://ehall.nju.edu.cn/appShow?appId=4770397878132218>
2. 目标网站发现你没登陆，于是给你重定向到统一认证
3. 你在统一认证完成登陆，它给你重定向回目标网站，此时URL会带上一个ticket
4. 目标网站根据ticket给你设置cookie，然后重定向到你一开始想去的页面

这里面只有第三步需要人工参与，其它地方都是自动重定向。

本项目要做的就是帮你跳过第三部。如果你访问统一认证网站时带上了有效的`CASTGC` cookie，那么它就会知道你已经登陆，并直接给你ticket然后带你重定向。

因此，如果想借助本项目登陆南大网站（比如ehall或者epay啥的），一般流程是：

1. 调用login，拿到castgc
2. 将castgc加到自己的request session的cookies里。此时你的session在统一认证有登陆，在服务站没登陆。
3. 用自己的session去访问nju服务。经过几次自动跳转，你就在服务站登陆上了。

## 示例使用代码

感谢 @[Chen-Rong-Zi](https://github.com/Chen-Rong-Zi) 提供的[示例代码和文档完善建议](https://github.com/SuperKenVery/nju-login/issues/11)。

```python3
import nju_login
import requests

# 登录获取 CASTGC
resp = nju_login.login('学号', '密码')
castgc = resp.cookies.get('CASTGC')

# 构建 session 并触发 SSO
session = requests.Session()
session.cookies.set('CASTGC', castgc, domain='authserver.nju.edu.cn')
session.get('https://epay.nju.edu.cn/epay/h5/nju/electric/index')

# 现在可以访问具体页面
r = session.get('https://epay.nju.edu.cn/epay/h5/nju/electric/charge?id=53463')
print(r.text)
```
