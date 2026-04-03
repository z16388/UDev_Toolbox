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
    CHARSET_OCTAL = "01234567"
    CHARSET_HEX_LOWER = "0123456789abcdef"
    CHARSET_HEX_UPPER = "0123456789ABCDEF"
    CHARSET_SPECIAL = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    
    @staticmethod
    def generate_random_string(
        length: int = 16,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_special: bool = False,
        custom_charset: str = "",
        number_min: int = None,
        number_max: int = None
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
            number_min: 数字范围最小值（仅当只使用数字时有效）
            number_max: 数字范围最大值（仅当只使用数字时有效）
        
        Returns:
            随机字符串
        """
        # 检查是否只使用数字且指定了范围
        only_digits = use_digits and not use_uppercase and not use_lowercase and not use_special and not custom_charset
        if only_digits and number_min is not None and number_max is not None:
            # 生成指定范围的随机数字
            number = random.randint(number_min, number_max)
            return str(number)
        
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
    def generate_combo_strings(
        template: str = "{UL:8}-{D:4}-{D:4}\n{H:4}-{h:4}"
    ) -> str:
        """
        生成组合字符串（根据模板格式）
        
        Args:
            template: 多行模板格式，每行生成一个字符串，支持三种占位符格式：
                    1. 单字符占位符：U L D S O H h（每个代表1个字符）
                       U = 大写字母 (A-Z)
                       L = 小写字母 (a-z)
                       D = 十进制数字 (0-9)
                       S = 特殊符号
                       O = 八进制数字 (0-7)
                       H = 大写十六进制 (0-9A-F)
                       h = 小写十六进制 (0-9a-f)
                    2. 扩展占位符：{类型组合:长度}
                       {U:5} = 5个大写字母
                       {UL:8} = 8个大小写字母混合
                       {ULD:10} = 10个大小写字母和数字混合
                       {h:4} = 4个小写十六进制
                    3. 数字范围占位符：{N:min-max}
                       {N:100-999} = 100到999之间的随机数字
                       {N:1000-9999} = 1000到9999之间的随机数字
                    其他字符保持不变
        
        Returns:
            生成的字符串组合
        """
        import re
        
        # 定义字符集映射
        charset_map = {
            'U': StringUtils.CHARSET_UPPERCASE,
            'L': StringUtils.CHARSET_LOWERCASE,
            'D': StringUtils.CHARSET_DIGITS,
            'S': StringUtils.CHARSET_SPECIAL,
            'O': StringUtils.CHARSET_OCTAL,
            'H': StringUtils.CHARSET_HEX_UPPER,
            'h': StringUtils.CHARSET_HEX_LOWER,
        }
        
        # 按行处理模板
        lines = template.split('\n')
        results = []
        
        for line in lines:
            if not line.strip():  # 跳过空行
                results.append('')
                continue
            
            result = ""
            i = 0
            while i < len(line):
                # 检查是否是扩展占位符 {类型:长度} 或 {N:min-max}
                if line[i] == '{':
                    # 查找匹配的 }
                    close_idx = line.find('}', i)
                    if close_idx != -1:
                        # 解析占位符内容
                        placeholder = line[i+1:close_idx]
                        if ':' in placeholder:
                            types_str, value_str = placeholder.split(':', 1)
                            
                            # 检查是否是数字范围格式 {N:min-max}
                            if types_str == 'N' and '-' in value_str:
                                try:
                                    min_val, max_val = value_str.split('-', 1)
                                    min_num = int(min_val)
                                    max_num = int(max_val)
                                    # 生成范围内的随机数字
                                    result += str(random.randint(min_num, max_num))
                                    i = close_idx + 1
                                    continue
                                except ValueError:
                                    # 解析失败，保持原样
                                    result += line[i]
                                    i += 1
                                    continue
                            
                            # 常规的 {类型:长度} 格式
                            try:
                                length = int(value_str)
                                # 构建字符集
                                charset = ""
                                for char_type in types_str:
                                    if char_type in charset_map:
                                        charset += charset_map[char_type]
                                
                                if charset:
                                    # 生成指定长度的随机字符
                                    result += ''.join(random.choice(charset) for _ in range(length))
                                else:
                                    # 未识别的类型，保持原样
                                    result += line[i:close_idx+1]
                                
                                i = close_idx + 1
                                continue
                            except ValueError:
                                # 长度不是有效数字，保持原样
                                result += line[i]
                                i += 1
                                continue
                        else:
                            # 没有冒号，保持原样
                            result += line[i]
                            i += 1
                            continue
                    else:
                        # 没有找到匹配的 }，保持原样
                        result += line[i]
                        i += 1
                        continue
                
                # 检查是否是单字符占位符
                if line[i] in charset_map:
                    result += random.choice(charset_map[line[i]])
                else:
                    result += line[i]
                
                i += 1
            
            results.append(result)
        
        return '\n'.join(results)
    
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
