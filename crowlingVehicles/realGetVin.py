# -*- coding: utf-8 -*-
from selenium import webdriver
import json
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from concurrent.futures import ThreadPoolExecutor, as_completed,ProcessPoolExecutor
import xlsxwriter
from xlwt import *
from image_match import distance
from image_match import get_tracks
from image_match import getSlideInstance
from bs4 import BeautifulSoup
import redis
from fake_useragent  import UserAgent
import random
import pandas

from pandas.core.frame import DataFrame
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class yiDundriver(object):
    def __init__(self, url, time2wait=10):

        '''self.firefoxOptions.add_argument('Accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3"')
        self.firefoxOptions.add_argument('Accept-Encoding="gzip, deflate"')
        self.firefoxOptions.add_argument('Accept-Language="zh-CN,zh;q=0.9,en;q=0.8"')
        self.firefoxOptions.add_argument('Proxy-Connection="keep-alive"')
        self.firefoxOptions.add_argument('Referer="http://www.miit-eidc.org.cn/miitxxgk/gonggao/xxgk/queryByPc?pc=173&querylb=cp&qyinfolb="')'''
        '''self.firefoxOptions =webdriver.FirefoxOptions()
        self.firefoxOptions.add_argument("user-data-dir=selenium")
        self.firefoxOptions.add_argument("")
        self.browser = webdriver.Firefox(firefox_options= self.firefoxOptions)'''
        #self.browser = webdriver.Edge()
        '''self.firefoxOptions = webdriver.FirefoxOptions()'''

        self.browser = webdriver.Chrome()

        #options.add_argument('user-agent="Mozilla/5.0 (iPod; U; CPU iPhone OS 2_1 like Mac OS X; ja-jp) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5F137 Safari/525.20"')
        #self.browser = webdriver.Chrome(chrome_options= self.chromeOptions)
        self.url = url
        #self.firefoxOptions = webdriver.FirefoxOptions()
        self.browser.set_window_size(500,800)
        self.browser.implicitly_wait(10)

        '''self.browser.get("http://www.miit-eidc.org.cn/miitxxgk/gonggao/xxgk/queryByPc?pc=173&querylb=cp&qyinfolb=")
        js = 'window.open("'+url+'");'
        self.browser.execute_script(js)
        handles = self.browser.window_handles
        self.browser.switch_to_window(handles[1])'''
        self.browser.get(url)
        with open("cookies.json", "r") as fp:
            cookies = json.load(fp)
        for cookie in cookies:
            # cookie.pop('domain')  # 如果报domain无效的错误
            self.browser.add_cookie(cookie)
        print self.browser.get_cookies()
        self.browser.delete_all_cookies()
        self.browser.implicitly_wait(5)
        self.count = 0
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
        self.wait.until(EC.presence_of_element_located((By.NAME, "NECaptchaValidate")))
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        yidun_tips__text = soup.find('input',{'name':'NECaptchaValidate'})
        yidun_tips__textvalue = yidun_tips__text['value']
        print yidun_tips__text['value']
        tips = yidun_tips__text['value']
        if len(tips) >1:
            pool = redis.ConnectionPool(host='localhost', port=6379)
            red = redis.Redis(connection_pool=pool)
            red.sadd('NECaptchaValidate',str(tips))
            print '存入redis'
        '''if len(yidun_tips__textvalue) > 1:
            print("success")
            butt = self.browser.find_element_by_id('submit-btn')
            butt.click()
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "query_result_table")))
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            title = soup.find('title')
            print title
            if title.get_text() == '禁止访问':
                self.browser.close()
                a = yiDundriver(self.url)
                a.verifySlideCode()
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
            return data'''

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
                    print (e)
                    soup = BeautifulSoup(self.browser.page_source, 'html.parser')
                    yidun_tips__text = soup.find('span',{'class':'yidun_tips__text'})
                    if yidun_tips__text.get_text() == '失败过多，点此重试':
                        print '失败过多'
                        self.browser.quit()
                        data.append(False)
                        return data
                    ActionChains(self.browser).release().perform()
                    refresh = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "yidun_refresh")))
                    refresh.click()
                    time.sleep(0.6)
            self.browser.quit()
            data.append(False)
            return data
        except Exception as e:
            print (e)
            self.browser.quit()
            a = yiDundriver(self.url)
            a.verifySlideCode()
def getVin(n):
    print n
    time.sleep(3)
    drv = yiDundriver('http://www.miit-eidc.org.cn/miitxxgk/gonggao/xxgk/queryCpData?dataTag=D&gid=1240848&pc=173')
    while True:
        data = drv.verifySlideCode()

    #return data
if __name__ == '__main__':
    executor = ThreadPoolExecutor(max_workers=5)
    #all_task = [ executor.submit(self.finVin,tag[lent],gid[lent],pc[lent]) for lent in range(len(tag))]
    all_task = [ executor.submit(getVin,n) for n in range(0,10000)]
    for future in as_completed(all_task):
        data = future.result()
        print("in main: get page {}s success".format(data))
