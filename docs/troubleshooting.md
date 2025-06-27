# PyProxy 故障排除指南

本文档帮助您诊断和解决PyProxy使用中遇到的常见问题。

## 🚨 常见问题

### 1. 连接问题

#### 问题：无法连接到Trojan服务器
```
❌ [ERROR] 连接服务器失败: [Errno 11001] getaddrinfo failed
```

**解决方案：**
1. 检查网络连接是否正常
2. 确认服务器地址是否正确
3. 检查DNS设置
4. 尝试使用IP地址替代域名

#### 问题：SSL连接错误
```
❌ [ERROR] SSL错误: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**解决方案：**
1. 在配置文件中设置 `verify_ssl: false`
2. 检查系统时间是否正确
3. 更新系统SSL证书

#### 问题：密码认证失败
```
❌ [ERROR] Trojan认证失败
```

**解决方案：**
1. 确认密码是否正确（区分大小写）
2. 检查配置文件中的密码字段
3. 联系服务器管理员确认账户状态

### 2. 性能问题

#### 问题：连接速度慢
**现象：** 网页加载缓慢，下载速度不理想

**解决方案：**
1. 检查网络环境和带宽
2. 调整配置文件中的超时设置：
   ```yaml
   performance:
     read_timeout: 600
     write_timeout: 60
     buffer_size: 16384
   ```
3. 尝试不同的服务器
4. 检查本地网络状况

#### 问题：频繁断连
**现象：** 连接经常中断，需要重新连接

**解决方案：**
1. 启用心跳监控：
   ```yaml
   heartbeat:
     enabled: true
     interval: 3
     timeout: 5
     max_failures: 2
   ```
2. 检查网络稳定性
3. 调整超时设置

### 3. 程序错误

#### 问题：端口被占用
```
❌ [ERROR] [Errno 10048] 通常每个套接字地址只允许使用一次
```

**解决方案：**
1. 更改配置文件中的端口：
   ```yaml
   local:
     port: 1081  # 使用其他端口
   ```
2. 检查并关闭占用端口的程序：
   ```bash
   netstat -ano | findstr :1080
   ```
3. 重启系统释放端口

#### 问题：权限不足
```
❌ [ERROR] [Errno 13] Permission denied
```

**解决方案：**
1. 以管理员身份运行程序
2. 检查防火墙设置
3. 确认有足够的系统权限

#### 问题：模块导入错误
```
❌ ModuleNotFoundError: No module named 'yaml'
```

**解决方案：**
1. 安装缺失的依赖：
   ```bash
   pip install pyyaml requests colorama
   ```
2. 运行设置脚本：
   ```bash
   python scripts/setup.py
   ```

### 4. 路由问题

#### 问题：某些网站无法访问
**现象：** 特定网站无法打开或加载失败

**解决方案：**
1. 检查路由配置：
   ```yaml
   routing:
     direct_domains:
       - "*.example.com"  # 添加到直连列表
   ```
2. 清除DNS缓存：
   ```bash
   ipconfig /flushdns
   ```
3. 尝试手动指定代理或直连

#### 问题：国内网站也走代理
**现象：** 国内网站访问慢，IP显示为代理IP

**解决方案：**
1. 检查直连域名列表：
   ```yaml
   routing:
     direct_domains:
       - "*.baidu.com"
       - "*.qq.com"
       - "*.taobao.com"
   ```
2. 重启代理程序使配置生效

## 🔍 诊断工具

### 1. 运行综合测试
```bash
python tests/comprehensive_test.py
```
这个工具会自动诊断常见问题并提供解决建议。

### 2. 启用调试模式
在配置文件中设置：
```yaml
log:
  level: "DEBUG"
  verbose_traffic: true
  show_http_details: true
```

### 3. 检查端口状态
```bash
# Windows
netstat -ano | findstr :1080

# Linux/Mac
netstat -tuln | grep :1080
```

### 4. 测试网络连接
```bash
# 测试直连
curl "https://httpbin.org/ip"

# 测试代理
curl --socks5 127.0.0.1:1080 "https://httpbin.org/ip"
```

## 📋 问题收集

### 收集诊断信息

在报告问题时，请提供以下信息：

1. **系统信息**
   - 操作系统版本
   - Python版本
   - PyProxy版本

2. **配置文件**（隐藏敏感信息）
   ```yaml
   trojan:
     server: "***"
     port: 8888
     password: "***"
   ```

3. **错误日志**
   启用DEBUG模式并提供完整错误信息

4. **网络环境**
   - 是否使用VPN
   - 防火墙设置
   - 网络类型（家庭/企业/公共）

### 生成诊断报告

```bash
# 运行诊断脚本
python tests/comprehensive_test.py > diagnosis.txt

# 查看日志
tail -f logs/pyproxy.log
```

## 🛠️ 高级故障排除

### 1. 网络抓包分析

使用Wireshark等工具分析网络流量：
1. 开始抓包
2. 启动PyProxy
3. 访问测试网站
4. 分析SSL握手和数据传输

### 2. 防火墙配置

**Windows防火墙：**
1. 控制面板 → 系统和安全 → Windows Defender防火墙
2. 点击"允许应用通过防火墙"
3. 添加Python.exe到允许列表

**第三方防火墙：**
- 将Python.exe添加到白名单
- 允许1080端口入站连接

### 3. 代理链测试

测试代理链的每个环节：
1. 本地SOCKS5代理 (127.0.0.1:1080)
2. Trojan连接到服务器
3. 服务器到目标网站

### 4. 性能优化

**系统级优化：**
1. 增加TCP连接数限制
2. 调整网络缓冲区大小
3. 优化DNS设置

**程序级优化：**
```yaml
performance:
  connection_pool_size: 20
  read_timeout: 300
  write_timeout: 30
  buffer_size: 16384
```

## 🆘 获取帮助

### 1. 文档资源
- [README.md](README.md) - 基础使用指南
- [configuration.md](configuration.md) - 配置详细说明
- [api.md](api.md) - API参考文档

### 2. 在线资源
- GitHub Issues - 报告Bug和功能请求
- 社区论坛 - 用户交流和经验分享
- 官方文档 - 最新版本信息

### 3. 自助排除步骤

1. **阅读错误信息** - 仔细查看控制台输出
2. **检查配置文件** - 确认所有设置正确
3. **运行测试工具** - 使用内置诊断功能
4. **查看日志文件** - 启用详细日志记录
5. **搜索已知问题** - 查看文档和FAQ
6. **创建最小复现** - 使用简单配置测试

### 4. 报告问题模板

```
### 问题描述
简要描述遇到的问题

### 复现步骤
1. 配置文件设置
2. 启动命令
3. 触发问题的操作

### 期望结果
描述期望的正常行为

### 实际结果
描述实际发生的情况

### 环境信息
- 操作系统: Windows 10
- Python版本: 3.9.0
- PyProxy版本: 1.1.0

### 日志信息
```
粘贴相关日志内容
```

### 已尝试的解决方案
列出已经尝试过的解决方法
```

## 💡 预防性维护

### 1. 定期检查
- 每周运行一次综合测试
- 定期检查日志文件大小
- 监控系统资源使用情况

### 2. 配置备份
```bash
# 备份工作配置
cp configs/standard.yaml configs/backup_$(date +%Y%m%d).yaml
```

### 3. 更新维护
- 关注PyProxy版本更新
- 定期更新Python和依赖包
- 检查服务器配置变化

### 4. 性能监控
- 记录平均延迟变化
- 监控连接成功率
- 观察内存和CPU使用

通过这些故障排除方法，您应该能够解决大部分常见问题。如果问题仍然存在，请参考其他文档或寻求社区帮助。 