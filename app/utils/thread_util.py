import threading
from time import ctime

from loguru import logger


class TaskThread(threading.Thread):

    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.func = func
        self.name = name
        self.args = args
        self.res = None

    def run(self):
        logger.debug("{}线程开始时间：{}".format(self.name, ctime()))
        self.res = self.func(*self.args)
        logger.debug("{}线程退出时间：{}".format(self.name, ctime()))

    def get_result(self):
        return self.res

    def get_name(self):
        return self.name
