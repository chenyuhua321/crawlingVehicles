# -*- coding: utf-8 -*-
from stem import Signal
from stem.control import Controller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# 通过Tor切换ip
def switchIP():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)

# 获取代理的浏览器
def get_browser(PROXY = None):
    chrome_options = webdriver.ChromeOptions()
    if PROXY != None:
        chrome_options.add_argument('--proxy-server=SOCKS5://{0}'.format(PROXY)) # 代理
    chrome_options.add_argument('blink-settings=imagesEnabled=false') #不加载图片, 提升速度
    chrome_options.add_argument('--headless') #浏览器不提供可视化页面.
    executable_path='/Users/fewave/project/python/demo/chromedriver' #设置启动驱动
    return webdriver.Chrome(executable_path=executable_path, options=chrome_options)

def main():

    for x in range(5):
        switchIP()
        browser = get_browser('127.0.0.1:9050')
        browser.get('https://cip.cc')
        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        print('======第%d次请求=======' % (x+1))
    print(soup.find_all('pre'))
    browser.quit()


if __name__ == '__main__':
    main()
