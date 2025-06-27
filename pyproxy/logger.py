import logging
import colorlog
import sys
import io
from typing import Optional
from .config import LogConfig


class Logger:
    """日志管理器"""
    
    def __init__(self, config: LogConfig):
        self.config = config
        self.logger = None
        self._setup_encoding()
        self._setup_logger()
        
    def _setup_encoding(self):
        """设置控制台编码，解决Windows中文乱码问题"""
        if sys.platform == 'win32':
            # Windows下设置控制台编码为UTF-8
            try:
                # 设置标准输出编码
                if hasattr(sys.stdout, 'reconfigure'):
                    sys.stdout.reconfigure(encoding='utf-8')
                if hasattr(sys.stderr, 'reconfigure'):
                    sys.stderr.reconfigure(encoding='utf-8')
            except:
                # 如果reconfigure不可用，尝试其他方法
                pass
        
    def _setup_logger(self):
        """设置日志器"""
        self.logger = logging.getLogger('pyproxy')
        self.logger.setLevel(getattr(logging, self.config.level))
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 控制台处理器，确保UTF-8编码
        console_handler = colorlog.StreamHandler()
        
        # 确保处理器使用UTF-8编码
        if hasattr(console_handler.stream, 'encoding'):
            if console_handler.stream.encoding != 'utf-8':
                # 尝试重新包装流以支持UTF-8
                try:
                    console_handler.stream = io.TextIOWrapper(
                        console_handler.stream.buffer, 
                        encoding='utf-8', 
                        errors='replace'
                    )
                except:
                    pass
        
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        if self.config.file:
            file_handler = logging.FileHandler(self.config.file, encoding='utf-8')
            file_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
    def debug(self, message: str):
        """调试日志"""
        self.logger.debug(message)
        
    def info(self, message: str):
        """信息日志"""
        self.logger.info(message)
        
    def warning(self, message: str):
        """警告日志"""
        self.logger.warning(message)
        
    def error(self, message: str):
        """错误日志"""
        self.logger.error(message)
        
    def critical(self, message: str):
        """严重错误日志"""
        self.logger.critical(message) 