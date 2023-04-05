import json
from random import choice

from loguru import logger
from redis import Redis
from redis.connection import BlockingConnectionPool
from redis.exceptions import TimeoutError, ConnectionError, ResponseError

from app.core.config import settings
from app.core.settings.app import AppSettings


async def redis_pool(settings: AppSettings) -> Redis:
    """
    根据环境创建 rds 客户端连接
    """
    import aioredis
    redis = await aioredis.from_url(
        url="rds://127.0.0.1", port=6379, password=None, db=2, encoding="utf-8", decode_responses=True
    )
    return redis


# def redis_list(host):
#     """
#     集群处理
#     """
#     REDIS_NODES = []
#     if "," in host:
#         lines = host.split(',')
#         for l in lines:
#             line = l.split(':')
#             REDIS_NODES.append({"host": line[0], "port": line[1]})
#     else:
#         line = host.split(":")
#         REDIS_NODES.append({"host": line[0], "port": line[1]})
#
#     return REDIS_NODES
#
#
# def redis_conn(host):
#     """
#     连接redis集群
#     """
#     nodes=redis_list(host)
#     req = None
#     try:
#         req = RedisCluster(startup_nodes=nodes, max_connections=1000, decode_responses=True)
#     except Exception as e:
#         logger.error("conn error:{}".format(e))
#     return req


class RedisClient(object):
    """
    Redis client

    Redis中代理存放的结构为hash：
    key为ip:port, value为代理属性的字典;
    """

    def __init__(self, **kwargs):
        """
        init
        :param host: host
        :param port: port
        :param password: password
        :param db: db
        :return:
        """
        self.name = ""
        db = kwargs.pop("db")
        host = kwargs.pop("host")
        port = kwargs.pop("port")
        logger.info(f"============================> redis conf host {host} port {port} db {db}")
        pool = BlockingConnectionPool(decode_responses=True, timeout=5, socket_timeout=5, host=host, port=port, db=db)
        # self.__conn = Redis(connection_pool=BlockingConnectionPool(decode_responses=True,
        #                                                            timeout=5,
        #                                                            socket_timeout=5,
        #                                                            **kwargs))
        self.__conn = Redis(connection_pool=pool)

    @logger.catch()
    def llen(self, k):
        """
        list size
        """
        if self.__conn.exists(k):
            return self.__conn.llen(k)
        return 0

    @logger.catch()
    def lrange(self, k, d=False):
        """
        lrange
        """
        if self.__conn.exists(k):
            da = self.__conn.lrange(k, 0, -1)
            if d:
                self.__conn.delete(k)
            return da
        return []

    @logger.catch()
    def lpush(self, k, v):
        """
        lpush
        """
        self.__conn.lpush(k, v)

    @logger.catch()
    def lpop(self, k):
        """
        lpop
        """
        return self.__conn.lpop(k)

    @logger.catch()
    def rpush(self, k, v):
        """
        rpush
        """
        self.__conn.rpush(k, v)

    @logger.catch()
    def rpop(self, k):
        """
        rpop
        """
        return self.__conn.rpop(k)

    @logger.catch()
    def hexists(self, lk, rk):
        """
        hexists
        """
        return self.__conn.hexists(lk, rk)

    @logger.catch()
    def hlen(self, lk):
        if self.__conn.exists(lk):
            return self.__conn.hlen(lk)
        return 0

    @logger.catch()
    def hget(self, lk, rk):
        """
        hget
        """
        if self.__conn.hexists(lk, rk):
            return self.__conn.hget(lk, rk)
        return None

    @logger.catch()
    def hset(self, lk, rk, v):
        """
        hset
        """
        self.__conn.hset(lk, rk, v)

    @logger.catch()
    def hkeys(self, lk):
        """
        hkeys
        """
        if self.__conn.exists(lk):
            return self.__conn.hkeys(lk)
        return []

    @logger.catch()
    def hgetall(self, lk):
        """
        hgetall
        """
        if self.__conn.exists(lk):
            return self.__conn.hgetall(lk)
        return []

    @logger.catch()
    def get(self, https):
        """
        返回一个代理
        """
        if https:
            items = self.__conn.hvals(self.name)
            proxies = list(filter(lambda x: json.loads(x).get("https"), items))
            return choice(proxies) if proxies else None
        else:
            proxies = self.__conn.hkeys(self.name)
            proxy = choice(proxies) if proxies else None
            return self.__conn.hget(self.name, proxy) if proxy else None

    @logger.catch()
    def put(self, proxy_obj):
        """
        将代理放入hash, 使用changeTable指定hash name
        """
        data = self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)
        return data

    @logger.catch()
    def pop(self, https):
        """
        弹出一个代理
        :return: dict {proxy: value}
        """
        proxy = self.get(https)
        if proxy:
            self.__conn.hdel(self.name, json.loads(proxy).get("proxy", ""))
        return proxy if proxy else None

    @logger.catch()
    def delete(self, proxy_str):
        """
        移除指定代理, 使用changeTable指定hash name
        :param proxy_str: proxy str
        :return:
        """
        return self.__conn.hdel(self.name, proxy_str)

    @logger.catch()
    def exists(self, proxy_str):
        """
        判断指定代理是否存在, 使用changeTable指定hash name
        :param proxy_str: proxy str
        :return:
        """
        return self.__conn.hexists(self.name, proxy_str)

    @logger.catch()
    def update(self, proxy_obj):
        """
        更新 proxy 属性
        :param proxy_obj:
        :return:
        """
        return self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)

    @logger.catch()
    def get_all(self, https):
        """
        字典形式返回所有代理, 使用changeTable指定hash name
        """
        items = self.__conn.hvals(self.name)
        if https:
            return list(filter(lambda x: json.loads(x).get("https"), items))
        else:
            return items

    @logger.catch()
    def clear(self):
        """
        清空所有代理, 使用changeTable指定hash name
        """
        return self.__conn.delete(self.name)

    @logger.catch()
    def get_count(self):
        """
        返回代理数量
        """
        proxies = self.getAll(https=False)
        return {'total': len(proxies), 'https': len(list(filter(lambda x: json.loads(x).get("https"), proxies)))}

    @logger.catch()
    def change_table(self, name):
        """
        切换操作对象
        """
        self.name = name

    @logger.catch()
    def test(self):
        """
        测试 rds 连接
        """
        try:
            self.get_count()
        except TimeoutError as e:
            logger.error('rds connection time out: %s' % str(e), exc_info=True)
            return e
        except ConnectionError as e:
            logger.error('rds connection error: %s' % str(e), exc_info=True)
            return e
        except ResponseError as e:
            logger.error('rds connection error: %s' % str(e), exc_info=True)
            return e

    @logger.catch()
    async def close(self):
        """
        close
        """
        self.__conn.close()


# redis_cli = redis_pool(settings)
redis_cli = RedisClient(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DATABASE)
