# -*- coding: utf-8 -*-
import requests
from lxml import etree
import re
import uuid

from utils import *

download_images = True


class JiYanSlide:
    def __init__(self):
        self.session = requests.session()

    def get_distance(self, bg_url, slice_url):
        bg_url = url_static + bg_url
        slice_url = url_static + slice_url
        bg = self.session.get(bg_url).content
        slice = self.session.get(slice_url).content
        if download_images:
            with open("static/image/bg.png", "wb") as f:
                f.write(bg)
            with open("static/image/slice.png", "wb") as j:
                j.write(slice)
        distance = identify_gaps1(bg, slice)
        return distance

    def get_captchaId(self) -> str:
        response_index = self.session.get(url_index)
        HTML = etree.HTML(response_index.text)
        adaptive_captcha_demo = HTML.xpath('/html/head/script[2]/@src')[0]
        response_js = self.session.get(url_host + adaptive_captcha_demo)
        captchaId = re.search('captchaId:"([0-9a-z]+)"', response_js.text).group(1)
        return captchaId

    def get_static(self, captcha_id: str, challenge: str) -> dict:
        params = {
            "captcha_id": captcha_id,
            "challenge": challenge,
            "client_type": "web",
            "risk_type": "ai",
            "lang": "zh",
        }
        response = self.session.get(url=url_load, params=params)
        data = eval(response.text.replace('false', '"false"').replace('true', '"true"'))
        return data["data"]

    def get_static_data(self) -> tuple:
        captchaId = self.get_captchaId()
        challenge = uuid.uuid4()
        params = {
            "captcha_id": captchaId,
            "challenge": challenge,
            "client_type": "web",
            "risk_type": "slide",
            "lang": "zh",
        }
        res = self.session.get(url_load, params=params)
        res_dict = eval(res.text.replace('false', '"false"').replace('true', '"true"'))["data"]
        lot_number = res_dict["lot_number"]
        payload = res_dict["payload"]
        process_token = res_dict["process_token"]
        detail_time = res_dict["pow_detail"]["datetime"]
        # 用来计算随机键值对,写死就行,这里留作扩展
        # gct_text = self.session.get(url_static + res_dict["gct_path"]).text
        # gct_key, gct_value = get_gct_value(gct_text)
        distance = self.get_distance(res_dict["bg"], res_dict["slice"])
        passtime, track = get_track(distance)
        w = get_w_slide(captchaId, lot_number, detail_time, distance, passtime, track)
        return captchaId, lot_number, payload, process_token, w

    def init_slide(self):
        captchaId, lot_number, payload, process_token, w = self.get_static_data()
        logger.debug(
            f"Init slide success -> \ncaptchaId: {captchaId}\nlot_number: {lot_number}\npayload: {payload}\nprocess_token: {process_token}\nw: {w}")
        return captchaId, lot_number, payload, process_token, w

    def get_validata(self, captchaId, lot_number, payload, process_token, w):
        params = {
            "captcha_id": captchaId,
            "client_type": "web",
            "lot_number": lot_number,
            "risk_type": "slide",
            "payload": payload,
            "process_token": process_token,
            "payload_protocol": "1",
            "pt": "1",
            "w": w
        }
        res = self.session.get(url_verify, params=params)
        res_dict = eval(res.text)
        logger.debug(f"verify-result -> {res_dict}")
        if res_dict["data"]["result"] == "success":
            logger.debug("验证成功\n")
        else:
            logger.debug("验证失败\n")

    def main(self):
        try:
            captchaId, lot_number, payload, process_token, w = self.init_slide()
            self.get_validata(captchaId, lot_number, payload, process_token, w)
        except Exception as e:
            logger.exception(e)


if __name__ == '__main__':
    jy = JiYanSlide()
    jy.main()
