"""
PyProxy - Python Trojan代理客户端

一个支持Trojan协议的轻量级代理客户端实现

MIT License
Copyright (c) 2024 huanmsf
"""

__version__ = "1.0.0"
__author__ = "huanmsf"
__license__ = "MIT"

# 导出主要类
from .client import PyProxyClient
from .config import Config  
from .logger import Logger

__all__ = ['PyProxyClient', 'Config', 'Logger'] 