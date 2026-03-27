#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unity Developer Toolbox - 主窗口
"""

import os
import sys

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDesktopWidget

from siui.core import SiColor, SiGlobal
from siui.components.widgets import SiPushButton, SiDenseHContainer
from siui.templates.application.application import SiliconApplication

from src.core.config_manager import ConfigManager
from src.ui.pages.page_home import HomePage
from src.ui.pages.page_apk import APKToolsPage
from src.ui.pages.page_string import StringToolsPage
from src.ui.pages.page_file import FileToolsPage
from src.ui.pages.page_unity import UnityToolsPage
from src.ui.pages.page_network import NetworkToolsPage
from src.ui.pages.page_time import TimeToolsPage
from src.ui.pages.page_wiki_new import WikiPage
from src.ui.pages.page_settings import SettingsPage
from src.ui.components.custom_page_view import CustomPageView


# 载入图标 - 使用空字典作为备用方案
# TODO: 需要提供正确的图标文件路径或生成图标数据
try:
    from src.icons import IconDictionary
    siui_icons = IconDictionary(color=SiGlobal.siui.colors.fromToken(SiColor.SVG_NORMAL))
    SiGlobal.siui.loadIcons(siui_icons.icons)
except FileNotFoundError:
    # 图标文件不存在时使用空图标字典
    SiGlobal.siui.loadIcons({})


class UDevToolbox(SiliconApplication):
    """Unity开发者工具箱主窗口"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 加载配置
        self.config = ConfigManager()
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        
        # 窗口拖动相关变量
        self._is_dragging = False
        self._drag_position = QPoint()
        
        # 窗口设置
        screen_geo = QDesktopWidget().screenGeometry()
        self.setMinimumSize(1024, 600)
        self.resize(1400, 900)
        self.move((screen_geo.width() - self.width()) // 2, 
                  (screen_geo.height() - self.height()) // 2)
        
        self.layerMain().setTitle("Unity 开发者工具箱")
        self.setWindowTitle("Unity 开发者工具箱 - UDev Toolbox")
        
        # 设置窗口图标
        base_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
        icon_files = ["app_icon.png", "app_icon.ico", "app_icon.svg"]
        for icon_file in icon_files:
            icon_path = os.path.join(base_path, icon_file)
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                if icon_file.endswith('.png') or icon_file.endswith('.ico'):
                    self.layerMain().app_icon.load(icon_path)
                break
        # 备用图标路径
        icon_path = os.path.join(os.path.dirname(__file__), "../../assets/icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            self.layerMain().app_icon.load(icon_path)
        
        # 添加窗口控制按钮
        self._setup_window_controls()
        
        # 使用自定义PageView替换默认视图
        self._setup_custom_page_view()
        
        # 重新加载样式
        SiGlobal.siui.reloadAllWindowsStyleSheet()
    
    def _setup_window_controls(self):
        """设置窗口控制按钮"""
        # 创建按钮容器
        controls_container = SiDenseHContainer(self.layerMain().container_title)
        controls_container.setSpacing(4)
        controls_container.setFixedHeight(64)
        
        # 最小化按钮
        self.btn_minimize = SiPushButton(controls_container)
        self.btn_minimize.resize(40, 40)
        self.btn_minimize.setHint("最小化")
        self.btn_minimize.setToolTip("最小化")  # 添加Qt原生工具提示作为备用
        # 尝试加载图标，如果没有则使用文本
        try:
            self.btn_minimize.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_subtract_filled"))
            self.btn_minimize.attachment().setSvgSize(16, 16)
        except:
            self.btn_minimize.setText("—")
        self.btn_minimize.clicked.connect(self.showMinimized)
        
        # 最大化/还原按钮
        self.btn_maximize = SiPushButton(controls_container)
        self.btn_maximize.resize(40, 40)
        self.btn_maximize.setHint("最大化")
        self.btn_maximize.setToolTip("最大化")  # 添加Qt原生工具提示作为备用
        # 尝试加载图标，如果没有则使用文本
        try:
            self.btn_maximize.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_maximize_filled"))
            self.btn_maximize.attachment().setSvgSize(16, 16)
        except:
            self.btn_maximize.setText("□")
        self.btn_maximize.clicked.connect(self._toggle_maximize)
        
        # 关闭按钮
        self.btn_close = SiPushButton(controls_container)
        self.btn_close.resize(40, 40)
        self.btn_close.setHint("关闭")
        self.btn_close.setToolTip("关闭")  # 添加Qt原生工具提示作为备用
        # 设置关闭按钮的红色悬停背景
        self.btn_close.colorGroup().assign(SiColor.BUTTON_HOVER, "#E81123")
        # 尝试加载图标，如果没有则使用文本
        try:
            self.btn_close.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_dismiss_filled"))
            self.btn_close.attachment().setSvgSize(16, 16)
        except:
            self.btn_close.setText("✕")
        self.btn_close.clicked.connect(self.close)
        
        # 添加按钮到容器
        controls_container.addWidget(self.btn_minimize)
        controls_container.addWidget(self.btn_maximize)
        controls_container.addWidget(self.btn_close)
        controls_container.addPlaceholder(8)  # 右侧留一些边距
        
        # 将控制按钮容器添加到标题栏右侧
        self.layerMain().container_title.addWidget(controls_container, side="right")
    
    def _toggle_maximize(self):
        """切换最大化/还原状态"""
        if self.isMaximized():
            self.showNormal()
            self.btn_maximize.setHint("最大化")
            self.btn_maximize.setToolTip("最大化")
            try:
                self.btn_maximize.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_maximize_filled"))
            except:
                self.btn_maximize.setText("□")
        else:
            self.showMaximized()
            self.btn_maximize.setHint("还原")
            self.btn_maximize.setToolTip("还原")
            try:
                self.btn_maximize.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_square_multiple_filled"))
            except:
                self.btn_maximize.setText("❐")
    
    def _setup_custom_page_view(self):
        """设置自定义页面视图"""
        # 获取原有page_view
        old_page_view = self.layerMain().page_view
        parent_widget = self.layerMain()
        
        # 创建自定义页面视图 - 直接使用layerMain作为父对象
        self.custom_page_view = CustomPageView(parent_widget)
        
        # 隐藏并删除旧视图
        old_page_view.hide()
        old_page_view.setParent(None)
        
        # 替换layerMain的page_view引用
        self.layerMain().page_view = self.custom_page_view
        
        # 将新视图添加到container_title_and_content
        self.layerMain().container_title_and_content.addWidget(self.custom_page_view)
        
        # 定义页面映射
        page_map = {
            "home": (HomePage, "ic_fluent_home_filled", "主页"),
            "apk": (APKToolsPage, "ic_fluent_phone_filled", "APK分析"),
            "string": (StringToolsPage, "ic_fluent_text_case_title_filled", "字符串工具"),
            "file": (FileToolsPage, "ic_fluent_folder_filled", "文件工具"),
            "unity": (UnityToolsPage, "ic_fluent_cube_filled", "Unity工具"),
            "network": (NetworkToolsPage, "ic_fluent_globe_filled", "网络工具"),
            "time": (TimeToolsPage, "ic_fluent_clock_filled", "时间工具"),
            "wiki": (WikiPage, "ic_fluent_book_filled", "Wiki文档"),
        }
        
        # 从配置读取侧边栏页面设置
        default_pages = [
            {"name": "主页", "key": "home", "visible": True},
            {"name": "APK分析", "key": "apk", "visible": True},
            {"name": "字符串工具", "key": "string", "visible": True},
            {"name": "文件工具", "key": "file", "visible": True},
            {"name": "Unity工具", "key": "unity", "visible": True},
            {"name": "网络工具", "key": "network", "visible": True},
            {"name": "时间工具", "key": "time", "visible": True},
            {"name": "Wiki文档", "key": "wiki", "visible": True},
        ]
        sidebar_pages = self.config.get('sidebar_pages', default_pages)
        
        # 根据配置添加页面
        for page_config in sidebar_pages:
            if page_config.get('visible', True) and page_config['key'] in page_map:
                page_class, icon_key, page_name = page_map[page_config['key']]
                self.custom_page_view.addPage(
                    page_class(self),
                    icon=SiGlobal.siui.iconpack.get(icon_key),
                    text=page_config.get('name', page_name),
                    side="top"
                )
        
        # 添加页面 - 底部设置页面
        self.custom_page_view.addPage(
            SettingsPage(self),
            icon=SiGlobal.siui.iconpack.get("ic_fluent_settings_filled"),
            text="设置",
            side="bottom"
        )
        
        # 默认显示主页
        self.custom_page_view.setPage(0)
    
    def reload_sidebar(self):
        """重新加载侧边栏（应用设置后立即生效）"""
        from siui.core import SiGlobal
        
        # 清空现有页面和按钮
        self.custom_page_view.clearPages()
        
        # 定义页面映射
        page_map = {
            "home": (HomePage, "ic_fluent_home_filled", "主页"),
            "apk": (APKToolsPage, "ic_fluent_phone_filled", "APK分析"),
            "string": (StringToolsPage, "ic_fluent_text_case_title_filled", "字符串工具"),
            "file": (FileToolsPage, "ic_fluent_folder_filled", "文件工具"),
            "unity": (UnityToolsPage, "ic_fluent_cube_filled", "Unity工具"),
            "network": (NetworkToolsPage, "ic_fluent_globe_filled", "网络工具"),
            "time": (TimeToolsPage, "ic_fluent_clock_filled", "时间工具"),
            "wiki": (WikiPage, "ic_fluent_book_filled", "Wiki文档"),
        }
        
        # 从配置读取侧边栏页面设置
        default_pages = [
            {"name": "主页", "key": "home", "visible": True},
            {"name": "APK分析", "key": "apk", "visible": True},
            {"name": "字符串工具", "key": "string", "visible": True},
            {"name": "文件工具", "key": "file", "visible": True},
            {"name": "Unity工具", "key": "unity", "visible": True},
            {"name": "网络工具", "key": "network", "visible": True},
            {"name": "时间工具", "key": "time", "visible": True},
            {"name": "Wiki文档", "key": "wiki", "visible": True},
        ]
        sidebar_pages = self.config.get('sidebar_pages', default_pages)
        
        # 按配置重新添加功能页面
        for page_config in sidebar_pages:
            if page_config.get('visible', True) and page_config['key'] in page_map:
                page_class, icon_key, page_name = page_map[page_config['key']]
                self.custom_page_view.addPage(
                    page_class(self),
                    icon=SiGlobal.siui.iconpack.get(icon_key),
                    text=page_config.get('name', page_name),
                    side="top"
                )
        
        # 重新添加设置页面
        self.custom_page_view.addPage(
            SettingsPage(self),
            icon=SiGlobal.siui.iconpack.get("ic_fluent_settings_filled"),
            text="设置",
            side="bottom"
        )
        
        # 跳转到设置页（最后一个）
        self.custom_page_view.setPage(self.custom_page_view.stacked_container.widgetsAmount() - 1)
        
        # 触发一次 resize 刷新导航栏布局
        nav = self.custom_page_view.page_navigator
        nav.resize(nav.width(), nav.height() + 1)
        nav.resize(nav.width(), nav.height() - 1)
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于窗口拖动"""
        if event.button() == Qt.LeftButton:
            # 只有在标题栏区域才允许拖动
            if event.y() <= 64:  # 标题栏高度
                self._is_dragging = True
                self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 用于窗口拖动"""
        if self._is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 结束窗口拖动"""
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
        super().mouseReleaseEvent(event)
