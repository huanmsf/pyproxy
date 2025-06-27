# PyProxy 代理客户端

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

**PyProxy** 是一个用Python实现的Trojan协议代理客户端，支持SOCKS5代理、智能路由、心跳监控等功能。

## 🚀 快速开始

### 1. 项目初始化
```bash
# 运行设置向导（推荐新用户）
python scripts/setup.py

# 或手动创建目录
mkdir logs temp
```

### 2. 配置服务器
编辑 `configs/config.yaml` 文件，将示例值替换为实际服务器信息：
```yaml
trojan:
  server: "your.trojan.server.com"    # 修改为你的服务器地址
  port: 443                            # 修改为正确端口
  password: "your_password_here"       # 修改为正确密码
```

💡 **配置提示**: 查看 `configs/配置说明.md` 获取详细配置指南

### 3. 启动代理
```bash
# 使用标准配置启动
python scripts/start.py

# 或指定配置文件
python scripts/start.py -c configs/config_advanced.yaml

# Windows用户可以双击
start.bat
```

### 4. 测试代理
```bash
# 运行综合测试
python tests/comprehensive_test.py

# Windows用户可以双击
test.bat
```

## 📁 项目结构

```
pyproxy/
├── pyproxy/              # 核心代码模块
│   ├── __init__.py
│   ├── client.py         # 主客户端
│   ├── config.py         # 配置管理
│   ├── logger.py         # 日志系统
│   ├── trojan.py         # Trojan协议
│   ├── socks5.py         # SOCKS5代理
│   ├── routing.py        # 路由管理
│   └── heartbeat.py      # 心跳监控
├── configs/              # 配置文件
│   ├── config.yaml       # 标准配置（推荐使用）
│   ├── config_advanced.yaml  # 高级配置
│   └── config_example.yaml   # 配置示例
├── scripts/              # 脚本文件
│   ├── start.py          # 启动脚本
│   └── setup.py          # 设置脚本
├── tests/                # 测试文件
│   └── comprehensive_test.py  # 综合测试工具
├── docs/                 # 文档文件
│   ├── README.md         # 主要说明
│   ├── configuration.md  # 配置说明
│   ├── troubleshooting.md # 故障排除
│   └── api.md           # API文档
├── logs/                 # 日志目录
├── temp/                 # 临时文件
├── start.bat            # Windows启动脚本
├── test.bat             # Windows测试脚本
├── LICENSE              # MIT许可证文件
├── LICENSE-zh.md        # 中文许可证说明
└── requirements.txt     # Python依赖列表
```

## ⚙️ 配置说明

### 基础配置
- **服务器设置**: 修改`trojan`部分的服务器信息
- **本地端口**: 默认监听`127.0.0.1:1080`
- **日志级别**: INFO, DEBUG, WARNING, ERROR

### 路由配置
- **直连域名**: 不使用代理的网站列表
- **代理域名**: 使用代理的网站列表
- **智能路由**: 自动判断是否使用代理

详细配置说明请查看 [docs/configuration.md](docs/configuration.md)

## 🧪 测试功能

运行 `python tests/comprehensive_test.py` 进行全面测试：

1. **代理状态检查** - 确认代理服务正在运行
2. **直接连接测试** - 测试不使用代理的连接
3. **代理连接测试** - 测试通过代理的连接
4. **路由规则测试** - 验证智能路由功能
5. **性能测试** - 测试连接速度和延迟
6. **压力测试** - 测试并发连接处理能力
7. **问题诊断** - 自动诊断常见问题

## 🛠️ 故障排除

### 常见问题

**1. 连接失败**
- 检查服务器地址、端口、密码
- 确认网络连接正常
- 查看日志文件获取详细错误

**2. 速度较慢**
- 调整配置文件中的超时设置
- 检查服务器网络状况
- 尝试不同的服务器

**3. 某些网站无法访问**
- 检查路由配置
- 确认域名是否在直连列表中
- 尝试手动添加到代理列表

更多故障排除信息请查看 [docs/troubleshooting.md](docs/troubleshooting.md)

## 📖 使用示例

### 浏览器配置
在浏览器中设置SOCKS5代理：
- 地址：`127.0.0.1`
- 端口：`1080`

### 命令行测试
```bash
# 测试代理连接
curl --socks5 127.0.0.1:1080 "https://httpbin.org/ip"

# 测试直连
curl "https://httpbin.org/ip"
```

## 🔧 高级功能

- **智能路由**: 自动判断是否使用代理
- **心跳监控**: 实时监控服务器连接状态
- **流量统计**: 记录传输数据量和连接数
- **错误恢复**: 自动重连和错误处理
- **多平台支持**: Windows, Linux, macOS

## 📄 许可证

本项目基于 [MIT许可证](LICENSE) 开源。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📞 支持

如果遇到问题，请：
1. 查看文档目录中的相关文档
2. 运行综合测试工具诊断问题
3. 查看日志文件获取详细信息
4. 提交Issue描述问题 