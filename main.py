import execjs  
import json          
import time
from urllib.parse import urljoin
from pyquery import PyQuery as jq

def Crack(Resp=None,Content=None,Url=None):
    Content = Resp.text if Resp else Content
    Url = Resp.url if Resp else Url
    JQData = jq(Content)("#challenge-form")
    JSCode = jq(Content)("script").eq(0).text().replace("\n", "").split("setTimeout(function(){")[1].split("f.action += location.hash")[0].replace("a.value", "res").replace("t.length", "12").split(";")
    KeyData = json.loads('{"' + JSCode[0].split(",")[-1].replace('":', '":"').replace("}", '"}').replace("=", '":') + "}")

    Key = list(KeyData.keys())[0]
    Key2 = list(KeyData[Key].keys())[0]
    Key3 = f"{Key}.{Key2}".strip()
    StartData = execjs.eval(JSCode[0].split(",")[-1])
    print(f"keyCode_{StartData[Key2]} -- > {JSCode[0].split(',')[-1]}")
    for i in JSCode[10:-3]:
        Code = i.replace(Key3, "")
        Method = Code[0]
        Code = "{" + f'"{Key2}":{Code[2:]}' + "}"
        StartData[Key2] = eval(f"StartData[Key2]{Method}{execjs.eval(Code)[Key2]}")
        print(f"keyCode_{StartData[Key2]} --> {Code}")

    Params = {i.attr("name"): i.attr("value") for i in JQData('input').items()}
    Params["jschl_answer"] = execjs.eval(JSCode[-3].replace(Key3, str(StartData[Key2])))

    time.sleep(4)
    return f'{urljoin(Url, JQData.attr("action"))}?{"&".join([f"{k}={v}" for k,v in Params.items()])}'

if __name__ == '__main__':
    with open("DemoPage.html","r") as Html:
        print(Crack(Content=Html.read(),Url="https://coinone.co.kr/exchange/trade/eth/"))