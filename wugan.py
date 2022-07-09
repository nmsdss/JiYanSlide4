# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import requests
from lxml import etree
import re
import uuid

from utils import *


class JiYanWuGan:
    def __init__(self):
        self.session = requests.session()

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
            "risk_type": "ai",
            "lang": "zh",
        }
        res = self.session.get(url_load, params=params)
        res_dict = eval(res.text.replace('false', '"false"').replace('true', '"true"'))["data"]
        lot_number = res_dict["lot_number"]
        payload = res_dict["payload"]
        process_token = res_dict["process_token"]
        detail_time = res_dict["pow_detail"]["datetime"]
        w = get_w_wugan(captchaId, lot_number, detail_time)
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
            "risk_type": "ai",
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
            logger.debug("验证成功")
        else:
            logger.debug("验证失败")

    def main(self):
        try:
            captchaId, lot_number, payload, process_token, w = self.init_slide()
            self.get_validata(captchaId, lot_number, payload, process_token, w)
        except Exception as e:
            logger.exception(e)


if __name__ == '__main__':
    jy = JiYanWuGan()
    jy.main()
