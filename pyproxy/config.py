import yaml
import os
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class TrojanConfig:
    """Trojan服务器配置"""
    server: str
    port: int
    password: str
    verify_ssl: bool = True
    sni: str = ""


@dataclass 
class LocalConfig:
    """本地代理配置"""
    listen: str = "127.0.0.1"
    port: int = 1080


@dataclass
class LogConfig:
    """日志配置"""
    level: str = "INFO"
    file: str = ""
    verbose_traffic: bool = False
    show_http_details: bool = False


@dataclass
class RoutingConfig:
    """路由配置"""
    direct_domains: List[str] = None
    proxy_domains: List[str] = None
    
    def __post_init__(self):
        if self.direct_domains is None:
            self.direct_domains = []
        if self.proxy_domains is None:
            self.proxy_domains = ["*"]


class Config:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.trojan: TrojanConfig = None
        self.local: LocalConfig = None
        self.log: LogConfig = None
        self.routing: RoutingConfig = None
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """从文件加载配置"""
        config = cls(config_path)
        config.load()
        return config
        
    def load(self) -> None:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
            
        self._parse_config(config_data)
        self._validate_config()
        
    def _parse_config(self, data: Dict[str, Any]) -> None:
        """解析配置数据"""
        # Trojan配置
        trojan_data = data.get('trojan', {})
        self.trojan = TrojanConfig(
            server=trojan_data.get('server', ''),
            port=trojan_data.get('port', 443),
            password=trojan_data.get('password', ''),
            verify_ssl=trojan_data.get('verify_ssl', True),
            sni=trojan_data.get('sni', trojan_data.get('server', ''))
        )
        
        # 本地配置
        local_data = data.get('local', {})
        self.local = LocalConfig(
            listen=local_data.get('listen', '127.0.0.1'),
            port=local_data.get('port', 1080)
        )
        
        # 日志配置
        log_data = data.get('log', {})
        self.log = LogConfig(
            level=log_data.get('level', 'INFO'),
            file=log_data.get('file', ''),
            verbose_traffic=log_data.get('verbose_traffic', False),
            show_http_details=log_data.get('show_http_details', False)
        )
        
        # 路由配置
        routing_data = data.get('routing', {})
        self.routing = RoutingConfig(
            direct_domains=routing_data.get('direct_domains', []),
            proxy_domains=routing_data.get('proxy_domains', ['*'])
        )
        
        # 绕过配置
        self.bypass = data.get('bypass', {})
        
    def _validate_config(self) -> None:
        """验证配置"""
        if not self.trojan.server:
            raise ValueError("Trojan服务器地址不能为空")
            
        if not self.trojan.password:
            raise ValueError("Trojan密码不能为空")
            
        if not (1 <= self.trojan.port <= 65535):
            raise ValueError("Trojan服务器端口必须在1-65535范围内")
            
        if not (1 <= self.local.port <= 65535):
            raise ValueError("本地监听端口必须在1-65535范围内")
            
        if self.log.level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            raise ValueError("日志级别必须是DEBUG、INFO、WARNING或ERROR之一") 