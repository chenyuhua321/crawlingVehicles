#coding=utf-8
import json
import urllib
import random
import codecs
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import requests
from bs4 import BeautifulSoup
import redis


def findByCode(tag,gid,pc,NECaptchaValidate):
    '''爬取汽车之家车辆信息'''
    data = []
    url = 'http://www.miit-eidc.org.cn/miitxxgk/gonggao/xxgk/queryCpData' # 获取车辆品牌信息
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
                      'Content-Type': 'application/x-www-form-urlencoded'
    }
    httpdatasf = codecs.open(unicode("http代理ip",'utf-8'),"r",encoding='utf-8')   #设置文件对象
    httpdatas = httpdatasf.readlines()  #直接将文件中按行读到list里，效果与方法2一样
    httpdatasf.close()

    httpsdatasf = codecs.open(unicode("https代理ip",'utf-8'),"r",encoding='utf-8')   #设置文件对象
    httpsdatas = httpsdatasf.readlines()  #直接将文件中按行读到list里，效果与方法2一样
    httpsdatasf.close()
    requests.adapters.DEFAULT_RETRIES = 8
    s = requests.session()
    s.keep_alive = False #设置不保持连接，否则会未关闭的连接太多报错

    s.proxies = {"https": random.choice(httpsdatas) , "http": random.choice(httpdatas) }#代理ip 获取网址http://www.zdaye.com/FreeIPlist.html
    requestdata ='dataTag='+tag+'&gid='+gid+'&pc='+pc+'&NECaptchaValidate='+NECaptchaValidate+''
    r = requests.post(url,data=requestdata,headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
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
    print data
    return data