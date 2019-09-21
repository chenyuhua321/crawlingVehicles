# -*- coding: utf-8 -*-
import time
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from realGetVin import getVin
from threading import Thread
import codecs
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import openpyxl
chromeOptions = webdriver.ChromeOptions()
# 设置代理
chromeOptions.add_argument("--proxy-server=http://218.240.53.53:8090")
# 一定要注意，=两边不能有空格，不能是这样--proxy-server = http://202.20.16.82:10152
driver = webdriver.Chrome(chrome_options = chromeOptions)
driver.get('https://www.baidu.com/')
driver.implicitly_wait(5)
wait = WebDriverWait(driver, 10)

soup = BeautifulSoup(driver.page_source, 'html.parser')
title = soup.find('title')
print title
print title.get_text()
if title.get_text() == '百度一下，你就知道':
    print 1