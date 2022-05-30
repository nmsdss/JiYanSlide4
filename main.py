# -*- coding: utf-8 -*-
import requests
from lxml import etree
import re
import uuid

from utils import *

download_images = True


class JiYanSlide():
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
        w = get_w(captchaId, lot_number, detail_time, distance, passtime, track)
        return captchaId, lot_number, payload, process_token, w

    # aa = {'lot_number': 'fb65eb2013fd49c2be7af9dae2dcd983', 'captcha_type': 'slide', 'js': '/js/gcaptcha4.js',
    #       'css': '/css/gcaptcha4.css', 'static_path': '/v4/static/v1.5.4',
    #       'slice': 'captcha_v4/e70fbf1d77/slide/22397859ec/2022-04-21T09/slice/b9620f8b1ad640498117ad2c7493d256.png',
    #       'bg': 'captcha_v4/e70fbf1d77/slide/22397859ec/2022-04-21T09/bg/b9620f8b1ad640498117ad2c7493d256.png',
    #       'ypos': 102,
    #       'gct_path': '/v4/gct/gct4.2083c1cdfe84557e2c0b524e90d405a9.js', 'arrow': 'arrow_1', 'show_voice': 'false',
    #       'feedback': 'https://www.geetest.com/Helper', 'logo': 'true', 'pt': '1', 'captcha_mode': 'risk_manage',
    #       'language': 'zh', 'custom_theme': {'_style': 'stereoscopic', '_color': 'hsla(224,98%,66%,1)',
    #                                          '_gradient': 'linear-gradient(180deg, hsla(224,98%,71%,1) 0%, hsla(224,98%,66%,1) 100%)',
    #                                          '_hover': 'linear-gradient(180deg, hsla(224,98%,66%,1) 0%, hsla(224,98%,71%,1) 100%)',
    #                                          '_brightness': 'system', '_radius': '4px'},
    #       'pow_detail': {'version': '1', 'bits': 0, 'datetime': '2022-05-28T23:21:08.200951+08:00', 'hashfunc': 'md5'},
    #       '': 'qgGaqrOsa7yf5glt6hJ8LIS8-UAVOeGQ7g7uc0Gc1FAZiDwQ4y_63YPdp_C6HOGIiqGnUcLdL7Eqcw_AKAwvlr2w3J_bmwJkWMBOj6FQamOaHPIJAI_FBqO6-eb6rU11EFHpswwaYLgSeEwjbPL05wEa1ut0m1KOzqp5kcf8RH14NONdjTZ19bzBtGPDt9X1VMS3YZgsUBgiWyNXQrxMTYy62xtiF7M6T3XgfzXR7fgC7g9WMvkK9iHYZdBwISsV_7Osh6v_99utHwcKgknD4s-8Ljv3EEtD4rCwBZtgLPKb1ibHdRn_ezru-5gP313jvcq7Pm540bm_8i7vKoIgkWYsYKiu6v2iK06Ogd0tHbA5Lzh05JzvnexbfBQwODRsfsSL7TM3v-s5GIGg54MvU3l7JF4tDarFhWp_oz81Z2DEU33yd3DyOMEmTGj--iIx7R-i8SsmtuybLA2JZ-ZNwHlGsIPIfuTfkub6is2SsTuD0ChLye1AH9fyop7_evmpg80nr9VPpUcsp7LEKw9Sv3KDEZ2A2lsJUkIuwNBTZdU=',
    #       'process_token': '52eec6a232df46a6e369953ee494ed367be536fe9c51de6c711211c7580e978f', 'payload_protocol': 1}

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
    jy = JiYanSlide()
    jy.main()
