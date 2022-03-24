# models.py
# -*- encoding: utf-8 -*-
from peewee import *
import datetime

# 如果第一次运行需要运行python3 >import models.py >models.create_tables()
db = SqliteDatabase('rss.db')


class BaseModel(Model):
    class Meta:
        database = db


class Rss(BaseModel):
    feed = CharField(unique=True) # rss 源地址
    cover = CharField(max_length=255) # 封面 
    title = CharField(max_length=20) # rss 的标题
    url = CharField(max_length=255) # 官网地址 可选


class History(BaseModel):
    url = CharField(max_length=255)
    publish_at = DateField(default=datetime.datetime.now)


def create_tables():
    with db:
        db.create_tables([Rss, History])