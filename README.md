# crawlingVehicles
爬取车型数据
由于公司需要，也正好趁此机会学习下python。爬取了汽车之家网站的汽车车型数据

# 一、项目背景

本人是一名java程序员。最近公司需要建立一个车辆的基础信息库。需要去网络上爬取相关的数据。之前都是使用java来编写爬虫。一直以来呢都想学习一下python的相关知识，拓宽自己的知识面。之前对python算是零基础，正好有一个项目需求，趁这个机会呢，学习一下python的相关知识。所以使用了python来编写这个爬虫。所以这篇文章属于我在使用python编写爬虫的一份学习笔记。记录一下在使用python时遇到的一些难题和疑惑内容可能会有错误，编写的代码上规范也不足。希望以后能慢慢的长进。

# 二、项目环境
    
IDE：idea。由于是个java程序员，所以编译器也就没有下载PyCharm。听说很好用。但是人比较懒，还是以后idea实在用不顺手再专门换吧

python版本：2.7（为什么不用python3？我也不知道python版本2,3之间具体的区别。但是想着java的版本更新到12了。大家用的最普遍的还是java8，就选个老版本的下载了。很多疑惑留着以后慢慢解决吧，毕竟是个项目需求，先让项目跑起来再说hhh）

## 三、项目代码
前情提要完毕，接下来开始撸代码

首先我爬的是汽车之家的信息。一共分三步

```
import requests
from bs4 import BeautifulSoup
```
主要使用了两个模块，使用requests可以模拟浏览器的请求，类似于java里的httpclient。Beautiful Soup 是一个可以从 HTML 或 XML 文件中提取数据的 Python 库可以用来解析我们爬取到的网页信息。
python里安装相关模块非常的简单。在控制台输入pip install ***相关模块就可以安装使用了。
在 [https://pypi.org/project]()可以搜索你想要的安装的模块获得对应的命令



![](https://user-gold-cdn.xitu.io/2019/9/22/16d597260eaff039?w=1445&h=341&f=png&s=42208)

下面是我爬取汽车之家网页信息的开始部分代码，也就是请求的部分。一共三个网址，分别第一个**url**是获取车辆品牌信息，这个网页有所有的车辆品牌信息，第二个**typeUrl**是每个品牌具体的型号信息。第三个**messageUrl**是每款型号的具体配置信息。有了这三个网址，其实大家就可以用自己熟悉的语言去爬取我们想要的所有的车辆信息了（其实没有所有的，比如车辆vin码信息。正是为了这个信息，我后面放弃了爬取汽车之家的信息，又去爬取了工信部的车辆信息。那个爬取的难度更加的大。）

```
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
```

http代理和https代理是我在网上找到的一些免费的代理ip（如下图）。因为爬虫爬网站信息毕竟是很多网站都不喜欢的事情。为了防止IP被封，我们需要设置一些代理IP去发送请求。通过request获取session，然后在proxies里设置好http和https的代理就好了。IP代理获取地址可以在[]()http://www.zdaye.com/FreeIPlist.html 这个网站找到。每个IP存活的时间有长有短。为了防止你在爬虫的时候时不时IP就不可用了，优先采用那些存活时间久一点的IP。对请求加入header，可以让我们的请求看起来更像是真实的网络请求。设置**keep——alive=False**这个比较重要，如果不设置的话，打开太多链接后就会报**Max retries exceeded with url**的错误。然后我们使用BeautifulSoup就可以获取到请求所返回的网页对象了。




![](https://user-gold-cdn.xitu.io/2019/9/23/16d59be3d5256a09?w=340&h=273&f=png&s=19173)

下面这段代码就是正式的爬取汽车之家车辆具体信息的三部曲了。首先我们将request返回信息用BeautifulSoup包装起来。BeautifulSoup的用法网上有很多例子，这里我不做具体一一表述。本身也就是一份学习笔记，也没有必要把用到的所有的东西一一清楚介绍。

我们所要爬取的车辆品牌信息在**id**名为‘div_ListBrand’的标签中。其中find方法查找的是一个元素，find_all方法查找的是一个结果集。所以要for循环每一个li标签就是每一个品牌名称的一个id号了。获取到这个li标签需要获取li标签里的值。这里id存在了‘v’元素对应的值里所以去li['v']就获取了id。如果你要获取li的value对应的值就是li['value']，以此类推。

我们获取了每个品牌对应的id后，需要查找这个品牌下的车型url2（额，这个网址没定义到全局里，由于赶进度，所以这个代码里可能有很多不规范的地方，命名啊，之类的。见谅，以后有空再改吧hh）这个请求呢返回的不是一个网页。而是一串json字符串。所以我们用了get请求，将response转出json进行处理。python获取json字符串里的值得方法跟之前获取网页标签元素的值类似。

之后我们将爬取到的车辆型号信息写入文件中，通过open方法可以创建文件，w表示写入，具体还有追加，读等等操作可以百度或者谷歌。

接下来的操作跟之前的也一样，我们将车辆型号id加到typeUrl后，获取车辆型号信息。最后呢由于每款型号又具体再有细分。本来我也是像请求获取具体车辆型号的网页信息然后解析的。当我解析之后发现，我需要的数据所在的div是空的。这是由于这些数据都是动态渲染上去的。在此，我们有两种解决办法，一个是这次使用的办法，打开chrome控制台，打开network标签，找到对应获取车辆型号具体数据的请求。在这里我找到了获取后台数据的请求就是messageUrl了。然后同样采用get请求的方式得到json字符串。然后对字符串进行对应的处理
```
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
```
最后我们得到了车辆信息的具体信息，主要的参数放在了paramItems里。这里有些比较操蛋的是，这个json字符串里有些数据居然是直接带js样式的比如这个
`"value": "<span class='hs_kw0_configpl'></span>A3 2019款 Spo**rtback 35 TFSI 进取型 <span class='hs_kw1_configpl'></span>`

后来由于汽车之家没有我想要的车辆vin码信息。我转而爬取了工信部的车辆信息。所以这方面对json数据的处理我也没有花精力去做。如果想要得到干净的数据。我们还可以采取另一种方法，直接得到网页动态渲染后的数据。这也是我在爬取工信部车辆数据所采用的方法。就是利用了selenium模块来模拟真实的浏览器请求。同时工信部获取车辆具体数据的接口还需要过一个滑动验证码的验证，同样可以利用selenium模块进行破解。关于这一部分的记录，等我有空了下回再写吧，因为还有一些问题没有处理完，一个就是python的多线程追加写入文件，如何保证写入的数据的线程安全。不过相关代码已上传到github上：[https://github.com/chenyuhua321/crawlingVehicles]()



![](https://user-gold-cdn.xitu.io/2019/9/23/16d59f8c4c960e3a?w=1448&h=218&f=png&s=43080)

最后，学习一门新的语言还是让我非常的有探索的快乐。希望不断的记录下我学习中遇到的坑，让自己不断地更好的成长吧。！
