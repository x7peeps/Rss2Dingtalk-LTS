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
import signal
import requests
import socket
import ssl
from requests.packages import urllib3

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context



urllib3.disable_warnings()
socket.setdefaulttimeout(10)
DD_WEBHOOK = ''  #  钉钉机器人自定义webhook填写
DD_SECRET = ''  # 创建机器人勾选“加签”选项时使用
cu=db.cursor()


if DD_WEBHOOK =="" or DD_SECRET == '':
    print("please recheck DD_WEBHOOK and DD_SECRET in rss.py config for dingtalk rob webhook.")
    exit()

class RssRobot:
    def __init__(self):
        try:
            self.robot = DingtalkChatbot(DD_WEBHOOK,pc_slide=False, secret=DD_SECRET) 
        except Exception as _:
            print("[-]RssRobot init Error:"+str(_))
    def parse_rss(self):
        rss_list= cu.execute('SELECT t1.id, t1.feed, t1.cover, t1.title, t1.url FROM rss AS t1' )       
        rss_history_list = []     
        try:
            today=datetime.date.today() 
            oneday=datetime.timedelta(days=1) 
            yesterday=today-oneday
            post_url_list = [rss_history.url for rss_history in History.select().where(History.publish_at >= yesterday)] # 查询当天的历史记录
            print("[#]近2日历史记录条目 : "+str(len(post_url_list)))
        except Exception as _:
            print(_)
        for rss in rss_list:
            rss_history_list=[]
            print("[+]Begin : "+str(rss[1]))
            try:
                try:
                    html = requests.head(str(rss[1]), timeout=10,verify=False) 
                    respone_code=html.status_code  
                    feed_test = feedparser.parse(str(rss[1]),agent="Mozilla/5.0 (X11; Linux x86) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17")
                    if respone_code==200 or feed_test.entries!=[]:
                        print("[+]connectable test pass.")
                    else: 
                        print("[!]connectable test faile response code:"+str(respone_code))
                        continue
                except Exception as _:
                    if "timed out" in repr(_):
                        continue
                    if "Connection aborted" in repr(_):
                        continue
                    else:
                        print("[!]connectable test error: "+str(_))
                md_msg_text="## **"+rss[3]+":**\n"
                md_msg=""
                feedparser.USER_AGENT = "Mozilla/5.0 (X11; Linux x86) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17"                
                feed = feedparser.parse(rss[1],agent="Mozilla/5.0 (X11; Linux x86) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17")                  
                new_ms_num=0
                for entry in feed.entries:
                    if entry.link not in post_url_list and self.is_today(entry): # 修改逻辑只要判断数据库中没有的就推送
                        try:print("[-]feed entry:"+str(entry)[:50]);print("[RSS]资源类型判断:")
                        except:pass
                        try:print("[RSS]entry.title: "+str(entry.title));ENTRY_TITLE_FLAG=1;ENTRY_title=str(entry.title)
                        except:ENTRY_TITLE_FLAG=0;ENTRY_title="";pass
                        try:print("[RSS]entry.link: "+str(entry.link));ENTRY_LINK_FLAG=1;ENTRY_link=str(entry.link)
                        except:ENTRY_LINK_FLAG=0;ENTRY_link="";pass
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

                        try:print("[-]ENTRY_TITLE_FLAG:"+str(ENTRY_TITLE_FLAG))
                        except Exception as _:print("[ENTRY_TITLE_FLAG error]"+str(_));pass
                        try:print("[-]ENTRY_LINK_FLAG:"+str(ENTRY_LINK_FLAG))
                        except Exception as _:print("[ENTRY_LINK_FLAG error]"+str(_));pass
                        try:print("[-]ENTRY_PUBLISHED_FLAG:"+str(ENTRY_PUBLISHED_FLAG))
                        except Exception as _:print("[ENTRY_PUBLISHED_FLAG error]"+str(_));pass
                        try:print("[-]ENTRY_UPDATE_FLAG:"+str(ENTRY_UPDATE_FLAG))
                        except Exception as _:print("[ENTRY_UPDATE_FLAG error]"+str(_));pass
                        try:print("[-]ENTRY_PUBLISHED_PARSED_FLAG:"+str(ENTRY_PUBLISHED_PARSED_FLAG))
                        except Exception as _:print("[ENTRY_PUBLISHED_PARSED_FLAG error]"+str(_));pass
                        try:print("[-]ENTRY_PUBDATE_FLAG:"+str(ENTRY_PUBDATE_FLAG))
                        except Exception as _:print("[ENTRY_PUBDATE_FLAG error]"+str(_));pass
                        try:print("[-]ENTRY_DESCRIPTION_FLAG:"+str(ENTRY_DESCRIPTION_FLAG))
                        except Exception as _:print("[ENTRY_DESCRIPTION_FLAG error]"+str(_));pass
                        try:print("[-]ENTRY_CONTENT_FLAG:"+str(ENTRY_CONTENT_FLAG))
                        except Exception as _:print("[ENTRY_CONTENT_FLAG error]"+str(_));pass
                        try:print("[-]ENTRY_SUMMARY_FLAG:"+str(ENTRY_SUMMARY_FLAG))
                        except Exception as _:print("[ENTRY_SUMMARY_FLAG error]"+str(_));pass
                        
                        if (ENTRY_TITLE_FLAG==1 and ENTRY_LINK_FLAG==1 and ( ENTRY_PUBLISHED_FLAG==1 or ENTRY_PUBLISHED_PARSED_FLAG==1 or ENTRY_UPDATE_FLAG==1 or ENTRY_PUBDATE_FLAG==1 )):
                            if (ENTRY_DESCRIPTION_FLAG==1 or ENTRY_CONTENT_FLAG==1 or ENTRY_SUMMARY_FLAG==1):
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
                if new_ms_num > 0:    
                    try:     
                        self.robot.send_markdown(title=rss[3],text=md_msg_text)
                        with db.atomic():
                            History.bulk_create(rss_history_list, batch_size=10)
                            print("   [#]histroy.blk_create:"+str(rss_history_list))  
                    except Exception as _:
                        print("   [!]send dingtalk Error :"+str(_))
                        print('   [-]repr(e):\t', repr(_))
                        print('   [-]e.message:\t', str(_))
                        print('   [-]traceback.print_exc():', traceback.print_exc())
                        print('   [-]traceback.format_exc():\n%s' % traceback.format_exc())
                        if "database is locked" in str(_):
                            db_ops()
                        pass
            except Exception as _:
                print('repr(e):\t', repr(_))
                print('e.message:\t', str(_))
                print('traceback.print_exc():', traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())

                print("   [-]URL "+rss[1]+" fetch error\n")
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
                if "Connection refused" in str(_):
                    ERROR_detail="连接拒绝"
                    ERROR_collect=str(_)
                # 处理database locked 异常情况
                # 1. 系统命令“fuser rss.db”查询rss.db占用情况，获取PID
                # 2. kill -9 PID删掉强制关闭进程
                if "database is locked" in str(_):
                    db_ops()
                print("[-]Error detail : "+str(ERROR_detail)+str(ERROR_collect))
                print("[-]Worker jump to next.")

    def db_ops():
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
                kill_pid=print(os.system('kill -9 %s'% os.getpid())) 
                pass
            print("[+]kill %s success."% (i))
        kill_pid=print(os.system('kill -9 %s'% os.getpid())) 
    def is_today(self, entry):
        today=datetime.date.today() 
        oneday=datetime.timedelta(days=1) 
        yesterday=today-oneday
        result=""
        try:
            if entry['updated']:
                result=dateparser.parse(entry['updated']).date() >= yesterday; return result
        except:pass
        try:
            if entry['published_parsed']:
                result=dateparser.parse(entry['published_parsed']).date() >= yesterday; return result
        except:pass        
        try:
            if entry['published']:
                result=dateparser.parse(entry['published']).date() >= yesterday; return result
        except:pass
        try:
            if entry['pubDate']:
                result=dateparser.parse(entry['pubDate']).date() >= yesterday; return result
        except:pass
        try:
            if result:
                # return result # 默认如果没有update则返回false，进行数据推送
                print("[+]isnew")
            # else:
            #     print("[-]istoday result :"+str(result))
        except Exception as _:
            print("[!]istoday test error:"+str(_))
            pass

    # ----markdown方法----
    def send_rss(self, rss_card_dict_m):
        for key in rss_card_dict_m:
            self.robot.markdown(rss_card_dict_m[key])

def send_rss():
    rss_bot = RssRobot()
    rss_bot.parse_rss()
    db.close()

if __name__ == '__main__':
    send_rss()