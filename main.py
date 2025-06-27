#!/usr/bin/env python3
"""
PyProxy - Trojan代理客户端
主程序入口
"""

import asyncio
import sys
import os
import click
from pyproxy.client import PyProxyClient


@click.command()
@click.option('--config', '-c', default='configs/config.yaml', help='配置文件路径')
@click.option('--version', '-v', is_flag=True, help='显示版本信息')
def main(config, version):
    """PyProxy - 轻量级Trojan代理客户端"""
    
    if version:
        from pyproxy import __version__
        click.echo(f"PyProxy v{__version__}")
        return
    
    # 检查配置文件
    if not os.path.exists(config):
        click.echo(f"❌ 错误: 配置文件不存在: {config}", err=True)
        click.echo("💡 请创建配置文件或使用 --config 指定配置文件路径")
        click.echo("📝 运行设置脚本: python scripts/setup.py")
        sys.exit(1)
    
    # 显示启动banner
    print("=" * 70)
    print("🚀 PyProxy - Trojan代理客户端启动中...")
    print("=" * 70)
    
    # 创建客户端
    client = PyProxyClient(config)
    
    try:
        # 运行客户端
        if sys.platform == 'win32':
            # Windows下使用ProactorEventLoop
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        asyncio.run(client.start())
        
    except KeyboardInterrupt:
        print("\n")
        print("=" * 70)
        print("👋 程序被用户中断")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        print("📋 详细错误信息:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main() 