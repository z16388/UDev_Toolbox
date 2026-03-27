#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具 - 核心功能模块
"""

import json
import socket
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
import ssl


@dataclass
class HTTPResponse:
    """HTTP响应数据类"""
    status_code: int
    headers: Dict[str, str]
    body: str
    elapsed_ms: float
    error: str = None


class NetworkUtils:
    """网络工具类"""
    
    # 公共IP查询API
    IP_APIS = [
        'https://api.ipify.org?format=json',
        'https://ipinfo.io/json',
        'https://ip-api.com/json',
    ]
    
    @staticmethod
    def get_local_ip() -> str:
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '127.0.0.1'
    
    @staticmethod
    def get_public_ip() -> Dict:
        """获取公网IP地址和相关信息"""
        for api_url in NetworkUtils.IP_APIS:
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                req = urllib.request.Request(api_url, headers={'User-Agent': 'UDevToolbox/1.0'})
                with urllib.request.urlopen(req, timeout=5, context=context) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    return data
            except Exception:
                continue
        
        return {'error': '无法获取公网IP'}
    
    @staticmethod
    def lookup_ip(ip: str) -> Dict:
        """查询IP地址信息"""
        try:
            url = f'http://ip-api.com/json/{ip}?lang=zh-CN'
            req = urllib.request.Request(url, headers={'User-Agent': 'UDevToolbox/1.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def dns_lookup(hostname: str) -> Dict:
        """DNS查询"""
        result = {
            'hostname': hostname,
            'addresses': [],
            'aliases': [],
            'error': None
        }
        
        try:
            # 获取IP地址
            result['addresses'] = socket.gethostbyname_ex(hostname)[2]
            result['aliases'] = socket.gethostbyname_ex(hostname)[1]
        except socket.gaierror as e:
            result['error'] = str(e)
        
        return result
    
    @staticmethod
    def reverse_dns(ip: str) -> Dict:
        """反向DNS查询"""
        result = {
            'ip': ip,
            'hostname': None,
            'error': None
        }
        
        try:
            result['hostname'] = socket.gethostbyaddr(ip)[0]
        except socket.herror as e:
            result['error'] = str(e)
        
        return result
    
    @staticmethod
    def http_request(
        url: str,
        method: str = 'GET',
        headers: Dict[str, str] = None,
        body: str = None,
        timeout: int = 30
    ) -> HTTPResponse:
        """
        发送HTTP请求
        
        Args:
            url: 请求URL
            method: 请求方法
            headers: 请求头
            body: 请求体
            timeout: 超时时间
        
        Returns:
            HTTPResponse对象
        """
        import time
        start_time = time.time()
        
        if headers is None:
            headers = {}
        
        headers.setdefault('User-Agent', 'UDevToolbox/1.0')
        
        try:
            # 准备请求数据
            data = body.encode('utf-8') if body else None
            
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            
            # 处理HTTPS
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
                elapsed = (time.time() - start_time) * 1000
                
                response_headers = dict(response.headers)
                response_body = response.read().decode('utf-8', errors='ignore')
                
                return HTTPResponse(
                    status_code=response.status,
                    headers=response_headers,
                    body=response_body,
                    elapsed_ms=elapsed
                )
        
        except urllib.error.HTTPError as e:
            elapsed = (time.time() - start_time) * 1000
            return HTTPResponse(
                status_code=e.code,
                headers=dict(e.headers) if e.headers else {},
                body=e.read().decode('utf-8', errors='ignore') if e.fp else '',
                elapsed_ms=elapsed,
                error=str(e)
            )
        
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return HTTPResponse(
                status_code=0,
                headers={},
                body='',
                elapsed_ms=elapsed,
                error=str(e)
            )
    
    @staticmethod
    def test_json_api(
        url: str,
        method: str = 'GET',
        headers: Dict[str, str] = None,
        json_body: Dict = None
    ) -> Dict:
        """
        测试JSON API
        
        Returns:
            包含响应信息的字典
        """
        if headers is None:
            headers = {}
        
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('Accept', 'application/json')
        
        body = json.dumps(json_body) if json_body else None
        
        response = NetworkUtils.http_request(url, method, headers, body)
        
        result = {
            'status_code': response.status_code,
            'elapsed_ms': response.elapsed_ms,
            'headers': response.headers,
            'error': response.error,
            'body_raw': response.body,
            'body_json': None,
            'is_valid_json': False
        }
        
        # 尝试解析JSON
        try:
            result['body_json'] = json.loads(response.body)
            result['is_valid_json'] = True
        except json.JSONDecodeError:
            pass
        
        return result
    
    @staticmethod
    def check_port(host: str, port: int, timeout: int = 3) -> bool:
        """检查端口是否开放"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    @staticmethod
    def scan_ports(host: str, ports: List[int], timeout: int = 1) -> List[int]:
        """扫描开放的端口"""
        open_ports = []
        for port in ports:
            if NetworkUtils.check_port(host, port, timeout):
                open_ports.append(port)
        return open_ports
    
    @staticmethod
    def ping(host: str, count: int = 4) -> Dict:
        """Ping主机"""
        import subprocess
        import platform
        
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        
        try:
            result = subprocess.run(
                ['ping', param, str(count), host],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
