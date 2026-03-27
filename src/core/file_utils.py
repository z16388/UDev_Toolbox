#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件工具 - 核心功能模块
"""

import os
import re
import hashlib
import difflib
import shutil
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def calculate_hash(file_path: str, algorithm: str = 'md5') -> str:
        """
        计算文件哈希值
        
        Args:
            file_path: 文件路径
            algorithm: 哈希算法 (md5, sha1, sha256, sha512)
        
        Returns:
            哈希值字符串
        """
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def calculate_all_hashes(file_path: str) -> Dict[str, str]:
        """计算文件的所有常用哈希值"""
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()
        sha512 = hashlib.sha512()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
                sha1.update(chunk)
                sha256.update(chunk)
                sha512.update(chunk)
        
        return {
            'md5': md5.hexdigest(),
            'sha1': sha1.hexdigest(),
            'sha256': sha256.hexdigest(),
            'sha512': sha512.hexdigest(),
        }
    
    @staticmethod
    def compare_files(file1: str, file2: str) -> bool:
        """比较两个文件是否相同"""
        return FileUtils.calculate_hash(file1) == FileUtils.calculate_hash(file2)
    
    @staticmethod
    def compare_multiple_files(file_paths: List[str]) -> Dict[str, str]:
        """
        比较多个文件的哈希值
        
        Returns:
            文件路径到哈希值的映射
        """
        return {path: FileUtils.calculate_hash(path) for path in file_paths}
    
    @staticmethod
    def text_diff(text1: str, text2: str, context_lines: int = 3) -> str:
        """
        比较两段文本的差异
        
        Args:
            text1: 原始文本
            text2: 新文本
            context_lines: 上下文行数
        
        Returns:
            统一差异格式的字符串
        """
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            lines1, lines2,
            fromfile='原始文件',
            tofile='新文件',
            n=context_lines
        )
        
        return ''.join(diff)
    
    @staticmethod
    def text_diff_html(text1: str, text2: str) -> str:
        """生成HTML格式的差异对比"""
        differ = difflib.HtmlDiff()
        return differ.make_file(
            text1.splitlines(),
            text2.splitlines(),
            fromdesc='原始文件',
            todesc='新文件'
        )
    
    @staticmethod
    def file_diff(file1: str, file2: str) -> str:
        """比较两个文件的差异"""
        with open(file1, 'r', encoding='utf-8', errors='ignore') as f:
            text1 = f.read()
        with open(file2, 'r', encoding='utf-8', errors='ignore') as f:
            text2 = f.read()
        
        return FileUtils.text_diff(text1, text2)
    
    @staticmethod
    def batch_rename(
        directory: str,
        pattern: str,
        replacement: str,
        use_regex: bool = False,
        preview: bool = True
    ) -> List[Tuple[str, str]]:
        """
        批量重命名文件
        
        Args:
            directory: 目录路径
            pattern: 匹配模式
            replacement: 替换字符串
            use_regex: 是否使用正则表达式
            preview: 是否只预览不执行
        
        Returns:
            (原文件名, 新文件名) 的列表
        """
        changes = []
        
        for filename in os.listdir(directory):
            if use_regex:
                new_name = re.sub(pattern, replacement, filename)
            else:
                new_name = filename.replace(pattern, replacement)
            
            if new_name != filename:
                changes.append((filename, new_name))
                
                if not preview:
                    old_path = os.path.join(directory, filename)
                    new_path = os.path.join(directory, new_name)
                    os.rename(old_path, new_path)
        
        return changes
    
    @staticmethod
    def search_files(
        directory: str,
        pattern: str,
        use_regex: bool = False,
        recursive: bool = True,
        include_dirs: bool = False
    ) -> List[str]:
        """
        搜索文件
        
        Args:
            directory: 搜索目录
            pattern: 匹配模式
            use_regex: 是否使用正则表达式
            recursive: 是否递归搜索
            include_dirs: 是否包含目录
        
        Returns:
            匹配的文件路径列表
        """
        matches = []
        
        if use_regex:
            regex = re.compile(pattern, re.IGNORECASE)
            match_func = lambda name: regex.search(name)
        else:
            pattern_lower = pattern.lower()
            match_func = lambda name: pattern_lower in name.lower()
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                for name in files:
                    if match_func(name):
                        matches.append(os.path.join(root, name))
                if include_dirs:
                    for name in dirs:
                        if match_func(name):
                            matches.append(os.path.join(root, name))
        else:
            for name in os.listdir(directory):
                path = os.path.join(directory, name)
                if os.path.isfile(path) or (include_dirs and os.path.isdir(path)):
                    if match_func(name):
                        matches.append(path)
        
        return matches
    
    @staticmethod
    def search_in_files(
        directory: str,
        content_pattern: str,
        file_pattern: str = "*",
        use_regex: bool = False,
        recursive: bool = True
    ) -> List[Dict]:
        """
        在文件内容中搜索
        
        Returns:
            包含匹配信息的字典列表
        """
        results = []
        
        if use_regex:
            regex = re.compile(content_pattern)
        
        for root, dirs, files in os.walk(directory) if recursive else [(directory, [], os.listdir(directory))]:
            for filename in files:
                # 检查文件名模式
                if file_pattern != "*" and not Path(filename).match(file_pattern):
                    continue
                
                file_path = os.path.join(root, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if use_regex:
                                matches = list(regex.finditer(line))
                                if matches:
                                    results.append({
                                        'file': file_path,
                                        'line_num': line_num,
                                        'line': line.strip(),
                                        'matches': [m.group() for m in matches]
                                    })
                            else:
                                if content_pattern in line:
                                    results.append({
                                        'file': file_path,
                                        'line_num': line_num,
                                        'line': line.strip(),
                                        'matches': [content_pattern]
                                    })
                except (IOError, OSError):
                    continue
        
        return results
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict:
        """获取文件信息"""
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'size_human': FileUtils.format_size(stat.st_size),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'is_file': os.path.isfile(file_path),
            'is_dir': os.path.isdir(file_path),
            'extension': os.path.splitext(file_path)[1],
        }
    
    @staticmethod
    def format_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
    
    @staticmethod
    def get_directory_size(directory: str) -> int:
        """获取目录大小"""
        total = 0
        for root, dirs, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    total += os.path.getsize(file_path)
                except (IOError, OSError):
                    pass
        return total
