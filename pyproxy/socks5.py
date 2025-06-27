import asyncio
import struct
import socket
import ssl
import time
from typing import Tuple, Optional
from .config import Config
from .logger import Logger
from .trojan import TrojanClient
from .router import Router


class SOCKS5Server:
    """SOCKS5代理服务器 - 修复版"""
    
    # SOCKS5版本
    VERSION = 0x05
    
    # 认证方法
    AUTH_NO_AUTH = 0x00
    AUTH_NO_ACCEPTABLE = 0xFF
    
    # 命令类型
    CMD_CONNECT = 0x01
    CMD_BIND = 0x02
    CMD_UDP_ASSOCIATE = 0x03
    
    # 地址类型
    ATYP_IPv4 = 0x01
    ATYP_DOMAIN = 0x03
    ATYP_IPv6 = 0x04
    
    # 回复代码
    REP_SUCCESS = 0x00
    REP_GENERAL_FAILURE = 0x01
    REP_CONNECTION_NOT_ALLOWED = 0x02
    REP_NETWORK_UNREACHABLE = 0x03
    REP_HOST_UNREACHABLE = 0x04
    REP_CONNECTION_REFUSED = 0x05
    REP_TTL_EXPIRED = 0x06
    REP_COMMAND_NOT_SUPPORTED = 0x07
    REP_ADDRESS_TYPE_NOT_SUPPORTED = 0x08
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.trojan_client = TrojanClient(config.trojan, logger)
        self.router = Router(config.routing, logger)
        self.server = None
        self.connection_counter = 0
        
    def get_connection_id(self):
        """获取连接ID"""
        self.connection_counter += 1
        return self.connection_counter
        
    def format_bytes(self, bytes_count):
        """格式化字节数"""
        if bytes_count < 1024:
            return f"{bytes_count}B"
        elif bytes_count < 1024 * 1024:
            return f"{bytes_count/1024:.1f}KB"
        else:
            return f"{bytes_count/(1024*1024):.1f}MB"
        
    async def start(self):
        """启动SOCKS5服务器"""
        try:
            self.server = await asyncio.start_server(
                self.handle_client,
                self.config.local.listen,
                self.config.local.port
            )
            
            addr = self.server.sockets[0].getsockname()
            self.logger.info(f"SOCKS5代理服务器已启动: {addr[0]}:{addr[1]}")
            
            async with self.server:
                await self.server.serve_forever()
                
        except Exception as e:
            self.logger.error(f"启动SOCKS5服务器失败: {e}")
            raise
            
    async def stop(self):
        """停止SOCKS5服务器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.logger.info("SOCKS5代理服务器已停止")
            
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理客户端连接"""
        client_addr = writer.get_extra_info('peername')
        connection_id = self.get_connection_id()
        
        try:
            self.logger.info(f"🔗 [连接#{connection_id}] 新客户端连接: {client_addr[0]}:{client_addr[1]}")
            
            # SOCKS5握手
            if not await self.socks5_handshake(reader, writer):
                return
            
            # 处理连接请求
            target_host, target_port = await self.handle_connect_request(reader, writer)
            if not target_host:
                return
                
            # 建立到目标的连接
            target_reader, target_writer = await self.connect_to_target(target_host, target_port, connection_id)
            
            # 发送成功响应
            await self.send_connect_response(writer, self.REP_SUCCESS)
            
            self.logger.info(f"🔄 [连接#{connection_id}] 开始数据转发: {target_host}:{target_port}")
            
            # 开始双向数据转发
            await self.relay_data(reader, writer, target_reader, target_writer, connection_id)
            
        except asyncio.CancelledError:
            self.logger.debug(f"🔒 [连接#{connection_id}] 连接被取消")
        except ConnectionResetError:
            self.logger.debug(f"🔒 [连接#{connection_id}] 连接被重置")
        except ssl.SSLError as e:
            if "APPLICATION_DATA_AFTER_CLOSE_NOTIFY" in str(e):
                self.logger.debug(f"🔒 [连接#{connection_id}] SSL连接正常关闭")
            elif "UNEXPECTED_EOF_WHILE_READING" in str(e):
                self.logger.debug(f"🔒 [连接#{connection_id}] SSL连接意外终止")
            else:
                self.logger.warning(f"⚠️ [连接#{connection_id}] SSL错误: {e}")
        except OSError as e:
            if e.errno == 10054:  # Connection reset by peer
                self.logger.debug(f"🔒 [连接#{connection_id}] 连接被对端重置")
            else:
                self.logger.warning(f"⚠️ [连接#{connection_id}] 网络错误: {e}")
        except Exception as e:
            self.logger.error(f"❌ [连接#{connection_id}] 处理客户端连接失败: {e}")
        finally:
            await self.close_connection(writer, connection_id, client_addr)
            
    async def close_connection(self, writer, connection_id, client_addr):
        """安全关闭连接"""
        try:
            if not writer.is_closing():
                writer.close()
                try:
                    await asyncio.wait_for(writer.wait_closed(), timeout=3.0)
                except asyncio.TimeoutError:
                    self.logger.debug(f"🔒 [连接#{connection_id}] 关闭连接超时")
        except Exception as e:
            self.logger.debug(f"🔒 [连接#{connection_id}] 关闭连接时出错: {e}")
        finally:
            self.logger.info(f"🔒 [连接#{connection_id}] 客户端连接已关闭: {client_addr[0]}:{client_addr[1]}")
            
    async def socks5_handshake(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> bool:
        """SOCKS5握手"""
        try:
            # 读取客户端握手请求
            data = await asyncio.wait_for(reader.read(262), timeout=30.0)
            if len(data) < 3:
                self.logger.warning("⚠️ SOCKS5握手数据不足")
                return False
                
            version, nmethods = struct.unpack('!BB', data[:2])
            if version != self.VERSION:
                self.logger.warning(f"⚠️ SOCKS5版本不匹配: {version}")
                return False
                
            self.logger.debug(f"🤝 SOCKS5握手: 版本={version}, 认证方法数={nmethods}")
                
            # 发送握手响应（无需认证）
            response = struct.pack('!BB', self.VERSION, self.AUTH_NO_AUTH)
            writer.write(response)
            await writer.drain()
            
            self.logger.debug("✅ SOCKS5握手成功")
            return True
            
        except asyncio.TimeoutError:
            self.logger.warning("⚠️ SOCKS5握手超时")
            return False
        except Exception as e:
            self.logger.error(f"❌ SOCKS5握手失败: {e}")
            return False
            
    async def handle_connect_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> Tuple[Optional[str], Optional[int]]:
        """处理连接请求"""
        try:
            # 读取请求头
            data = await asyncio.wait_for(reader.read(4), timeout=30.0)
            if len(data) != 4:
                self.logger.warning("⚠️ 连接请求头数据不足")
                return None, None
                
            version, cmd, rsv, atyp = struct.unpack('!BBBB', data)
            
            if version != self.VERSION:
                self.logger.warning(f"⚠️ 版本不匹配: {version}")
                await self.send_connect_response(writer, self.REP_GENERAL_FAILURE)
                return None, None
                
            if cmd != self.CMD_CONNECT:
                self.logger.warning(f"⚠️ 不支持的命令: {cmd}")
                await self.send_connect_response(writer, self.REP_COMMAND_NOT_SUPPORTED)
                return None, None
                
            # 读取目标地址
            if atyp == self.ATYP_IPv4:
                addr_data = await reader.read(4)
                target_host = socket.inet_ntoa(addr_data)
            elif atyp == self.ATYP_IPv6:
                addr_data = await reader.read(16)
                target_host = socket.inet_ntop(socket.AF_INET6, addr_data)
            elif atyp == self.ATYP_DOMAIN:
                domain_len_data = await reader.read(1)
                domain_len = struct.unpack('!B', domain_len_data)[0]
                domain_data = await reader.read(domain_len)
                target_host = domain_data.decode('utf-8')
            else:
                self.logger.warning(f"⚠️ 不支持的地址类型: {atyp}")
                await self.send_connect_response(writer, self.REP_ADDRESS_TYPE_NOT_SUPPORTED)
                return None, None
                
            # 读取目标端口
            port_data = await reader.read(2)
            target_port = struct.unpack('!H', port_data)[0]
            
            self.logger.debug(f"📋 解析目标: {target_host}:{target_port}")
            return target_host, target_port
            
        except asyncio.TimeoutError:
            self.logger.warning("⚠️ 连接请求处理超时")
            return None, None
        except Exception as e:
            self.logger.error(f"❌ 处理连接请求失败: {e}")
            await self.send_connect_response(writer, self.REP_GENERAL_FAILURE)
            return None, None
            
    async def send_connect_response(self, writer: asyncio.StreamWriter, rep: int, bind_host: str = "0.0.0.0", bind_port: int = 0):
        """发送连接响应"""
        try:
            # 构造响应
            response = struct.pack('!BBBB', self.VERSION, rep, 0, self.ATYP_IPv4)
            response += socket.inet_aton(bind_host)
            response += struct.pack('!H', bind_port)
            
            writer.write(response)
            await writer.drain()
            
        except Exception as e:
            self.logger.debug(f"发送连接响应失败: {e}")
            
    async def connect_to_target(self, target_host: str, target_port: int, connection_id: int):
        """建立到目标的连接"""
        use_proxy = self.router.should_proxy(target_host)
        proxy_method = "🌐 代理" if use_proxy else "🔗 直连"
        self.logger.info(f"📡 [连接#{connection_id}] 目标: {target_host}:{target_port} | 方式: {proxy_method}")
        
        if use_proxy:
            target_reader, target_writer = await self.trojan_client.connect(target_host, target_port)
            self.logger.info(f"✅ [连接#{connection_id}] 代理连接已建立: {target_host}:{target_port}")
        else:
            target_reader, target_writer = await asyncio.open_connection(target_host, target_port)
            self.logger.info(f"✅ [连接#{connection_id}] 直连已建立: {target_host}:{target_port}")
        
        return target_reader, target_writer
     
    async def relay_data(self, client_reader, client_writer, target_reader, target_writer, connection_id):
        """双向数据转发"""
        start_time = time.time()
        client_to_target_bytes = 0
        target_to_client_bytes = 0
        client_to_target_packets = 0
        target_to_client_packets = 0
        
        async def forward_data(reader, writer, direction):
            """转发数据的通用函数"""
            nonlocal client_to_target_bytes, target_to_client_bytes
            nonlocal client_to_target_packets, target_to_client_packets
            
            bytes_transferred = 0
            packets_count = 0
            
            try:
                while True:
                    try:
                        # 设置较短的读取超时
                        data = await asyncio.wait_for(reader.read(8192), timeout=300.0)
                        if not data:
                            break
                            
                        packets_count += 1
                        bytes_transferred += len(data)
                        
                        # 更新全局计数器
                        if direction == "client_to_target":
                            client_to_target_bytes += len(data)
                            client_to_target_packets += 1
                        else:
                            target_to_client_bytes += len(data)
                            target_to_client_packets += 1
                        
                        # HTTP协议解析
                        if self.config.log.show_http_details and len(data) > 0:
                            await self.parse_http_data(data, direction, connection_id)
                        
                        # 写入数据
                        writer.write(data)
                        await asyncio.wait_for(writer.drain(), timeout=30.0)
                        
                        # 详细流量日志
                        if self.config.log.verbose_traffic:
                            self.logger.debug(f"📡 [连接#{connection_id}] {direction}: {len(data)}字节")
                            
                    except asyncio.TimeoutError:
                        self.logger.debug(f"⏰ [连接#{connection_id}] {direction} 读取超时")
                        break
                    except ConnectionResetError:
                        self.logger.debug(f"🔗 [连接#{connection_id}] {direction} 连接被重置")
                        break
                    except ssl.SSLError as e:
                        if any(msg in str(e) for msg in ["APPLICATION_DATA_AFTER_CLOSE_NOTIFY", "UNEXPECTED_EOF"]):
                            self.logger.debug(f"🔒 [连接#{connection_id}] {direction} SSL正常关闭")
                        else:
                            self.logger.debug(f"🔒 [连接#{connection_id}] {direction} SSL错误: {e}")
                        break
                    except OSError as e:
                        if e.errno in [10054, 10053]:  # Connection reset/aborted
                            self.logger.debug(f"🔗 [连接#{connection_id}] {direction} 网络连接中断")
                        else:
                            self.logger.debug(f"❌ [连接#{connection_id}] {direction} 网络错误: {e}")
                        break
                    except Exception as e:
                        self.logger.debug(f"❌ [连接#{connection_id}] {direction} 转发错误: {e}")
                        break
                        
            except Exception as e:
                self.logger.debug(f"❌ [连接#{connection_id}] {direction} 转发失败: {e}")
            finally:
                try:
                    if not writer.is_closing():
                        writer.close()
                except Exception:
                    pass
                    
                elapsed_time = time.time() - start_time
                self.logger.info(f"📊 [连接#{connection_id}] {direction}完成: {packets_count}个包, {bytes_transferred}字节, 耗时{elapsed_time:.2f}秒")
        
        # 启动双向转发任务
        tasks = [
            asyncio.create_task(forward_data(client_reader, target_writer, "上传 (客户端→目标)")),
            asyncio.create_task(forward_data(target_reader, client_writer, "下载 (目标→客户端)"))
        ]
        
        try:
            # 等待任意一个方向完成或出错
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            
            # 取消剩余的任务
            for task in pending:
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=1.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
                    
        except Exception as e:
            self.logger.debug(f"❌ [连接#{connection_id}] 数据转发异常: {e}")
        finally:
            # 关闭连接
            for writer in [client_writer, target_writer]:
                try:
                    if not writer.is_closing():
                        writer.close()
                except Exception:
                    pass
            
            # 统计信息
            elapsed_time = time.time() - start_time
            total_bytes = client_to_target_bytes + target_to_client_bytes
            speed = total_bytes / elapsed_time if elapsed_time > 0 else 0
            
            speed_str = self.format_bytes(speed) + "/s"
            total_str = self.format_bytes(total_bytes)
            
            self.logger.info(f"📈 [连接#{connection_id}] 传输统计: ⬆️{self.format_bytes(client_to_target_bytes)} ⬇️{self.format_bytes(target_to_client_bytes)} 📊总计{total_str} ⏱️{elapsed_time:.2f}秒 🚀{speed_str}")
     
    async def parse_http_data(self, data: bytes, direction: str, connection_id: int):
        """记录HTTP请求/响应信息"""
        try:
            text_data = data.decode('utf-8', errors='ignore')
            
            if direction == "client_to_target" and text_data.startswith(('GET ', 'POST ', 'PUT ', 'DELETE ', 'HEAD ', 'OPTIONS ')):
                # HTTP请求
                lines = text_data.split('\n')
                if lines:
                    request_line = lines[0].strip()
                    self.logger.info(f"🌐 [连接#{connection_id}] HTTP请求: {request_line}")
                    
                    # 提取Host头
                    for line in lines[1:5]:  # 只检查前几行
                        if line.lower().startswith('host:'):
                            host = line.split(':', 1)[1].strip()
                            self.logger.info(f"🏠 [连接#{connection_id}] 目标主机: {host}")
                            break
            
            elif direction == "target_to_client" and text_data.startswith('HTTP/'):
                # HTTP响应
                lines = text_data.split('\n')
                if lines:
                    status_line = lines[0].strip()
                    self.logger.info(f"📨 [连接#{connection_id}] HTTP响应: {status_line}")
                    
        except Exception as e:
            # 忽略解析错误，可能是二进制数据
            pass 