"""Bilibili 必剪 TTS (endpoint as used by LunaTranslator/tts/bcuttts.py).  bcut_tts.py "text" out.mp3 [voice]"""
import sys, json, urllib.request

H = {"Accept-Language": "zh-CN,en,*", "User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}


def tts(text, voice='jieshuonannew'):
    body = {"model_id": "tts_bcut_pc", "raw_data": [text],
            "raw_params": {"format": "mp3", "logid": "b98553e4-09bb-4d77-bb05-529c27674587", "method": 0, "pitch_rate": 0,
                           "sample_rate": 24000, "speech_rate": 0, "task_type": 0, "voice": voice,
                           "voice_engine": "bili", "volume": 50}}
    req = urllib.request.Request("https://member.bilibili.com/x/material/rubick-interface/sync-task",
                                 data=json.dumps(body).encode(), headers=H)
    r = json.load(urllib.request.urlopen(req, timeout=60))
    url = r["data"]["result"]["results"][0]["url"]
    return urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60).read()


if __name__ == '__main__':
    a = tts(sys.argv[1], sys.argv[3] if len(sys.argv) > 3 else 'jieshuonannew')
    open(sys.argv[2], 'wb').write(a); print(sys.argv[2], len(a))
