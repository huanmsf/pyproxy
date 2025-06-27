import asyncio
import time
import ssl
import socket
from typing import Optional, Tuple
from .config import TrojanConfig
from .logger import Logger


class HeartbeatMonitor:
    """心跳监控器 - 定期检测服务器连接状态和延迟"""
    
    def __init__(self, config: TrojanConfig, logger: Logger, interval: int = 5):
        self.config = config
        self.logger = logger
        self.interval = interval
        self.running = False
        self.last_status = None
        self.consecutive_failures = 0
        self.monitor_task = None
        
    async def start(self):
        """启动心跳监控"""
        if self.running:
            return
            
        self.running = True
        self.logger.info("心跳监控已启动")
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        
    async def stop(self):
        """停止心跳监控"""
        if not self.running:
            return
            
        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("心跳监控已停止")
        
    async def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 检测连接状态和延迟
                status, latency, error = await self._check_server_status()
                
                # 打印状态信息
                self._print_status(status, latency, error)
                
                # 记录状态变化
                if status != self.last_status:
                    if status:
                        self.logger.info(f"✓ 服务器连接已恢复 - {self.config.server}:{self.config.port}")
                        self.consecutive_failures = 0
                    else:
                        self.logger.warning(f"✗ 服务器连接失败 - {self.config.server}:{self.config.port}")
                        
                self.last_status = status
                
                # 处理连续失败
                if not status:
                    self.consecutive_failures += 1
                    if self.consecutive_failures >= 3:
                        self.logger.error(f"服务器连续失败 {self.consecutive_failures} 次: {error}")
                else:
                    self.consecutive_failures = 0
                    
                # 等待下次检测
                await asyncio.sleep(self.interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"心跳监控异常: {e}")
                await asyncio.sleep(self.interval)
                
    async def _check_server_status(self) -> Tuple[bool, Optional[float], Optional[str]]:
        """检测服务器状态
        
        Returns:
            (连接状态, 延迟毫秒, 错误信息)
        """
        start_time = time.time()
        error_msg = None
        
        try:
            # 创建SSL上下文
            ssl_context = ssl.create_default_context()
            if not self.config.verify_ssl:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
            # 设置超时时间
            connect_timeout = 5.0
            
            # 尝试连接服务器
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(
                    self.config.server,
                    self.config.port,
                    ssl=ssl_context,
                    server_hostname=self.config.sni or self.config.server
                ),
                timeout=connect_timeout
            )
            
            # 计算延迟
            latency = (time.time() - start_time) * 1000
            
            # 关闭连接
            writer.close()
            await writer.wait_closed()
            
            return True, latency, None
            
        except asyncio.TimeoutError:
            error_msg = "连接超时"
        except ssl.SSLError as e:
            error_msg = f"SSL错误: {str(e)[:50]}"
        except socket.gaierror as e:
            error_msg = f"DNS解析失败: {str(e)[:50]}"
        except ConnectionRefusedError:
            error_msg = "连接被拒绝"
        except Exception as e:
            error_msg = f"未知错误: {str(e)[:50]}"
            
        return False, None, error_msg
        
    def _print_status(self, status: bool, latency: Optional[float], error: Optional[str]):
        """打印状态信息到控制台"""
        timestamp = time.strftime("%H:%M:%S")
        server_info = f"{self.config.server}:{self.config.port}"
        
        if status and latency is not None:
            # 根据延迟显示不同颜色
            if latency < 100:
                latency_color = "绿色"
                latency_icon = "🟢"
            elif latency < 300:
                latency_color = "黄色" 
                latency_icon = "🟡"
            else:
                latency_color = "红色"
                latency_icon = "🔴"
                
            print(f"[{timestamp}] {latency_icon} 服务器状态: 正常 | 延迟: {latency:.1f}ms | 服务器: {server_info}")
        else:
            print(f"[{timestamp}] 🔴 服务器状态: 异常 | 错误: {error or '未知'} | 服务器: {server_info}")
            
    def get_status(self) -> dict:
        """获取当前状态信息"""
        return {
            'running': self.running,
            'last_status': self.last_status,
            'consecutive_failures': self.consecutive_failures,
            'server': f"{self.config.server}:{self.config.port}"
        } 