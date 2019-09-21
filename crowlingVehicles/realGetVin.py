# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import xlsxwriter
from xlwt import *
from image_match import distance
from image_match import get_tracks
from image_match import getSlideInstance
from bs4 import BeautifulSoup
import pandas

from pandas.core.frame import DataFrame
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class yiDundriver(object):
    def __init__(self, url, time2wait=10):
        self.chromeOptions = webdriver.ChromeOptions()
        self.url = url
        # 设置代理
        self.chromeOptions.add_argument("--proxy-server=http://218.240.53.53:8090")
        # 一定要注意，=两边不能有空格，不能是这样--proxy-server = http://202.20.16.82:10152
        self.browser = webdriver.Chrome(chrome_options = self.chromeOptions)
        self.browser.set_window_size(500,800)
        self.browser.implicitly_wait(10)
        self.browser.get(url)
        self.browser.implicitly_wait(5)
        self.wait = WebDriverWait(self.browser, time2wait)

    def __clickVerifyBtn(self):
        verify_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "btnCertificationpone")))
        verify_btn.click()

    def __slideVerifyCode(self):
        slider = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_slider')))
        ActionChains(self.browser).click_and_hold(slider).perform()
        slider_loc_x = slider.location["x"]
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "yidun_bg-img")))
        icon = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "yidun_jigsaw")))
        pic_width = img.size['width']
        icon_width = icon.size['width']
        img_tags = self.browser.find_elements_by_tag_name("img")
        img_url = img_tags[0].get_attribute("src")
        icon_url = img_tags[1].get_attribute("src")
        match_x = distance(img_url, icon_url, pic_width)
        if match_x == -1:
            raise Exception()

        slider_instance = getSlideInstance(pic_width, icon_width, match_x)
        tracks = get_tracks(slider_instance)

        for track in tracks:
            ActionChains(self.browser).move_by_offset(xoffset=track, yoffset=0).perform()
        else:
            ActionChains(self.browser).move_by_offset(xoffset=3, yoffset=0).perform()
            ActionChains(self.browser).move_by_offset(xoffset=-3, yoffset=0).perform()
            time.sleep(0.5)
            ActionChains(self.browser).release().perform()
        time.sleep(3)
        cur_loc_x = slider.location["x"]
        data = []
        if cur_loc_x > slider_loc_x:
            print("success")
            butt = self.browser.find_element_by_id('submit-btn')
            butt.click()
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            title = soup.find('title')
            print title
            if title.get_text() == '禁止访问':
                self.browser.quit()
                yiDundriver(self.url)
                return
            table = soup.find('table',{'class':'query_result_table'})
            tbody = table.find('tbody')
            titletds = tbody.find_all('td',{'valign':'top'})
            entitytds = tbody.find_all('span')
            data.append(True)
            TitleTexts = []
            dataTexts = []
            for titletd in titletds:
                TitleTexts.append(titletd.get_text())
            for entitytd in entitytds:
                dataTexts.append(entitytd.get_text())
            data.append(TitleTexts)
            data.append(dataTexts)
            return data
        else:
            data.append(False)
            return data

    def verifySlideCode(self,attempt_times=10):
        #尝试attempt_times次滑动验证，返回是否验证通过
        try:
            self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME,"yidun_tips__text"), r"向右拖动滑块填充拼图"))
            data = []
            for attempt in range(attempt_times):

                try:
                    data1 = self.__slideVerifyCode()
                    if data1[0]:
                        self.browser.quit()
                        return data1
                except Exception as e:
                    print(e)
                    ActionChains(self.browser).release().perform()
                    refresh = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "yidun_refresh")))
                    refresh.click()
                    time.sleep(0.6)
            data.append(False)
            return data
        except Exception:
            yiDundriver(self.url)

def getVin(dataTag,gid,pc):

    drv = yiDundriver('http://www.miit-eidc.org.cn/miitxxgk/gonggao/xxgk/queryCpData?dataTag='+dataTag+'&gid='+gid+'&pc='+pc+'')

    data = drv.verifySlideCode()

    return data