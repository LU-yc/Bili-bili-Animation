import requests,re,sqlite3,time

class FANJU_information(object):
    #伪装请求头  UA等
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70"
                            ".0.3538.25 Safari/537.36 Core/1.70.3776.400 QQBro"
                            "wser/10.6.4212.400",
              "accept-language": "zh-CN,zh;q=0.9",
              "accept-encoding": "gzip, deflate, br"}
    def get_fanjuID(self,paimingleixxing,num):
        '''获取番剧id'''

        getid_start=time.perf_counter()

        #以下是哔哩哔哩索引排名信息的api地址
        #追番排名     &order=3
        self.url1 = 'https://api.bilibili.com/pgc/season/index/result?st=1&order=3' \
                    '&season_version=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1' \
                    '&season_month=-1&year=-1&style_id=-1&sort=0&season_type=1&pagesize=20&type=1&page={}'

        # 2评分排名   &order=4
        self.url2 = 'https://api.bilibili.com/pgc/season/index/result?st=1&order=4' \
                    '&season_version=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1' \
                    '&season_month=-1&year=-1&style_id=-1&sort=0&season_type=1&pagesize=20&type=1&page={}'

        # 3播放排名   &order=2
        self.url3 = 'https://api.bilibili.com/pgc/season/index/result?st=1&order=2' \
                    '&season_version=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1' \
                    '&season_month=-1&year=-1&style_id=-1&sort=0&season_type=1&pagesize=20&type=1&page={}'

        # 通过更改url实现不同检索的id爬取
        if paimingleixxing=='zhuifan':
            url=self.url1
            print('爬取追番排名，页数为:{}页--开始爬取--'.format(num))
        elif paimingleixxing=='pingfen':
            url=self.url2
            print('爬取评分排名，页数为:{}页--开始爬取--'.format(num))
        elif paimingleixxing=='bofan':
            url=self.url3
            print('爬取播放排名，页数为:{}页--开始爬取--'.format(num))
        else:
            raise Exception('能使用的参数只有，zhuifan，pingfen，bofan')


        fanjuid = re.compile('"season_id":(.*?),"season_type')

        # 存放番剧id的列表
        fanjuidlist = []

        for index in range(1,num+1):
            #通过对模板连接的重构，实现多页的爬取
            html = requests.get(url=url.format(index), headers=self.header)
            i = html.text


            y = fanjuid.findall(i)  # 番剧排行id(url对应的)

            for r in y:
                fanjuidlist.append(r)
        getid_end = time.perf_counter()
        print('爬取番剧ID成功,用时{}秒'.format(round(getid_end-getid_start,2)))
        return fanjuidlist

    def fanjudata(self,fanjuid_list):
        '''获取每个番剧的信息，返回列表   番名 评分  评分人数 硬币数 弹幕数 追番数 播放数'''

        getdata_start = time.perf_counter()
        # 编译  番名  的正则表达式
        www = re.compile('<meta name="keywords" content=".*?">')
        # 编译  评分  的正则表达式
        pingfen = re.compile('<div class="media-rating"><h4 class="score">.*?</h4>')
        # 编译  评分人数   的正则表达式
        pfrs = re.compile('<div class="media-rating"><h4 class="score">.*?</h4> <p>.*?</p>')
        # 编译  硬币数  的正则表达式
        ybi = re.compile('"coins":.*?,')
        # 编译  弹幕数   的正则表达式
        dmu = re.compile('"danmakus":.*?,')
        # 编译  追番数   的正则表达式
        zfa = re.compile('"follow":.*?,')
        # 编译  播放数   的正则表达式
        bfa = re.compile('"views":.*?}')

        #定义一个空的存所有爬取番剧信息的列表
        datalist = []

        #遍历番剧排名顺序的id
        for i in fanjuid_list:
            # 能获取到含 番名 评分，评分人数的地址模板 加上参数（番剧id）
            url = 'https://www.bilibili.com/bangumi/play/ss' + i
            # 能获取到含 硬币数 弹幕数，追番数 播放数 的地址模板
            url1 = 'https://api.bilibili.com/pgc/web/season/stat?season_id=' + i


            html = requests.get(url=url, headers=self.header)  # 获取到含番名 评分，评分人数
            i = html.text

            html1 = requests.get(url=url1, headers=self.header)  # 获取到含硬币 弹幕，追番 播放
            ii = html1.text

            qwqw = www.findall(i)[0][31:-2]  # 番名
            q = pingfen.findall(i)[0][44:-5]  # 评分
            q = float(q)
            w = pfrs.findall(i)[0][56:-7]  # 评分人数

            yb = ybi.findall(ii)[0][8:-1]  # 硬币数
            dm = dmu.findall(ii)[0][11:-1]  # 弹幕数
            zf = zfa.findall(ii)[0][9:-1]  # 追番数
            bf = bfa.findall(ii)[0][8:-1]  # 播放数

            #一部番剧的信息组成一个列表
            xx = [qwqw, str(q), w, yb, dm, zf, bf]

            #含所有番剧信息的列表（列表套娃）
            datalist.append(xx)

        getdata_end = time.perf_counter()
        print('爬取番剧信息成功,用时{}秒'.format(round(getdata_end-getdata_start,2)))

        return datalist

    def savedata(self,fanjuleixing,yeshu=1,savepath=r'blbl2.db'):
        '''将爬取到的番剧信息保存到指定位置数据库中'''

        getsave_start = time.perf_counter()

        id_data=self.get_fanjuID(fanjuleixing,yeshu)

        datalist=self.fanjudata(id_data)

        #打开或创建数据库
        conn = sqlite3.connect(savepath)

        print('打开数据库成功，即将插入数据，数据库位置为{}（默认路径为当前路径的blbl.db）'.format(savepath))
        #获取游标
        c = conn.cursor()
        #建表语句（if not exists 这个可以无表创表，有表跳过）
        sql = '''
            create table if not exists {}
            (id integer primary key autoincrement,
             name text not null,
             pingfen real not null,
             pfrenshu text not null,
             yingbishu int not null,
             danmushu int not null,
             zhuifanshu int not null,
             bofangshu int not null)

        '''.format(fanjuleixing)
        # 执行sql语句
        c = conn.execute(sql)

        #遍历番剧信息列表依次插入数据库
        for i in datalist:
            i[0] = '"' + i[0] + '"'
            i[2] = '"' + i[2] + '"'

            #插入数据库sql语句
            sql1 = '''
                insert into %s (name,pingfen,pfrenshu,yingbishu,danmushu,zhuifanshu,bofangshu)
                values (%s)

            ''' % (fanjuleixing,",".join(i))

            # 执行sql语句
            c.execute(sql1)
            #提交数据库操作
            conn.commit()

        c.close()
        #关闭数据库
        conn.close()
        getsave_end = time.perf_counter()
        print('存入数据库成功，用时{}秒'.format(round(getsave_end-getsave_start,2)))


if __name__ == '__main__':
    id = FANJU_information()
    #fanjuleixing：不同检索的id爬取   bofan   zhuifan   pingfen
    #yeshu：需要爬取的页数  默认为1
    #savepath：保存sqlite数据库文件的位置 默认当前目录的blbl2.db
    id.savedata(fanjuleixing="bofan",yeshu=1,savepath=r'blbl666.db')