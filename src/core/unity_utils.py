#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unity工具 - 核心功能模块
"""

import os
import re
import json
import struct
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import sqlite3


class UnityUtils:
    """Unity工具类"""
    
    # PlayerPrefs路径 (Windows)
    PLAYERPREFS_PATH_WINDOWS = os.path.join(
        os.environ.get('USERPROFILE', ''),
        'AppData', 'LocalLow'
    )
    
    @staticmethod
    def find_playerprefs_files(company_name: str = None, product_name: str = None) -> List[str]:
        """
        查找PlayerPrefs文件
        
        Args:
            company_name: 公司名称
            product_name: 产品名称
        
        Returns:
            PlayerPrefs文件路径列表
        """
        prefs_files = []
        base_path = UnityUtils.PLAYERPREFS_PATH_WINDOWS
        
        if not os.path.exists(base_path):
            return prefs_files
        
        # 遍历LocalLow目录
        for company in os.listdir(base_path):
            company_path = os.path.join(base_path, company)
            if not os.path.isdir(company_path):
                continue
            
            if company_name and company.lower() != company_name.lower():
                continue
            
            for product in os.listdir(company_path):
                product_path = os.path.join(company_path, product)
                if not os.path.isdir(product_path):
                    continue
                
                if product_name and product.lower() != product_name.lower():
                    continue
                
                # 查找prefs文件
                for filename in os.listdir(product_path):
                    if filename.endswith('.pref') or filename == 'PlayerPrefs.txt':
                        prefs_files.append(os.path.join(product_path, filename))
        
        return prefs_files
    
    @staticmethod
    def read_playerprefs(prefs_path: str) -> Dict:
        """读取PlayerPrefs文件"""
        prefs = {}
        
        try:
            with open(prefs_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 尝试解析为JSON
            try:
                prefs = json.loads(content)
            except json.JSONDecodeError:
                # 尝试其他格式解析
                for line in content.split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        prefs[key.strip()] = value.strip()
        except Exception as e:
            print(f"读取PlayerPrefs失败: {e}")
        
        return prefs
    
    @staticmethod
    def find_guid_in_project(project_path: str, guid: str) -> List[str]:
        """
        在Unity项目中查找GUID对应的资源
        
        Args:
            project_path: 项目路径
            guid: 要查找的GUID
        
        Returns:
            匹配的文件路径列表
        """
        matches = []
        guid_lower = guid.lower()
        
        # 搜索.meta文件
        assets_path = os.path.join(project_path, 'Assets')
        if not os.path.exists(assets_path):
            return matches
        
        for root, dirs, files in os.walk(assets_path):
            for filename in files:
                if filename.endswith('.meta'):
                    meta_path = os.path.join(root, filename)
                    try:
                        with open(meta_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if f'guid: {guid_lower}' in content.lower():
                            # 返回对应的资源文件路径
                            asset_path = meta_path[:-5]  # 去掉.meta
                            if os.path.exists(asset_path):
                                matches.append(asset_path)
                            else:
                                matches.append(meta_path)
                    except Exception:
                        pass
        
        return matches
    
    @staticmethod
    def find_guid_references(project_path: str, guid: str) -> List[Dict]:
        """
        查找GUID的引用
        
        Returns:
            包含引用信息的字典列表
        """
        references = []
        guid_lower = guid.lower()
        
        assets_path = os.path.join(project_path, 'Assets')
        if not os.path.exists(assets_path):
            return references
        
        # 搜索所有可能包含引用的文件
        search_extensions = ['.unity', '.prefab', '.asset', '.mat', '.controller', '.anim']
        
        for root, dirs, files in os.walk(assets_path):
            for filename in files:
                if any(filename.endswith(ext) for ext in search_extensions):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                if guid_lower in line.lower():
                                    references.append({
                                        'file': file_path,
                                        'line': line_num,
                                        'content': line.strip()
                                    })
                    except Exception:
                        pass
        
        return references
    
    @staticmethod
    def parse_assetbundle_header(ab_path: str) -> Dict:
        """
        解析AssetBundle头信息
        
        Returns:
            AssetBundle信息字典
        """
        info = {
            'path': ab_path,
            'size': os.path.getsize(ab_path),
            'signature': '',
            'version': 0,
            'unity_version': '',
            'compressed': False,
        }
        
        try:
            with open(ab_path, 'rb') as f:
                # 读取签名
                signature = b''
                while True:
                    byte = f.read(1)
                    if byte == b'\x00' or not byte:
                        break
                    signature += byte
                
                info['signature'] = signature.decode('utf-8', errors='ignore')
                
                # 判断是否压缩
                if info['signature'] in ['UnityFS', 'UnityWeb', 'UnityRaw']:
                    # 读取版本号
                    info['version'] = struct.unpack('>I', f.read(4))[0]
                    
                    # 读取Unity版本
                    unity_ver = b''
                    while True:
                        byte = f.read(1)
                        if byte == b'\x00' or not byte:
                            break
                        unity_ver += byte
                    info['unity_version'] = unity_ver.decode('utf-8', errors='ignore')
                    
                    info['compressed'] = info['signature'] != 'UnityRaw'
        
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    @staticmethod
    def analyze_project_assets(project_path: str) -> List[Dict]:
        """
        分析项目资源体积
        
        Returns:
            资源信息列表，按大小排序
        """
        assets = []
        assets_path = os.path.join(project_path, 'Assets')
        
        if not os.path.exists(assets_path):
            return assets
        
        for root, dirs, files in os.walk(assets_path):
            for filename in files:
                if filename.endswith('.meta'):
                    continue
                
                file_path = os.path.join(root, filename)
                try:
                    size = os.path.getsize(file_path)
                    ext = os.path.splitext(filename)[1].lower()
                    
                    assets.append({
                        'path': file_path,
                        'relative_path': os.path.relpath(file_path, project_path),
                        'name': filename,
                        'size': size,
                        'extension': ext,
                        'type': UnityUtils._get_asset_type(ext),
                    })
                except Exception:
                    pass
        
        # 按大小排序
        assets.sort(key=lambda x: x['size'], reverse=True)
        return assets
    
    @staticmethod
    def _get_asset_type(extension: str) -> str:
        """根据扩展名判断资源类型"""
        type_map = {
            '.png': '纹理',
            '.jpg': '纹理',
            '.jpeg': '纹理',
            '.tga': '纹理',
            '.psd': '纹理',
            '.fbx': '模型',
            '.obj': '模型',
            '.blend': '模型',
            '.wav': '音频',
            '.mp3': '音频',
            '.ogg': '音频',
            '.anim': '动画',
            '.controller': '动画控制器',
            '.cs': '脚本',
            '.shader': '着色器',
            '.mat': '材质',
            '.prefab': '预制体',
            '.unity': '场景',
            '.asset': '资产',
        }
        return type_map.get(extension, '其他')
    
    @staticmethod
    def parse_unity_log(log_content: str) -> List[Dict]:
        """
        解析Unity日志
        
        Returns:
            解析后的日志条目列表
        """
        entries = []
        
        # 匹配日志条目的正则
        log_pattern = re.compile(
            r'(?P<type>[\w]+):?\s*(?P<message>.*?)(?=\n(?:[\w]+:|\Z))',
            re.DOTALL
        )
        
        # 简单的行级解析
        current_entry = None
        for line in log_content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # 检测日志类型
            log_type = 'Info'
            if line.startswith('Error') or 'Exception' in line:
                log_type = 'Error'
            elif line.startswith('Warning'):
                log_type = 'Warning'
            elif line.startswith('Log'):
                log_type = 'Log'
            
            entries.append({
                'type': log_type,
                'message': line,
                'timestamp': None,
            })
        
        return entries
    
    @staticmethod
    def run_adb_logcat(
        package_name: str = None,
        tag_filter: str = None,
        level: str = 'V'
    ) -> subprocess.Popen:
        """
        启动adb logcat
        
        Args:
            package_name: 包名过滤
            tag_filter: 标签过滤
            level: 日志级别 (V, D, I, W, E)
        
        Returns:
            Popen对象
        """
        cmd = ['adb', 'logcat', '-v', 'time']
        
        if tag_filter:
            cmd.extend(['-s', f'{tag_filter}:{level}'])
        else:
            cmd.append(f'*:{level}')
        
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
