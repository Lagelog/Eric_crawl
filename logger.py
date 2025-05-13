import time
from queue import Queue
from typing import Set

# 全局变量存储日志消息和订阅者
log_messages = []
log_subscribers: Set[Queue] = set()

def add_log_message(message: str) -> None:
    """
    添加一条日志消息并通知所有订阅者
    
    Args:
        message: 日志消息内容
    """
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    formatted_message = f"[{timestamp}] {message}"
    log_messages.append(formatted_message)
    
    # 通知所有订阅者
    for queue in log_subscribers:
        queue.put(formatted_message)

def clear_logs() -> None:
    """清空所有日志消息"""
    log_messages.clear()

def add_subscriber(queue: Queue) -> None:
    """
    添加日志订阅者
    
    Args:
        queue: 订阅者的消息队列
    """
    log_subscribers.add(queue)

def remove_subscriber(queue: Queue) -> None:
    """
    移除日志订阅者
    
    Args:
        queue: 要移除的订阅者的消息队列
    """
    log_subscribers.remove(queue)

def get_all_logs() -> list:
    """
    获取所有日志消息
    
    Returns:
        包含所有日志消息的列表
    """
    return log_messages.copy() 