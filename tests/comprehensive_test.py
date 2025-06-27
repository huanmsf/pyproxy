#!/usr/bin/env python3
"""
PyProxy 综合测试工具
包含所有测试功能的一体化测试脚本
"""

import os
import sys
import time
import subprocess
import requests
import socket
import json
from typing import List, Tuple

class PyProxyTester:
    """PyProxy 综合测试器"""
    
    def __init__(self):
        self.proxy_url = "socks5://127.0.0.1:1080"
        self.proxies = {
            'http': self.proxy_url,
            'https': self.proxy_url
        }
        self.test_results = []
        
    def print_header(self, title: str):
        """打印测试标题"""
        print("\n" + "=" * 60)
        print(f"🧪 {title}")
        print("=" * 60)
        
    def print_step(self, step: str):
        """打印测试步骤"""
        print(f"\n📋 {step}")
        print("-" * 50)
        
    def wait_for_input(self, message: str = "按 Enter 继续下一项测试..."):
        """等待用户输入"""
        input(f"\n⏸️  {message}")
        
    def check_proxy_port(self) -> bool:
        """检查代理端口是否开放"""
        self.print_step("检查代理服务器状态")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('127.0.0.1', 1080))
            sock.close()
            
            if result == 0:
                print("✅ 代理端口 1080 正在监听")
                return True
            else:
                print("❌ 代理端口 1080 未开启")
                return False
        except Exception as e:
            print(f"❌ 检查端口时出错: {e}")
            return False
            
    def test_direct_connection(self) -> bool:
        """测试直接连接"""
        self.print_step("测试直接连接 (不使用代理)")
        
        test_sites = [
            ("http://httpbin.org/ip", "httpbin IP检测"),
            ("https://www.baidu.com", "百度首页"),
        ]
        
        success_count = 0
        for url, name in test_sites:
            try:
                print(f"🌐 测试 {name}: {url}")
                start_time = time.time()
                response = requests.get(url, timeout=10)
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    print(f"✅ {name} - 成功 ({response.status_code}) - {elapsed:.2f}秒")
                    
                    if "ip" in url:
                        try:
                            ip_info = response.json()
                            print(f"   直连IP: {ip_info.get('origin', 'N/A')}")
                        except:
                            pass
                    success_count += 1
                else:
                    print(f"⚠️ {name} - HTTP {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"❌ {name} - 连接超时")
            except Exception as e:
                print(f"❌ {name} - 错误: {e}")
            
            time.sleep(1)
            
        return success_count > 0
        
    def test_proxy_connection(self) -> bool:
        """测试代理连接"""
        self.print_step("测试代理连接")
        
        test_sites = [
            ("https://httpbin.org/ip", "IP检测 (查看代理IP)"),
            ("https://httpbin.org/get", "HTTP GET测试"),
            ("https://httpbin.org/user-agent", "User-Agent测试"),
        ]
        
        success_count = 0
        for url, name in test_sites:
            try:
                print(f"🌐 测试 {name}: {url}")
                start_time = time.time()
                response = requests.get(url, proxies=self.proxies, timeout=15)
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    print(f"✅ {name} - 成功 ({response.status_code}) - {elapsed:.2f}秒")
                    
                    if "ip" in url:
                        try:
                            ip_info = response.json()
                            print(f"   代理IP: {ip_info.get('origin', 'N/A')}")
                        except:
                            pass
                    elif "user-agent" in url:
                        try:
                            ua_info = response.json()
                            print(f"   User-Agent: {ua_info.get('user-agent', 'N/A')[:50]}...")
                        except:
                            pass
                    success_count += 1
                else:
                    print(f"⚠️ {name} - HTTP {response.status_code}")
                    
            except requests.exceptions.ProxyError as e:
                print(f"❌ {name} - 代理错误: {e}")
            except requests.exceptions.Timeout:
                print(f"❌ {name} - 连接超时")
            except Exception as e:
                print(f"❌ {name} - 错误: {e}")
            
            time.sleep(2)
            
        return success_count > 0
        
    def test_routing_rules(self) -> bool:
        """测试路由规则"""
        self.print_step("测试智能路由规则")
        
        # 测试直连网站（应该不通过代理）
        direct_sites = [
            ("https://www.baidu.com", "百度（应该直连）"),
        ]
        
        # 测试代理网站（应该通过代理）
        proxy_sites = [
            ("https://httpbin.org/ip", "httpbin（应该走代理）"),
        ]
        
        print("🔗 测试直连网站:")
        for url, name in direct_sites:
            try:
                print(f"   测试 {name}")
                response = requests.get(url, proxies=self.proxies, timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ {name} - 连接成功")
                else:
                    print(f"   ⚠️ {name} - HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {name} - 错误: {e}")
        
        print("\n🌐 测试代理网站:")
        for url, name in proxy_sites:
            try:
                print(f"   测试 {name}")
                response = requests.get(url, proxies=self.proxies, timeout=15)
                if response.status_code == 200:
                    print(f"   ✅ {name} - 连接成功")
                    if "ip" in url:
                        try:
                            ip_info = response.json()
                            print(f"   📍 显示IP: {ip_info.get('origin', 'N/A')}")
                        except:
                            pass
                else:
                    print(f"   ⚠️ {name} - HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {name} - 错误: {e}")
                
        return True
        
    def test_performance(self) -> bool:
        """测试性能"""
        self.print_step("测试性能表现")
        
        test_urls = [
            "https://httpbin.org/ip",
            "https://httpbin.org/get", 
            "https://httpbin.org/headers",
        ]
        
        total_time = 0
        success_count = 0
        
        print("🚀 连续请求测试:")
        for i, url in enumerate(test_urls * 2, 1):  # 每个URL测试2次
            try:
                start_time = time.time()
                response = requests.get(url, proxies=self.proxies, timeout=10)
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    print(f"   请求 #{i}: ✅ {elapsed:.2f}秒")
                    total_time += elapsed
                    success_count += 1
                else:
                    print(f"   请求 #{i}: ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   请求 #{i}: ❌ 错误: {e}")
                
        if success_count > 0:
            avg_time = total_time / success_count
            print(f"\n📊 性能统计:")
            print(f"   成功请求: {success_count}")
            print(f"   平均延迟: {avg_time:.2f}秒")
            print(f"   总耗时: {total_time:.2f}秒")
            
        return success_count > 0
        
    def test_stress(self) -> bool:
        """压力测试"""
        self.print_step("并发连接压力测试")
        
        print("⚠️  这将进行10个并发连接测试，请确保代理服务器能正常处理")
        self.wait_for_input("确认开始压力测试？")
        
        import threading
        import queue
        
        results = queue.Queue()
        
        def worker(thread_id):
            try:
                start_time = time.time()
                response = requests.get("https://httpbin.org/ip", 
                                      proxies=self.proxies, timeout=15)
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    results.put((thread_id, True, elapsed, None))
                else:
                    results.put((thread_id, False, elapsed, f"HTTP {response.status_code}"))
                    
            except Exception as e:
                elapsed = time.time() - start_time
                results.put((thread_id, False, elapsed, str(e)))
        
        print("🔥 启动10个并发连接...")
        threads = []
        start_time = time.time()
        
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i+1,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        total_time = time.time() - start_time
        
        # 统计结果
        success_count = 0
        failed_count = 0
        total_elapsed = 0
        
        print(f"\n📊 并发测试结果:")
        while not results.empty():
            thread_id, success, elapsed, error = results.get()
            if success:
                print(f"   线程 #{thread_id}: ✅ {elapsed:.2f}秒")
                success_count += 1
                total_elapsed += elapsed
            else:
                print(f"   线程 #{thread_id}: ❌ {error}")
                failed_count += 1
                
        print(f"\n📈 压力测试统计:")
        print(f"   成功连接: {success_count}")
        print(f"   失败连接: {failed_count}")
        print(f"   成功率: {success_count/(success_count+failed_count)*100:.1f}%")
        print(f"   平均延迟: {total_elapsed/success_count:.2f}秒" if success_count > 0 else "   平均延迟: N/A")
        print(f"   总耗时: {total_time:.2f}秒")
        
        return success_count > 5  # 至少50%成功率
        
    def diagnose_issues(self):
        """诊断常见问题"""
        self.print_step("诊断常见问题")
        
        print("🔍 检查常见问题:")
        
        # 检查端口
        if not self.check_proxy_port():
            print("\n💡 解决建议:")
            print("   1. 确保PyProxy代理客户端正在运行")
            print("   2. 检查配置文件中的端口设置")
            print("   3. 确认没有其他程序占用1080端口")
            return
            
        # 检查网络连接
        print("\n🌐 检查网络连接:")
        try:
            response = requests.get("https://httpbin.org/ip", timeout=5)
            print("   ✅ 直接网络连接正常")
        except:
            print("   ❌ 直接网络连接失败")
            print("\n💡 解决建议:")
            print("   1. 检查网络连接")
            print("   2. 检查防火墙设置")
            print("   3. 检查DNS设置")
            
        # 检查代理连接
        print("\n🔗 检查代理连接:")
        try:
            response = requests.get("https://httpbin.org/ip", 
                                  proxies=self.proxies, timeout=10)
            if response.status_code == 200:
                ip_info = response.json()
                print(f"   ✅ 代理连接正常，IP: {ip_info.get('origin')}")
            else:
                print(f"   ⚠️ 代理连接异常，HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ 代理连接失败: {e}")
            print("\n💡 解决建议:")
            print("   1. 检查Trojan服务器配置")
            print("   2. 确认服务器地址和端口正确")
            print("   3. 检查密码是否正确")
            print("   4. 检查SSL设置")
        
    def run_all_tests(self):
        """运行所有测试"""
        self.print_header("PyProxy 综合测试工具")
        
        print("🎯 这个工具将帮助您全面测试PyProxy代理客户端")
        print("📋 测试项目包括:")
        print("   1. 代理服务器状态检查")
        print("   2. 直接连接测试")
        print("   3. 代理连接测试") 
        print("   4. 智能路由测试")
        print("   5. 性能测试")
        print("   6. 压力测试")
        print("   7. 问题诊断")
        
        self.wait_for_input("开始测试？")
        
        # 测试1: 检查代理状态
        if not self.check_proxy_port():
            print("\n❌ 代理服务器未运行，无法继续测试")
            print("\n💡 请先启动PyProxy代理客户端:")
            print("   python scripts/start.py")
            return
            
        self.wait_for_input()
        
        # 测试2: 直接连接
        self.test_direct_connection()
        self.wait_for_input()
        
        # 测试3: 代理连接
        self.test_proxy_connection() 
        self.wait_for_input()
        
        # 测试4: 路由规则
        self.test_routing_rules()
        self.wait_for_input()
        
        # 测试5: 性能测试
        self.test_performance()
        self.wait_for_input()
        
        # 测试6: 压力测试
        print("\n⚠️  是否进行压力测试？(可能需要较长时间)")
        choice = input("输入 'y' 进行压力测试，其他键跳过: ").lower()
        if choice == 'y':
            self.test_stress()
            
        # 测试7: 问题诊断
        print("\n🔍 是否进行问题诊断？")
        choice = input("输入 'y' 进行诊断，其他键跳过: ").lower()
        if choice == 'y':
            self.diagnose_issues()
        
        # 测试总结
        self.print_header("测试完成")
        print("🎉 所有测试已完成！")
        print("\n📋 测试建议:")
        print("   • 如果所有基础测试都通过，说明代理工作正常")
        print("   • 如果某些网站访问失败，可能是网络环境限制")
        print("   • 如果性能较差，可以调整配置文件中的超时设置")
        print("   • 如果压力测试失败，说明并发处理能力需要优化")
        print("\n📄 更多信息请查看docs文件夹中的文档")

def main():
    """主函数"""
    try:
        tester = PyProxyTester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n🛑 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    main() 