#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置管理器 - 管理应用程序配置
"""

import os
import json
from typing import Any, Dict, List, Optional
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        'version': '1.0.0',
        'theme': 'dark',
        'language': 'zh-CN',
        'page_order': [
            'home', 'apk', 'string', 'file', 'unity', 'network', 'time', 'wiki'
        ],
        'recent_files': [],
        'wiki_pages': [],
        'custom_wiki_icons': {},
        'git_settings': {
            'auto_sync': False,
            'remote_url': '',
            'branch': 'main',
        },
        'apk_settings': {
            'aapt_path': '',
            'auto_extract_icon': True,
        },
        'network_settings': {
            'timeout': 30,
            'verify_ssl': False,
        },
        'string_settings': {
            'combo_template': '{UL:8}-{D:4}-{D:4}\n订单号:{U:4}{N:10000-99999}\n会员卡:{N:100000-999999}',
        }
    }
    
    def __init__(self, config_dir: str = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置目录路径
        """
        if config_dir is None:
            config_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config'
            )
        
        self.config_dir = config_dir
        self.config_path = os.path.join(config_dir, 'settings.json')
        self.wiki_dir = os.path.join(config_dir, 'wiki')
        
        # 确保目录存在
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(self.wiki_dir, exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置
                return self._merge_config(self.DEFAULT_CONFIG, config)
            except Exception as e:
                print(f"加载配置失败: {e}")
        
        return self.DEFAULT_CONFIG.copy()
    
    def _merge_config(self, default: Dict, custom: Dict) -> Dict:
        """合并配置，保留自定义值"""
        result = default.copy()
        for key, value in custom.items():
            if key in result:
                if isinstance(value, dict) and isinstance(result[key], dict):
                    result[key] = self._merge_config(result[key], value)
                else:
                    result[key] = value
            else:
                result[key] = value
        return result
    
    def save(self):
        """保存配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """设置配置项"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save()
    
    def get_page_order(self) -> List[str]:
        """获取页面顺序"""
        return self.config.get('page_order', self.DEFAULT_CONFIG['page_order'])
    
    def set_page_order(self, order: List[str]):
        """设置页面顺序"""
        self.set('page_order', order)
    
    def get_wiki_pages(self) -> List[Dict]:
        """获取Wiki页面列表"""
        return self.config.get('wiki_pages', [])
    
    def add_wiki_page(self, title: str, icon: str = 'ic_fluent_document_filled') -> str:
        """
        添加Wiki页面
        
        Returns:
            页面ID
        """
        import uuid
        page_id = str(uuid.uuid4())[:8]
        
        wiki_pages = self.get_wiki_pages()
        wiki_pages.append({
            'id': page_id,
            'title': title,
            'icon': icon,
            'created': self._current_time(),
            'modified': self._current_time(),
        })
        
        self.set('wiki_pages', wiki_pages)
        
        # 创建Wiki文件
        wiki_path = os.path.join(self.wiki_dir, f'{page_id}.md')
        with open(wiki_path, 'w', encoding='utf-8') as f:
            f.write(f'# {title}\n\n在这里编写你的内容...\n')
        
        return page_id
    
    def get_wiki_content(self, page_id: str) -> str:
        """获取Wiki内容"""
        wiki_path = os.path.join(self.wiki_dir, f'{page_id}.md')
        if os.path.exists(wiki_path):
            with open(wiki_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ''
    
    def save_wiki_content(self, page_id: str, content: str):
        """保存Wiki内容"""
        wiki_path = os.path.join(self.wiki_dir, f'{page_id}.md')
        with open(wiki_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 更新修改时间
        wiki_pages = self.get_wiki_pages()
        for page in wiki_pages:
            if page['id'] == page_id:
                page['modified'] = self._current_time()
                break
        self.set('wiki_pages', wiki_pages)
    
    def delete_wiki_page(self, page_id: str):
        """删除Wiki页面"""
        wiki_path = os.path.join(self.wiki_dir, f'{page_id}.md')
        if os.path.exists(wiki_path):
            os.remove(wiki_path)
        
        wiki_pages = self.get_wiki_pages()
        wiki_pages = [p for p in wiki_pages if p['id'] != page_id]
        self.set('wiki_pages', wiki_pages)
    
    def add_recent_file(self, file_path: str, file_type: str = 'apk'):
        """添加最近文件"""
        recent = self.config.get('recent_files', [])
        
        # 移除重复项
        recent = [f for f in recent if f['path'] != file_path]
        
        # 添加到开头
        recent.insert(0, {
            'path': file_path,
            'type': file_type,
            'time': self._current_time()
        })
        
        # 限制数量
        recent = recent[:20]
        
        self.set('recent_files', recent)
    
    def _current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    # Wiki可选图标列表
    WIKI_ICONS = [
        'ic_fluent_document_filled',
        'ic_fluent_book_filled',
        'ic_fluent_notebook_filled',
        'ic_fluent_note_filled',
        'ic_fluent_clipboard_filled',
        'ic_fluent_folder_filled',
        'ic_fluent_archive_filled',
        'ic_fluent_bookmark_filled',
        'ic_fluent_star_filled',
        'ic_fluent_heart_filled',
        'ic_fluent_flag_filled',
        'ic_fluent_tag_filled',
        'ic_fluent_lightbulb_filled',
        'ic_fluent_puzzle_piece_filled',
        'ic_fluent_wrench_filled',
        'ic_fluent_code_filled',
        'ic_fluent_bug_filled',
        'ic_fluent_beaker_filled',
        'ic_fluent_rocket_filled',
        'ic_fluent_globe_filled',
        'ic_fluent_home_filled',
        'ic_fluent_person_filled',
        'ic_fluent_people_filled',
        'ic_fluent_chat_filled',
        'ic_fluent_mail_filled',
        'ic_fluent_calendar_filled',
        'ic_fluent_clock_filled',
        'ic_fluent_camera_filled',
        'ic_fluent_image_filled',
        'ic_fluent_video_filled',
        'ic_fluent_music_note_filled',
        'ic_fluent_games_filled',
    ]
