# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
import threading
import re
import uuid
import requests
import pymysql
from fake_useragent  import UserAgent
from retrying import retry
from concurrent.futures import ThreadPoolExecutor, as_completed,ProcessPoolExecutor
import openpyxl
import Queue
import redis
from NeCodeTest import findByCode

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from DBUtils.PooledDB import PooledDB
'''爬取cn357车辆信息'''
class getVehicleParam(threading.Thread):
    def __init__(self,queue,batch, time2wait=10):
        threading.Thread.__init__(self)
        print batch+'批次'
        self.pool = self.mysql_connection()
        pool = redis.ConnectionPool(host='localhost', port=6379)
        red = redis.Redis(connection_pool=pool)
        self.red = red
        self.batch = batch
        self.queue = queue
        self.thread_stop = False
        self.sleepCount = 0
        self.defeatCount =0
        self.defeatFlag = True

    def mysql_connection(self):
        maxconnections = 250  # 最大连接数
        pool = PooledDB(
            creator=pymysql,
            maxconnections=maxconnections,
            host='47.105.199.147',
            user='root',
            port=3306,
            passwd='123456',
            db='youjia',
            charset='utf8')
        return pool

    @retry(stop_max_attempt_number=10,wait_fixed=3)
    def getParam(self,param):
        conn = pymysql.connect(host="47.105.199.147", user="root",password="123456",database="youjia",charset='utf8')
        cursor = conn.cursor()
        #param = self.red.spop('/notice_'+self.batch+'vehicle')
        url = 'https://www.cn357.com'+param
        ua = UserAgent()
        useragent = ua.random
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': 'PHPSESSID=3dbde360e767047597e7ef94704528ea; __51cke__=; Hm_lvt_112d2d53b0bcc050dce49a7ee804554a=1570526543,1571126611; security_session_verify=84b7b4d85ad7609e8a7f87b9a1d3790a; __tins__2077028=%7B%22sid%22%3A%201571131338594%2C%20%22vd%22%3A%202%2C%20%22expires%22%3A%201571133141528%7D; __51laig__=17; Hm_lpvt_112d2d53b0bcc050dce49a7ee804554a=1571131342',
            'Host': 'www.cn357.com',
            'Referer': 'https://www.cn357.com/notice_323',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': useragent
        }
        response = requests.get(url,headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        listTable = soup.find('table',{'class','listTable itemTable uiLinkList'})
        trs = soup.find_all('tr')
        first = trs[1:22]
        data = []
        for tr in first :
            tds = tr.find_all('td')
            for td in tds :
                data.append(str(td.get_text()).decode(encoding='utf-8'))
        firstTitle =data[::2]
        firstEntity = data[1::2]
        second = trs[23:25]
        newengin = []
        if not len(second)==0:
            allengine = []
            entitysecond = second[1].find_all('td')
            for ti in entitysecond:
                s = str(ti)
                s = s.replace('<td>','')
                s = s.replace('</td>','')
                s = s.replace('<br/>',',')
                s = s.rstrip(',')
                engs = s.split(',')
                if not len(engs) == 1:
                    engs = filter(None, engs)
                allengine.append(engs)
                firstEntity.append(s.decode(encoding='utf-8'))
            if not len(allengine[0])==len(allengine[1]) or not len(allengine[3]) ==len(allengine[4]) or (not len(allengine[2]) == 1 and not len(allengine[2]) == len(allengine[1])):
                File = open('wrongengin.txt','a+')
                File.write(str(firstEntity[0])+'\n')
                File.close()
            else:
                for length in range(len(allengine[0])):
                    engine = []
                    for lenen in range(len(allengine)):
                        engine.append(allengine[lenen][0].decode(encoding='utf-8') if len(allengine[lenen])==1 else allengine[lenen][length].decode(encoding='utf-8'))
                    newengin.append(engine)
            end = trs[25:]
        else:
            firstTitle.append('发动机型号')
            firstTitle.append('发动机生产企业')
            firstTitle.append('发动机商标')
            firstTitle.append('排量')
            firstTitle.append('功率')
            for i in range(0,5):
                firstEntity.append('')
            end = trs[22:]
        newdata = []
        for tr in end :
            tds = tr.find_all('td')
            for td in tds :
                newdata.append(str(td.get_text()).decode(encoding='utf-8'))
        newfirstEntity = newdata[1::2]
        lowentity = firstEntity+newfirstEntity
        entity = []
        for i in lowentity:
            entity.append(re.sub('"','',i))
        vin = entity[19].split(',')
        if not entity[45].strip().isdigit():
            entity[45]=''
        rightengin = []
        for en in newengin:
            ri = []
            for n in en:
                ri.append(re.sub('"','',n))
            rightengin.append(ri)
        vincode = []
        for vi in vin:
            vincode.append(vi.rstrip('\r').decode(encoding='utf-8'))
        vehiclelibsqlvalue = '"," '.join(entity);
        try:
            vehiclelibsql = "INSERT INTO `youjia`.`vehicle_base_lib_copy1`(`vehicle_model`, `batch`, `brand`, `vehicle_type`, `rated_mass`, `total_mass`, `unladen_mass`, `fuel_type`, `emission_standard`, `axle_num`, `wheelbase`, `axle_load`, `spring_num`, `tyre_num`, `tyre_spec`, `approach_departure_angle`, `front_rear_suspensioin`, `front_tread`, `tread`, `vin_code`, `vehicle_length`, `vehicle_width`, `vehicle_height`, `trunk_length`, `trunk_width`, `trunk_height`, `max_speed`, `rated_pasenger`, `cab_pass_num`, `steering_form`, `total_quality_trailer`, `carrier_mass_utill_coe`, `semitrailer_saddle_max_load_bear`, `business_name`, `business_address`, `telephone_num`, `fax_num`, `post_code`, `chassis_one`, `chassis_two`, `chassis_three`, `chassis_four`, `engine_model`, `engine_manufacturer`, `engine_brand`, `displacement`, `power`, `remark`)" \
                            "values (%s)" %('"' + vehiclelibsqlvalue + '"')
            cursor.execute(vehiclelibsql)
            insert_id = cursor.lastrowid
            for neweng in rightengin:
                vehicleenginevalue = '"," '.join(neweng)
                vehicleenginesql = "INSERT INTO `youjia`.`vehicle_engine_lib`(`engine_model`, `engine_manufacturer`, `engine_brand`, `displacement`, `power`, `vehicle_model`,`batch`,`brand`,`vehicle_type`,`vehicle_id`) " \
                                   "VALUES (%s);" % ('"' + vehicleenginevalue + '","'+str(entity[0])+'","'+str(self.batch)+'","'+str(entity[2])+'","'+str(entity[3])+'","'+str(insert_id)+'"')
                cursor.execute(vehicleenginesql)
            for vin in vincode:
                vinsql ="INSERT INTO `youjia`.`vehicle_vin` (`vin`, `vehicle_model`,`batch`,`vehicle_id`) VALUES (%s);" %('"'+str(vin)+'","'+str(entity[0])+'","'+str(self.batch)+'","'+str(insert_id)+'"')
                cursor.execute(vinsql)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def toexcel(self):
        try:
            print '开始作业'
            while self.red.scard('/notice_'+self.batch+'vehicle') == 0 and self.defeatCount<2:
                self.defeatCount = self.defeatCount+1
                time.sleep(1)
            if self.defeatCount>=2:
                return False
            data = self.red.smembers('/notice_'+self.batch+'vehicle')
            for i in data:
                try:
                    self.getParam(i)
                except Exception as e:
                    print e
            return True
        except Exception as e:
            print e
    def run(self):
        while not self.thread_stop:
            tasks = []
            while not self.queue.empty():
                task = self.queue.get(block=True, timeout=2)# 接收消息
                self.queue.task_done()
                tasks.append(task)
            if len(tasks) >0:
                for task in tasks:
                    entity = task[0]
                    newengin = task[1]
                    vincode = task[2]
                    conn = pymysql.connect(host="47.105.199.147", user="root",password="123456",database="youjia",charset='utf8')
                    cursor = conn.cursor()
                    vehiclelibsqlvalue = '"," '.join(entity);
                    vehiclelibsql = "INSERT INTO `youjia`.`vehicle_base_lib_copy1`(`vehicle_model`, `batch`, `brand`, `vehicle_type`, `rated_mass`, `total_mass`, `unladen_mass`, `fuel_type`, `emission_standard`, `axle_num`, `wheelbase`, `axle_load`, `spring_num`, `tyre_num`, `tyre_spec`, `approach_departure_angle`, `front_rear_suspensioin`, `front_tread`, `tread`, `vin_code`, `vehicle_length`, `vehicle_width`, `vehicle_height`, `trunk_length`, `trunk_width`, `trunk_height`, `max_speed`, `rated_pasenger`, `cab_pass_num`, `steering_form`, `total_quality_trailer`, `carrier_mass_utill_coe`, `semitrailer_saddle_max_load_bear`, `business_name`, `business_address`, `telephone_num`, `fax_num`, `post_code`, `chassis_one`, `chassis_two`, `chassis_three`, `chassis_four`, `engine_model`, `engine_manufacturer`, `engine_brand`, `displacement`, `power`, `remark`)" \
                                    "values (%s)" %('"' + vehiclelibsqlvalue + '"')
                    cursor.execute(vehiclelibsql)
                    insert_id = conn.insert_id()
                    for neweng in newengin:
                        vehicleenginevalue = '"," '.join(neweng)
                        vehicleenginesql = "INSERT INTO `youjia`.`vehicle_engine_lib`(`engine_model`, `engine_manufacturer`, `engine_brand`, `displacement`, `power`, `vehicle_id`) " \
                                           "VALUES (%s)" % ('"' + vehicleenginevalue + '","'+str(insert_id)+'"')
                        cursor.execute(vehicleenginesql)
                    for vin in vincode:
                        vinsql ="INSERT INTO `youjia`.`vehicle_vin` (`vin`, `vehicle_id`) VALUES (%s)" %('"'+str(vin)+'","'+str(insert_id)+'"')
                        cursor.execute(vinsql)
                    conn.commit()
                print("work finished!")
                # 完成一个任务
            print("Nothing to do! I will go home!")
            break
    def stop(self):
        self.thread_stop = True
def realmain(num):
    q = Queue.Queue()
    allbegin = time.time()
    g = getVehicleParam(q,num)
    flag = g.toexcel()
    time.sleep(1)                                  # 将队列加入类中
    allend = time.time()
    alltime = allend - allbegin
    File = open('over.txt','a+')
    File.write(str(num)+'\n')
    print (str(num) + 'batchalltime:',alltime)


if __name__ == '__main__':
    print 'begin find'
    executor = ProcessPoolExecutor(max_workers=50)
    all_task = [executor.submit(realmain,str(i)) for i in range(2,324)]