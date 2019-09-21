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
from concurrent.futures import ThreadPoolExecutor
import openpyxl
import pymysql
import portalocker

import sys
reload(sys)
sys.setdefaultencoding('utf8')
'''爬取工信部车辆信息'''
class findVin(object):
    def __init__(self, time2wait=10):
        self.chromeOptions = webdriver.ChromeOptions()
        # 设置代理
        self.chromeOptions.add_argument("--proxy-server=http://218.240.53.53:8090")
        # 一定要注意，=两边不能有空格，不能是这样--proxy-server = http://202.20.16.82:10152
        self.driver = webdriver.Chrome(chrome_options = self.chromeOptions)
        self.driver.get('http://www.miit-eidc.org.cn/miitxxgk/gonggao/xxgk/queryByPc?pc=173&querylb=cp&qyinfolb=')
        self.driver.implicitly_wait(5)
        self.wait = WebDriverWait(self.driver, time2wait)

        self.driver.find_element_by_id("query_qymc_input").send_keys(u"公司")
        self.driver.find_element_by_id("query_button").click()
        self.count =1
        self.vehicount =1

    def printclick(self,allTypes):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        query_result = soup.find('div',{'id':'query_result'})
        d = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'query_page_count')))
        pagesize = int(soup.find('input', {'id':'query_page_count'})['value'])
        pagenow = '0'
        while int(pagenow) != self.count:
            try:
                e = WebDriverWait(self.driver, 10,0.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'query_result_now_page')))
                pagenow = e.text
            except Exception:
                time.sleep(1)
                e = WebDriverWait(self.driver, 10,0.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'query_result_now_page')))
                pagenow = e.text
        tbody = query_result.find('tbody')
        trs = tbody.find_all('tr')
        alltypeFile = open("173alltype.txt", "a+")
        Num = []
        Id = []
        batch = []
        for tr in trs:
            tds = tr.find_all('td')
            td = tds[3]
            a = td.find('a')
            if a != None:
                hrefs = re.findall('"([^"]+)"', a['href'])
                Num.append(hrefs[0])
                Id.append(hrefs[1])
                batch.append(hrefs[2])
                alltypeFile.write(hrefs[0]+" "+hrefs[1]+" "+hrefs[2]+"\n")
        alltypeFile.close()
        allType = []
        allType.append(Num)
        allType.append(Id)
        allType.append(batch)
        allTypes.append(allType)
        if(pagesize != self.count):
            input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'query_goto_page')))
            #input = driver.find_element_by_id('query_goto_page')
            input.clear()
            self.count = self.count +1
            input.send_keys(self.count)
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, 'GO'))).click()
            #driver.find_element_by_link_text('GO').click()
            self.printclick(allTypes)
        else:
            print len(allTypes)
        return allTypes

    def finVin(self,ws,tag,gid,batch):
        connent = pymysql.connect(host='localhost', user='root', passwd='123456', db='youjia', charset='utf8mb4')
        cursor = connent.cursor()

        print self.vehicount
        self.vehicount+1
        time_begin = time.time()
        vehicledata = None
        while vehicledata == None :
            vehicledata = getVin(tag,gid,batch)
        if vehicledata != None:
            while len(vehicledata)<3:
                vehicledata = getVin(tag,gid,batch)
        print vehicledata
        time_end = time.time()
        alltime = time_end - time_begin
        print ('time:',alltime)
        title = []
        entity = []
        for vehi in vehicledata[1]:
            title.append(vehi.decode('utf-8'))
        for realdata in vehicledata[2]:
            entity.append(realdata.decode('utf-8'))
        s = str(entity[0:41]).decode('utf-8')
        s = s.replace('[','')
        s =s.replace(']','')
        sql = "insert into 173vehicle values("+s.decode('utf-8')+")"
        print(sql)
        cursor.execute(sql)
        connent.commit()
        print len(title)
        print len(entity)
        ws.append(title)
        ws.append(entity)


    def toexcel(self,data):
        wbo = openpyxl.Workbook()
        ws2 = wbo.create_sheet('173vehicle')
        wbo.save('173allvehicle.xlsx')
        tag = []
        gid =[]
        pc = []
        for da in data:
            for ln in range(len(da[0])):
                tag.append(da[0][ln])
                gid.append(da[1][ln])
                pc.append(da[2][ln])
        print len(tag)
        with ThreadPoolExecutor(10) as executor1:
            for lend in range(len(tag)):
                wb = openpyxl.load_workbook('173allvehicle.xlsx')
                #portalocker.flock(wb.fileno(), portalocker.LOCK_EX)
                ws = wb['173vehicle']
                executor1.submit(self.finVin,ws,tag[lend],gid[lend],pc[lend])
                wb.save('173allvehicle.xlsx')
                #portalocker.flock(wb.fileno(),portalocker.LOCK_UN)


if __name__ == '__main__':
    a = findVin()
    alltype = []
    time.sleep(1)
    allbegin = time.time()
    data = a.printclick(alltype)
    a.toexcel(data)
    allend = time.time()
    alltime = allend - allbegin
    print ('alltime:',alltime)



