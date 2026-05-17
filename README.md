# 南京大学统一认证登陆

从账号密码拿到 `CASTGC` cookie

```python3
import nju_login
response = nju_login.login('学号', '统一认证密码')
```

## 高级用法

```
response = nju_login.login(
  '学号',
  '统一认证密码',
  # 验证码识别回调，不传则使用ddddocr识别
  lambda x: "45cx"
)

# Now the cookies in response represent your login state.
# Specifically the CASTGC cookie.
```
