# -*- coding: utf-8 -*-
# @Time : 2020/3/25 15:55
# @Author : yangzishuang
# @Site :
# @File : main.py
# @Software: PyCharm

from tornado.options import define
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from session_view.view import *
from config.env_config import settings
# 定义端口，  未知
define("port", default=8080, type=int)


def main():
    tornado.options.parse_command_line()

    # 定义app
    app = tornado.web.Application([
        (r'/achievementTypes', AchievementTypeHandler),
        (r'/achievements', AchievementListHandler),
        (r'/achievementPostPrivilege', AchievementPostPrivilegeHandler),
        (r'/upload', AchievementFilesHandler),
        (r'/achievement', AchievementHandler),
        (r'/achievementDetail', AchievementDetailHandler),
        (r'/achievementDoc', AchievementDocHandler),

        (r'/post/detail', PostHandler),  # 获取帖子详情/发帖
        (r'/post', PostHandler),  # 获取帖子详情/发帖
        (r'/upload', UploadImageHandler),  # 上传图片的接口
        (r'/replies', ReplyHandler),  # 获取帖子评论列表
        (r'/reply', ReplyHandler2),  # 发表帖子评论
        (r'/boardTypes', BoardHandler),  # 获取科技论坛板块类型
        (r'/addTypes', AddTypesHandler),  # 数据库操作

        (r'^/posts$', HomepageHandler),
        (r'/feedback$', OpinionHandler),
        (r'^/login/address$', Login_addressHandler),
        (r'^/login/user/info$', Get_Login_infoHandler),
        (r'^/#/homePage$', HomeHandler)
    ], **settings)

    # 绑定监听
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
    # http_server = tornado.httpserver.HTTPServer(app, xheaders=True)  # 暂时ip和端口号未知
    # http_server.listen(options.port,"127.0.0.1")


if __name__ == '__main__':
    main()
