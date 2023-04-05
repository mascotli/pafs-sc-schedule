import json
import threading
import time
from time import ctime

from loguru import logger

from app.common.redis_constant import pending_task_queue_key, task_param_key, running_task_queue_key, \
    complete_task_queue_key
from app.job.dispatcher import do_dispatch
from app.utils.thread_util import TaskThread


def rest(log, interval):
    """
    rest
    """
    try:
        time.sleep(interval)
    except Exception as e:
        logger.error(log, e)


class WorkerThread(threading.Thread):

    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.func = func
        self.name = name
        self.args = args
        self.res = None
        self.idle = True
        self.interval = 300
        self.__run = True
        from app.rds.redis_client import redis_cli as cli
        self.__redis = cli

    def do_serve(self):
        while True:
            # 停机检测
            if not self.__run:
                break
            # 新任务检测
            try:
                if self.__redis.llen(pending_task_queue_key) <= 0:
                    logger.info(f"worker thread {self.name} sleep start because no task")
                    rest(f"worker thread {self.name} sleep error", self.interval)
                    logger.info(f"worker thread {self.name} sleep end because no task")
                    continue
            except Exception as e:
                logger.error(f"worker thread {self.name} llen error", e)
                rest(f"worker thread {self.name} sleep because llen error", self.interval)
                continue

            # 获取请求任务
            task_id = None
            task_param = None
            try:
                task_id = self.__redis.rpop(pending_task_queue_key)
                if not task_id:
                    logger.info(f"worker thread {self.name} task id {task_id} is empty ")
                    continue
                param_k = task_param_key + task_id
                task_param = self.__redis.get(param_k)
            except Exception as e:
                logger.error(f"worker thread {self.name} rpop error", e)
                rest(f"worker thread {self.name} sleep beacuse rpop error", self.interval)

            if not task_param:
                logger.info(f"worker thread task id {task_id} param is empty")
                continue

            self.idle = False
            try:
                logger.debug("{}线程执行任务({})开始时间：{}".format(self.name, task_id, ctime()))
                res = self.func(task_id, task_param)
                logger.debug("{}线程执行任务({})退出时间：{}".format(self.name, task_id, ctime()))
            except Exception as e:
                logger.info("work thread task id ", task_id, " fail", e)
            self.idle = True

    def run(self):
        logger.debug("{}线程开始时间：{}".format(self.name, ctime()))
        self.do_serve()
        logger.debug("{}线程退出时间：{}".format(self.name, ctime()))

    def stop(self):
        self.__run = False

    def get_run(self):
        return self.__run

    def get_result(self):
        return self.res

    def get_name(self):
        return self.name

    def get_idle(self):
        return self.idle


class Scheduler(object):
    """
    调度器
    """

    def __init__(self, **kwargs):
        """
        init
        """
        self.name = "训练任务调度器"
        # kwargs.pop("")
        from app.rds.redis_client import redis_cli as cli
        self.__redis = cli
        self.__run = True
        self.__interval = 300
        self.__init_size = 1
        self.__core_size = 10
        self.__max_size = 15
        self.__main_thread = TaskThread(func=self.schedule, args=(), name=self.name)
        self.__work_thread_list = [WorkerThread(func=do_dispatch, args=(i,), name='work-thread-' + str(i + 1)) for i in range(self.__init_size)]

    @property
    def run(self):
        return self.__run

    @run.setter
    def run(self, val):
        self.__run = val

    async def stop(self):
        """
        stop main thread
        """
        self.__run = False
        for t in self.__work_thread_list:
            t.stop()

    async def start(self):
        """
        start main thread
        """
        self.__main_thread.start()

    def statistic(self):
        d = {"running":0, "pending":0, "complete":0, "idle": 0, "available": 0}

        for t in self.__work_thread_list:
            if t.get_run() and t.get_idle():
                d['available'] += 1
            if t.get_idle():
                d['idle'] += 1

        try:
            d["pending"] = self.__redis.llen(pending_task_queue_key)
            d["running"] = self.__redis.llen(running_task_queue_key)
            d["complete"] = self.__redis.llen(complete_task_queue_key)
        except Exception as e:
            logger.error(f"main thread statistic error", e)

        return d

    def schedule(self):
        """
        schedule
        """

        # for i in range(self.__init_size):
        #     t = WorkerThread(func=self.serve, args=(i,), name='work-thread-' + str(i + 1))
        #     self.__work_thread_list.append(t)

        for t in self.__work_thread_list:
            # t.setDaemon(True)  # 设置为守护线程，不会因主线程结束而中断
            t.start()

        while True:
            if not self.__run:
                for t in self.__work_thread_list:
                    t.stop()
                break
            stats = self.statistic()

            logger.info(f"main thread statistic running: {stats['running']} pending: {stats['pending']} complete: {stats['complete']}, idle: {stats['idle']}, available: {stats['available']}")

            logger.info(f"main thread {self.name} sleep start ")
            try:
                time.sleep(self.__interval)
            except Exception as e:
                logger.error(f"main thread {self.name} sleep error", e)
            logger.info(f"main thread {self.name} sleep end ")

        # wait thread end
        for t in self.__work_thread_list:
            t.join()

        logger.info(f"main thread {self.name} wait all worker thread complete end ")

        for t in self.__work_thread_list:
            logger.error(t.get_name() + " 's result is " + json.dumps(t.get_result(), ensure_ascii=False).encode('utf8').decode('utf-8'))


job_scheduler = Scheduler()

