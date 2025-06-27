# PyProxy 配置说明

本文档详细说明PyProxy的配置选项和使用方法。

## 📄 配置文件

PyProxy使用YAML格式的配置文件，默认提供三个配置模板：

- `configs/config.yaml` - 标准配置，适合日常使用
- `configs/config_advanced.yaml` - 高级配置，包含所有可用选项
- `configs/config_example.yaml` - 配置示例，包含实际服务器信息

## 🔧 配置选项详解

### Trojan服务器配置

```yaml
trojan:
  server: "www.example.com"    # 服务器地址
  port: 8888                   # 服务器端口 (1-65535)
  password: "your_password"    # Trojan密码
  verify_ssl: false            # 是否验证SSL证书
  sni: "www.example.com"      # SNI (Server Name Indication)
```

**配置说明：**
- `server`: Trojan服务器的域名或IP地址
- `port`: 服务器监听端口，通常是443或其他端口
- `password`: 连接服务器的密码，必须与服务器配置一致
- `verify_ssl`: 是否验证SSL证书，设为false可避免证书问题
- `sni`: SSL握手时使用的服务器名，通常与server相同

### 本地代理配置

```yaml
local:
  listen: "127.0.0.1"         # 监听地址
  port: 1080                  # 监听端口
```

**配置说明：**
- `listen`: 本地监听地址，建议使用127.0.0.1（仅本机访问）
- `port`: SOCKS5代理监听端口，默认1080

### 日志配置

```yaml
log:
  level: "INFO"                    # 日志级别
  file: "logs/pyproxy.log"        # 日志文件路径
  verbose_traffic: false          # 是否显示详细流量
  show_http_details: false        # 是否显示HTTP详情
```

**日志级别：**
- `DEBUG`: 最详细，包含所有调试信息
- `INFO`: 一般信息，推荐日常使用
- `WARNING`: 警告信息
- `ERROR`: 仅错误信息

**其他选项：**
- `file`: 日志文件路径，为空则输出到控制台
- `verbose_traffic`: 显示详细的数据传输信息
- `show_http_details`: 显示HTTP请求的详细信息

### 路由配置

```yaml
routing:
  direct_domains:              # 直连域名列表
    - "*.baidu.com"
    - "*.qq.com"
    - "localhost"
    - "127.0.0.1"
  
  proxy_domains:               # 代理域名列表
    - "*"                      # 匹配所有其他域名
```

**路由规则：**
- `direct_domains`: 这些域名将直接连接，不使用代理
- `proxy_domains`: 这些域名将通过代理连接
- 支持通配符 `*` 匹配，如 `*.example.com` 匹配所有子域名
- 规则按顺序匹配，先匹配的规则优先

### 高级配置（完整版）

```yaml
# 防火墙绕过配置
bypass:
  enabled: false               # 是否启用绕过功能
  domain_fronting: false       # 域名前置
  ip_fragmentation: false      # IP分片
  custom_dns: []              # 自定义DNS服务器

# 心跳监控配置
heartbeat:
  enabled: true               # 是否启用心跳监控
  interval: 5                 # 心跳间隔(秒)
  timeout: 10                 # 连接超时(秒)
  max_failures: 3            # 最大失败次数

# 性能调优配置
performance:
  connection_pool_size: 10    # 连接池大小
  read_timeout: 300          # 读取超时(秒)
  write_timeout: 30          # 写入超时(秒)
  buffer_size: 8192          # 缓冲区大小(字节)
```

## 📋 配置示例

### 基础配置示例

```yaml
# 最简单的配置
trojan:
  server: "your-server.com"
  port: 443
  password: "your_password123"
  verify_ssl: false
  sni: "your-server.com"

local:
  listen: "127.0.0.1"
  port: 1080

log:
  level: "INFO"
  file: ""

routing:
  direct_domains:
    - "*.baidu.com"
    - "*.qq.com"
    - "localhost"
  proxy_domains:
    - "*"
```

### 高性能配置示例

```yaml
# 适合高流量使用的配置
trojan:
  server: "your-server.com"
  port: 443
  password: "your_password123"
  verify_ssl: false
  sni: "your-server.com"

local:
  listen: "127.0.0.1"
  port: 1080

log:
  level: "WARNING"           # 减少日志输出
  file: "logs/pyproxy.log"
  verbose_traffic: false
  show_http_details: false

performance:
  connection_pool_size: 20   # 增加连接池
  read_timeout: 600         # 增加读取超时
  write_timeout: 60         # 增加写入超时
  buffer_size: 16384        # 增加缓冲区

routing:
  direct_domains:
    - "*.baidu.com"
    - "*.qq.com"
    - "*.taobao.com"
    - "*.alipay.com"
    - "localhost"
    - "127.0.0.1"
    - "192.168.*"
    - "10.*"
  proxy_domains:
    - "*"
```

### 调试配置示例

```yaml
# 用于问题诊断的配置
trojan:
  server: "your-server.com"
  port: 443
  password: "your_password123"
  verify_ssl: false
  sni: "your-server.com"

local:
  listen: "127.0.0.1"
  port: 1080

log:
  level: "DEBUG"             # 最详细的日志
  file: "logs/debug.log"
  verbose_traffic: true      # 显示详细流量
  show_http_details: true    # 显示HTTP详情

heartbeat:
  enabled: true
  interval: 3                # 更频繁的心跳
  timeout: 5
  max_failures: 2

routing:
  direct_domains:
    - "localhost"
    - "127.0.0.1"
  proxy_domains:
    - "*"
```

## 🎯 使用技巧

### 1. 路由规则优化

**国内网站直连：**
```yaml
direct_domains:
  - "*.baidu.com"
  - "*.qq.com"
  - "*.weixin.qq.com"
  - "*.taobao.com"
  - "*.tmall.com"
  - "*.alipay.com"
  - "*.163.com"
  - "*.sina.com.cn"
  - "*.douban.com"
  - "*.zhihu.com"
  - "*.bilibili.com"
```

**局域网直连：**
```yaml
direct_domains:
  - "localhost"
  - "127.0.0.1"
  - "192.168.*"
  - "10.*"
  - "172.16.*"
  - "*.local"
```

### 2. 性能调优

**低延迟配置：**
- 减少 `read_timeout` 和 `write_timeout`
- 增加 `connection_pool_size`
- 设置 `level: "WARNING"` 减少日志开销

**高并发配置：**
- 增加 `buffer_size`
- 增加 `connection_pool_size`
- 调整心跳间隔

### 3. 故障排除

**连接问题：**
- 启用 `DEBUG` 日志级别
- 设置 `verbose_traffic: true`
- 检查 `server`、`port`、`password` 配置

**性能问题：**
- 调整超时设置
- 检查路由规则是否合理
- 监控心跳状态

## 📝 配置文件管理

### 创建新配置

1. 复制现有配置文件：
```bash
cp configs/config.yaml configs/my_config.yaml
```

2. 编辑新配置文件
3. 使用新配置启动：
```bash
python scripts/start.py -c configs/my_config.yaml
```

### 配置验证

使用测试工具验证配置：
```bash
python tests/comprehensive_test.py
```

### 配置备份

建议定期备份工作正常的配置文件：
```bash
cp configs/config.yaml configs/config_backup_$(date +%Y%m%d).yaml
```

## ⚠️ 注意事项

1. **密码安全**: 不要在公共场所或版本控制中暴露密码
2. **端口冲突**: 确保本地端口没有被其他程序占用
3. **防火墙**: 确保防火墙允许代理程序运行
4. **DNS**: 在某些网络环境下可能需要自定义DNS设置
5. **SSL证书**: 如果遇到SSL问题，尝试设置 `verify_ssl: false`

## 🔄 配置热更新

目前PyProxy不支持配置热更新，修改配置后需要重启程序：

1. 停止当前程序 (Ctrl+C)
2. 修改配置文件
3. 重新启动程序

未来版本将考虑添加配置热更新功能。 