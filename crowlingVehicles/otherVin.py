# -*- coding: utf-8 -*-

import requests
import demjson
import simplejson
import redis
import json
from concurrent.futures import ThreadPoolExecutor
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from fake_useragent  import UserAgent

class otherVin():
    def __init__(self,time2wait=10):
        self.count =1
        self.vehicount =1
        self.thread_stop = False

        self.url = 'http://www.chinacar.com.cn/Home/GonggaoSearch/GonggaoSearch/search_json?_dc=1569584115936'

    def getpage(self,batchid,page):
        ua = UserAgent()
        useragent = ua.random
        headers = {
            'Accept':'application/x-json;text/x-json;charset=utf-8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection':'keep-alive',
            'Content-Length': '244',
            'Content-Type':'application/x-www-form-urlencoded',
            'Cookie': 'PHPSESSID=511bpb2a85rho27t3flpehqlr1; Hm_lvt_6c1a81e7deb77ce536977738372f872a=1568626376,1569489687; rel_search=1; relv=1; vin_cookie=0506; news_view_ids=%7C88215%7C; BDPCIEXP=30; BDTUJIAID=f034d8969b597e7ffc0b29cd54e18993; clcp_list=437948%7C428562%7C428680%7C796132%7C795730%7C795736%7C; ck_gg_1=y; Hm_lpvt_6c1a81e7deb77ce536977738372f872a=1569579039',
            'Host' : 'www.chinacar.com.cn',
            'Origin':'http://www.chinacar.com.cn',
            'Referer':'http://www.chinacar.com.cn/ggcx_new/list.html',
            'User-Agent':useragent,
            'X-Requested-With':'XMLHttpRequest'
        }
        requestdata ='s0=&s1=&s2=&s3=&s4='+batchid+'&s5=&s6=&s7=&s8=&s9=&s10=&s11=&s12=&s13=&s14=&s15=&s16=&s17=&s18=&s20=0&s28=0&s29=0&s30=1' \
                     '&s_1=&ss_1=1&s_2=&ss_2=1&s_3=&ss_3=1&s_4=&ss_4=1&s_5=&ss_5=1&s_6=&ss_6=1&s_7=&ss_7=1&s_8=&ss_8=1&s_9=&ss_9=1&page='+page+'&start=0&limit=400'
        response = requests.post(self.url,data=requestdata,headers=headers)
        data = demjson.decode(response.text)
        #data = json.loads(response.text)
        topics = data['topics']
        totalCount =data['totalCount']
        return int(totalCount)/400 +1

    def getVehicle(self,batchid,page):
        print str(batchid)+'的'+str(page)+'页'
        ua = UserAgent()
        useragent = ua.random
        headers = {
            'Accept':'application/x-json;text/x-json;charset=utf-8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection':'keep-alive',
            'Content-Length': '244',
            'Content-Type':'application/x-www-form-urlencoded',
            'Cookie': 'PHPSESSID=511bpb2a85rho27t3flpehqlr1; Hm_lvt_6c1a81e7deb77ce536977738372f872a=1568626376,1569489687; rel_search=1; relv=1; vin_cookie=0506; news_view_ids=%7C88215%7C; BDPCIEXP=30; BDTUJIAID=f034d8969b597e7ffc0b29cd54e18993; clcp_list=437948%7C428562%7C428680%7C796132%7C795730%7C795736%7C; ck_gg_1=y; Hm_lpvt_6c1a81e7deb77ce536977738372f872a=1569579039',
            'Host' : 'www.chinacar.com.cn',
            'Origin':'http://www.chinacar.com.cn',
            'Referer':'http://www.chinacar.com.cn/ggcx_new/list.html',
            'User-Agent':useragent,
            'X-Requested-With':'XMLHttpRequest'
        }
        requestdata ='s0=&s1=&s2=&s3=&s4='+batchid+'&s5=&s6=&s7=&s8=&s9=&s10=&s11=&s12=&s13=&s14=&s15=&s16=&s17=&s18=&s20=0&s28=0&s29=0&s30=1' \
                                                   '&s_1=&ss_1=1&s_2=&ss_2=1&s_3=&ss_3=1&s_4=&ss_4=1&s_5=&ss_5=1&s_6=&ss_6=1&s_7=&ss_7=1&s_8=&ss_8=1&s_9=&ss_9=1&page='+page+'&start=0&limit=400'
        response = requests.post(self.url,data=requestdata,headers=headers)
        data = demjson.decode(response.text)
        topics = data['topics']
        pool = redis.ConnectionPool(host='localhost', port=6379)
        red = redis.Redis(connection_pool=pool)
        for topic in topics:
            tarid = topic['tarid']
            print tarid
            red.sadd(batchid+'vehicle',str(tarid))
            red.sadd(batchid+'allvehicle',str(tarid))

    def everyBatch(self,batch):
        print str(batch)+'开始'
        page = self.getpage(batchid=str(batch),page='1')
        print str(batch)+'有'+str(page)+'页'
        for lenth in range(page):
            self.getVehicle(str(batch),str(lenth+1))
        print str(batch) + '批次车辆代码完成'

if __name__ == '__main__':
    print '启动'
    o = otherVin()
    data = []
    for lenth in range(173,250):
        data.append(lenth+1)
    data.reverse()
    with ThreadPoolExecutor(1) as executor:
        [executor.submit(o.everyBatch,each) for each in data]

