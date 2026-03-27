#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
时间工具 - 核心功能模块
"""

import time
import calendar
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple


class TimeUtils:
    """时间工具类"""
    
    # 常用时区
    TIMEZONES = {
        'UTC': timezone.utc,
        'UTC+8': timezone(timedelta(hours=8)),  # 北京时间
        'UTC+9': timezone(timedelta(hours=9)),  # 东京时间
        'UTC-5': timezone(timedelta(hours=-5)), # 纽约时间
        'UTC-8': timezone(timedelta(hours=-8)), # 洛杉矶时间
        'UTC+1': timezone(timedelta(hours=1)),  # 伦敦夏令时
    }
    
    @staticmethod
    def timestamp_to_datetime(
        timestamp: float,
        is_milliseconds: bool = False,
        tz_name: str = 'UTC+8'
    ) -> datetime:
        """
        时间戳转日期时间
        
        Args:
            timestamp: 时间戳
            is_milliseconds: 是否为毫秒级时间戳
            tz_name: 时区名称
        """
        if is_milliseconds:
            timestamp = timestamp / 1000
        
        tz = TimeUtils.TIMEZONES.get(tz_name, timezone.utc)
        return datetime.fromtimestamp(timestamp, tz)
    
    @staticmethod
    def datetime_to_timestamp(
        dt: datetime,
        to_milliseconds: bool = False
    ) -> float:
        """日期时间转时间戳"""
        ts = dt.timestamp()
        if to_milliseconds:
            ts = ts * 1000
        return ts
    
    @staticmethod
    def get_current_timestamp(milliseconds: bool = False) -> float:
        """获取当前时间戳"""
        ts = time.time()
        if milliseconds:
            ts = ts * 1000
        return ts
    
    @staticmethod
    def format_timestamp(
        timestamp: float,
        is_milliseconds: bool = False,
        format_str: str = '%Y-%m-%d %H:%M:%S',
        tz_name: str = 'UTC+8'
    ) -> str:
        """格式化时间戳为字符串"""
        dt = TimeUtils.timestamp_to_datetime(timestamp, is_milliseconds, tz_name)
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_datetime(
        date_str: str,
        format_str: str = '%Y-%m-%d %H:%M:%S'
    ) -> datetime:
        """解析日期字符串"""
        return datetime.strptime(date_str, format_str)
    
    @staticmethod
    def convert_timezone(
        dt: datetime,
        from_tz: str,
        to_tz: str
    ) -> datetime:
        """转换时区"""
        from_timezone = TimeUtils.TIMEZONES.get(from_tz, timezone.utc)
        to_timezone = TimeUtils.TIMEZONES.get(to_tz, timezone.utc)
        
        # 如果datetime没有时区信息，添加源时区
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=from_timezone)
        
        return dt.astimezone(to_timezone)
    
    @staticmethod
    def calculate_countdown(target: datetime) -> Dict:
        """
        计算倒计时
        
        Returns:
            包含天、时、分、秒的字典
        """
        now = datetime.now(target.tzinfo)
        delta = target - now
        
        total_seconds = int(delta.total_seconds())
        
        if total_seconds < 0:
            return {
                'expired': True,
                'days': 0,
                'hours': 0,
                'minutes': 0,
                'seconds': 0,
                'total_seconds': total_seconds
            }
        
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            'expired': False,
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': total_seconds
        }
    
    @staticmethod
    def calculate_duration(start: datetime, end: datetime) -> Dict:
        """计算时间间隔"""
        delta = end - start
        total_seconds = abs(int(delta.total_seconds()))
        
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': total_seconds,
            'human_readable': TimeUtils._format_duration(days, hours, minutes, seconds)
        }
    
    @staticmethod
    def _format_duration(days: int, hours: int, minutes: int, seconds: int) -> str:
        """格式化时间间隔为人类可读字符串"""
        parts = []
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}秒")
        return ' '.join(parts)
    
    @staticmethod
    def parse_cron(expression: str) -> Dict:
        """
        解析Cron表达式
        
        格式: 分钟 小时 日 月 星期
        """
        parts = expression.strip().split()
        
        if len(parts) != 5:
            return {'error': 'Cron表达式应包含5个部分: 分钟 小时 日 月 星期'}
        
        field_names = ['minute', 'hour', 'day', 'month', 'weekday']
        field_ranges = [
            (0, 59),   # 分钟
            (0, 23),   # 小时
            (1, 31),   # 日
            (1, 12),   # 月
            (0, 6),    # 星期
        ]
        
        result = {
            'expression': expression,
            'fields': {},
            'description': '',
            'next_runs': []
        }
        
        for i, part in enumerate(parts):
            field = field_names[i]
            min_val, max_val = field_ranges[i]
            
            result['fields'][field] = {
                'expression': part,
                'values': TimeUtils._parse_cron_field(part, min_val, max_val)
            }
        
        result['description'] = TimeUtils._describe_cron(result['fields'])
        result['next_runs'] = TimeUtils._get_next_cron_runs(result['fields'], count=5)
        
        return result
    
    @staticmethod
    def _parse_cron_field(field: str, min_val: int, max_val: int) -> List[int]:
        """解析Cron字段"""
        values = set()
        
        for part in field.split(','):
            if part == '*':
                values.update(range(min_val, max_val + 1))
            elif '/' in part:
                # 步长
                base, step = part.split('/')
                step = int(step)
                if base == '*':
                    start = min_val
                else:
                    start = int(base)
                values.update(range(start, max_val + 1, step))
            elif '-' in part:
                # 范围
                start, end = map(int, part.split('-'))
                values.update(range(start, end + 1))
            else:
                values.add(int(part))
        
        return sorted(values)
    
    @staticmethod
    def _describe_cron(fields: Dict) -> str:
        """生成Cron表达式的描述"""
        parts = []
        
        minute = fields['minute']['expression']
        hour = fields['hour']['expression']
        day = fields['day']['expression']
        month = fields['month']['expression']
        weekday = fields['weekday']['expression']
        
        # 简单描述生成
        if minute == '0' and hour == '0':
            parts.append('每天午夜')
        elif minute == '0':
            if hour == '*':
                parts.append('每小时整点')
            else:
                parts.append(f'每天 {hour} 点')
        elif minute == '*' and hour == '*':
            parts.append('每分钟')
        else:
            parts.append(f'在第 {minute} 分钟, 第 {hour} 小时')
        
        if day != '*':
            parts.append(f'每月第 {day} 天')
        if month != '*':
            parts.append(f'第 {month} 月')
        if weekday != '*':
            weekday_names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
            parts.append(f'{weekday_names[int(weekday)]}')
        
        return ', '.join(parts)
    
    @staticmethod
    def _get_next_cron_runs(fields: Dict, count: int = 5) -> List[str]:
        """获取Cron的下一次运行时间"""
        # 简化实现：只返回描述
        return [f"下次运行时间计算需要完整实现" for _ in range(count)]
    
    @staticmethod
    def generate_cron(
        minute: str = '*',
        hour: str = '*',
        day: str = '*',
        month: str = '*',
        weekday: str = '*'
    ) -> str:
        """生成Cron表达式"""
        return f"{minute} {hour} {day} {month} {weekday}"
    
    @staticmethod
    def get_week_info(date: datetime = None) -> Dict:
        """获取周信息"""
        if date is None:
            date = datetime.now()
        
        iso_calendar = date.isocalendar()
        
        return {
            'year': date.year,
            'month': date.month,
            'day': date.day,
            'weekday': date.weekday(),  # 0-6, 周一为0
            'weekday_name': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date.weekday()],
            'iso_week': iso_calendar[1],
            'iso_weekday': iso_calendar[2],
            'day_of_year': date.timetuple().tm_yday,
        }
    
    @staticmethod
    def add_time(
        dt: datetime,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0
    ) -> datetime:
        """添加时间"""
        return dt + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    
    @staticmethod
    def get_month_calendar(year: int, month: int) -> List[List[int]]:
        """获取月历"""
        return calendar.monthcalendar(year, month)
