# -*- coding: utf-8 -*-
# author__ = "lyao"
# version__ = "1.0.1"
# Date: 2017/09/05 20:09

import requests
from PIL import Image
from io import BytesIO
import pytesseract as ocr

def retrive_img(resp):
    '''获取要识别的图片'''
    img_fp = BytesIO(resp.content)
    return Image.open(img_fp)
def process_img(img, threshold=180):
    '''对图片进行二值化 255 是白色 0是黑色'''
    # 灰度转换
    img.show()
    img = img.convert('L')
    # 二值化
    pixels = img.load()
    for x in range(img.width):
        for y in range(img.height):
            pixels[x,y] = 255 if pixels[x,y] > threshold else 0
    return img


def Smooth(Picture):
    '''平滑降噪
        二值化的图片传入 去除像噪小点
    '''
    Pixels = Picture.load()
    (Width, Height) = Picture.size

    xx = [1, 0, -1, 0]
    yy = [0, 1, 0, -1]

    for i in xrange(Width):
        for j in xrange(Height):
            if Pixels[i, j] != 255:
                Count = 0
                for k in xrange(4):
                    try:
                        if Pixels[i + xx[k], j + yy[k]] == 255:
                            Count += 1
                    except IndexError:  # 忽略访问越界的情况
                        pass
                if Count > 3:
                    Pixels[i, j] = 255
    return Picture

def recognize(img, lang='eng'):
    return ocr.image_to_string(img, lang)

if __name__ == '__main__':
    recognize(process_img(retrive_img()))