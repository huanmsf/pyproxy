#!/usr/bin/env python3
"""
PyProxy 启动脚本
用于启动代理客户端的标准脚本（集成修复版功能）
"""

import sys
import os
import argparse
import asyncio
import signal

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from pyproxy import PyProxyClient
from pyproxy.config import Config

# Windows编码设置
if sys.platform == "win32":
    try:
        # 设置控制台编码为UTF-8
        os.system("chcp 65001 > nul 2>&1")
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

def setup_signal_handlers(client):
    """设置信号处理器"""
    def signal_handler(signum, frame):
        print(f"\n收到停止信号 {signum}")
        asyncio.create_task(client.stop())
    
    if hasattr(signal, 'SIGINT'):
        signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

async def run_client(client):
    """运行客户端的异步函数（包含错误处理）"""
    try:
        await client.start()
    except KeyboardInterrupt:
        print("\n🛑 收到键盘中断信号")
    except asyncio.CancelledError:
        print("\n🔄 客户端被取消")
    except Exception as e:
        print(f"❌ 客户端运行错误: {e}")
    finally:
        # 确保正确清理
        try:
            await client.stop()
        except Exception as e:
            print(f"⚠️ 停止客户端时出现问题: {e}")

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='PyProxy 代理客户端')
    parser.add_argument('-c', '--config', 
                       default='configs/config.yaml',
                       help='配置文件路径 (默认: configs/config.yaml)')
    parser.add_argument('-v', '--verbose', 
                       action='store_true',
                       help='详细日志输出')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🚀 PyProxy - Trojan代理客户端启动中...")
    print("=" * 70)
    
    try:
        # 检查配置文件是否存在
        print(f"📄 检查配置文件: {args.config}")
        if not os.path.exists(args.config):
            print(f"❌ 配置文件不存在: {args.config}")
            print("💡 请运行设置脚本创建配置文件:")
            print("   python scripts/setup.py")
            return
        
        # 如果启用详细模式，需要修改配置文件或传递参数
        if args.verbose:
            print("🔍 启用详细日志模式")
        
        # 创建客户端（传递配置文件路径）
        print("🔧 初始化代理客户端...")
        client = PyProxyClient(args.config)
        
        # 设置信号处理
        setup_signal_handlers(client)
        
        # 启动客户端
        await run_client(client)
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断，正在关闭...")
    except FileNotFoundError:
        print(f"❌ 配置文件不存在: {args.config}")
        print("💡 请检查文件路径或使用以下命令创建配置文件:")
        print("   python scripts/setup.py")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
    finally:
        print("👋 程序已退出")

if __name__ == "__main__":
    try:
        # Windows平台特殊处理
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断程序")
    except Exception as e:
        print(f"❌ 程序运行错误: {e}")
        sys.exit(1) 