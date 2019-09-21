# -*- coding:utf-8 -*-

import pymysql

list=['20','5','wangyan']

connent = pymysql.connect(host='localhost', user='root', passwd='123456', db='youjia', charset='utf8mb4')

cursor = connent.cursor()

s = str(list[0:3])
s =s.replace('[','')
s =s.replace(']','')
print s
print list[0:3]
sql= "insert into test values("+s+")"

print(sql)

cursor.execute(sql)

connent.commit()