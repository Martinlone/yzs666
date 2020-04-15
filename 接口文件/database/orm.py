# -*- coding: utf-8 -*-
# @Time : 2020/3/25 13:59
# @Author : yangzishuang
# @Site : 
# @File : database.py
# @Software: PyCharm

import datetime
from sqlalchemy import Column, String, Text, DateTime, DATETIME, Integer, Boolean
from config.env_config import BaseModel, Base, engine


# 首页热贴
class HomepageHotModel(BaseModel):
    __tablename__ = "t_homepage_hot"
    homepage_hot_id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)  # 帖子id
    homepage_hot_board_id = Column(String(600), nullable=False)  # 板块id，可以为""||"all" 表示全部板块
    homepage_hot_title = Column(String(4000), nullable=False)  # 帖子标题
    homepage_hot_author_name = Column(String(600), nullable=False)  # 作者名
    homepage_hot_author_profile = Column(String(600), nullable=False)  # 作者头像地址
    homepage_hot_last_reply_date = Column(DateTime, nullable=False, comment="最后回复时间", default=datetime.date.today())
    homepage_hot_type = Column(String(600), nullable=False)
    homepage_hot_reply_num = Column(Integer(), nullable=False, default=0)  # 回复条数
    homepage_hot_type_name = Column(String(600), nullable=False)  # 类型名
    homepage_hot_click = Column(Integer(), nullable=False, default=0)
    is_delete = Column(Boolean, nullable=False, server_default='0')


# 意见反馈
class FeadbackModel(BaseModel):
    __tablename__ = "t_feedback"
    feedback_id = Column(Integer(), primary_key=True, autoincrement=True)  # 序号
    feedback_user_account = Column(String(600), nullable=False)  # 用户账号
    feedback_org_id = Column(String(600), nullable=False)  # 公司id
    feedback_dept_id = Column(String(600), nullable=False)  # 部门id
    feedback_tele = Column(String(600), nullable=False)  # 联系方式
    feedback_email = Column(String(600), nullable=False)  # 邮箱
    feedback_content = Column(String(4000), nullable=False)  # 反馈意见
    feedback_save_time = Column(String(600), nullable=False)
    is_delete = Column(Boolean, nullable=False, server_default='0')


# 用户个人信息表 暂时不用
class UserInfoModel(BaseModel):
    __tablename__ = "t_user_info"
    user_info_id = Column(Integer(), primary_key=True, autoincrement=True)  # 序号
    user_info_user_account = Column(String(600), unique=True, nullable=False)  # 用户账号
    user_info_user_name = Column(String(600), nullable=False)  # 用户名字
    user_info_email = Column(String(600), nullable=False)  # 用户邮箱
    user_info_tele = Column(String(600), nullable=False)  # 用户联系方式
    user_info_org_id = Column(String(600), nullable=False)  # 用户机构id
    user_info_dept_id = Column(String(600), nullable=False)  # 用户部门id
    user_info_org_name = Column(String(600), nullable=False)  # 机构名称
    user_info_dept_name = Column(String(600), nullable=False)  # 部门名称
    is_delete = Column(Boolean, nullable=False, server_default='0')


# 刘路路部分

class User(BaseModel):
    __tablename__ = 'user'

    # 主键自增的int类型的id主键
    pk_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(20))  # 用户姓名
    user_profile = Column(String(100))  # 用户头像链接


class BoardTypes(BaseModel):
    __tablename__ = 'board_types'

    board_id = Column(String(20), primary_key=True)
    board_name = Column(String(20))  # 板块名


# 创建Post(帖子详情）表
class Post(BaseModel):
    __tablename__ = 'post_detail'

    # 主键自增的int类型的id主键
    pk_id = Column(Integer, primary_key=True, autoincrement=True)
    board_id = Column(String(20))  # 帖子所属模块id,是board_types的外键
    title = Column(String(100))  # 标题
    author_name = Column(String(20))  # 作者名
    author_profile = Column(String(100))  # 作者头像地址
    post_time = Column(DATETIME)  # 发帖时间
    content = Column(Text)  # 帖子内容
    image_url = Column(String(100))


# 创建Reply表
class Reply(BaseModel):
    __tablename__ = 'reply_detail'

    post_id = Column(Integer)  # 帖子id
    pk_id = Column(Integer, primary_key=True, autoincrement=True)  # 回复id
    title = Column(String(100))  # 帖子标题
    user_name = Column(String(20))  # 回复人姓名
    user_profile = Column(String(100))  # 回复人头像地址
    reply_time = Column(DATETIME)  # 回复时间
    content = Column(Text)  # 回复内容


# 杨鸿晋部分

class AchievementTypeModel(BaseModel):
    __tablename__ = 't_achievement_type'
    achievement_type_id = Column(Integer, primary_key=True, autoincrement=True)
    achievement_type_code = Column(String(255), unique=True, nullable=False)
    achievement_type_name = Column(String(255), nullable=False)
    is_delete = Column(Boolean, nullable=False, server_default='0')


class AchievementModel(BaseModel):
    __tablename__ = 't_achievement'
    achievement_id = Column(Integer, primary_key=True, autoincrement=True)
    achievement_type_code = Column(String(255), nullable=False, comment="成功类型")
    achievement_title = Column(String(1000), nullable=False, comment="成果标题")
    achievement_publish_time = Column(DateTime, nullable=False, comment="发布时间")
    achievement_source = Column(String(1000), nullable=False, comment="出处")
    achievement_abstract = Column(String(1000), nullable=False, comment="摘要")
    achievement_content = Column(String(65535), nullable=True, comment="内容")
    achievement_doc_path = Column(String(1000), nullable=True, comment="文档地址")
    gmt_create = Column(DateTime, nullable=False, comment="添加时间")
    read_count = Column(Integer, nullable=False, server_default='0', comment="阅读量")
    is_delete = Column(Boolean, nullable=False, server_default='0', comment="是否删除")


class AchievementPrivilegeModel(BaseModel):
    __tablename__ = 't_achievement_privilege'
    priv_id = Column(Integer, primary_key=True, autoincrement=True)
    user_account = Column(String(255), nullable=False, comment='用户账户')
    is_allowed = Column(Boolean, nullable=False, server_default='0', comment='是否有权限，1-有，0-无')
    is_delete = Column(Boolean, nullable=False, server_default='0', comment="是否删除")


if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    # create_all函数会先检查以上mysql表是否已经创建，若已经创建，则不会重新创建
    Base.metadata.create_all(engine)
