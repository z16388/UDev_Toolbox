#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
页面模块
"""

from .page_home import HomePage
from .page_apk import APKToolsPage
from .page_string import StringToolsPage
from .page_file import FileToolsPage
from .page_unity import UnityToolsPage
from .page_network import NetworkToolsPage
from .page_time import TimeToolsPage
from .page_wiki import WikiPage
from .page_settings import SettingsPage

__all__ = [
    'HomePage',
    'APKToolsPage', 
    'StringToolsPage',
    'FileToolsPage',
    'UnityToolsPage',
    'NetworkToolsPage',
    'TimeToolsPage',
    'WikiPage',
    'SettingsPage',
]
