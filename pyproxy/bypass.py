"""
防火墙绕过模块
实现多种反检测和绕过技术
"""

import asyncio
import random
import time
import socket
import ssl
import struct
from typing import Tuple, Optional, List
from .logger import Logger


class BypassTechniques:
    """防火墙绕过技术集合"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        
    async def random_delay(self, min_ms: int = 50, max_ms: int = 200):
        """随机延迟以模拟人类行为"""
        delay = random.uniform(min_ms, max_ms) / 1000
        await asyncio.sleep(delay)
        
    def fragment_data(self, data: bytes, chunk_size: int = None) -> List[bytes]:
        """将数据分片以避免DPI检测"""
        if chunk_size is None:
            chunk_size = random.randint(64, 512)
            
        chunks = []
        for i in range(0, len(data), chunk_size):
            chunks.append(data[i:i + chunk_size])
        return chunks
        
    def add_noise_padding(self, data: bytes) -> bytes:
        """添加随机填充数据"""
        noise_size = random.randint(1, 16)
        noise = bytes([random.randint(0, 255) for _ in range(noise_size)])
        # 在真实数据前后添加噪声（需要接收端能识别）
        return data + noise
        
    def mimic_http_request(self, target_host: str, target_port: int) -> bytes:
        """伪装成正常HTTP请求"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        
        fake_request = (
            f"GET / HTTP/1.1\r\n"
            f"Host: {target_host}\r\n"
            f"User-Agent: {random.choice(user_agents)}\r\n"
            f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
            f"Accept-Language: en-US,en;q=0.5\r\n"
            f"Accept-Encoding: gzip, deflate\r\n"
            f"Connection: keep-alive\r\n"
            f"Upgrade-Insecure-Requests: 1\r\n"
            f"\r\n"
        )
        return fake_request.encode()


class EnhancedTrojanClient:
    """增强的Trojan客户端，支持防火墙绕过"""
    
    def __init__(self, config, logger: Logger):
        self.config = config
        self.logger = logger
        self.bypass = BypassTechniques(logger)
        
    async def connect_with_bypass(self, target_host: str, target_port: int) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """使用绕过技术建立连接"""
        
        # 方法1: 直接IP连接（绕过DNS污染）
        try:
            return await self._connect_by_ip(target_host, target_port)
        except Exception as e:
            self.logger.debug(f"IP直连失败: {e}")
            
        # 方法2: 使用域名前置
        try:
            return await self._connect_with_domain_fronting(target_host, target_port)
        except Exception as e:
            self.logger.debug(f"域名前置失败: {e}")
            
        # 方法3: 分片连接
        try:
            return await self._connect_with_fragmentation(target_host, target_port)
        except Exception as e:
            self.logger.debug(f"分片连接失败: {e}")
            
        # 方法4: 使用代理链
        try:
            return await self._connect_via_proxy_chain(target_host, target_port)
        except Exception as e:
            self.logger.debug(f"代理链失败: {e}")
            
        raise Exception("所有绕过方法都失败了")
        
    async def _connect_by_ip(self, target_host: str, target_port: int) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """通过IP地址直接连接"""
        try:
            # 尝试解析域名到IP
            ip = socket.gethostbyname(target_host)
            self.logger.info(f"🔍 域名解析: {target_host} -> {ip}")
            
            # 使用IP直接连接Trojan服务器
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            reader, writer = await asyncio.open_connection(
                self.config.trojan.server,
                self.config.trojan.port,
                ssl=context,
                server_hostname=self.config.trojan.sni
            )
            
            # 发送Trojan请求（使用真实IP）
            trojan_request = await self._build_trojan_request(ip, target_port)
            writer.write(trojan_request)
            await writer.drain()
            
            self.logger.info(f"✅ IP直连成功: {target_host}({ip}):{target_port}")
            return reader, writer
            
        except Exception as e:
            self.logger.debug(f"IP直连失败: {e}")
            raise
            
    async def _connect_with_domain_fronting(self, target_host: str, target_port: int) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """使用域名前置技术"""
        # 使用CDN域名作为SNI
        cdn_domains = [
            "cloudflare.com",
            "amazonaws.com", 
            "cloudfront.net",
            "fastly.com",
            "cdn.jsdelivr.net"
        ]
        
        sni_domain = random.choice(cdn_domains)
        self.logger.info(f"🎭 使用域名前置: SNI={sni_domain}")
        
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        reader, writer = await asyncio.open_connection(
            self.config.trojan.server,
            self.config.trojan.port,
            ssl=context,
            server_hostname=sni_domain  # 伪装SNI
        )
        
        # 发送Trojan请求
        trojan_request = await self._build_trojan_request(target_host, target_port)
        writer.write(trojan_request)
        await writer.drain()
        
        self.logger.info(f"✅ 域名前置成功: {target_host}:{target_port}")
        return reader, writer
        
    async def _connect_with_fragmentation(self, target_host: str, target_port: int) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """使用数据包分片"""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        reader, writer = await asyncio.open_connection(
            self.config.trojan.server,
            self.config.trojan.port,
            ssl=context,
            server_hostname=self.config.trojan.sni
        )
        
        # 构建Trojan请求
        trojan_request = await self._build_trojan_request(target_host, target_port)
        
        # 分片发送
        chunks = self.bypass.fragment_data(trojan_request)
        self.logger.info(f"📦 分片发送: {len(chunks)}个数据包")
        
        for i, chunk in enumerate(chunks):
            writer.write(chunk)
            await writer.drain()
            # 随机延迟
            await self.bypass.random_delay(10, 50)
            
        self.logger.info(f"✅ 分片连接成功: {target_host}:{target_port}")
        return reader, writer
        
    async def _connect_via_proxy_chain(self, target_host: str, target_port: int) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """使用代理链（如果配置了多个代理）"""
        # 这里可以实现多级代理
        # 目前先使用单个代理
        return await self._connect_by_ip(target_host, target_port)
        
    async def _build_trojan_request(self, target_host: str, target_port: int) -> bytes:
        """构建Trojan请求包"""
        import hashlib
        
        # 密码哈希
        password_hash = hashlib.sha224(self.config.trojan.password.encode()).hexdigest()
        
        # 构建请求
        request = bytearray()
        request.extend(bytes.fromhex(password_hash))
        request.extend(b'\r\n')
        
        # 命令：CONNECT
        request.append(0x01)
        
        # 目标地址类型和地址
        if target_host.replace('.', '').isdigit():  # IP地址
            request.append(0x01)  # IPv4
            parts = target_host.split('.')
            for part in parts:
                request.append(int(part))
        else:  # 域名
            request.append(0x03)  # Domain
            host_bytes = target_host.encode()
            request.append(len(host_bytes))
            request.extend(host_bytes)
            
        # 端口
        request.extend(struct.pack('>H', target_port))
        request.extend(b'\r\n')
        
        return bytes(request)


class DNSBypass:
    """DNS绕过技术"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        
    async def resolve_with_doh(self, domain: str, doh_server: str = "https://1.1.1.1/dns-query") -> Optional[str]:
        """使用DoH (DNS over HTTPS)解析域名"""
        try:
            import aiohttp
            import base64
            import struct
            
            # 构建DNS查询包
            query = self._build_dns_query(domain)
            query_b64 = base64.urlsafe_b64encode(query).decode().rstrip('=')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{doh_server}?dns={query_b64}",
                    headers={'Accept': 'application/dns-message'}
                ) as resp:
                    if resp.status == 200:
                        dns_response = await resp.read()
                        ip = self._parse_dns_response(dns_response)
                        if ip:
                            self.logger.info(f"🔒 DoH解析成功: {domain} -> {ip}")
                            return ip
                            
        except Exception as e:
            self.logger.debug(f"DoH解析失败: {e}")
            
        return None
        
    def _build_dns_query(self, domain: str) -> bytes:
        """构建DNS查询包"""
        query = bytearray()
        
        # DNS头部
        query.extend(struct.pack('>H', 0x1234))  # ID
        query.extend(struct.pack('>H', 0x0100))  # Flags
        query.extend(struct.pack('>H', 1))       # Questions
        query.extend(struct.pack('>H', 0))       # Answers
        query.extend(struct.pack('>H', 0))       # Authority
        query.extend(struct.pack('>H', 0))       # Additional
        
        # 查询部分
        for part in domain.split('.'):
            query.append(len(part))
            query.extend(part.encode())
        query.append(0)  # 结束标记
        
        query.extend(struct.pack('>H', 1))   # Type A
        query.extend(struct.pack('>H', 1))   # Class IN
        
        return bytes(query)
        
    def _parse_dns_response(self, response: bytes) -> Optional[str]:
        """解析DNS响应包"""
        try:
            # 简化的DNS响应解析
            # 跳过头部（12字节）和查询部分
            offset = 12
            
            # 跳过查询部分
            while offset < len(response) and response[offset] != 0:
                length = response[offset]
                offset += length + 1
            offset += 5  # 跳过结束标记和类型/类别
            
            # 解析答案部分
            if offset + 16 <= len(response):
                # 跳过名称、类型、类别、TTL
                offset += 10
                # 读取数据长度
                data_len = struct.unpack('>H', response[offset:offset+2])[0]
                offset += 2
                
                if data_len == 4:  # IPv4地址
                    ip_bytes = response[offset:offset+4]
                    ip = '.'.join(str(b) for b in ip_bytes)
                    return ip
                    
        except Exception as e:
            pass
            
        return None 