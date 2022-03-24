# -*- encoding: utf-8 -*-
# prod rss2dingtalk
# Version LTS 0.2.0 
"""
Rss订阅到钉钉机器人
"""
import datetime
import feedparser
from dingtalkchatbot.chatbot import DingtalkChatbot, CardItem, ActionCard
import dateparser
from models import db, Rss, History
import os,sqlite3,time,sys,traceback
import ssl
# begin patch: disable SSL certificate verification
# @see: http://stackoverflow.com/a/35960702
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
# end patch
import signal
import requests
from requests.packages import urllib3
urllib3.disable_warnings()
# [fixing:超时问题]
import socket
socket.setdefaulttimeout(10)



DD_WEBHOOK = '' 
DD_SECRET = ''
cu=db.cursor()





class RssRobot:
    def __init__(self):
        # DD_WEBHOOK //dingtalk webhook
        # DD_SECRET  //dingtalk secure code
        # pc_slide
        #   False：在新窗口中打开
        #   True：在新标签中打开
        try:
            self.robot = DingtalkChatbot(DD_WEBHOOK,pc_slide=False, secret=DD_SECRET) 
        except Exception as _:
            print("[-]RssRobot init Error:"+str(_))
    # 返回rss字典rss_card_dict
    def parse_rss(self):
        rss_list= cu.execute('SELECT t1.id, t1.feed, t1.cover, t1.title, t1.url FROM rss AS t1')  # 查询数据库
        # rss_card_dict = {}
        rss_history_list = []   # rss history list 
        # 获取历史posturl
        try:
            today=datetime.date.today() 
            oneday=datetime.timedelta(days=1) 
            yesterday=today-oneday
            post_url_list = [rss_history.url for rss_history in History.select().where(History.publish_at >= yesterday)] # 查询当天的历史记录
            print("[#]近2日历史记录条目 : "+str(len(post_url_list)))
        except Exception as _:
            print(_)
 
        # 从rss_list中读取并处理rss保存到rss_card_dict中
        for rss in rss_list:
            # print("rss:")
            rss_history_list=[]
            # rss_card_dict={}
            print("[+]Begin : "+str(rss[1]))
            try:
                try:
                    # [fixing:dev-4-1] 提前访问一遍网站，如果返回200，则继续，否则直接跳出循环了
                    html = requests.head(str(rss[1]), timeout=10,verify=False)  # 用head方法去请求资源头
                    respone_code=html.status_code  
                    feed_test = feedparser.parse(str(rss[1]),agent="Mozilla/5.0 (X11; Linux x86) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17")

                    if respone_code==200 or feed_test.entries!=[]:
                        print("[+]connectable test pass.")
                    else: 
                        print("[!]connectable test faile response code:"+str(respone_code))
                        continue
                except Exception as _:
                    # [fixing]异常处理，“[Errno 60] Operation timed out”
                    if "timed out" in repr(_):
                        continue
                    else:
                        print("[!]connectable test error: "+str(_))
                # 提取rss中的title,url,cover列，分别对应标题，官网地址，封面地址
                # card_list = [CardItem(title=rss[3], url=rss[4], pic_url=rss[2])]  
                md_msg_text="## **"+rss[3]+":**\n"
                md_msg=""
                # print("   [#]card_list check:"+str(card_list))
                # 读取rss中feed订阅地址内容
                # 存在超时情况，需要通过socket默认超时解决
                feedparser.USER_AGENT = "Mozilla/5.0 (X11; Linux x86) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17"

                feed = feedparser.parse(rss[1],agent="Mozilla/5.0 (X11; Linux x86) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17")  
                print("    [+]check feeds 获取情况: "+str(feed)[:100])  
                # 获取feed订阅的rss中更新内容 
                new_ms_num=0
                for entry in feed.entries:
                    if entry.link not in post_url_list and self.is_today(entry): # 修改逻辑只要判断数据库中没有的就推送
                        try:print("    [-]feed entry:"+str(entry)[:50]);print("[RSS]资源类型判断:")
                        except:pass
                        try:print("[RSS]entry.title: "+str(entry.title));ENTRY_TITLE_FLAG=1;ENTRY_title=str(entry.title)
                        except:ENTRY_TITLE_FLAG=0;ENTRY_title="";pass
                        try:print("[RSS]entry.link: "+str(entry.link));ENTRY_LINK_FLAG=1;ENTRY_link=str(entry.link)
                        except:ENTRY_LINK=0;ENTRY_link="";pass
                        try:print("[RSS]entry.description: "+str(entry.description)[:100]);ENTRY_DESCRIPTION_FLAG=1;ENTRY_description=str(entry.description)[:100]
                        except:ENTRY_DESCRIPTION_FLAG=0;ENTRY_description="";pass
                        try:print("[RSS]entry.published: "+str(entry.published));ENTRY_PUBLISHED_FLAG=1;ENTRY_published=str(entry.published)
                        except:ENTRY_PUBLISHED_FLAG=0;ENTRY_published="";pass
                        try:print("[RSS]entry.published_parsed: "+str(entry.published_parsed));ENTRY_PUBLISHED_PARSED_FLAG=1;ENTRY_published_parsed=str(entry.published_parsed)
                        except:ENTRY_PUBLISHED_PARSED_FLAG=0;ENTRY_published_parsed="";pass
                        try:print("[RSS]entry.updated: "+str(entry.updated));ENTRY_UPDATE_FLAG=1;ENTRY_updated=str(entry.updated)
                        except:ENTRY_UPDATE_FLAG=0;ENTRY_updated="";pass
                        try:print("[RSS]entry.pubDate: "+str(entry.pubDate));ENTRY_PUBDATE_FLAG=1;ENTRY_pubDate=str(entry.pubDate)
                        except:ENTRY_PUBDATE_FLAG=0;ENTRY_pubDate="";pass
                        try:print("[RSS]entry.content[0].value: "+str(entry.content[0].value)[:100]);ENTRY_CONTENT_FLAG=1;ENRTY_CONTENT=str(entry.content[0].value)[:100]
                        except:ENTRY_CONTENT_FLAG=0;ENTRY_content="";pass
                        try:print("[RSS]entry.summary: "+str(entry.summary)[:100]);ENTRY_SUMMARY_FLAG=1;ENTRY_summary=str(entry.summary)[:100]
                        except:ENTRY_SUMMARY_FLAG=0;ENTRY_summary="";pass


                        new_ms_num+=1


                        if ENTRY_TITLE_FLAG==1 & ENTRY_LINK_FLAG==1 & ( ENTRY_PUBLISHED_FLAG==1|ENTRY_PUBLISHED_PARSED_FLAG==1|ENTRY_UPDATE_FLAG==1|ENTRY_PUBDATE_FLAG==1 ):
                            if ENTRY_DESCRIPTION_FLAG==1 | ENTRY_CONTENT_FLAG==1 | ENTRY_SUMMARY_FLAG==1:
                                n=0
                                while n<1:
                                    try:md_msg_text+="### ["+ENTRY_title+"]("+ENTRY_link+")\n"+ENTRY_description+"\n\n";n=n+1;continue
                                    except:pass
                                    try:md_msg_text+="### ["+ENTRY_title+"]("+ENTRY_link+")\n"+ENTRY_content+"\n\n";n=n+1;continue
                                    except:pass
                                    try:md_msg_text+="### ["+ENTRY_title+"]("+ENTRY_link+")\n"+ENTRY_summary+"\n\n";n=n+1;continue
                                    except:pass
                                m=0
                                while m<1:
                                    try:md_msg_text+=ENTRY_published+"\n\n";m=m+1;continue
                                    except:pass
                                    try:md_msg_text+=ENTRY_published_parsed+"\n\n";m=m+1;continue
                                    except:pass
                                    try:md_msg_text+=ENTRY_updated+"\n\n";m=m+1;continue
                                    except:pass
                                    try:md_msg_text+=ENTRY_pubDate+"\n\n";m=m+1;continue
                                    except:pass
                            else:
                                try:md_msg_text+="### ["+ENTRY_title+"]("+ENTRY_link+")\n"
                                except:pass
                            print("[+]md_msg_text check: "+md_msg_text[:100])
                            if entry.link!=None:
                                rss_history_list.append(History(url=entry.link)) # 用于存储数据库
                        else:
                            print("[-]FLAGS not sufficient.")
                            continue

                print("   [#]"+str(new_ms_num)+"条更新")
                # card_list>1则有更新
                if new_ms_num > 0:
                    # rss_card_dict[rss[3]] = card_list
                    # print("   [#]rss_card_dict:"+str(rss_card_dict))
                    # 先判断发送成功再入库
                    try:
                        self.robot.send_markdown(title=rss[3],text=md_msg_text)
                        with db.atomic():
                            History.bulk_create(rss_history_list, batch_size=10)
                            print("   [#]histroy.blk_create:"+str(rss_history_list))
                    except Exception as _:
                        print("   [!]send dingtalk or db Error :"+str(_))
                        pass

            except Exception as _:
                print("   [-]URL "+rss[1]+" fetch error\n")
                print('str(Exception):\t', str(Exception))
                print('str(e):\t\t', str(_))
                print('repr(e):\t', repr(_))
                print('e.message:\t', str(_))

                ERROR_detail=""
                ERROR_collect=str(_)
                if ("nodename nor servname provided" in str(_)) | ("Temporary failure in name resolution" in str(_)):
                    ERROR_detail="解析域名失败"
                    ERROR_collect=str(_)
                if "reset by peer" in str(_):
                    ERROR_detail="可能IP被封"
                    ERROR_collect=str(_)
                if "TLSV1_ALERT_PROTOCOL_VERSION" in str(_):
                    ERROR_detail="SSL异常"
                    ERROR_collect=str(_)
                # [fixing]异常处理，“str(e): <urlopen error [Errno 61] Connection refused>”
                if "Connection refused" in str(_):
                    ERROR_detail="连接拒绝"
                    ERROR_collect=str(_)
                # 处理database locked 异常情况
                # 1. 系统命令“fuser rss.db”查询rss.db占用情况，获取PID
                # 2. kill -9 PID删掉强制关闭进程
                if "database is locked" in str(_):
                    print("[-]database is locked begin deail with it:")
                    get_pid=str(os.popen("fuser rss.db").read()).replace(" ", "",1).split(" ")
                    print("[=]success get fuser rss.db PID:"+str(get_pid).replace(" ", "",1))
                    for i in reversed(get_pid):
                        print("[+]begin deail with %s"% i)
                        print("[+]get self pid:%s"% str(os.getpid()))
                        if i == "" or i==str(os.getpid()):
                            print("[+]pid %s passed."% str(os.getpid()))
                            continue
                        kill_pid=print(os.system('kill -9 %s'% i)) 
                        try: 
                            os.kill(i,signal.SIGKILL)
                        except Exception as _:
                            # print("[=]try os.kill(%s,signal.SIGKILL fail.)"%(str(i)))
                            kill_pid=print(os.system('kill -9 %s'% os.getpid())) 
                            pass
                        print("[+]kill %s success."% (i))
                    kill_pid=print(os.system('kill -9 %s'% os.getpid())) 
                print("[-]Error detail : "+str(ERROR_detail)+str(ERROR_collect))
                print("[-]Worker jump to next.")

        
        

    def is_today(self, entry):
        # print("[-]entry:"+str(entry))
        try:
            if entry['updated']:
                # print("[#]get date : "+str(dateparser.parse(entry['updated']).date()))
                # print("[#]today : "+str(datetime.today().date()))
                today=datetime.date.today() 
                oneday=datetime.timedelta(days=1) 
                yesterday=today-oneday
                result= dateparser.parse(entry['updated']).date() >= yesterday
                return result
        except Exception as _:
            pass
        try:
            if entry['published_parsed']:
                # print("[#]get date : "+str(dateparser.parse(entry['published_parsed']).date()))
                # print("[#]today : "+str(datetime.today().date()))
                result= dateparser.parse(entry['published_parsed']).date() >= yesterday#== datetime.today().date()
                return result
        except Exception as _:
            pass
        try:
            if entry['published']:
                # print("[#]get date : "+str(dateparser.parse(entry['published']).date()))
                # print("[#]today : "+str(datetime.today().date()))
                result= dateparser.parse(entry['published']).date() >= yesterday # == datetime.today().date()
                return result
        except Exception as _:
            pass
        try:
            if entry['pubDate']:
                print("[+]entry['pubDate']: "+str(entry['pubDate'].date()))
                result= dateparser.parse(entry['pubDate']).date() >= yesterday #== datetime.today().date()
                return result
        except Exception as _:
            pass
        # 如果前面都失败则返回true
        # print("[-]Error entry['update'] not useful, content of it :"+str(entry['updated']))
        try:
            if result:
                # return result # 默认如果没有update则返回false，进行数据推送
                print("[+]istoday")
            else:
                print("[-]istoday result :"+str(result))
        except Exception as _:
            print("[!]istoday test error:"+str(_))
        # return dateparser.parse(entry['updated']).date() == datetime.today().date() #test 3/3 



    # ----feed_card方法----
    def send_rss(self, rss_card_dict_m):
        for key in rss_card_dict_m:
            # print(key)
            self.robot.send_feed_card(rss_card_dict_m[key])

    # ----markdown方法----
    def send_rss(self, rss_card_dict_m):
        for key in rss_card_dict_m:
            # print(key)
            self.robot.markdown(rss_card_dict_m[key])

 

def send_rss():
    rss_bot = RssRobot()
    rss_bot.parse_rss()
    # * 数据库不用关闭，退出程序，系统会自动回收
    db.close()
 

if __name__ == '__main__':
    send_rss()