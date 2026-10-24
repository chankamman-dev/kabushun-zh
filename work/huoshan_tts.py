"""Volcano Engine translate TTS (endpoint as in LunaTranslator/tts/huoshantts.py).  huoshan_tts.py "text" out.mp3 voice"""
import sys, json, base64, urllib.request
H = {"accept": "application/json, text/plain, */*", "accept-language": "zh-CN,zh;q=0.9", "content-type": "application/json",
     "origin": "chrome-extension://klgfhbdadaspgppeadghjjemk"}
def tts(text, voice='zh_male_zhubo'):
    req = urllib.request.Request("https://translate.volcengine.com/crx/tts/v1/", data=json.dumps({"text": text, "speaker": voice}).encode(), headers=H)
    return base64.b64decode(json.load(urllib.request.urlopen(req, timeout=60))["audio"]["data"])
if __name__ == '__main__':
    a = tts(sys.argv[1], sys.argv[3] if len(sys.argv) > 3 else 'zh_male_zhubo'); open(sys.argv[2], 'wb').write(a); print(sys.argv[2], len(a))
