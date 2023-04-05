import threading

from loguru import logger


def do_dispatch(task_id, task_param):
    """
    业务执行
    """
    logger.info("开始调度")
    logger.info('Workthread %s is running...' % threading.current_thread().name + " " + task_id + " " + task_param)
    logger.info("结束调度")