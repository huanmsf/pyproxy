#!/usr/bin/env python3
"""
PyProxy 项目设置脚本
用于初始化项目和配置文件
"""

import os
import sys
import shutil

def create_directories():
    """创建必要的目录"""
    directories = ['logs', 'temp']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 创建目录: {directory}")
        else:
            print(f"📁 目录已存在: {directory}")

def setup_config():
    """设置配置文件"""
    print("\n📋 配置文件设置")
    print("=" * 50)
    
    # 检查是否存在配置文件
    config_file = "configs/config.yaml"
    if os.path.exists(config_file):
        print(f"✅ 配置文件已存在: {config_file}")
        return
    
    print("🔧 请配置Trojan服务器信息:")
    
    # 获取用户输入
    server = input("服务器地址 (例: www.example.com): ").strip()
    if not server:
        server = "www.seohelp.cn"
        
    port = input("服务器端口 (默认 8888): ").strip()
    if not port:
        port = "8888"
    else:
        try:
            port = int(port)
        except ValueError:
            port = 8888
            
    password = input("Trojan密码: ").strip()
    if not password:
        password = "your_password"
        print("⚠️  使用默认密码，请记得修改！")
    
    sni = input(f"SNI (默认与服务器地址相同): ").strip()
    if not sni:
        sni = server
    
    # 生成配置内容
    config_content = f"""# PyProxy 配置文件
# 由设置脚本自动生成

# Trojan服务器配置
trojan:
  server: "{server}"
  port: {port}
  password: "{password}"
  verify_ssl: false
  sni: "{sni}"

# 本地代理配置
local:
  listen: "127.0.0.1"
  port: 1080

# 日志配置
log:
  level: "INFO"
  file: ""
  verbose_traffic: false
  show_http_details: false

# 路由配置
routing:
  direct_domains:
    - "*.baidu.com"
    - "*.qq.com"
    - "*.weixin.qq.com"
    - "*.taobao.com"
    - "*.tmall.com"
    - "localhost"
    - "127.0.0.1"
    - "*.local"
  proxy_domains:
    - "*"
"""
    
    # 写入配置文件
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ 配置文件已创建: {config_file}")

def check_dependencies():
    """检查依赖"""
    print("\n🔍 检查Python依赖")
    print("=" * 50)
    
    required_packages = [
        'pyyaml',
        'requests',
        'colorama'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (未安装)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 请安装缺失的依赖:")
        print(f"   pip install {' '.join(missing_packages)}")
        
        install = input("\n是否立即安装？(y/n): ").lower()
        if install == 'y':
            import subprocess
            for package in missing_packages:
                print(f"📦 安装 {package}...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', package])
    else:
        print("\n🎉 所有依赖都已安装！")

def create_batch_files():
    """创建Windows批处理文件"""
    if sys.platform != 'win32':
        return
        
    print("\n📝 创建Windows批处理文件")
    print("=" * 50)
    
    # 启动脚本
    start_bat = """@echo off
echo 启动PyProxy代理客户端...
python scripts/start.py -c configs/standard.yaml
pause
"""
    
    with open('start.bat', 'w', encoding='gbk') as f:
        f.write(start_bat)
    print("✅ 创建文件: start.bat")
    
    # 测试脚本
    test_bat = """@echo off
echo 运行PyProxy综合测试...
python tests/comprehensive_test.py
pause
"""
    
    with open('test.bat', 'w', encoding='gbk') as f:
        f.write(test_bat)
    print("✅ 创建文件: test.bat")

def main():
    """主函数"""
    print("🎯 PyProxy 项目设置向导")
    print("=" * 60)
    print("这个脚本将帮助您设置PyProxy项目")
    print()
    
    # 1. 创建目录
    print("1️⃣ 创建项目目录")
    create_directories()
    
    # 2. 检查依赖
    check_dependencies()
    
    # 3. 设置配置
    print("\n2️⃣ 设置配置文件")
    setup_config()
    
    # 4. 创建批处理文件
    print("\n3️⃣ 创建便捷脚本")
    create_batch_files()
    
    # 完成设置
    print("\n" + "=" * 60)
    print("🎉 项目设置完成！")
    print("\n📋 使用方法:")
    print("   • 启动代理: python scripts/start.py")
    print("   • 运行测试: python tests/comprehensive_test.py")
    if sys.platform == 'win32':
        print("   • Windows用户也可以双击 start.bat 或 test.bat")
    print("\n📄 更多信息请查看 docs 文件夹中的文档")

if __name__ == "__main__":
    main() 