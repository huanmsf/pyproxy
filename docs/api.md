# PyProxy API 参考文档

本文档提供PyProxy的详细API参考，包括所有类、方法和配置选项。

## 📚 核心类

### PyProxyClient

主要的代理客户端类，负责协调所有组件。

```python
from pyproxy import PyProxyClient, Config

# 创建客户端
config = Config.from_file('configs/standard.yaml')
client = PyProxyClient(config)

# 启动客户端
await client.start()
```

#### 方法

- `__init__(config: Config)` - 初始化客户端
- `async start()` - 启动代理服务
- `async stop()` - 停止代理服务
- `get_stats()` - 获取统计信息

### Config

配置管理类，处理配置文件的加载和验证。

```python
from pyproxy import Config

# 从文件加载配置
config = Config.from_file('configs/config.yaml')

# 访问配置项
server = config.trojan.server
port = config.local.port
```

#### 配置结构

```python
class Config:
    trojan: TrojanConfig
    local: LocalConfig
    log: LogConfig
    routing: RoutingConfig
    heartbeat: HeartbeatConfig
    performance: PerformanceConfig
```

#### 方法

- `@classmethod from_file(cls, file_path: str) -> Config` - 从文件加载配置
- `@classmethod from_dict(cls, data: dict) -> Config` - 从字典创建配置
- `to_dict() -> dict` - 转换为字典
- `validate()` - 验证配置有效性

### Logger

日志管理类，提供统一的日志记录功能。

```python
from pyproxy import Logger

# 创建日志器
logger = Logger("component_name", level="INFO")

# 记录日志
logger.info("信息")
logger.warning("警告")
logger.error("错误")
logger.debug("调试信息")
```

#### 方法

- `__init__(name: str, level: str = "INFO", file: str = None)`
- `info(message: str)` - 记录信息日志
- `warning(message: str)` - 记录警告日志
- `error(message: str)` - 记录错误日志
- `debug(message: str)` - 记录调试日志

## 🔧 组件类

### TrojanProtocol

实现Trojan协议的核心类。

```python
from pyproxy.trojan import TrojanProtocol

# 创建Trojan连接
trojan = TrojanProtocol(config.trojan, logger)
await trojan.connect()
```

#### 方法

- `__init__(config: TrojanConfig, logger: Logger)`
- `async connect() -> ssl.SSLSocket` - 建立连接
- `async send_request(data: bytes)` - 发送数据
- `async receive_response() -> bytes` - 接收数据
- `close()` - 关闭连接

### SOCKS5Proxy

SOCKS5代理服务器实现。

```python
from pyproxy.socks5 import SOCKS5Proxy

# 创建SOCKS5代理
proxy = SOCKS5Proxy(config, logger)
await proxy.start()
```

#### 方法

- `__init__(config: Config, logger: Logger)`
- `async start()` - 启动代理服务
- `async stop()` - 停止代理服务
- `async handle_client(reader, writer)` - 处理客户端连接

### Router

路由管理器，处理域名路由规则。

```python
from pyproxy.router import Router

# 创建路由器
router = Router(config.routing, logger)

# 检查域名是否需要代理
should_proxy = router.should_proxy("www.google.com")
```

#### 方法

- `__init__(config: RoutingConfig, logger: Logger)`
- `should_proxy(domain: str) -> bool` - 判断是否需要代理
- `add_direct_domain(domain: str)` - 添加直连域名
- `add_proxy_domain(domain: str)` - 添加代理域名

### HeartbeatMonitor

心跳监控器，监控服务器连接状态。

```python
from pyproxy.heartbeat import HeartbeatMonitor

# 创建心跳监控
monitor = HeartbeatMonitor(config.heartbeat, logger)
await monitor.start()
```

#### 方法

- `__init__(config: HeartbeatConfig, logger: Logger)`
- `async start()` - 开始监控
- `async stop()` - 停止监控
- `async check_connection() -> bool` - 检查连接状态

## 📊 配置类详解

### TrojanConfig

```python
class TrojanConfig:
    server: str          # 服务器地址
    port: int            # 服务器端口
    password: str        # 连接密码
    verify_ssl: bool     # 是否验证SSL
    sni: str            # SNI
```

### LocalConfig

```python
class LocalConfig:
    listen: str          # 监听地址
    port: int           # 监听端口
```

### LogConfig

```python
class LogConfig:
    level: str                  # 日志级别
    file: str                  # 日志文件路径
    verbose_traffic: bool      # 详细流量日志
    show_http_details: bool    # HTTP详情
```

### RoutingConfig

```python
class RoutingConfig:
    direct_domains: List[str]   # 直连域名列表
    proxy_domains: List[str]    # 代理域名列表
```

### HeartbeatConfig

```python
class HeartbeatConfig:
    enabled: bool        # 是否启用
    interval: int        # 心跳间隔(秒)
    timeout: int         # 超时时间(秒)
    max_failures: int    # 最大失败次数
```

### PerformanceConfig

```python
class PerformanceConfig:
    connection_pool_size: int   # 连接池大小
    read_timeout: int          # 读取超时
    write_timeout: int         # 写入超时
    buffer_size: int           # 缓冲区大小
```

## 🔧 工具函数

### format_bytes

格式化字节数为可读字符串。

```python
from pyproxy.utils import format_bytes

print(format_bytes(1024))      # "1.0 KB"
print(format_bytes(1048576))   # "1.0 MB"
```

### parse_address

解析地址字符串为主机和端口。

```python
from pyproxy.utils import parse_address

host, port = parse_address("www.google.com:443")
# host = "www.google.com", port = 443
```

### validate_domain

验证域名格式是否正确。

```python
from pyproxy.utils import validate_domain

is_valid = validate_domain("www.example.com")  # True
```

## 📈 统计信息

### 获取运行统计

```python
stats = client.get_stats()
print(f"连接数: {stats['connections']}")
print(f"传输字节: {stats['bytes_sent']}")
print(f"运行时间: {stats['uptime']}")
```

### 统计信息结构

```python
{
    "connections": int,         # 总连接数
    "active_connections": int,  # 活动连接数
    "bytes_sent": int,         # 发送字节数
    "bytes_received": int,     # 接收字节数
    "uptime": float,           # 运行时间(秒)
    "errors": int,             # 错误次数
    "server_status": str       # 服务器状态
}
```

## 🛠️ 自定义扩展

### 创建自定义路由器

```python
from pyproxy.router import Router

class CustomRouter(Router):
    def should_proxy(self, domain: str) -> bool:
        # 自定义路由逻辑
        if domain.endswith('.cn'):
            return False  # 中国域名直连
        return True       # 其他域名走代理
```

### 创建自定义日志器

```python
from pyproxy.logger import Logger

class CustomLogger(Logger):
    def info(self, message: str):
        # 自定义日志格式
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ℹ️  {message}")
```

## ⚠️ 异常处理

### 常见异常类型

```python
from pyproxy.exceptions import (
    ConfigError,          # 配置错误
    ConnectionError,      # 连接错误
    ProxyError,          # 代理错误
    TrojanError          # Trojan协议错误
)

try:
    client = PyProxyClient(config)
    await client.start()
except ConfigError as e:
    print(f"配置错误: {e}")
except ConnectionError as e:
    print(f"连接错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 🔒 安全注意事项

1. **密码保护**: 不要在代码中硬编码密码
2. **SSL验证**: 生产环境建议启用SSL验证
3. **日志安全**: 注意不要在日志中泄露敏感信息
4. **权限控制**: 确保程序有适当的运行权限

## 📝 使用示例

### 基础使用

```python
import asyncio
from pyproxy import PyProxyClient, Config

async def main():
    # 加载配置
    config = Config.from_file('configs/standard.yaml')
    
    # 创建客户端
    client = PyProxyClient(config)
    
    try:
        # 启动服务
        await client.start()
    except KeyboardInterrupt:
        # 优雅关闭
        await client.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### 自定义配置

```python
from pyproxy import Config

# 从字典创建配置
config_data = {
    'trojan': {
        'server': 'your-server.com',
        'port': 443,
        'password': 'your-password',
        'verify_ssl': False,
        'sni': 'your-server.com'
    },
    'local': {
        'listen': '127.0.0.1',
        'port': 1080
    },
    'log': {
        'level': 'INFO'
    }
}

config = Config.from_dict(config_data)
```

### 监控和统计

```python
import asyncio
from pyproxy import PyProxyClient, Config

async def monitor_stats(client):
    while True:
        stats = client.get_stats()
        print(f"活动连接: {stats['active_connections']}")
        print(f"传输数据: {stats['bytes_sent']} bytes")
        await asyncio.sleep(10)

async def main():
    config = Config.from_file('configs/standard.yaml')
    client = PyProxyClient(config)
    
    # 启动监控任务
    monitor_task = asyncio.create_task(monitor_stats(client))
    
    try:
        await client.start()
    finally:
        monitor_task.cancel()

asyncio.run(main())
```

## 📚 更多资源

- [README.md](README.md) - 项目概述和快速开始
- [configuration.md](configuration.md) - 详细配置说明
- [troubleshooting.md](troubleshooting.md) - 故障排除指南
- GitHub Repository - 源代码和Issues
- 测试工具 - `tests/comprehensive_test.py`

这个API文档涵盖了PyProxy的所有主要功能和使用方法。如果您需要更多信息或有疑问，请参考其他文档或提交Issue。 