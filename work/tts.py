"""Edge read-aloud neural TTS (protocol as in LunaTranslator/tts/edgetts.py), minimal stdlib websocket.
usage: tts.py "text" out.mp3 [voice] [rate e.g. +10%]"""
import sys, os, ssl, socket, base64, struct, hashlib, uuid, time, re, datetime

TOKEN = '6A5AA1D4EAFF4E9FB37E23D68491D6F4'
HOST = 'speech.platform.bing.com'
VER = '130.0.2849.68'
PROXY = ('127.0.0.1', 7897)


def sec_ms_gec():
    t = datetime.datetime.now(datetime.timezone.utc).timestamp() + 11644473600
    t -= t % 300
    return hashlib.sha256(('%.0f%s' % (t * 1e7, TOKEN)).encode()).hexdigest().upper()


def connect():
    path = (f'/consumer/speech/synthesize/readaloud/edge/v1?TrustedClientToken={TOKEN}'
            f'&Sec-MS-GEC={sec_ms_gec()}&Sec-MS-GEC-Version=1-{VER}&ConnectionId={uuid.uuid4().hex}')
    raw = socket.create_connection(PROXY, timeout=30)
    raw.sendall(f'CONNECT {HOST}:443 HTTP/1.1\r\nHost: {HOST}:443\r\n\r\n'.encode())
    resp = b''
    while b'\r\n\r\n' not in resp: resp += raw.recv(4096)
    assert b' 200' in resp.split(b'\r\n')[0], resp
    s = ssl.create_default_context().wrap_socket(raw, server_hostname=HOST)
    key = base64.b64encode(os.urandom(16)).decode()
    major = VER.split('.')[0]
    s.sendall((f'GET {path} HTTP/1.1\r\nHost: {HOST}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
               f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\nPragma: no-cache\r\nCache-Control: no-cache\r\n'
               f'Origin: chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold\r\n'
               f'Cookie: muid={uuid.uuid4().hex.upper()};\r\nAccept-Language: en-US,en;q=0.9\r\n'
               f'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
               f'Chrome/{major}.0.0.0 Safari/537.36 Edg/{major}.0.0.0\r\n\r\n').encode())
    resp = b''
    while b'\r\n\r\n' not in resp: resp += s.recv(4096)
    head, rest = resp.split(b'\r\n\r\n', 1)
    assert b'101' in head.split(b'\r\n')[0], head
    return s, bytearray(rest)


def send(s, text):
    data = text.encode(); mask = os.urandom(4)
    hdr = bytearray([0x81])
    n = len(data)
    if n < 126: hdr.append(0x80 | n)
    elif n < 65536: hdr.append(0x80 | 126); hdr += struct.pack('>H', n)
    else: hdr.append(0x80 | 127); hdr += struct.pack('>Q', n)
    s.sendall(bytes(hdr) + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))


def recv(s, buf):
    def need(k):
        while len(buf) < k:
            c = s.recv(65536)
            if not c: raise EOFError
            buf.extend(c)
    need(2); op = buf[0] & 15; n = buf[1] & 127; p = 2
    if n == 126: need(4); n = struct.unpack('>H', bytes(buf[2:4]))[0]; p = 4
    elif n == 127: need(10); n = struct.unpack('>Q', bytes(buf[2:10]))[0]; p = 10
    need(p + n); data = bytes(buf[p:p + n]); del buf[:p + n]
    return op, data


def tts(text, voice='zh-CN-YunxiNeural', rate='+0%', pitch='+0Hz'):
    s, buf = connect()
    date = time.strftime('%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)', time.gmtime())
    send(s, f'X-Timestamp:{date}\r\nContent-Type:application/json; charset=utf-8\r\nPath:speech.config\r\n\r\n'
            '{"context":{"synthesis":{"audio":{"metadataoptions":{"sentenceBoundaryEnabled":false,'
            '"wordBoundaryEnabled":false},"outputFormat":"audio-24khz-96kbitrate-mono-mp3"}}}}\r\n')
    ssml = (f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'><voice name='{voice}'>"
            f"<prosody pitch='{pitch}' rate='{rate}' volume='+0%'>{text}</prosody></voice></speak>")
    send(s, f'X-RequestId:{uuid.uuid4().hex}\r\nContent-Type:application/ssml+xml\r\nX-Timestamp:{date}Z\r\nPath:ssml\r\n\r\n{ssml}')
    audio = b''
    while True:
        op, data = recv(s, buf)
        if op == 1 and b'Path:turn.end' in data: break
        if op == 2:
            hl = struct.unpack('>H', data[:2])[0]
            audio += data[2 + hl:]
        if op == 8: break
    s.close()
    return audio


if __name__ == '__main__':
    text, out = sys.argv[1], sys.argv[2]
    voice = sys.argv[3] if len(sys.argv) > 3 else 'zh-CN-YunxiNeural'
    rate = sys.argv[4] if len(sys.argv) > 4 else '+0%'
    a = tts(text, voice, rate)
    open(out, 'wb').write(a); print(out, len(a))
