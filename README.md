### 使用方法

```python
>>> from crack import Crack
>>> import requests
>>> import time
>>> import logging
>>> logging.basicConfig(level=logging.DEBUG)
>>> resp = requests.get('https://coinone.co.kr/')
>>> Crack(resp.text,resp.url,time.time()+4)
'https://coinone.co.kr/cdn-cgi/l/chk_jschl?s=42c28df7a2081751bc2de49f82d4ba562c40161d-1554887499-1800-AdmLyALohtCDdHD4PcFr1bDbhB+Aq8I2flmTqe7q7ic6VhGnm3dJkybzy2Hxas32IVNDAifyC2bbx5qZwMJaWStUMyp6k6oq94rtS+kohdHNi4Zvd2l88zSrDL56Re/AtA==&jschl_vc=972255ab0dc00bb538b944b0173bcbc2&pass=1554887503.845-wzlRZjQDi3&jschl_answer=12.2863902079'
```

### 案例网站
![demo1](https://github.com/aoii103/AntiCloudFare/blob/master/img/demo1.png)

### 测试结果
![demo2](https://github.com/aoii103/AntiCloudFare/blob/master/img/demo2.png?raw=true)
