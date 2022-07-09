# -*- coding: utf-8 -*-
import json
import random
import execjs
from binascii import b2a_hex
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pksc1_v1_5, AES
from Crypto.PublicKey import RSA
import numpy as np
from Crypto.Util.Padding import pad
import cv2
import hashlib
# import ddddocr

from settings import *

# det = ddddocr.DdddOcr(det=False, ocr=False)
with open("static/json/tracks.json", "r") as f:
    tracks_json = json.load(f)


def identify_gaps1(bg, slice):
    bg_img = cv2.imdecode(np.frombuffer(bg, np.uint8), cv2.IMREAD_ANYCOLOR)
    slice_img = cv2.imdecode(np.frombuffer(slice, np.uint8), cv2.IMREAD_ANYCOLOR)
    bg_edge = cv2.Canny(bg_img, 300, 200)
    slice_edge = cv2.Canny(slice_img, 80, 80)
    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
    slice_pic = cv2.cvtColor(slice_edge, cv2.COLOR_GRAY2RGB)
    res = cv2.matchTemplate(bg_pic, slice_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    tl = max_loc
    return tl[0]


# def identify_gaps2(bg, slice):
#     result = det.slide_match(slice, bg)
#     print(result)


def choice_track_2(distance: int) -> tuple:
    def __ease_out_expo(step):
        return 1 if step == 1 else 1 - pow(2, -10 * step)

    tracks = [[random.randint(20, 60), random.randint(10, 40), 0]]
    count = 30 + int(distance / 2)
    _x, _y = 0, 0
    for item in range(count):
        x = round(__ease_out_expo(item / count) * distance)
        t = random.randint(10, 20)
        if x == _x:
            continue
        tracks.append([x - _x, _y, t])
        _x = x
    tracks.append([0, 0, random.randint(200, 300)])
    passtime = sum([track[2] for track in tracks])
    return tracks, passtime


def random_str():
    data = ""
    for i in range(4):
        data += (format((int((1 + random.random()) * 65536) | 0), "x")[1:])
    return data


# 获取随机键值对,写死就行
# def get_gct_value(gct_text):
#     # with open("./aaa.js", "w", encoding="utf-8")as f:
#     #     f.write("exports = undefined; module = undefined;" + gct_text)
#     call_func = """
#         function get_gct_data() {
#             var aa = {
#                 ep: "123",
#                 geetest: "captcha",
#                 lang: "zh"
#             };
#             return _gct(aa), aa
#         }
#     """
#     ctx = execjs.compile("exports = undefined; module = undefined;" + gct_text + call_func)
#     gct_value = ctx.call("get_gct_data").popitem()
#     return gct_value[0], gct_value[1]


def RSA_encrypt(data):
    public_key_1 = 0x00C1E3934D1614465B33053E7F48EE4EC87B14B95EF88947713D25EECBFF7E74C7977D02DC1D9451F79DD5D1C10C29ACB6A9B4D6FB7D0A0279B6719E1772565F09AF627715919221AEF91899CAE08C0D686D748B20A3603BE2318CA6BC2B59706592A9219D0BF05C9F65023A21D2330807252AE0066D59CEEFA5F2748EA80BAB81
    public_key_2 = 0x10001
    public_key = RSA.construct((public_key_1, public_key_2))
    cipher = Cipher_pksc1_v1_5.new(public_key)
    cipher_text = b2a_hex(cipher.encrypt(data.encode()))
    return cipher_text.decode()


def AES_encrypt(data, key):
    iv = "0000000000000000".encode()
    aes = AES.new(key.encode(), mode=AES.MODE_CBC, iv=iv)
    encrypt_aes = aes.encrypt(pad(data.encode(), AES.block_size))
    encode_str = b2a_hex(encrypt_aes).decode()

    return encode_str


def track_offset(track):
    t = s = n = None
    a = []
    o = 0
    r = 0
    i = len(track) - 1
    while r < i:
        t = round(track[r + 1][0] - track[r][0])
        s = round(track[r + 1][1] - track[r][1])
        n = round(track[r + 1][2] - track[r][2])
        if t == 0 and s == 0 and n == 0:
            continue
        if t == 0 and s == 0:
            o += n
        else:
            a.append([t, s, n + o])
            o = 0
        r += 1
    if o != 0:
        a.append([t, s, o])
    return a


def get_track(distance):
    for track in tracks_json:
        if distance == track[-1][0]:
            passtime = track[-1][-1]
            return passtime, track_offset(track)
    logger.warning(f"距离{distance} -> 未找到途径，采用快速算法")
    track, passtime = choice_track_2(distance)
    return passtime, track


def get_w_slide(captchaId, lot_number, detail_time, distance, passtime, track, gct_key=None, gct_value=None):
    key = random_str()
    rsa_encode = RSA_encrypt(key)
    encrypt_data = {
        "setLeft": distance,  # 移动距离
        "track": track,  # 轨迹
        "passtime": passtime,  # 耗时
        "userresponse": distance / (.8876 * 340 / 300),
        "device_id": "D00D",
        "lot_number": lot_number,
        "pow_msg": f"1|0|md5|{detail_time}|{captchaId}|{lot_number}||{random_str()}",
        "pow_sign": "",
        "geetest": "captcha",
        "lang": "zh",
        "ep": "123",
        'cuel': '632729377',  # gct_key: gct_value 随机键值对
        "em": {"ph": 0, "cp": 0, "ek": "11", "wd": 1, "nt": 0, "si": 0, "sc": 0}
    }
    encrypt_data["pow_sign"] = hashlib.md5(encrypt_data["pow_msg"].encode()).hexdigest()
    aes_encode = AES_encrypt(str(encrypt_data).replace(" ", "").replace("'", '"'), key)
    return aes_encode + rsa_encode


def get_w_wugan(captchaId, lot_number, detail_time, gct_key=None, gct_value=None):
    key = random_str()
    rsa_encode = RSA_encrypt(key)
    encrypt_data = {
        "device_id": "D00D",
        "lot_number": lot_number,
        "pow_msg": f"1|0|md5|{detail_time}|{captchaId}|{lot_number}||{random_str()}",
        "pow_sign": "",
        "geetest": "captcha",
        "lang": "zh",
        "ep": "123",
        'cuel': '632729377',  # gct_key: gct_value 随机键值对
        "em": {"ph": 0, "cp": 0, "ek": "11", "wd": 1, "nt": 0, "si": 0, "sc": 0}
    }
    encrypt_data["pow_sign"] = hashlib.md5(encrypt_data["pow_msg"].encode()).hexdigest()
    aes_encode = AES_encrypt(str(encrypt_data).replace(" ", "").replace("'", '"'), key)
    return aes_encode + rsa_encode
