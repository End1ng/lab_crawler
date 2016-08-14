# lab_crawler
实验系统报告下载
# 用法
```
usage: crawler_lab.py [options]

        作者：End1ng blog:end1ng.wordpress.com
        --------------------------------
        爆破并下载实验报告
        结果保存在 "lab1.0" 中
        每个人有一个独立文件夹
        文本在 "实验名/text.txt"
        压缩包在 "实验名/ok.zip" 中

optional arguments:
  -h, --help            help of the crawler_lab.py program
  --version             show program's version number and exit

auto arguments:
  --auto 你的学号           *输入你的学号，自动去寻找下载 ^_-

Necessary parameter:
  -u [用户名 [用户名 ...]], --user [用户名 [用户名 ...]]
                        *用户名 多个用空格分隔
  -U 文件名, --userfile 文件名
                        *用户名列表文件
  -p [密码 [密码 ...]], --pass [密码 [密码 ...]]
                        *密码 多个用空格分隔
  -P 文件名, --passfile 文件名
                        *密码列表文件

other arguments:
  --level level         程序运行级别:CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
```
