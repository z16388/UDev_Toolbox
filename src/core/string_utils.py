#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
字符串工具 - 核心功能模块
"""

import base64
import hashlib
import hmac
import json
import random
import re
import string
import urllib.parse
import uuid
from typing import Optional, List, Tuple


class StringUtils:
    """字符串工具类"""
    
    # 字符集常量
    CHARSET_UPPERCASE = string.ascii_uppercase
    CHARSET_LOWERCASE = string.ascii_lowercase
    CHARSET_DIGITS = string.digits
    CHARSET_SPECIAL = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    
    @staticmethod
    def generate_random_string(
        length: int = 16,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_special: bool = False,
        custom_charset: str = ""
    ) -> str:
        """
        生成随机字符串
        
        Args:
            length: 字符串长度
            use_uppercase: 是否包含大写字母
            use_lowercase: 是否包含小写字母
            use_digits: 是否包含数字
            use_special: 是否包含特殊符号
            custom_charset: 自定义字符集
        
        Returns:
            随机字符串
        """
        charset = custom_charset
        if not charset:
            if use_uppercase:
                charset += StringUtils.CHARSET_UPPERCASE
            if use_lowercase:
                charset += StringUtils.CHARSET_LOWERCASE
            if use_digits:
                charset += StringUtils.CHARSET_DIGITS
            if use_special:
                charset += StringUtils.CHARSET_SPECIAL
        
        if not charset:
            charset = string.ascii_letters + string.digits
        
        return ''.join(random.choice(charset) for _ in range(length))
    
    @staticmethod
    def generate_multiple_strings(
        count: int,
        length: int = 16,
        **kwargs
    ) -> List[str]:
        """生成多个随机字符串"""
        return [StringUtils.generate_random_string(length, **kwargs) for _ in range(count)]
    
    @staticmethod
    def base64_encode(text: str, encoding: str = 'utf-8') -> str:
        """Base64编码"""
        return base64.b64encode(text.encode(encoding)).decode('ascii')
    
    @staticmethod
    def base64_decode(text: str, encoding: str = 'utf-8') -> str:
        """Base64解码"""
        # 添加填充
        padding = 4 - len(text) % 4
        if padding != 4:
            text += '=' * padding
        return base64.b64decode(text).decode(encoding)
    
    @staticmethod
    def url_encode(text: str) -> str:
        """URL编码"""
        return urllib.parse.quote(text, safe='')
    
    @staticmethod
    def url_decode(text: str) -> str:
        """URL解码"""
        return urllib.parse.unquote(text)
    
    @staticmethod
    def json_format(text: str, indent: int = 2) -> str:
        """JSON格式化"""
        obj = json.loads(text)
        return json.dumps(obj, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def json_minify(text: str) -> str:
        """JSON压缩"""
        obj = json.loads(text)
        return json.dumps(obj, separators=(',', ':'), ensure_ascii=False)
    
    @staticmethod
    def json_validate(text: str) -> Tuple[bool, str]:
        """验证JSON格式"""
        try:
            json.loads(text)
            return True, "JSON格式正确"
        except json.JSONDecodeError as e:
            return False, f"JSON格式错误: {e}"
    
    @staticmethod
    def unicode_encode(text: str) -> str:
        """Unicode编码 (转换为\\uXXXX格式)"""
        return text.encode('unicode_escape').decode('ascii')
    
    @staticmethod
    def unicode_decode(text: str) -> str:
        """Unicode解码"""
        return text.encode('ascii').decode('unicode_escape')
    
    @staticmethod
    def generate_guid() -> str:
        """生成GUID (Unity常用格式)"""
        return str(uuid.uuid4()).replace('-', '')
    
    @staticmethod
    def generate_uuid() -> str:
        """生成标准UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_multiple_guids(count: int) -> List[str]:
        """生成多个GUID"""
        return [StringUtils.generate_guid() for _ in range(count)]
    
    @staticmethod
    def regex_test(pattern: str, text: str, flags: int = 0) -> dict:
        """
        正则表达式测试
        
        Returns:
            包含匹配结果的字典
        """
        result = {
            'is_valid': True,
            'matches': [],
            'groups': [],
            'error': None
        }
        
        try:
            compiled = re.compile(pattern, flags)
            matches = list(compiled.finditer(text))
            
            result['matches'] = [
                {
                    'match': m.group(),
                    'start': m.start(),
                    'end': m.end(),
                    'groups': m.groups()
                }
                for m in matches
            ]
            
        except re.error as e:
            result['is_valid'] = False
            result['error'] = str(e)
        
        return result
    
    @staticmethod
    def regex_replace(pattern: str, replacement: str, text: str, flags: int = 0) -> str:
        """正则表达式替换"""
        return re.sub(pattern, replacement, text, flags=flags)
    
    @staticmethod
    def hash_md5(text: str) -> str:
        """计算MD5哈希"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_sha1(text: str) -> str:
        """计算SHA1哈希"""
        return hashlib.sha1(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_sha256(text: str) -> str:
        """计算SHA256哈希"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_sha512(text: str) -> str:
        """计算SHA512哈希"""
        return hashlib.sha512(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hmac_sign(key: str, message: str, algorithm: str = 'sha256') -> str:
        """HMAC签名"""
        hash_func = getattr(hashlib, algorithm)
        return hmac.new(
            key.encode('utf-8'),
            message.encode('utf-8'),
            hash_func
        ).hexdigest()
    
    @staticmethod
    def hex_encode(text: str) -> str:
        """十六进制编码"""
        return text.encode('utf-8').hex()
    
    @staticmethod
    def hex_decode(text: str) -> str:
        """十六进制解码"""
        return bytes.fromhex(text).decode('utf-8')
    
    @staticmethod
    def convert_case(text: str, case_type: str) -> str:
        """
        转换大小写
        
        Args:
            text: 输入文本
            case_type: 转换类型 (upper, lower, title, capitalize, swap)
        """
        case_map = {
            'upper': text.upper,
            'lower': text.lower,
            'title': text.title,
            'capitalize': text.capitalize,
            'swap': text.swapcase,
        }
        return case_map.get(case_type, lambda: text)()
    
    @staticmethod
    def count_characters(text: str) -> dict:
        """统计字符"""
        return {
            'total': len(text),
            'letters': sum(1 for c in text if c.isalpha()),
            'digits': sum(1 for c in text if c.isdigit()),
            'spaces': sum(1 for c in text if c.isspace()),
            'lines': text.count('\n') + 1,
            'words': len(text.split()),
        }
