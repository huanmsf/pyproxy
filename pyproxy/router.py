import fnmatch
from typing import List
from .config import RoutingConfig
from .logger import Logger


class Router:
    """路由管理器"""
    
    def __init__(self, config: RoutingConfig, logger: Logger):
        self.config = config
        self.logger = logger
        
    def should_proxy(self, host: str) -> bool:
        """判断主机是否应该使用代理"""
        # 首先检查直连列表
        if self._match_patterns(host, self.config.direct_domains):
            self.logger.debug(f"域名 {host} 匹配直连规则")
            return False
            
        # 然后检查代理列表
        if self._match_patterns(host, self.config.proxy_domains):
            self.logger.debug(f"域名 {host} 匹配代理规则")
            return True
            
        # 默认不使用代理
        self.logger.debug(f"域名 {host} 未匹配任何规则，使用直连")
        return False
        
    def _match_patterns(self, host: str, patterns: List[str]) -> bool:
        """检查主机是否匹配模式列表"""
        for pattern in patterns:
            if self._match_pattern(host, pattern):
                return True
        return False
        
    def _match_pattern(self, host: str, pattern: str) -> bool:
        """检查主机是否匹配单个模式"""
        # 精确匹配
        if host == pattern:
            return True
            
        # 通配符匹配
        if fnmatch.fnmatch(host, pattern):
            return True
            
        # 域名后缀匹配（*.example.com 匹配 sub.example.com）
        if pattern.startswith('*.'):
            domain_suffix = pattern[2:]
            if host.endswith('.' + domain_suffix) or host == domain_suffix:
                return True
                
        return False 