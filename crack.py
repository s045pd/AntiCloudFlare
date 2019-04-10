import json
import time
from urllib.parse import urljoin, urlparse, quote

import execjs
import requests
from pyquery import PyQuery as jq
from log import success, info, error, warning
import click

from contextlib import contextmanager


@contextmanager
def checkTimes(level=3):
    timeStart = time.time()
    yield
    info(f"cost times: {round(time.time()-timeStart,level)}s")


def Crack(content, url, end_time, save_res=False):

    scheme, netloc, *_ = urlparse(url)

    if save_res:
        with open("example/demo.html", "w") as f:
            f.write(
                content.replace("f.submit();", "console.log(a.value);")
                .replace("t.match(/https?:\/\//)[0]", f'"{scheme}://"')
                .replace("t.firstChild.href", f'"{url}"')
            )

    info(f"url: {url}")
    info(f"content: {len(content)}")

    jq_data = jq(content)("#challenge-form")
    js_code = (
        jq(content)("script")
        .eq(0)
        .text()
        .replace("\n", "")
        .split("setTimeout(function(){")[1]
        .split("f.action += location.hash")[0]
        .replace("a.value", "res")
        .replace("t.length", str(len(url.replace(f"{scheme}://", "")) - 1))
        .split(";")
    )
    info(f"codes: {js_code}")
    key_data = json.loads(
        '{"'
        + js_code[0]
        .split(",")[-1]
        .replace('":', '":"')
        .replace("}", '"}')
        .replace("=", '":')
        + "}"
    )

    # warning(f"start_code: {key_data}")

    key_1 = list(key_data.keys())[0]
    key_2 = list(key_data[key_1].keys())[0]
    key_3 = f"{key_1}.{key_2}".strip()
    start_data = execjs.eval(js_code[0].split(",")[-1])

    info(key_1)
    info(key_2)
    info(key_3)

    success(f"{start_data[key_2]}: {js_code[0].split(',')[-1]}")

    for i in js_code[11:-3]:
        try:
            code = i.replace(key_3, "")
            method = code[0]
            code = "{" + f'"{key_2}":{code[2:]}' + "}"
            start_data[key_2] = eval(
                f"start_data[key_2]{method}{execjs.eval(code)[key_2]}"
            )
            success(f"{start_data[key_2]}: {method} {code}")
        except Exception as e:
            pass

    params = {i.attr("name"): i.attr("value") for i in jq_data("input").items()}
    params["jschl_answer"] = execjs.eval(
        js_code[-3].replace(key_3, str(start_data[key_2]))
    )
    info(f'jschl_answer: {params["jschl_answer"]}')

    wait_times = round(end_time - time.time(), 3)
    if wait_times > 0:
        warning(f"waiting for {wait_times} seconds")
        time.sleep(wait_times)

    redirect_url = f'{urljoin(url, jq_data.attr("action"))}?{"&".join([f"{k}={v}" for k,v in params.items()])}'

    info(f"redirecting: {redirect_url}")
    return redirect_url


@click.command()
@click.option("--url", default="https://coinone.co.kr/", help="Target url.")
def test(url):
    while True:
        with checkTimes():
            end_time = time.time() + 4
            session = requests.Session()
            session.headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
                "cache-control": "no-cache",
                "dnt": "2",
                "pragma": "no-cache",
                "referer": url,
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
            }
            resp = session.get(url)
            info(session.cookies)
            info(
                session.get(
                    Crack(resp.text, resp.url, end_time, save_res=True),
                    allow_redirects=False,
                ).headers
            )
            error(f"cf_clearance: {session.cookies.get('cf_clearance','')}")


def test_local():
    # 24.5685020541
    with open("example/demo.html", "r") as f:
        content = f.read()
        url = "https://coinone.co.kr/"
        info(
            Crack(content, url, time.time(), False)
            == "https://coinone.co.kr/cdn-cgi/l/chk_jschl?s=2923ae212ba0bc78667c36998d9318cddd4c1c54-1554883527-1800-AYwHB3rPS1DnyuTKbZnposynqvvMSVF3O%2F%2FlYTvABrXWrsAmkLBqwvafg1fJVVSnvpFZcbCmfL7sj3PJUQ%2BKXrCGNth0%2BcwMVY5s0w6aWyigjCF%2FSC7Infj3y46UopAW6A%3D%3D&jschl_vc=b934979895320cc3505fbb1ce949050c&pass=1554883531.55-JMlpBBaLZJ&jschl_answer=10.8761383509"
        )


if __name__ == "__main__":
    try:
        test()
    except KeyboardInterrupt:
        pass
