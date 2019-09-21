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
'''爬取汽车之家车辆信息'''
url = 'https://car.m.autohome.com.cn/' # 获取车辆品牌信息
typeUrl = 'https://m.autohome.com.cn/' # 车辆型号信息
messageUrl = 'https://car.m.autohome.com.cn/ashx/car/GetModelConfig2.ashx?ids=' #车辆具体信息
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
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
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')
tags = soup.find('div',{'id':'div_ListBrand'})
File = open("vehicle.txt", "w")
ullist = tags.find_all('ul')
for link in ullist:
    lilist = link.find_all('li')
    for li in lilist:
        url2 ='https://car.m.autohome.com.cn/ashx/GetSeriesByBrandId.ashx?b=' + li['v']
        response = requests.request("GET", url2, headers=headers)
        data = response.json()
        ary = data['result']
        arry = ary['sellSeries']
        for sell in arry:
            File.write(str(sell['Id']) +'  '+str(sell['name']) +'\n')
            SeriesItems = sell['SeriesItems']
            for SeriesItem in SeriesItems:
                File.write(str(SeriesItem['id'])+' '+str(SeriesItem['name']) +'\n')
                typeRes = requests.get(typeUrl+str(SeriesItem['id']), headers=headers)
                typeSoup = BeautifulSoup(typeRes.text, 'html.parser')
                typeTags = typeSoup.find('div',{'class':'summary-cartype'})
                typeDivs = typeTags.find_all('div',{'class':'fn-hide'})
                for typeDiv in typeDivs:
                    typeUls = typeDiv.find_all('ul')
                    for typeUl in typeUls:
                        typeLis = typeUl.find_all('li')
                        for typeLi in typeLis:
                            print messageUrl+str(typeLi['data-modelid'])
                            print typeLi.find('a',{'class':'caption'}).get_text()
                            File.write(typeLi.find('a',{'class':'caption'}).get_text()+'\n')
                            messageResponse = requests.request("GET", messageUrl+str(typeLi['data-modelid']), headers=headers)
                            messageData = messageResponse.json()
                            baseData = messageData['data']
                            baseJson = json.loads(baseData)
                            baikeconfigpar = baseJson['baikeconfigpar']
                            config = baseJson['config']
                            configbag = baseJson['configbag']
                            param = baseJson['param']
                            search = baseJson['search']
                            File.write(json.dumps(baikeconfigpar,ensure_ascii=False)+'\n')
                            File.write(json.dumps(config,ensure_ascii=False)+'\n')
                            File.write(json.dumps(param,ensure_ascii=False)+'\n')
                            File.write(json.dumps(configbag,ensure_ascii=False)+'\n')
                            File.write(json.dumps(search,ensure_ascii=False)+'\n')
File.close()





