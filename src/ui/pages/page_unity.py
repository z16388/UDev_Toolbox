#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unity专用工具页面
"""

import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog

from siui.components.option_card import SiOptionCardPlane
from siui.components.page import SiPage
from siui.components.titled_widget_group import SiTitledWidgetGroup
from siui.components.widgets import (
    SiDenseHContainer,
    SiLabel,
    SiLineEdit,
    SiPushButton,
)
from siui.core import Si, SiGlobal

from src.core.unity_utils import UnityUtils
from src.core.file_utils import FileUtils


class UnityToolsPage(SiPage):
    """Unity专用工具页面"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.scroll_container = SiTitledWidgetGroup(self)
        
        self.body_area = SiLabel(self)
        self.body_area.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.body_area.resized.connect(lambda _: self.scroll_container.adjustSize())
        
        self.titled_widget_group = SiTitledWidgetGroup(self.body_area)
        self.titled_widget_group.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.titled_widget_group.resized.connect(lambda size: self.body_area.setFixedHeight(size[1]))
        self.titled_widget_group.move(64, 32)
        
        self.titled_widget_group.setSpacing(16)
        
        # PlayerPrefs查看
        self.titled_widget_group.addTitle("PlayerPrefs 查看")
        self.titled_widget_group.addWidget(self._create_playerprefs_panel())
        
        # GUID查找
        self.titled_widget_group.addTitle("GUID 资源查找")
        self.titled_widget_group.addWidget(self._create_guid_panel())
        
        # AssetBundle分析
        self.titled_widget_group.addTitle("AssetBundle 分析")
        self.titled_widget_group.addWidget(self._create_assetbundle_panel())
        
        # 资源体积分析
        self.titled_widget_group.addTitle("项目资源体积分析")
        self.titled_widget_group.addWidget(self._create_asset_size_panel())
        
        # Unity日志解析
        self.titled_widget_group.addTitle("Unity 日志解析")
        self.titled_widget_group.addWidget(self._create_log_panel())
        
        self.titled_widget_group.addPlaceholder(64)
        
        self.body_area.setFixedHeight(self.titled_widget_group.height())
        self.scroll_container.addWidget(self.body_area)
        
        self.setAttachment(self.scroll_container)
    
    def _create_playerprefs_panel(self):
        """创建PlayerPrefs面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("查看和搜索PlayerPrefs文件")
        
        search_row = SiDenseHContainer(self)
        search_row.setFixedHeight(36)
        search_row.setSpacing(8)
        
        company_label = SiLabel(self)
        company_label.setText("公司名:")
        company_label.setFixedWidth(60)
        
        self.company_edit = SiLineEdit(self)
        self.company_edit.setFixedSize(150, 32)
        self.company_edit.lineEdit().setPlaceholderText("可选")
        
        product_label = SiLabel(self)
        product_label.setText("产品名:")
        product_label.setFixedWidth(60)
        
        self.product_edit = SiLineEdit(self)
        self.product_edit.setFixedSize(150, 32)
        self.product_edit.lineEdit().setPlaceholderText("可选")
        
        search_btn = SiPushButton(self)
        search_btn.resize(80, 32)
        search_btn.setUseTransition(True)
        search_btn.attachment().setText("搜索")
        search_btn.clicked.connect(self._search_playerprefs)
        
        search_row.addWidget(company_label)
        search_row.addWidget(self.company_edit)
        search_row.addWidget(product_label)
        search_row.addWidget(self.product_edit)
        search_row.addWidget(search_btn)
        
        self.prefs_result = SiLabel(self)
        self.prefs_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.prefs_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']};")
        self.prefs_result.setText("点击搜索查找PlayerPrefs文件 (默认路径: %USERPROFILE%/AppData/LocalLow)")
        
        panel.body().addWidget(search_row)
        panel.body().addWidget(self.prefs_result)
        panel.adjustSize()
        
        return panel
    
    def _create_guid_panel(self):
        """创建GUID查找面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("在Unity项目中查找GUID对应的资源")
        
        project_row = SiDenseHContainer(self)
        project_row.setFixedHeight(36)
        project_row.setSpacing(8)
        
        self.project_path_edit = SiLineEdit(self)
        self.project_path_edit.setFixedHeight(32)
        self.project_path_edit.lineEdit().setPlaceholderText("选择Unity项目目录...")
        
        browse_btn = SiPushButton(self)
        browse_btn.resize(80, 32)
        browse_btn.attachment().setText("浏览")
        browse_btn.clicked.connect(self._browse_project)
        
        project_row.addWidget(self.project_path_edit)
        project_row.addWidget(browse_btn, "right")
        
        guid_row = SiDenseHContainer(self)
        guid_row.setFixedHeight(36)
        guid_row.setSpacing(8)
        
        guid_label = SiLabel(self)
        guid_label.setText("GUID:")
        guid_label.setFixedWidth(50)
        
        self.guid_edit = SiLineEdit(self)
        self.guid_edit.setFixedHeight(32)
        self.guid_edit.lineEdit().setPlaceholderText("输入要查找的GUID...")
        
        find_btn = SiPushButton(self)
        find_btn.resize(80, 32)
        find_btn.setUseTransition(True)
        find_btn.attachment().setText("查找")
        find_btn.clicked.connect(self._find_guid)
        
        find_refs_btn = SiPushButton(self)
        find_refs_btn.resize(100, 32)
        find_refs_btn.attachment().setText("查找引用")
        find_refs_btn.clicked.connect(self._find_guid_refs)
        
        guid_row.addWidget(guid_label)
        guid_row.addWidget(self.guid_edit)
        guid_row.addWidget(find_btn, "right")
        guid_row.addWidget(find_refs_btn, "right")
        
        self.guid_result = SiLabel(self)
        self.guid_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.guid_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']};")
        self.guid_result.setText("输入GUID后点击查找")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(project_row)
        panel.body().addWidget(guid_row)
        panel.body().addWidget(self.guid_result)
        panel.adjustSize()
        
        return panel
    
    def _create_assetbundle_panel(self):
        """创建AssetBundle分析面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("分析AssetBundle文件信息")
        
        file_row = SiDenseHContainer(self)
        file_row.setFixedHeight(36)
        file_row.setSpacing(8)
        
        self.ab_path_edit = SiLineEdit(self)
        self.ab_path_edit.setFixedHeight(32)
        self.ab_path_edit.lineEdit().setPlaceholderText("选择AssetBundle文件...")
        
        browse_btn = SiPushButton(self)
        browse_btn.resize(80, 32)
        browse_btn.attachment().setText("浏览")
        browse_btn.clicked.connect(self._browse_assetbundle)
        
        analyze_btn = SiPushButton(self)
        analyze_btn.resize(80, 32)
        analyze_btn.setUseTransition(True)
        analyze_btn.attachment().setText("分析")
        analyze_btn.clicked.connect(self._analyze_assetbundle)
        
        file_row.addWidget(self.ab_path_edit)
        file_row.addWidget(browse_btn, "right")
        file_row.addWidget(analyze_btn, "right")
        
        self.ab_result = SiLabel(self)
        self.ab_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.ab_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']}; font-family: Consolas, monospace;")
        self.ab_result.setText("选择AssetBundle文件进行分析")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(file_row)
        panel.body().addWidget(self.ab_result)
        panel.adjustSize()
        
        return panel
    
    def _create_asset_size_panel(self):
        """创建资源体积分析面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("分析Unity项目资源体积排行")
        
        dir_row = SiDenseHContainer(self)
        dir_row.setFixedHeight(36)
        dir_row.setSpacing(8)
        
        self.asset_project_edit = SiLineEdit(self)
        self.asset_project_edit.setFixedHeight(32)
        self.asset_project_edit.lineEdit().setPlaceholderText("选择Unity项目目录...")
        
        browse_btn = SiPushButton(self)
        browse_btn.resize(80, 32)
        browse_btn.attachment().setText("浏览")
        browse_btn.clicked.connect(self._browse_asset_project)
        
        analyze_btn = SiPushButton(self)
        analyze_btn.resize(80, 32)
        analyze_btn.setUseTransition(True)
        analyze_btn.attachment().setText("分析")
        analyze_btn.clicked.connect(self._analyze_asset_size)
        
        dir_row.addWidget(self.asset_project_edit)
        dir_row.addWidget(browse_btn, "right")
        dir_row.addWidget(analyze_btn, "right")
        
        self.asset_size_result = SiLabel(self)
        self.asset_size_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.asset_size_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']};")
        self.asset_size_result.setText("选择项目目录分析资源体积")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(dir_row)
        panel.body().addWidget(self.asset_size_result)
        panel.adjustSize()
        
        return panel
    
    def _create_log_panel(self):
        """创建日志解析面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("解析Unity日志文件")
        
        file_row = SiDenseHContainer(self)
        file_row.setFixedHeight(36)
        file_row.setSpacing(8)
        
        self.log_path_edit = SiLineEdit(self)
        self.log_path_edit.setFixedHeight(32)
        self.log_path_edit.lineEdit().setPlaceholderText("选择Unity日志文件...")
        
        browse_btn = SiPushButton(self)
        browse_btn.resize(80, 32)
        browse_btn.attachment().setText("浏览")
        browse_btn.clicked.connect(self._browse_log)
        
        parse_btn = SiPushButton(self)
        parse_btn.resize(80, 32)
        parse_btn.setUseTransition(True)
        parse_btn.attachment().setText("解析")
        parse_btn.clicked.connect(self._parse_log)
        
        file_row.addWidget(self.log_path_edit)
        file_row.addWidget(browse_btn, "right")
        file_row.addWidget(parse_btn, "right")
        
        self.log_result = SiLabel(self)
        self.log_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.log_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']};")
        self.log_result.setText("选择日志文件进行解析")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(file_row)
        panel.body().addWidget(self.log_result)
        panel.adjustSize()
        
        return panel
    
    # 功能方法
    def _search_playerprefs(self):
        company = self.company_edit.lineEdit().text().strip() or None
        product = self.product_edit.lineEdit().text().strip() or None
        
        files = UnityUtils.find_playerprefs_files(company, product)
        
        if files:
            result = f"找到 {len(files)} 个PlayerPrefs文件:\n\n"
            for f in files[:20]:
                result += f"• {f}\n"
            self.prefs_result.setText(result)
        else:
            self.prefs_result.setText("未找到PlayerPrefs文件")
    
    def _browse_project(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择Unity项目目录")
        if dir_path:
            self.project_path_edit.lineEdit().setText(dir_path)
    
    def _find_guid(self):
        project = self.project_path_edit.lineEdit().text().strip()
        guid = self.guid_edit.lineEdit().text().strip()
        
        if not project or not guid:
            self._show_message("请输入项目路径和GUID", msg_type=2)
            return
        
        matches = UnityUtils.find_guid_in_project(project, guid)
        
        if matches:
            result = f"找到 {len(matches)} 个匹配:\n\n"
            for m in matches:
                result += f"• {m}\n"
            self.guid_result.setText(result)
        else:
            self.guid_result.setText("未找到匹配的资源")
    
    def _find_guid_refs(self):
        project = self.project_path_edit.lineEdit().text().strip()
        guid = self.guid_edit.lineEdit().text().strip()
        
        if not project or not guid:
            self._show_message("请输入项目路径和GUID", msg_type=2)
            return
        
        refs = UnityUtils.find_guid_references(project, guid)
        
        if refs:
            result = f"找到 {len(refs)} 个引用:\n\n"
            for ref in refs[:30]:
                result += f"• {ref['file']}:{ref['line']}\n"
            self.guid_result.setText(result)
        else:
            self.guid_result.setText("未找到引用")
    
    def _browse_assetbundle(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择AssetBundle文件")
        if file_path:
            self.ab_path_edit.lineEdit().setText(file_path)
    
    def _analyze_assetbundle(self):
        ab_path = self.ab_path_edit.lineEdit().text().strip()
        if not ab_path:
            self._show_message("请选择AssetBundle文件", msg_type=2)
            return
        
        info = UnityUtils.parse_assetbundle_header(ab_path)
        
        result = f"AssetBundle 信息:\n\n"
        result += f"文件: {info['path']}\n"
        result += f"大小: {FileUtils.format_size(info['size'])}\n"
        result += f"签名: {info['signature']}\n"
        result += f"版本: {info['version']}\n"
        result += f"Unity版本: {info['unity_version']}\n"
        result += f"已压缩: {'是' if info['compressed'] else '否'}\n"
        
        if 'error' in info:
            result += f"\n错误: {info['error']}"
        
        self.ab_result.setText(result)
    
    def _browse_asset_project(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择Unity项目目录")
        if dir_path:
            self.asset_project_edit.lineEdit().setText(dir_path)
    
    def _analyze_asset_size(self):
        project = self.asset_project_edit.lineEdit().text().strip()
        if not project:
            self._show_message("请选择项目目录", msg_type=2)
            return
        
        assets = UnityUtils.analyze_project_assets(project)
        
        if assets:
            result = f"资源体积排行 (前50):\n\n"
            for asset in assets[:50]:
                size_str = FileUtils.format_size(asset['size'])
                result += f"• [{asset['type']}] {asset['name']} - {size_str}\n"
            
            total = sum(a['size'] for a in assets)
            result += f"\n总计: {len(assets)} 个文件, {FileUtils.format_size(total)}"
            self.asset_size_result.setText(result)
        else:
            self.asset_size_result.setText("未找到资源文件")
    
    def _browse_log(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择日志文件", "", "日志文件 (*.log *.txt)")
        if file_path:
            self.log_path_edit.lineEdit().setText(file_path)
    
    def _parse_log(self):
        log_path = self.log_path_edit.lineEdit().text().strip()
        if not log_path:
            self._show_message("请选择日志文件", msg_type=2)
            return
        
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            entries = UnityUtils.parse_unity_log(content)
            
            # 统计
            error_count = sum(1 for e in entries if e['type'] == 'Error')
            warning_count = sum(1 for e in entries if e['type'] == 'Warning')
            
            result = f"日志解析结果:\n\n"
            result += f"总条目: {len(entries)}\n"
            result += f"错误: {error_count}\n"
            result += f"警告: {warning_count}\n\n"
            
            # 显示错误
            if error_count > 0:
                result += "错误信息:\n"
                for e in entries:
                    if e['type'] == 'Error':
                        result += f"• {e['message'][:100]}...\n"
                        if len([x for x in entries if x['type'] == 'Error']) > 10:
                            break
            
            self.log_result.setText(result)
        except Exception as e:
            self.log_result.setText(f"解析失败: {e}")
    
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
