import asyncio
import signal
import sys
import os
from .config import Config
from .logger import Logger
from .socks5 import SOCKS5Server
from .heartbeat import HeartbeatMonitor


class PyProxyClient:
    """PyProxy客户端主类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = None
        self.logger = None
        self.socks5_server = None
        self.heartbeat_monitor = None
        self.running = False
        
    async def start(self):
        """启动代理客户端"""
        try:
            # 设置Windows控制台编码
            self._setup_console_encoding()
            
            # 加载配置
            self.config = Config(self.config_path)
            self.config.load()
            
            # 初始化日志
            self.logger = Logger(self.config.log)
            self.logger.info("PyProxy代理客户端启动中...")
            
            # 创建SOCKS5服务器
            self.socks5_server = SOCKS5Server(self.config, self.logger)
            
            # 创建心跳监控器
            self.heartbeat_monitor = HeartbeatMonitor(self.config.trojan, self.logger)
            
            # 设置信号处理
            self._setup_signal_handlers()
            
            # 启动服务器
            self.running = True
            self.logger.info("✓ 代理客户端已启动")
            self.logger.info(f"📡 本地SOCKS5代理: {self.config.local.listen}:{self.config.local.port}")
            self.logger.info(f"🌐 Trojan服务器: {self.config.trojan.server}:{self.config.trojan.port}")
            
            # 启动心跳监控
            await self.heartbeat_monitor.start()
            
            # 添加分隔线，便于区分启动信息和状态监控
            print("=" * 70)
            print("🔍 服务器状态监控 (每5秒更新)")
            print("=" * 70)
            
            # 启动SOCKS5服务器（这会阻塞直到服务器停止）
            await self.socks5_server.start()
            
        except KeyboardInterrupt:
            if self.logger:
                self.logger.info("接收到退出信号")
            await self.stop()
        except Exception as e:
            if self.logger:
                self.logger.error(f"启动失败: {e}")
                # 记录详细错误信息到日志
                import traceback
                self.logger.error(f"详细错误信息: {traceback.format_exc()}")
            else:
                print(f"启动失败: {e}")
            raise
            
    async def stop(self):
        """停止代理客户端"""
        if not self.running:
            return
            
        self.running = False
        
        if self.logger:
            self.logger.info("🛑 正在停止代理客户端...")
            
        # 停止心跳监控
        if self.heartbeat_monitor:
            await self.heartbeat_monitor.stop()
            
        # 停止SOCKS5服务器
        if self.socks5_server:
            await self.socks5_server.stop()
            
        if self.logger:
            self.logger.info("✓ 代理客户端已停止")
            
    def _setup_console_encoding(self):
        """设置控制台编码，解决Windows中文显示问题"""
        if sys.platform == 'win32':
            try:
                # 设置Windows控制台代码页为UTF-8
                os.system('chcp 65001 >nul 2>&1')
                
                # 设置环境变量
                os.environ['PYTHONIOENCODING'] = 'utf-8'
                
                # 重新配置标准输出流
                if hasattr(sys.stdout, 'reconfigure'):
                    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                if hasattr(sys.stderr, 'reconfigure'):
                    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
                    
            except Exception:
                # 忽略编码设置错误，使用默认编码
                pass
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            if self.logger:
                self.logger.info(f"接收到信号 {signum}")
            # 创建停止任务
            asyncio.create_task(self.stop())
            
        # 注册信号处理器
        if sys.platform != 'win32':
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
        else:
            # Windows下只支持SIGINT
            signal.signal(signal.SIGINT, signal_handler) 