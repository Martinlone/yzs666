部署服务器可能需要修改之处：

    /config/env_config.py  连接redis的地方（2处）
    /config/env_config.py  连接mysql的地方
    /session_view/view.py  类UploadImageHandler、ReplyHandler2、PostHandler(BaseHandler)中的path
    /session_view/view.py  类Login_addressHandler中需要根据部署环境不同修改env[参数]中的参数
    /main                  所有出现的端口号,监听ip

服务器上直接python运行main文件  启动接口项目

PS：需要提前在部署环境上创建好相应的数据库表！

