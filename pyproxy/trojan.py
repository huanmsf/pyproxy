import asyncio
import ssl
import socket
import struct
import hashlib
from typing import Tuple, Optional
from .config import TrojanConfig
from .logger import Logger


class TrojanProtocol:
    """Trojan协议实现"""
    
    # 命令类型
    CMD_CONNECT = 0x01
    CMD_UDP_ASSOCIATE = 0x03
    
    # 地址类型
    ATYP_IPv4 = 0x01
    ATYP_DOMAIN = 0x03
    ATYP_IPv6 = 0x04
    
    def __init__(self, config: TrojanConfig, logger: Logger):
        self.config = config
        self.logger = logger
        self.password_hash = self._hash_password(config.password)
        
    def _hash_password(self, password: str) -> bytes:
        """计算密码的SHA224哈希值"""
        return hashlib.sha224(password.encode('utf-8')).hexdigest().encode('utf-8')
        
    async def create_connection(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """创建到Trojan服务器的连接"""
        try:
            # 创建SSL上下文
            ssl_context = ssl.create_default_context()
            if not self.config.verify_ssl:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
            # 连接服务器
            reader, writer = await asyncio.open_connection(
                self.config.server,
                self.config.port,
                ssl=ssl_context,
                server_hostname=self.config.sni or self.config.server
            )
            
            self.logger.debug(f"已连接到Trojan服务器: {self.config.server}:{self.config.port}")
            return reader, writer
            
        except Exception as e:
            self.logger.error(f"连接Trojan服务器失败: {e}")
            raise
            
    def build_request(self, target_host: str, target_port: int, cmd: int = CMD_CONNECT) -> bytes:
        """构建Trojan请求数据包"""
        # 密码哈希 + CRLF
        data = self.password_hash + b'\r\n'
        
        # 命令
        data += struct.pack('!B', cmd)
        
        # 目标地址
        if self._is_ipv4(target_host):
            # IPv4地址
            data += struct.pack('!B', self.ATYP_IPv4)
            data += socket.inet_aton(target_host)
        elif self._is_ipv6(target_host):
            # IPv6地址
            data += struct.pack('!B', self.ATYP_IPv6)
            data += socket.inet_pton(socket.AF_INET6, target_host)
        else:
            # 域名
            data += struct.pack('!B', self.ATYP_DOMAIN)
            host_bytes = target_host.encode('utf-8')
            data += struct.pack('!B', len(host_bytes))
            data += host_bytes
            
        # 目标端口
        data += struct.pack('!H', target_port)
        
        # CRLF结束
        data += b'\r\n'
        
        return data
        
    def _is_ipv4(self, host: str) -> bool:
        """检查是否为IPv4地址"""
        try:
            socket.inet_aton(host)
            return True
        except socket.error:
            return False
            
    def _is_ipv6(self, host: str) -> bool:
        """检查是否为IPv6地址"""
        try:
            socket.inet_pton(socket.AF_INET6, host)
            return True
        except socket.error:
            return False


class TrojanClient:
    """Trojan客户端"""
    
    def __init__(self, config: TrojanConfig, logger: Logger):
        self.config = config
        self.logger = logger
        self.protocol = TrojanProtocol(config, logger)
        
    async def connect(self, target_host: str, target_port: int) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """连接到目标服务器（通过Trojan代理）"""
        try:
            # 连接Trojan服务器
            server_reader, server_writer = await self.protocol.create_connection()
            
            # 发送Trojan请求
            request = self.protocol.build_request(target_host, target_port)
            server_writer.write(request)
            await server_writer.drain()
            
            self.logger.debug(f"已通过Trojan代理连接到: {target_host}:{target_port}")
            return server_reader, server_writer
            
        except Exception as e:
            self.logger.error(f"Trojan连接失败: {e}")
            raise 