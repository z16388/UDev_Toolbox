#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设置页面
"""

from PyQt5.QtCore import Qt

from siui.components.option_card import SiOptionCardPlane, SiOptionCardLinear
from siui.components.page import SiPage
from siui.components.titled_widget_group import SiTitledWidgetGroup
from siui.components.widgets import (
    SiDenseHContainer,
    SiDenseVContainer,
    SiLabel,
    SiLineEdit,
    SiPushButton,
    SiSwitch,
)
from siui.core import Si, SiColor, SiGlobal

from src.core.config_manager import ConfigManager


class SettingsPage(SiPage):
    """设置页面"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.config = ConfigManager()
        
        self.scroll_container = SiTitledWidgetGroup(self)
        
        self.body_area = SiLabel(self)
        self.body_area.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.body_area.resized.connect(lambda _: self.scroll_container.adjustSize())
        
        self.titled_widget_group = SiTitledWidgetGroup(self.body_area)
        self.titled_widget_group.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.titled_widget_group.resized.connect(lambda size: self.body_area.setFixedHeight(size[1]))
        self.titled_widget_group.move(64, 32)
        
        self.titled_widget_group.setSpacing(16)
        
        # 关于
        self.titled_widget_group.addTitle("关于")
        self.titled_widget_group.addWidget(self._create_about_panel())
        
        # 侧边栏设置
        self.titled_widget_group.addTitle("侧边栏管理")
        self.titled_widget_group.addWidget(self._create_sidebar_panel())
        
        # APK工具设置
        self.titled_widget_group.addTitle("APK 工具设置")
        self.titled_widget_group.addWidget(self._create_apk_panel())
        
        # 网络设置
        self.titled_widget_group.addTitle("网络设置")
        self.titled_widget_group.addWidget(self._create_network_panel())
        
        # 数据管理
        self.titled_widget_group.addTitle("数据管理")
        self.titled_widget_group.addWidget(self._create_data_panel())
        
        self.titled_widget_group.addPlaceholder(64)
        
        self.body_area.setFixedHeight(self.titled_widget_group.height())
        self.scroll_container.addWidget(self.body_area)
        
        self.setAttachment(self.scroll_container)
    
    def _create_about_panel(self):
        """创建关于面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("Unity 开发者工具箱")
        
        about_text = """版本: 1.0.0
作者: UDev Toolbox Team
基于: PyQt5 + PyQt-SiliconUI

这是一个为Unity开发者打造的多功能工具箱，包含：
• APK分析 - 分析Android包信息、权限、架构等
• 字符串工具 - 编码解码、随机生成、正则测试
• 文件工具 - 哈希计算、批量重命名、文件对比
• Unity工具 - PlayerPrefs、GUID查找、资源分析
• 网络工具 - IP查询、HTTP测试、DNS解析
• 时间工具 - 时间戳转换、Cron解析
• Wiki文档 - Markdown笔记，支持Git同步"""
        
        about_label = SiLabel(self)
        about_label.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        about_label.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_B']};")
        about_label.setText(about_text)
        
        panel.body().addWidget(about_label)
        panel.adjustSize()
        
        return panel
    
    def _create_sidebar_panel(self):
        """创建侧边栏管理面板"""
        self.sidebar_panel = SiOptionCardPlane(self)
        self.sidebar_panel.setTitle("侧边栏按钮显示与排序")
        
        # 说明文本
        hint_label = SiLabel(self)
        hint_label.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        hint_label.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_C']};")
        hint_label.setText("勾选显示按钮，取消勾选隐藏按钮。可使用上/下移按钮调整顺序。")
        
        self.sidebar_panel.body().addWidget(hint_label)
        
        # 获取默认的侧边栏页面配置
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
        
        # 有效的页面 key 列表
        valid_keys = {"home", "apk", "string", "file", "unity", "network", "time", "wiki"}
        
        # 从配置中读取当前设置
        saved_config = self.config.get('sidebar_pages', default_pages)
        # 过滤掉无效的页面配置
        if saved_config:
            self.sidebar_pages = [page for page in saved_config if page.get("key") in valid_keys]
        else:
            self.sidebar_pages = default_pages
        
        # 如果过滤后为空，使用默认配置
        if not self.sidebar_pages:
            self.sidebar_pages = default_pages
        
        # 初始化页面项列表容器
        self._init_page_items_container()
        
        # 保存按钮
        save_row = SiDenseHContainer(self)
        save_row.setFixedHeight(36)
        save_row.setSpacing(8)
        
        save_btn = SiPushButton(self)
        save_btn.resize(100, 32)
        save_btn.setUseTransition(True)
        save_btn.attachment().setText("保存设置")
        save_btn.clicked.connect(self._save_sidebar_settings)
        
        reset_btn = SiPushButton(self)
        reset_btn.resize(100, 32)
        reset_btn.attachment().setText("恢复默认")
        reset_btn.clicked.connect(self._reset_sidebar_settings)
        
        save_row.addWidget(save_btn)
        save_row.addWidget(reset_btn)
        
        self.sidebar_panel.body().addWidget(save_row)
        self.sidebar_panel.adjustSize()
        
        return self.sidebar_panel
    
    def _init_page_items_container(self):
        """初始化页面项列表容器"""
        # 创建新的页面项列表容器
        self.page_items_container = SiDenseVContainer(self)
        self.page_items_container.setSpacing(4)
        
        self.page_items = []
        for page_data in self.sidebar_pages:
            item_row = self._create_page_item(page_data)
            self.page_items.append({"row": item_row, "data": page_data})
            self.page_items_container.addWidget(item_row)
        
        # 直接添加到面板body
        self.sidebar_panel.body().addWidget(self.page_items_container)
    
    def _create_page_item(self, page_data):
        """创建单个页面项"""
        row = SiDenseHContainer(self)
        row.setFixedHeight(40)
        row.setSpacing(8)
        
        # 复选框
        switch = SiSwitch(self)
        switch.setFixedSize(48, 32)
        switch.setChecked(page_data.get("visible", True))
        switch.toggled.connect(lambda checked: page_data.update({"visible": checked}))
        
        # 页面名称
        name_label = SiLabel(self)
        name_label.setText(page_data["name"])
        name_label.setFixedWidth(120)
        
        # 上移按钮
        up_btn = SiPushButton(self)
        up_btn.resize(60, 32)
        up_btn.attachment().setText("上移")
        up_btn.clicked.connect(lambda: self._move_page_up(page_data))
        
        # 下移按钮
        down_btn = SiPushButton(self)
        down_btn.resize(60, 32)
        down_btn.attachment().setText("下移")
        down_btn.clicked.connect(lambda: self._move_page_down(page_data))
        
        row.addWidget(switch)
        row.addWidget(name_label)
        row.addWidget(up_btn)
        row.addWidget(down_btn)
        
        return row
    
    def _move_page_up(self, page_data):
        """上移页面"""
        index = next((i for i, data in enumerate(self.sidebar_pages) if data == page_data), -1)
        if index > 0:
            # 交换数据
            self.sidebar_pages[index], self.sidebar_pages[index - 1] = self.sidebar_pages[index - 1], self.sidebar_pages[index]
            # 直接交换容器内部列表和page_items的顺序
            self.page_items[index], self.page_items[index - 1] = self.page_items[index - 1], self.page_items[index]
            self.page_items_container.widgets_top[index], self.page_items_container.widgets_top[index - 1] = \
                self.page_items_container.widgets_top[index - 1], self.page_items_container.widgets_top[index]
            # 重新排列位置
            self.page_items_container.arrangeWidget()
    
    def _move_page_down(self, page_data):
        """下移页面"""
        index = next((i for i, data in enumerate(self.sidebar_pages) if data == page_data), -1)
        if index >= 0 and index < len(self.sidebar_pages) - 1:
            # 交换数据
            self.sidebar_pages[index], self.sidebar_pages[index + 1] = self.sidebar_pages[index + 1], self.sidebar_pages[index]
            # 直接交换容器内部列表和page_items的顺序
            self.page_items[index], self.page_items[index + 1] = self.page_items[index + 1], self.page_items[index]
            self.page_items_container.widgets_top[index], self.page_items_container.widgets_top[index + 1] = \
                self.page_items_container.widgets_top[index + 1], self.page_items_container.widgets_top[index]
            # 重新排列位置
            self.page_items_container.arrangeWidget()
    
    def _refresh_page_items(self):
        """刷新页面项列表（用于重置时重建）"""
        # 移除所有旧控件
        for item in self.page_items:
            self.page_items_container.removeWidget(item["row"])
            item["row"].hide()
            item["row"].deleteLater()
        self.page_items.clear()
        
        # 按新顺序重新创建并添加
        for page_data in self.sidebar_pages:
            item_row = self._create_page_item(page_data)
            self.page_items.append({"row": item_row, "data": page_data})
            self.page_items_container.addWidget(item_row)
        
        self.page_items_container.adjustSize()
    
    def _save_sidebar_settings(self):
        """保存侧边栏设置"""
        self.config.set('sidebar_pages', self.sidebar_pages)
        self._show_message("侧边栏设置已保存，重启应用后生效")
    
    def _reset_sidebar_settings(self):
        """重置侧边栏设置（带二次确认）"""
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "确认恢复默认",
            "确定要恢复侧边栏的默认设置吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
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
        self.sidebar_pages = default_pages
        self.config.set('sidebar_pages', self.sidebar_pages)
        self._refresh_page_items()
        self._show_message("已恢复默认侧边栏设置，重启应用后生效")
    
    def _create_apk_panel(self):
        """创建APK设置面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("APK分析工具配置")
        
        # aapt路径
        aapt_row = SiDenseHContainer(self)
        aapt_row.setFixedHeight(36)
        aapt_row.setSpacing(8)
        
        aapt_label = SiLabel(self)
        aapt_label.setText("aapt路径:")
        aapt_label.setFixedWidth(70)
        
        self.aapt_edit = SiLineEdit(self)
        self.aapt_edit.setFixedHeight(32)
        self.aapt_edit.lineEdit().setPlaceholderText("自动检测或手动指定aapt路径")
        self.aapt_edit.lineEdit().setText(self.config.get('apk_settings.aapt_path', ''))
        
        browse_btn = SiPushButton(self)
        browse_btn.resize(80, 32)
        browse_btn.attachment().setText("浏览")
        browse_btn.clicked.connect(self._browse_aapt)
        
        aapt_row.addWidget(aapt_label)
        aapt_row.addWidget(self.aapt_edit)
        aapt_row.addWidget(browse_btn, "right")
        
        # 选项
        option_row = SiDenseHContainer(self)
        option_row.setFixedHeight(36)
        option_row.setSpacing(16)
        
        extract_icon_label = SiLabel(self)
        extract_icon_label.setText("自动提取图标:")
        
        self.extract_icon_switch = SiSwitch(self)
        self.extract_icon_switch.setFixedHeight(32)
        self.extract_icon_switch.setChecked(self.config.get('apk_settings.auto_extract_icon', True))
        
        option_row.addWidget(extract_icon_label)
        option_row.addWidget(self.extract_icon_switch)
        
        # 保存按钮
        save_btn = SiPushButton(self)
        save_btn.resize(100, 32)
        save_btn.setUseTransition(True)
        save_btn.attachment().setText("保存设置")
        save_btn.clicked.connect(self._save_apk_settings)
        
        panel.body().addWidget(aapt_row)
        panel.body().addWidget(option_row)
        panel.body().addWidget(save_btn)
        panel.adjustSize()
        
        return panel
    
    def _create_network_panel(self):
        """创建网络设置面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("网络请求配置")
        
        # 超时设置
        timeout_row = SiDenseHContainer(self)
        timeout_row.setFixedHeight(36)
        timeout_row.setSpacing(8)
        
        timeout_label = SiLabel(self)
        timeout_label.setText("请求超时(秒):")
        timeout_label.setFixedWidth(100)
        
        self.timeout_edit = SiLineEdit(self)
        self.timeout_edit.setFixedSize(100, 32)
        self.timeout_edit.lineEdit().setText(str(self.config.get('network_settings.timeout', 30)))
        
        ssl_label = SiLabel(self)
        ssl_label.setText("验证SSL:")
        
        self.verify_ssl_switch = SiSwitch(self)
        self.verify_ssl_switch.setFixedHeight(32)
        self.verify_ssl_switch.setChecked(self.config.get('network_settings.verify_ssl', False))
        
        timeout_row.addWidget(timeout_label)
        timeout_row.addWidget(self.timeout_edit)
        timeout_row.addWidget(ssl_label)
        timeout_row.addWidget(self.verify_ssl_switch)
        
        # 保存按钮
        save_btn = SiPushButton(self)
        save_btn.resize(100, 32)
        save_btn.setUseTransition(True)
        save_btn.attachment().setText("保存设置")
        save_btn.clicked.connect(self._save_network_settings)
        
        panel.body().addWidget(timeout_row)
        panel.body().addWidget(save_btn)
        panel.adjustSize()
        
        return panel
    
    def _create_data_panel(self):
        """创建数据管理面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("数据与缓存管理")
        
        action_row = SiDenseHContainer(self)
        action_row.setFixedHeight(36)
        action_row.setSpacing(8)
        
        clear_recent_btn = SiPushButton(self)
        clear_recent_btn.resize(120, 32)
        clear_recent_btn.attachment().setText("清空最近文件")
        clear_recent_btn.clicked.connect(self._clear_recent_files)
        
        export_btn = SiPushButton(self)
        export_btn.resize(120, 32)
        export_btn.attachment().setText("导出Wiki")
        export_btn.clicked.connect(self._export_wiki)
        
        reset_btn = SiPushButton(self)
        reset_btn.resize(120, 32)
        reset_btn.attachment().setText("重置所有设置")
        reset_btn.clicked.connect(self._reset_settings)
        
        action_row.addWidget(clear_recent_btn)
        action_row.addWidget(export_btn)
        action_row.addWidget(reset_btn)
        
        # 配置文件位置
        config_path_label = SiLabel(self)
        config_path_label.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        config_path_label.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_C']};")
        config_path_label.setText(f"配置目录: {self.config.config_dir}")
        
        panel.body().addWidget(action_row)
        panel.body().addWidget(config_path_label)
        panel.adjustSize()
        
        return panel
    
    # 功能方法
    def _browse_aapt(self):
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择aapt可执行文件", "", "可执行文件 (*.exe);;所有文件 (*)"
        )
        if file_path:
            self.aapt_edit.lineEdit().setText(file_path)
    
    def _save_apk_settings(self):
        self.config.set('apk_settings.aapt_path', self.aapt_edit.lineEdit().text())
        self.config.set('apk_settings.auto_extract_icon', self.extract_icon_switch.isChecked())
        self._show_message("APK设置已保存")
    
    def _save_network_settings(self):
        try:
            timeout = int(self.timeout_edit.lineEdit().text())
            self.config.set('network_settings.timeout', timeout)
        except ValueError:
            pass
        self.config.set('network_settings.verify_ssl', self.verify_ssl_switch.isChecked())
        self._show_message("网络设置已保存")
    
    def _clear_recent_files(self):
        self.config.set('recent_files', [])
        self._show_message("最近文件已清空")
    
    def _export_wiki(self):
        from PyQt5.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if dir_path:
            import shutil
            import os
            wiki_src = self.config.wiki_dir
            wiki_dst = os.path.join(dir_path, 'wiki_export')
            if os.path.exists(wiki_src):
                shutil.copytree(wiki_src, wiki_dst, dirs_exist_ok=True)
                self._show_message(f"Wiki已导出到: {wiki_dst}")
            else:
                self._show_message("没有找到Wiki内容", msg_type=2)
    
    def _reset_settings(self):
        self.config.config = ConfigManager.DEFAULT_CONFIG.copy()
        self.config.save()
        self._show_message("所有设置已重置，请重启应用")
    
    def _show_message(self, text: str, msg_type: int = 1):
        try:
            window = self.window()
            if hasattr(window, 'LayerRightMessageSidebar'):
                window.LayerRightMessageSidebar().send(text=text, msg_type=msg_type, fold_after=2000)
        except Exception:
            pass
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = event.size().width()
        if w > 200:
            self.body_area.setFixedWidth(w)
            self.titled_widget_group.setFixedWidth(min(w - 128, 1200))
