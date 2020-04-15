# -*- coding: utf-8 -*-
# @Time : 2020/4/2 10:14
# @Author : yangzishuang
# @Site : 
# @File : env_config.py
# @Software: PyCharm
import os
import time
import redis
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base  # 声明映射

# echo=True，就是把整个过程打印出来
engine = create_engine("mysql+pymysql://root:123456@127.0.0.1:3306/test", encoding='utf-8', echo=False)
# 生成ORM基类
Base = declarative_base()

# 实例化一个session会话
sql_session_ = sessionmaker(bind=engine)
sql_session = sql_session_()


class BaseModel(Base):
    __abstract__ = True
    __metadata__ = MetaData(bind=engine)
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }


# 域登陆接口需要用
env = {
    'dev': '\http://sys-sso.dev.com/ChamcSSO/LoginWin.ashx?appName=JsjPlatform&retURL=http://localhost:8082/loginPage',
    'test': 'http://tst-sys-sso.dev.com/ChamcSSO/LoginWin.ashx?appName=JsjPlatform&retURL=http://localhost:8082/loginPage',
    'jdemu': 'http://bak-sys-sso.chamc.com.cn/ChamcSSO/LoginWin.ashx?appName=JsjPlatform&retURL=http://localhost:8082/loginPage',
    'pro': 'http://sys-sso.chamc.com.cn/ChamcSSO/LoginWin.ashx?appName=JsjPlatform&retURL=http://localhost:8082/loginPage',
    'gdemu': 'http://sim-sys-sso.chamc.com.cn/ChamcSSO/LoginWin.ashx?appName=JsjPlatform&retURL=http://localhost:8082/loginPage'}

# app
settings = {
    "cookie_secret": "2wd7rtaw3i7feerfrtrhdrytrftey5e",
    "xsrf_cookies": False,
    "xsrf"
    "login_url": "/#/homePage$",
    'pycket': {
        'engine': 'redis',
        'storage': {
            'host': '127.0.0.1',
            'redis_password': '123456',
            'port': 6379,
            'db_sessions': 5,
            'db_notifications': 11,
            'max_connections': 2 ** 31,
        },
        'cookies': {
            'expires_days': 30,
            'max_age': 100
        },
    },
}

try:
    pool = redis.ConnectionPool(host="127.0.0.1", port=6370)
    redis_connect = redis.Redis(connection_pool=pool)
except Exception as e:
    local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    logging.error(local_time + "redis connect wrong!!")

# 静态文件
BASE_DIR = os.path.abspath('..')
static_path = os.path.join(BASE_DIR, "static")
