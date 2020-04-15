# -*- coding: utf-8 -*-
# @Time : 2020/3/25 15:55
# @Author : yangzishuang
# @Site : 
# @File : view.py
# @Software: PyCharm

__all__ = ["DateEncoder", "AddTypesHandler", "PostHandler",
           "UploadImageHandler", "ReplyHandler", "ReplyHandler2",
           "BoardHandler", "HomepageHandler", "OpinionHandler",
           "Login_addressHandler", "Get_Login_infoHandler",
           "HomeHandler", "AchievementTypeHandler",
           "AchievementListHandler", "AchievementPostPrivilegeHandler",
           "AchievementFilesHandler", "AchievementHandler",
           "AchievementDetailHandler", "AchievementDocHandler"]

import os
import jwt
import math
import json
import time
import logging
import datetime
import functools
import tornado.web
import tornado.ioloop
from requests import HTTPError
from sqlalchemy import and_, or_
from session_view.session import Session
from config.env_config import sql_session
from tornado_sqlalchemy import SessionMixin
from config.env_config import redis_connect
from config.env_config import env, static_path
from database.orm import HomepageHotModel as HHM
from database.orm import FeadbackModel as FBM
from database.orm import Post, User, Reply, BoardTypes
from database.orm import AchievementTypeModel as ATM
from database.orm import AchievementModel as AM
from database.orm import AchievementPrivilegeModel as APM

try:
    path = os.path.abspath('..')
    log_path = path + r'\log\yzs.log'
    logging.basicConfig(filename=log_path, filemode="a+", level=logging.ERROR)
except:
    pass


class BaseHandler(SessionMixin, tornado.web.RequestHandler):

    def initialize(self):
        try:
            self.backend_session = Session(self, redis_connect)
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "BaseHandler initialize wrong!!")

    def get_current_user(self):
        return self.backend_session.get_session('userId')

    def authenticated(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.current_user:
                if self.request.method in ('GET', 'POST'):
                    self.send_error(401)
                    return
                raise HTTPError(403)
            return method(self, *args, **kwargs)

        return wrapper


# 暂时不用
class HomeHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        pass


# 杨鸿晋部分
class AchievementTypeHandler(BaseHandler):
    @BaseHandler.authenticated
    def get(self):
        try:
            with self.make_session() as session:
                achievement_types_ = session.query(ATM.achievement_type_code, \
                                                   ATM.achievement_type_name).filter(ATM.is_delete == 0).all()
            achievement_type_list = [{ \
                'code': i.achievement_type_code, \
                'name': i.achievement_type_name \
                } for i in achievement_types_]
            self.write({'data': achievement_type_list})
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "yhj AchievementTypeHandler wrong {}".format(e))
            self.set_status(500, str(e))


# 六
class AchievementListHandler(BaseHandler):
    """docstring for achievementListHandler."""

    @BaseHandler.authenticated
    def get(self):
        result = {}
        try:
            type_code = self.get_argument('typeCode', '').strip()
            search_key = self.get_argument('search', '').strip()
            sort_rule = self.get_argument('sort', '0')
            page = int(self.get_argument('page', 0))
            size = int(self.get_argument('size', 20))
            if type_code != 'all':
                if search_key:
                    query = sql_session.query(AM.achievement_id, \
                                              AM.achievement_type_code, AM.achievement_title, \
                                              AM.achievement_publish_time, AM.achievement_source, \
                                              AM.achievement_abstract, AM.gmt_create, AM.read_count).filter( \
                        AM.achievement_type_code == type_code, or_( \
                            AM.achievement_title.like(f'%{search_key}%'), \
                            AM.achievement_abstract.like(f'%{search_key}%')), \
                        AM.is_delete == 0)
                else:
                    query = sql_session.query(AM.achievement_id, \
                                              AM.achievement_type_code, AM.achievement_title, \
                                              AM.achievement_publish_time, AM.achievement_source, \
                                              AM.achievement_abstract).filter( \
                        AM.achievement_type_code == type_code, AM.is_delete == 0)
            else:
                if search_key:
                    query = sql_session.query(AM.achievement_id, \
                                              AM.achievement_type_code, AM.achievement_title, \
                                              AM.achievement_publish_time, AM.achievement_source, \
                                              AM.achievement_abstract, AM.gmt_create, AM.read_count).filter( \
                        or_(AM.achievement_title.like(f'%{search_key}%'), \
                            AM.achievement_abstract.like(f'%{search_key}%')), \
                        AM.is_delete == 0)
                else:
                    query = sql_session.query(AM.achievement_id, \
                                              AM.achievement_type_code, AM.achievement_title, \
                                              AM.achievement_publish_time, AM.achievement_source, \
                                              AM.achievement_abstract).filter(AM.is_delete == 0)
            if sort_rule == '1':
                sorted_achievements_ = query.order_by( \
                    AM.read_count.desc())
            else:
                sorted_achievements_ = query.order_by( \
                    AM.achievement_publish_time.desc())
            total_items = len(sorted_achievements_.all())
            total_pages = math.ceil(total_items / size)
            limit_start = page * size

            achievements_ = sorted_achievements_.offset(limit_start).limit(size).all()
            achievement_list = [{
                'id': str(item.achievement_id),
                'title': item.achievement_title,
                'publishTime': item.achievement_publish_time.strftime('%Y-%m-%d'),
                'source': item.achievement_source,
                'abstract': item.achievement_abstract
            } for item in achievements_]

            result.update({"content": achievement_list,
                           "last": page >= total_pages - 1,
                           "totalPages": total_pages,
                           "totalElements": total_items,
                           "number": page,
                           "size": size,
                           "first": page <= 0,
                           "numberOfElements": len(achievement_list)
                           })
            self.write(result)
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "yhj AchievementListHandler wrong {}".format(e))
            self.set_status(500, str(e))


# 六
class AchievementDetailHandler(BaseHandler):
    @BaseHandler.authenticated
    def get(self):
        achievement_id = self.get_argument('id', '')
        if not achievement_id:
            self.set_status(404, 'no id')
        try:
            query_ = sql_session.query(AM.achievement_id, \
                                       AM.achievement_title, \
                                       AM.achievement_publish_time, AM.achievement_source, \
                                       AM.achievement_abstract, AM.achievement_content, \
                                       AM.read_count).filter( \
                AM.achievement_id == int(achievement_id), \
                AM.is_delete == 0)
            if query_.first():
                query = query_.first()
                data = {
                    'id': str(query.achievement_id),
                    'title': query.achievement_title,
                    'publishTime': query.achievement_publish_time.strftime('%Y-%m-%d'),
                    'source': query.achievement_source,
                    'abstract': query.achievement_abstract,
                    'content': query.achievement_content,
                }
                # 将阅读量加1
                query_.update({'read_count': query.read_count + 1})
                sql_session.commit()
            else:
                self.set_status(404, 'no id')
                return

            self.write(data)
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "yhj AchievementDetailHandler wrong {}".format(e))
            self.set_status(500, str(e))


# 六
class AchievementDocHandler(BaseHandler):
    @BaseHandler.authenticated
    def get(self):
        achievement_id = self.get_argument('id', '')
        if not achievement_id:
            self.set_status(404, 'no id')
            return

        query = sql_session.query(AM.achievement_id, \
                                  AM.achievement_doc_path).filter( \
            AM.achievement_id == int(achievement_id), \
            AM.is_delete == 0).first()

        if not query:
            self.set_status(404)
            return

        filename = query.achievement_doc_path
        if not filename:
            self.set_status(404)
            return

        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Access-Control-Allow-Origin', "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        with open(filename, 'rb') as f:
            while True:
                data = f.read(10240)
                if not data:
                    break
                self.write(data)
        self.finish()


# 六
class AchievementHandler(BaseHandler):

    @BaseHandler.authenticated
    def post(self):
        try:
            req_data_ = self.request.body.decode('utf-8')
            req_data = json.loads(req_data_)
            user_account = req_data.get('userAccount', '')
            type_code = req_data.get('typeCode', '')
            title = req_data.get('title', '')
            publish_time = req_data.get('publishTime', datetime.now())
            source = req_data.get('source', '')
            abstract = req_data.get('abstract', '')

            files = self.backend_session.get_session('files')

            new_arch = AM(achievement_type_code=type_code, \
                          achievement_title=title, \
                          achievement_publish_time=publish_time, \
                          achievement_source=source, \
                          achievement_abstract=abstract, \
                          achievement_content='', \
                          achievement_doc_path=files, \
                          gmt_create=datetime.now())

            # add new record

            sql_session.add(new_arch)
            sql_session.commit()

            self.backend_session.set_session('files', '')
            self.write({"isSuccess": "1"})
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "yhj AchievementHandler wrong {}".format(e))
            self.set_status(500)
            self.write({"isSuccess": "0"})


# 六
class AchievementPostPrivilegeHandler(BaseHandler):
    @BaseHandler.authenticated
    def get(self):
        user_account = self.get_argument('userAccount', '').strip()
        if not user_account:
            data = {
                "userAccount": user_account,
                "privilege": "0"
            }
        else:
            try:

                query = sql_session.query(APM.user_account, \
                                          APM.is_allowed).filter( \
                    APM.user_account == user_account, \
                    AM.is_delete == 0).first()
                if query:
                    data = {
                        "userAccount": user_account,
                        "privilege": '1' if query.is_allowed else '0'
                    }
                else:
                    data = {
                        "userAccount": user_account,
                        "privilege": '0'
                    }
                self.write(data)
            except Exception as e:
                local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                logging.error(local_time + "yhj AchievementPostPrivilegeHandler wrong {}".format(e))
                self.set_status(500, str(e))


# 六
class AchievementFilesHandler(BaseHandler):

    @BaseHandler.authenticated
    def post(self):
        try:
            file_metas = self.request.files.get('file', None)
            files = []
            if not file_metas:
                self.set_status(500, 'no files')
                return
            if len(file_metas) != 1:
                self.set_status(500, 'more than one file')
                return
            files = file_metas[0]

            self.backend_session.set_session('files', ';'.join(files))
            self.write({'isSuccess': "1"})
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "yhj AchievementFilesHandler wrong {}".format(e))
            self.set_status(500)
            self.write({'isSuccess': "0"})


# 刘路路部分
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')

        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")

        else:
            return json.JSONEncoder.default(self, obj)


# 刘
class AddTypesHandler(BaseHandler):
    @BaseHandler.authenticated
    def get(self):
        try:
            types = []
            type1 = BoardTypes()
            type1.board_id = 'finTechImag'
            type1.board_name = '金融科技脑洞'
            types.append(type1)

            type2 = BoardTypes()
            type2.board_id = 'techArgue'
            type2.board_name = '技术论剑'
            types.append(type2)

            type3 = BoardTypes()
            type3.board_id = 'finTechRoast'
            type3.board_name = '金融科技吐槽'
            types.append(type3)
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "ll AddType Wrong{}".format(e))


# 刘 获取板块类型
class BoardHandler(BaseHandler):
    @BaseHandler.authenticated
    def get(self):
        try:
            ret = sql_session.query(BoardTypes).order_by(BoardTypes.board_id).all()
            json_list = []
            for i in ret:
                json_dict = {}
                json_dict["id"] = i.board_id
                json_dict["name"] = i.board_name
                json_list.append(json_dict)

            ret1 = json.dumps(json_list, ensure_ascii=False, cls=DateEncoder)
            self.write(ret1)
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "ll 板块类型那里出错{}".format(e))


# 刘
class PostHandler(BaseHandler):
    @BaseHandler.authenticated
    # 获取帖子详情
    def get(self):
        """测试"""
        try:
            id = self.get_argument('id')
            res = sql_session.query(Post).filter(Post.pk_id == id).first()
            json_dict = {}
            json_dict["id"] = res.pk_id
            json_dict["title"] = res.title
            json_dict["authorName"] = res.author_name
            json_dict["authorProfile"] = res.author_profile
            json_dict["postTime"] = res.post_time
            json_dict["content"] = res.content
            json_dict["urls"] = res.image_url
            result = json.dumps(json_dict, ensure_ascii=False, cls=DateEncoder)
            self.write(result)
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "ll PostHandler get Wrong{}".format(e))

    # 发帖
    def post(self):
        try:
            # 获取前端数据
            username = self.backend_session.get_session('userName')
            # res = sql_session.query(User).filter(User.user_name == username).first()
            """
            ************************************
            这里的用户头像先写死，后期有数据再改
            ************************************
            """
            # 服务器域名
            path = 'http://129.28.193.59'
            file_path = os.path.join(static_path, 'profile')
            user_profile = path + file_path
            req_data = self.request.body.decode('utf8')
            req_data = json.loads(req_data)

            post = Post()
            post.title = req_data['title']  # 标题
            post.board_id = req_data['boardId']  # 板块id
            if req_data['urls']:
                post.image_url = req_data['urls']  # 获取上传图片连接
            post.author_name = username
            post.author_profile = user_profile
            post.post_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            post.content = req_data['content']
            print(post)
            sql_session.add(post)
            sql_session.commit()
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "ll post post Wrong{}".format(e))


# 刘
class UploadImageHandler(BaseHandler):
    @BaseHandler.authenticated
    def get(self):
        try:
            result_dict = {"imageActionName": "image",
                           "imageFieldName": "image",
                           "imageAllowFiles": [
                               ".png",
                               ".jpg",
                               ".jpeg",
                               ".gif",
                               ".bmp"
                           ],
                           "imageUrlPrefix": "",
                           "imagePathFormat": "/app/chamc/liululu/comment/static/upload",
                           "scrawlUrlPrefix": "",
                           "scrawlPathFormat": "/app/chamc/liululu/comment/static/upload",
                           "snapscreenUrlPrefix": "",
                           "snapscreenPathFormat": "/app/chamc/liululu/comment/static/upload",
                           "scrawlActionName": "",
                           "snapscreenActionName": ""}
            result = json.dumps(result_dict)
            self.write(result)
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "ll Upload Wrong{}".format(e))

    def post(self):
        """单图上传"""
        try:
            meta = self.request.files['image'][0]
            # 获取文件标题
            file_name = meta['filename']
            # 服务器域名
            path = 'http://129.28.193.59'

            # 创建文件保存路径
            file_path = os.path.join(static_path, 'uploads', file_name)
            url = path + file_path
            # 保存文件
            with open(file_path, 'wb') as up:
                up.write((meta['body']))
            # 返回目录
            # print(url)
            ret = {'status': True, 'url': url, 'state': "SUCCESS"}
            self.write(ret)
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "ll image post Wrong{}".format(e))


# 刘
class ReplyHandler(BaseHandler):
    @BaseHandler.authenticated
    def get(self):
        """
        http://localhost:8080/replies?postId=1&page=0&size=20
        """
        flag = 0
        try:
            postId = self.get_argument('postId')
            page = self.get_argument('page')
            page = int(page)
            size = self.get_argument('size')
            size = int(size)
            # print(postId, page, size)
            results = sql_session.query(Reply).filter(Reply.post_id == postId).all()
            # 评论个数
            total = len(results)
            # print(total)
            # 下面进行按照页数和每页数量进行选取数据
            total_pages = total / size + 1 if total % size else total / size  # 获取总页数
            total_pages = int(total_pages)
            first = 'true' if page == 1 else 'false'
            last = 'true' if page == total_pages else 'false'
            if page > total_pages:  # 如果前端查询的页数大于总量了，把result置空，查询空  ***默认首页为第零页
                results = []

            if page == total_pages:  # 如果是最后一页
                """假如page=total_pages=2，每页20个，则应该返回第21到最后的结果"""
                results = results[(page - 1) * size:]
            else:
                """不是最后一页，如total_pages=5,page=2,则返回第21到30的结果"""
                results = results[(page - 1) * size:page * size]
            num = len(results)
            flag = 1
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "ll reply divide page Wrong{}".format(e))

        try:
            if flag:
                # 构造response
                content = []
                for i in results:
                    info = {"id": i.pk_id,
                            "title": i.title,
                            "userName": i.user_name,
                            "userProfile": i.user_profile,
                            "replyTime": i.reply_time,
                            "content": i.content,
                            }
                    content.append(info)

                result_dict = {"content": content,
                               "last": last,  # 是否最后一页
                               "totalPages": total_pages,  # 总页数
                               "totalElements": total,  # 数据总条数
                               "number": page,  # 当前页码
                               "size": size,  # 每页展示多少条
                               "first": first,  # 是否第一页
                               "numberOfElements": num,  # 本页条数
                               }

            else:
                result_dict = {"result": "query failed!"}

            result = json.dumps(result_dict, ensure_ascii=False, cls=DateEncoder)
            self.write(result)
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "ll reply response wrong{}".format(e))


# 刘
class ReplyHandler2(BaseHandler):
    """发布评论"""

    @BaseHandler.authenticated
    def post(self):
        try:
            username = self.backend_session.get_session('userName')
            # res = sql_session.query(User).filter(User.user_name == username).first()
            # user_profile = res.user_profile
            """
            ************************************
            这里的用户头像先写死，后期有数据再改
            ************************************
            """
            # 服务器域名
            path = 'http://129.28.193.59'
            file_path = os.path.join(static_path, 'profile')
            user_profile = path + file_path

            req_data = self.request.body.decode('utf8')
            req_data = json.loads(req_data)
            reply = Reply()
            postId = req_data['postId']
            reply.post_id = postId  # 帖子id
            reply.title = sql_session.query(Post).filter(Post.pk_id == postId).first().title  # 帖子标题
            reply.user_name = username  # 回复人姓名
            reply.user_profile = user_profile  # 回复人头像地址
            reply.content = req_data['content']  # 回复内容
            reply.reply_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 回复时间
            sql_session.add(reply)
            sql_session.commit()
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "ll reply 2 wrong{}".format(e))


# 杨子爽部分 首页热帖
class HomepageHandler(BaseHandler):
    @BaseHandler.authenticated  # 用户未登录时，tornado将不会运行这个方法
    def get(self):
        # 获取请求json
        try:
            board_id = self.get_query_argument('boardId', default='', strip=True)
            search = self.get_query_argument('search', default='', strip=True)
            page = self.get_query_argument('page', default='', strip=True)
            size = self.get_query_argument('size', default='', strip=True)
            type = self.get_query_argument('type', default='', strip=True)
        except:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + " HomepageHandler获取前端传的json失败  ")
        # 查询数据库
        flag = 0
        try:
            if board_id == "all" or board_id == '':
                if type == '':
                    try:
                        results_ = sql_session.query(HHM.homepage_hot_id, HHM.homepage_hot_title, \
                                                     HHM.homepage_hot_author_name, HHM.homepage_hot_author_profile, \
                                                     HHM.homepage_hot_last_reply_date, HHM.homepage_hot_reply_num, \
                                                     HHM.homepage_hot_type, HHM.homepage_hot_type_name).filter( \
                            HHM.homepage_hot_title.like(f'%{search}%'))
                        results = results_.all()
                        try:

                            res = results_.update({"homepage_hot_click": HHM.homepage_hot_click + 1},
                                                  synchronize_session='fetch')
                            sql_session.commit()
                        except Exception as e:
                            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                            logging.error(local_time + "update hot click wrong!")
                    except Exception as e:
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        logging.error(local_time + "query database wrong ! type = all,boardid = all:{}".format(e))
                elif type == 'hot':
                    results_ = sql_session.query(HHM.homepage_hot_id, HHM.homepage_hot_title, \
                                                 HHM.homepage_hot_author_name, HHM.homepage_hot_author_profile, \
                                                 HHM.homepage_hot_last_reply_date, HHM.homepage_hot_reply_num, \
                                                 HHM.homepage_hot_type, HHM.homepage_hot_type_name).filter( \
                        HHM.homepage_hot_title.like(f'%{search}%'))
                    results = results_.order_by(HHM.homepage_hot_click.desc()).all()
                    try:

                        res = results_.update({"homepage_hot_click": HHM.homepage_hot_click + 1},
                                              synchronize_session='fetch')
                        sql_session.commit()
                    except Exception as e:
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        logging.error(local_time + "query database wrong ! type = hot,boardid = all:{}".format(e))

                else:
                    results_ = sql_session.query(HHM.homepage_hot_id, HHM.homepage_hot_title, \
                                                 HHM.homepage_hot_author_name, HHM.homepage_hot_author_profile, \
                                                 HHM.homepage_hot_last_reply_date, HHM.homepage_hot_reply_num, \
                                                 HHM.homepage_hot_type, HHM.homepage_hot_type_name).filter(and_( \
                        HHM.homepage_hot_type == type, HHM.homepage_hot_title.like(f'%{search}%')))
                    results = results_.all()
                    try:

                        res = results_.update({"homepage_hot_click": HHM.homepage_hot_click + 1},
                                              synchronize_session='fetch')
                        sql_session.commit()
                    except Exception as e:
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        logging.error(local_time + "query database wrong ! type = type,boardid = all:{}".format(e))

            else:
                if type == '':
                    results_ = sql_session.query(HHM.homepage_hot_id, HHM.homepage_hot_title, \
                                                 HHM.homepage_hot_author_name, HHM.homepage_hot_author_profile, \
                                                 HHM.homepage_hot_last_reply_date, HHM.homepage_hot_reply_num, \
                                                 HHM.homepage_hot_type, HHM.homepage_hot_type_name).filter(and_( \
                        HHM.homepage_hot_title.like(f'%{search}%'), HHM.homepage_hot_board_id == board_id))
                    results = results_.all()
                    try:

                        res = results_.update({"homepage_hot_click": HHM.homepage_hot_click + 1},
                                              synchronize_session='fetch')
                        sql_session.commit()
                    except Exception as e:
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        logging.error(local_time + "query database wrong ! type = all,boardid = boardid:{}".format(e))
                elif type == 'hot':
                    results_ = sql_session.query(HHM.homepage_hot_id, HHM.homepage_hot_title, \
                                                 HHM.homepage_hot_author_name, HHM.homepage_hot_author_profile, \
                                                 HHM.homepage_hot_last_reply_date, HHM.homepage_hot_reply_num, \
                                                 HHM.homepage_hot_type, HHM.homepage_hot_type_name).filter(and_( \
                        HHM.homepage_hot_title.like(f'%{search}%'), HHM.homepage_hot_board_id == board_id))
                    results = results_.order_by(HHM.homepage_hot_click.desc()).all()
                    try:

                        res = results_.update({"homepage_hot_click": HHM.homepage_hot_click + 1},
                                              synchronize_session='fetch')
                        sql_session.commit()
                    except Exception as e:
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        logging.error(local_time + "query database wrong ! type = hot,boardid = boardid:{}".format(e))
                else:
                    results_ = sql_session.query(HHM.homepage_hot_id, HHM.homepage_hot_title, \
                                                 HHM.homepage_hot_author_name, HHM.homepage_hot_author_profile, \
                                                 HHM.homepage_hot_last_reply_date, HHM.homepage_hot_reply_num, \
                                                 HHM.homepage_hot_type, HHM.homepage_hot_type_name).filter(and_( \
                        HHM.homepage_hot_type == type, HHM.homepage_hot_title \
                        .like(f'%{search}%'), HHM.homepage_hot_board_id == board_id))
                    results = results_.all()
                    try:

                        res = results_.update({"homepage_hot_click": HHM.homepage_hot_click + 1},
                                              synchronize_session='fetch')
                        sql_session.commit()
                    except Exception as e:
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        logging.error(local_time + "query database wrong ! type = type,boardid = boardid:{}".format(e))

            try:
                total = len(results)
                size = int(size)
                page = int(page)
                # 下面进行按照页数和每页数量进行选取数据
                total_pages = total / size if not total % size else total / size + 1  # 获取总页数
                total_pages = int(total_pages)
                first = 'true' if page == 0 else 'false'
                last = 'true' if page >= (total_pages - 1) else 'false'
                if page > total_pages - 1:  # 如果前端查询的页数大于总量了，把result置空，查询空  ***默认首页为第零页
                    results = []
                if page == total_pages - 1:
                    results = results[page * size:]
                else:
                    results = results[page * size:(page + 1) * size]
                num = len(results)
                flag = 1
            except Exception as e:
                local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                logging.error(local_time + "divide page wrong:{}".format(e))

        except Exception as e:
            flag = 0
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + "homepage query wrong!:{}".format(e))

        if flag:
            # 构造response
            content = []
            for i in results:
                info = {"id": i[0],
                        "title": i[1],
                        "authorName": i[2],
                        "authorProfile": i[3],
                        "lastReplyDate": str(i[4])[0:11],
                        "replyNum": i[5],
                        "type": i[6],
                        'typeName': i[7]
                        }
                content.append(info)

            result_dict = {"content": content,
                           "last": last,  # 是否最后一页
                           "totalPages": total_pages,  # 总页数
                           "totalElements": total,  # 数据总条数
                           "number": page,  # 当前页码
                           "size": size,  # 每页展示多少条
                           "first": first,  # 是否第一页
                           "numberOfElements": num,  # 本页条数
                           }

        else:
            result_dict = {"result": "query failed!"}
        try:
            self.write(json.dumps(result_dict))
        except Exception as e:
            self.write('json decode wrong!', e)


# 爽 发布意见反馈（是否要穿用户信息？待定）
class OpinionHandler(BaseHandler):
    def get(self):
        self.write('111')
        pass

    @BaseHandler.authenticated
    def post(self):
        # 获取请求json
        try:
            # 解析请求
            userAccount = self.get_argument('userAccount', default='')  # 用户账号
            orgId = self.get_argument('orgId', default='')  # 公司id
            deptId = self.get_argument('deptId', default='')  # 部门id
            tele = self.get_argument('tele', default='')  # 联系方式
            email = self.get_argument('email', default='')  # 邮箱
            content = self.get_argument('content', default='')  # 反馈意见
            # 存入数据库
            try:
                local_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                sql_session.add(FBM(feedback_user_account=userAccount, feedback_org_id=orgId, \
                                    feedback_dept_id=deptId, feedback_tele=tele, \
                                    feedback_email=email, feedback_content=content, feedback_save_time=local_time))

                sql_session.commit()
            except Exception as e:
                local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                logging.error(local_time + "save to database feedback wrong!:{}".format(e))
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + 'OpinionHandler wrong:{}'.format(e))


# 爽 获取登陆域地址
class Login_addressHandler(BaseHandler):  # 它不用验证登录
    # @BaseHandler.authenticated
    def get(self):
        login_address = env['jdemu']
        self.write(login_address)

    def post(self):
        pass


# 爽 获取当前登录用户信息
class Get_Login_infoHandler(BaseHandler):
    # @BaseHandler.authenticated
    def get(self):
        try:
            try:
                arg1 = self.get_query_argument('userInfo58914', default='', strip=False)
            except Exception as e:
                local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                logging.error(local_time + 'get user info url wrong:{}'.format(e))
            req_data = jwt.decode(arg1, "DKfe8ef9DS3", algorithms=['HS256'], audience='JsjPlatform')
            user_id = req_data['userId']
            userName = req_data['userName']
            email = req_data['email']
            user_info = {"userId": user_id, "userName": userName, "email": email}

            self.backend_session.set_session('userId', user_id)
            self.backend_session.set_session('username', userName)
            self.write(json.dumps(user_info))
        except Exception as e:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.error(local_time + 'get user info wrong:{}'.format(e))
