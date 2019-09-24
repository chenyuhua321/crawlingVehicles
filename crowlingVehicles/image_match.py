# -*- coding: utf-8 -*-
import cv2
import numpy as np
import urllib
import time

def mathc_img(img_gray, template, value):
    #图标和原图的匹配位置，即为图标要移动的距离
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = value
    loc = np.where(res >= threshold)
    result_size = len(loc[1])
    if result_size > 0:
        middle = round(result_size/2)
        middle = int(middle)
        '''
        #show match result
        guess_points = zip(*loc[::-1])
        for pt in guess_points:
            cv2.rectangle(img_gray, pt, (pt[0] + w, pt[1] + h), (7, 249, 151), 1)
        cv2.imshow('Detected', img_gray)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        '''
        a = loc[1]
        b = a[middle]
        return b

    else:
        return -1

def cropHeight(icon):
    mid = round(icon.shape[1] / 2)
    mid = int(mid)
    c = icon[:, mid, 2]
    no0 = np.where(c != 0)
    first, last = no0[0][0], no0[0][-1]
    return first, last

def loadImg(url):
    resp = urllib.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

def cropImage(img,top_y,bottom_y):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    crop_img = img_gray[top_y:bottom_y,:]
    return crop_img

def showImg(img,name):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def distance(img_url,icon_url,display_width):
    value = 0.45
    img_rgb = loadImg(img_url)
    tmp_rgb = loadImg(icon_url)
    crop_height = cropHeight(tmp_rgb)
    pic = cropImage(img_rgb,*crop_height)
    icon = cropImage(tmp_rgb,*crop_height)
    src_width = img_rgb.shape[1]
    guess_px = mathc_img(pic, icon, value)

    if guess_px is not -1:
        return round(guess_px * display_width / src_width)
    else:
        return -1

# copy demo
def get_tracks(distance):
    '''''
    拿到移动轨迹，模仿人的滑动行为，先匀加速后匀减速
    匀变速运动基本公式：
    ①v=v0+at
    ②s=v0t+½at²
    ③v²-v0²=2as

    :param distance: 需要移动的距离
    :return: 存放每0.3秒移动的距离
    '''
    # 初速度
    v = 0
    # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
    t = 0.2
    # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
    tracks = []
    # 当前的位移
    current = 0
    # 到达mid值开始减速
    mid = distance * 4 / 5

    while current < distance:
        if current < mid:
            # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
            a = 2
        else:
            a = -3
            # 初速度
        v0 = v
        # 0.2秒时间内的位移
        s = v0 * t + 0.5 * a * (t ** 2)
        # 当前的位置
        current += s
        # 添加到轨迹列表
        tracks.append(round(s))

        # 速度已经达到v,该速度作为下次的初速度
        v = v0 + a * t
    return tracks

def getSlideInstance(img_w,icon_w,match_x):
    #考虑到滑块和图标的速度不总是1:1,获取滑块实际滑动的距离
    slider_width = 40
    iconMslider = icon_w - slider_width
    first_l = round(iconMslider / 2)
    mid_l = img_w - first_l
    #end_l = img_w - first_l - mid_l  #eliminate 1px error
    if match_x <= first_l:
        return match_x * 2
    elif match_x <= first_l + mid_l:
        return match_x + first_l
    else:
        return 2 * match_x - mid_l