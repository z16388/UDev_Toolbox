#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件工具页面
"""

import os
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QApplication

from siui.components.option_card import SiOptionCardPlane
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

from src.core.file_utils import FileUtils


class HashCalculateThread(QThread):
    """哈希计算线程"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            hashes = FileUtils.calculate_all_hashes(self.file_path)
            self.finished.emit(hashes)
        except Exception as e:
            self.error.emit(str(e))


class FileToolsPage(SiPage):
    """文件工具页面"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.hash_thread = None
        
        self.scroll_container = SiTitledWidgetGroup(self)
        
        self.body_area = SiLabel(self)
        self.body_area.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.body_area.resized.connect(lambda _: self.scroll_container.adjustSize())
        
        self.titled_widget_group = SiTitledWidgetGroup(self.body_area)
        self.titled_widget_group.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.titled_widget_group.resized.connect(lambda size: self.body_area.setFixedHeight(size[1]))
        self.titled_widget_group.move(64, 32)
        
        self.titled_widget_group.setSpacing(16)
        
        # 文件哈希计算
        self.titled_widget_group.addTitle("文件哈希计算")
        self.titled_widget_group.addWidget(self._create_hash_panel())
        
        # 多文件比较
        self.titled_widget_group.addTitle("多文件哈希比较")
        self.titled_widget_group.addWidget(self._create_compare_panel())
        
        # 文件搜索
        self.titled_widget_group.addTitle("文件搜索")
        self.titled_widget_group.addWidget(self._create_search_panel())
        
        # 批量重命名
        self.titled_widget_group.addTitle("批量重命名")
        self.titled_widget_group.addWidget(self._create_rename_panel())
        
        # 文本对比
        self.titled_widget_group.addTitle("文本对比")
        self.titled_widget_group.addWidget(self._create_diff_panel())
        
        self.titled_widget_group.addPlaceholder(64)
        
        self.body_area.setFixedHeight(self.titled_widget_group.height())
        self.scroll_container.addWidget(self.body_area)
        
        self.setAttachment(self.scroll_container)
    
    def _create_hash_panel(self):
        """创建哈希计算面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("计算文件的MD5/SHA1/SHA256/SHA512")
        
        file_row = SiDenseHContainer(self)
        file_row.setFixedHeight(36)
        file_row.setSpacing(8)
        
        self.hash_file_edit = SiLineEdit(self)
        self.hash_file_edit.setFixedHeight(32)
        self.hash_file_edit.lineEdit().setPlaceholderText("选择或拖入文件...")
        
        browse_btn = SiPushButton(self)
        browse_btn.resize(80, 32)
        browse_btn.attachment().setText("浏览")
        browse_btn.clicked.connect(self._browse_hash_file)
        
        self.calc_hash_btn = SiPushButton(self)
        self.calc_hash_btn.resize(80, 32)
        self.calc_hash_btn.setUseTransition(True)
        self.calc_hash_btn.attachment().setText("计算")
        self.calc_hash_btn.clicked.connect(self._calculate_hash)
        
        file_row.addWidget(self.hash_file_edit)
        file_row.addWidget(browse_btn, "right")
        file_row.addWidget(self.calc_hash_btn, "right")
        
        # 结果显示
        self.hash_result = SiLabel(self)
        self.hash_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.hash_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']}; font-family: Consolas, monospace;")
        self.hash_result.setText("请选择文件进行计算")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(file_row)
        panel.body().addWidget(self.hash_result)
        panel.adjustSize()
        
        return panel
    
    def _create_compare_panel(self):
        """创建多文件比较面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("比较多个文件的哈希值")
        
        action_row = SiDenseHContainer(self)
        action_row.setFixedHeight(36)
        action_row.setSpacing(8)
        
        add_files_btn = SiPushButton(self)
        add_files_btn.resize(100, 32)
        add_files_btn.attachment().setText("选择文件")
        add_files_btn.clicked.connect(self._add_compare_files)
        
        clear_btn = SiPushButton(self)
        clear_btn.resize(80, 32)
        clear_btn.attachment().setText("清空")
        clear_btn.clicked.connect(self._clear_compare)
        
        action_row.addWidget(add_files_btn)
        action_row.addWidget(clear_btn)
        
        self.compare_result = SiLabel(self)
        self.compare_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.compare_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']}; font-family: Consolas, monospace;")
        self.compare_result.setText("选择多个文件进行比较")
        
        panel.body().addWidget(action_row)
        panel.body().addWidget(self.compare_result)
        panel.adjustSize()
        
        return panel
    
    def _create_search_panel(self):
        """创建文件搜索面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("在目录中搜索文件")
        
        dir_row = SiDenseHContainer(self)
        dir_row.setFixedHeight(36)
        dir_row.setSpacing(8)
        
        dir_label = SiLabel(self)
        dir_label.setText("目录:")
        dir_label.setFixedWidth(50)
        
        self.search_dir_edit = SiLineEdit(self)
        self.search_dir_edit.setFixedHeight(32)
        self.search_dir_edit.lineEdit().setPlaceholderText("选择搜索目录...")
        
        browse_dir_btn = SiPushButton(self)
        browse_dir_btn.resize(80, 32)
        browse_dir_btn.attachment().setText("浏览")
        browse_dir_btn.clicked.connect(self._browse_search_dir)
        
        dir_row.addWidget(dir_label)
        dir_row.addWidget(self.search_dir_edit)
        dir_row.addWidget(browse_dir_btn, "right")
        
        pattern_row = SiDenseHContainer(self)
        pattern_row.setFixedHeight(36)
        pattern_row.setSpacing(8)
        
        pattern_label = SiLabel(self)
        pattern_label.setText("模式:")
        pattern_label.setFixedWidth(50)
        
        self.search_pattern_edit = SiLineEdit(self)
        self.search_pattern_edit.setFixedHeight(32)
        self.search_pattern_edit.lineEdit().setPlaceholderText("文件名模式 (支持正则)")
        
        self.search_regex_switch = SiSwitch(self)
        self.search_regex_switch.setFixedHeight(32)
        regex_label = SiLabel(self)
        regex_label.setText("正则")
        
        search_btn = SiPushButton(self)
        search_btn.resize(80, 32)
        search_btn.setUseTransition(True)
        search_btn.attachment().setText("搜索")
        search_btn.clicked.connect(self._search_files)
        
        pattern_row.addWidget(pattern_label)
        pattern_row.addWidget(self.search_pattern_edit)
        pattern_row.addWidget(regex_label, "right")
        pattern_row.addWidget(self.search_regex_switch, "right")
        pattern_row.addWidget(search_btn, "right")
        
        self.search_result = SiLabel(self)
        self.search_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.search_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']};")
        self.search_result.setText("输入搜索条件后点击搜索")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(dir_row)
        panel.body().addWidget(pattern_row)
        panel.body().addWidget(self.search_result)
        panel.adjustSize()
        
        return panel
    
    def _create_rename_panel(self):
        """创建批量重命名面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("批量重命名文件")
        
        dir_row = SiDenseHContainer(self)
        dir_row.setFixedHeight(36)
        dir_row.setSpacing(8)
        
        self.rename_dir_edit = SiLineEdit(self)
        self.rename_dir_edit.setFixedHeight(32)
        self.rename_dir_edit.lineEdit().setPlaceholderText("选择目录...")
        
        browse_btn = SiPushButton(self)
        browse_btn.resize(80, 32)
        browse_btn.attachment().setText("浏览")
        browse_btn.clicked.connect(self._browse_rename_dir)
        
        dir_row.addWidget(self.rename_dir_edit)
        dir_row.addWidget(browse_btn, "right")
        
        pattern_row = SiDenseHContainer(self)
        pattern_row.setFixedHeight(36)
        pattern_row.setSpacing(8)
        
        find_label = SiLabel(self)
        find_label.setText("查找:")
        find_label.setFixedWidth(50)
        
        self.rename_find_edit = SiLineEdit(self)
        self.rename_find_edit.setFixedHeight(32)
        self.rename_find_edit.lineEdit().setPlaceholderText("要替换的文本")
        
        replace_label = SiLabel(self)
        replace_label.setText("替换:")
        replace_label.setFixedWidth(50)
        
        self.rename_replace_edit = SiLineEdit(self)
        self.rename_replace_edit.setFixedHeight(32)
        self.rename_replace_edit.lineEdit().setPlaceholderText("替换为")
        
        pattern_row.addWidget(find_label)
        pattern_row.addWidget(self.rename_find_edit)
        pattern_row.addWidget(replace_label)
        pattern_row.addWidget(self.rename_replace_edit)
        
        action_row = SiDenseHContainer(self)
        action_row.setFixedHeight(36)
        action_row.setSpacing(8)
        
        preview_btn = SiPushButton(self)
        preview_btn.resize(80, 32)
        preview_btn.attachment().setText("预览")
        preview_btn.clicked.connect(self._preview_rename)
        
        execute_btn = SiPushButton(self)
        execute_btn.resize(80, 32)
        execute_btn.setUseTransition(True)
        execute_btn.attachment().setText("执行")
        execute_btn.clicked.connect(self._execute_rename)
        
        action_row.addWidget(preview_btn)
        action_row.addWidget(execute_btn)
        
        self.rename_result = SiLabel(self)
        self.rename_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.rename_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']};")
        self.rename_result.setText("设置重命名规则后点击预览")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(dir_row)
        panel.body().addWidget(pattern_row)
        panel.body().addWidget(action_row)
        panel.body().addWidget(self.rename_result)
        panel.adjustSize()
        
        return panel
    
    def _create_diff_panel(self):
        """创建文本对比面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("文本/文件对比 (支持多文件)")
        
        # 文件列表容器
        self.diff_files_list = []
        self.diff_files_display = SiLabel(self)
        self.diff_files_display.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.diff_files_display.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_B']}; padding: 8px;")
        self.diff_files_display.setText("尚未选择文件")
        
        action_row = SiDenseHContainer(self)
        action_row.setFixedHeight(40)
        action_row.setSpacing(8)
        
        add_files_btn = SiPushButton(self)
        add_files_btn.resize(120, 36)
        add_files_btn.attachment().setText("选择文件...")
        add_files_btn.clicked.connect(self._add_diff_files)
        
        clear_files_btn = SiPushButton(self)
        clear_files_btn.resize(100, 36)
        clear_files_btn.attachment().setText("清空列表")
        clear_files_btn.clicked.connect(self._clear_diff_files)
        
        diff_btn = SiPushButton(self)
        diff_btn.resize(100, 36)
        diff_btn.setUseTransition(True)
        diff_btn.attachment().setText("开始对比")
        diff_btn.clicked.connect(self._compare_files)
        
        action_row.addWidget(add_files_btn)
        action_row.addWidget(clear_files_btn)
        action_row.addWidget(diff_btn)
        
        self.diff_result = SiLabel(self)
        self.diff_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.diff_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']}; font-family: Consolas, monospace;")
        self.diff_result.setText("选择2个或多个文件进行对比")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(self.diff_files_display)
        panel.body().addWidget(action_row)
        panel.body().addWidget(self.diff_result)
        panel.adjustSize()
        
        return panel
    
    # 功能方法
    def _browse_hash_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_path:
            self.hash_file_edit.lineEdit().setText(file_path)
    
    def _calculate_hash(self):
        file_path = self.hash_file_edit.lineEdit().text().strip()
        if not file_path or not os.path.exists(file_path):
            self._show_message("请选择有效的文件", msg_type=2)
            return
        
        self.calc_hash_btn.setEnabled(False)
        self.calc_hash_btn.attachment().setText("计算中...")
        
        self.hash_thread = HashCalculateThread(file_path)
        self.hash_thread.finished.connect(self._on_hash_finished)
        self.hash_thread.error.connect(self._on_hash_error)
        self.hash_thread.start()
    
    def _on_hash_finished(self, hashes: dict):
        result = f"文件: {self.hash_file_edit.lineEdit().text()}\n\n"
        result += f"MD5:    {hashes['md5']}\n"
        result += f"SHA1:   {hashes['sha1']}\n"
        result += f"SHA256: {hashes['sha256']}\n"
        result += f"SHA512: {hashes['sha512']}"
        self.hash_result.setText(result)
        
        self.calc_hash_btn.setEnabled(True)
        self.calc_hash_btn.attachment().setText("计算")
    
    def _on_hash_error(self, error: str):
        self.hash_result.setText(f"错误: {error}")
        self.calc_hash_btn.setEnabled(True)
        self.calc_hash_btn.attachment().setText("计算")
    
    def _add_compare_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择多个文件")
        if files:
            hashes = FileUtils.compare_multiple_files(files)
            result = "文件哈希对比:\n\n"
            for path, hash_val in hashes.items():
                result += f"{os.path.basename(path)}\n  MD5: {hash_val}\n\n"
            
            # 检查是否有相同的哈希
            hash_values = list(hashes.values())
            if len(hash_values) == len(set(hash_values)):
                result += "结果: 所有文件都不相同"
            else:
                result += "结果: 存在相同的文件"
            
            self.compare_result.setText(result)
    
    def _clear_compare(self):
        self.compare_result.setText("选择多个文件进行比较")
    
    def _browse_search_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择搜索目录")
        if dir_path:
            self.search_dir_edit.lineEdit().setText(dir_path)
    
    def _search_files(self):
        dir_path = self.search_dir_edit.lineEdit().text().strip()
        pattern = self.search_pattern_edit.lineEdit().text().strip()
        
        if not dir_path or not pattern:
            self._show_message("请输入目录和搜索模式", msg_type=2)
            return
        
        use_regex = self.search_regex_switch.isChecked()
        results = FileUtils.search_files(dir_path, pattern, use_regex=use_regex)
        
        if results:
            result_text = f"找到 {len(results)} 个文件:\n\n"
            for path in results[:50]:
                result_text += f"• {path}\n"
            if len(results) > 50:
                result_text += f"\n... 还有 {len(results) - 50} 个文件"
            self.search_result.setText(result_text)
        else:
            self.search_result.setText("没有找到匹配的文件")
    
    def _browse_rename_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择目录")
        if dir_path:
            self.rename_dir_edit.lineEdit().setText(dir_path)
    
    def _preview_rename(self):
        dir_path = self.rename_dir_edit.lineEdit().text().strip()
        find = self.rename_find_edit.lineEdit().text()
        replace = self.rename_replace_edit.lineEdit().text()
        
        if not dir_path or not find:
            self._show_message("请输入目录和查找文本", msg_type=2)
            return
        
        changes = FileUtils.batch_rename(dir_path, find, replace, preview=True)
        
        if changes:
            result_text = f"预览 - 将重命名 {len(changes)} 个文件:\n\n"
            for old, new in changes[:20]:
                result_text += f"• {old} → {new}\n"
            if len(changes) > 20:
                result_text += f"\n... 还有 {len(changes) - 20} 个文件"
            self.rename_result.setText(result_text)
        else:
            self.rename_result.setText("没有找到需要重命名的文件")
    
    def _execute_rename(self):
        dir_path = self.rename_dir_edit.lineEdit().text().strip()
        find = self.rename_find_edit.lineEdit().text()
        replace = self.rename_replace_edit.lineEdit().text()
        
        if not dir_path or not find:
            self._show_message("请输入目录和查找文本", msg_type=2)
            return
        
        changes = FileUtils.batch_rename(dir_path, find, replace, preview=False)
        self._show_message(f"已重命名 {len(changes)} 个文件", msg_type=1)
        self.rename_result.setText(f"已完成重命名 {len(changes)} 个文件")
    
    def _add_diff_files(self):
        """添加要对比的文件"""
        files, _ = QFileDialog.getOpenFileNames(self, "选择要对比的文件")
        if files:
            self.diff_files_list.extend(files)
            self._update_diff_files_display()
    
    def _clear_diff_files(self):
        """清空文件列表"""
        self.diff_files_list.clear()
        self._update_diff_files_display()
        self.diff_result.setText("选择2个或多个文件进行对比")
    
    def _update_diff_files_display(self):
        """更新文件列表显示"""
        if not self.diff_files_list:
            self.diff_files_display.setText("尚未选择文件")
        else:
            display_text = f"已选择 {len(self.diff_files_list)} 个文件:\n"
            for i, file in enumerate(self.diff_files_list, 1):
                display_text += f"{i}. {os.path.basename(file)}\n"
            self.diff_files_display.setText(display_text)
    
    def _compare_files(self):
        """对比文件"""
        if len(self.diff_files_list) < 2:
            self._show_message("请至少选择2个文件", msg_type=2)
            return
        
        try:
            if len(self.diff_files_list) == 2:
                # 两个文件 - 显示详细差异
                diff = FileUtils.file_diff(self.diff_files_list[0], self.diff_files_list[1])
                if diff:
                    result_text = f"对比 {os.path.basename(self.diff_files_list[0])} 和 {os.path.basename(self.diff_files_list[1])}:\n\n"
                    result_text += diff[:5000]
                    if len(diff) > 5000:
                        result_text += "\n\n... (结果已截断，仅显示前5000字符)"
                    self.diff_result.setText(result_text)
                else:
                    self.diff_result.setText("两个文件内容相同")
            else:
                # 多个文件 - 显示哈希对比
                result_text = f"对比 {len(self.diff_files_list)} 个文件的哈希值:\n\n"
                hashes = {}
                for file in self.diff_files_list:
                    hash_result = FileUtils.calculate_all_hashes(file)
                    hashes[file] = hash_result['md5']
                    result_text += f"{os.path.basename(file)}\n  MD5: {hash_result['md5']}\n\n"
                
                # 检查是否有相同的文件
                hash_values = list(hashes.values())
                unique_hashes = set(hash_values)
                
                if len(unique_hashes) == len(hash_values):
                    result_text += "✓ 结果: 所有文件都不相同"
                else:
                    result_text += "⚠ 结果: 存在相同的文件\n\n"
                    # 找出相同的文件组
                    from collections import defaultdict
                    hash_groups = defaultdict(list)
                    for file, hash_val in hashes.items():
                        hash_groups[hash_val].append(file)
                    
                    for hash_val, files in hash_groups.items():
                        if len(files) > 1:
                            result_text += f"相同组 (MD5: {hash_val}):\n"
                            for file in files:
                                result_text += f"  - {os.path.basename(file)}\n"
                            result_text += "\n"
                
                self.diff_result.setText(result_text)
        except Exception as e:
            self.diff_result.setText(f"对比失败: {e}")
    
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
