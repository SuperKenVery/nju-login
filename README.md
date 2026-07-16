# NJU Login

Login to authserver.nju.edu.cn and get `CASTGC` cookie.

```python3
import nju_login
response = nju_login.login('student_id', 'password')
```

## Advanced Usage

### Custom CAPTCHA callback

```python
response = nju_login.login(
  'student_id',
  'password',
  # Custom CAPTCHA recognition callback, defaults to ddddocr
  lambda x: "45cx"
)

# The cookies in response represent your login state.
# Specifically the CASTGC cookie.
```

### Get full session (for SSO services like epay)

```python
session = nju_login.login(
  'student_id',
  'password',
  follow_redirect=True,
)

# Session contains route, JSESSIONID, CASTGC, MOD_AUTH_CAS etc.
# Ready to use with SSO services like epay.
cookies = session.cookies.get_dict()
```
