# -*- coding: utf-8 -*-
from loguru import logger

# 日志设置
logger.add("./logs/jiyan_slide.log", rotation='00:00', level="WARNING", encoding='utf-8')

# 目标网址
url_host = "https://gt4.geetest.com"
url_static = "https://static.geetest.com/"
url_index = "https://gt4.geetest.com/"
url_load = "https://gcaptcha4.geetest.com/load"
url_verify = "https://gcaptcha4.geetest.com/verify"

