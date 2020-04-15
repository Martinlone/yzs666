# -*- coding: utf-8 -*-
# @Time : 2020/4/2 13:46
# @Author : yangzishuang
# @Site :
# @File : session_view.py
# @Software: PyCharm

# 随机生成session_id
# create_session_id = lambda: sha1(bytes('%s%s' % (os.urandom(16), time.time()), encoding='utf-8')).hexdigest()

class RedisStorage():

    def __init__(self, redis, session_id, prefix="fin_tech"):
        self._redis = redis
        self._session_id = session_id
        self._prefix = prefix

    def _wrapper(self, key):
        return "session_view:{prefix}:{key}".format(
            prefix=self._prefix,
            key=key
        )

    def get_value(self, key, default=None):
        value = self._redis.hget(self._session_id, key)
        return value

    def set_value(self, key, value, expires=86400):
        self._redis.hset(self._session_id, key, value)
        self._redis.expire(self._session_id, expires)

    def delete_value(self):
        return self._redis.delete(self._session_id)

class Session:
    """
    自定义session
    """

    def __init__(self, handler, redis, session_expire=86400, cookie_expire=None):
        self.handler = handler
        self.random_str = None
        self.session_expire = session_expire
        self.cookie_expire = cookie_expire
        self.get_session_id()
        # redis.Redis object
        self.session_storage = RedisStorage(redis, self.random_str)
        if self.get_session('username'):
            pass
        else:
            self.session_storage = RedisStorage(redis, self.random_str)


    def __generate_random_str(self):
        """
        生成用户的唯一标识字符串
        """
        import hashlib
        import time
        obj = hashlib.md5()
        obj.update(bytes(str(time.time()), 'utf-8'))
        random_str = obj.hexdigest()
        return random_str

    def set_session(self, key, value=''):
        self.session_storage.set_value(key, value, self.session_expire)

    def get_session(self, key):
        return self.session_storage.get_value(key)

    def delete_session(self):
        return self.session_storage.delete_value()

    def get_session_id(self):
        """
        获取连接的session_id，或者生成新id
        """
        random_str = self.handler.get_secure_cookie('_')
        if not random_str:
            random_str = self.__generate_random_str()
        self.random_str = random_str
        self.handler.set_secure_cookie('_', self.random_str, expires_days=1)


