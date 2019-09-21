#coding=utf-8
import pandas
import sys
import codecs
import random
reload(sys)
sys.setdefaultencoding('utf8')
import requests
from bs4 import BeautifulSoup


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
}
f = codecs.open(unicode("vin码",'utf-8'),"r",encoding='utf-8')   #设置文件对象
vindatas = f.readlines()  #直接将文件中按行读到list里，效果与方法2一样
f.close()

httpdatasf = codecs.open(unicode("http代理ip",'utf-8'),"r",encoding='utf-8')   #设置文件对象
httpdatas = httpdatasf.readlines()  #直接将文件中按行读到list里，效果与方法2一样
httpdatasf.close()

httpsdatasf = codecs.open(unicode("https代理ip",'utf-8'),"r",encoding='utf-8')   #设置文件对象
httpsdatas = httpsdatasf.readlines()  #直接将文件中按行读到list里，效果与方法2一样
httpsdatasf.close()

requests.adapters.DEFAULT_RETRIES = 5
s = requests.session()
s.keep_alive = False #设置不保持连接，否则会未关闭的连接太多报错
s.proxies = {"https": random.choice(httpsdatas) , "http": random.choice(httpdatas) }#代理ip 获取网址http://www.zdaye.com/FreeIPlist.html
count = 0
for vindata in vindatas:
    url = 'http://www.yiparts.com/vin?type=vin&keyword='+vindata # 根据vin码查车辆信息
    print url
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        MarkDiffTr = soup.find('tr',{'class','MarkDiffTr'})
        try:
            markDiffths = MarkDiffTr.find_all('td')
            for markDiffth in markDiffths:
                print markDiffth.get_text()
                count + 1
                if count>3:
                    count =0
                    s.proxies = {"https": random.choice(httpsdatas) , "http": random.choice(httpdatas) }
        except AttributeError:
            print vindata+'没有查到vin码信息'
            s.proxies = {"https": random.choice(httpsdatas) , "http": random.choice(httpdatas) }
    else:
        s.proxies = {"https": random.choice(httpsdatas) , "http": random.choice(httpdatas) }