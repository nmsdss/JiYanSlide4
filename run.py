# -*- coding: utf-8 -*-
from slide import JiYanSlide
from wugan import JiYanWuGan


if __name__ == '__main__':
    # 滑块
    ss = JiYanSlide()
    ss.main()
    # 无感验证
    ww = JiYanWuGan()
    ww.main()
