import json
import time
from urllib.parse import urljoin, urlparse, quote,unquote,urlencode

import execjs
import requests
from pyquery import PyQuery as jq
from log import success, info, error, warning
import click

from contextlib import contextmanager


import requests
from hyper.contrib import HTTP20Adapter


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
    params['s'] = quote(params['s'])
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
        session = requests.Session()
        session.mount(url.split("/")[0], HTTP20Adapter())
        session.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "cache-control": "no-cache",
            "dnt": "1",
            "pragma": "no-cache",
            "referer": url,
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        }
        resp = session.get(url)
        with checkTimes():
            end_time = time.time() + 4
            info(session.cookies)
            resp = session.get(
                Crack(resp.text, resp.url, end_time, save_res=True),
                allow_redirects=True,
            )
            info(resp.request.headers)
            error(f"cf_clearance: {session.cookies.get('cf_clearance','')}")


def test_local():
    # 24.5685020541
    with open("example/demo.html", "r") as f:
        content = f.read()
        url = "https://coinone.co.kr/"
        info(
            Crack(content, url, time.time(), False)
            == "https://coinone.co.kr/cdn-cgi/l/chk_jschl?s=3c3bff10311f4a2a7465190684507b4b55e40886-1574326333-0-AcEt1Ao9a1Micfg%2FWTHqvRj025Iy6P9zXMcTdFbQ8w1rS3KmQtdqSCfIg9vFXrKQL%2FQl9c0AKKOizKUfcSr529MxwQB2EzgdCkTUcJmj55%2BDgFUG0H7sPtpz5Lq4lOUSl5peRNVWyQxmeSMgb5kUf%2BE%3D&jschl_vc=3ac74535829c1a46193f6272a1e9e29f&pass=1574326337.264-4c2z7JxfaY&jschl_answer=34.9853718953"
        )


if __name__ == "__main__":
    try:
        test()
    except KeyboardInterrupt:
        pass
