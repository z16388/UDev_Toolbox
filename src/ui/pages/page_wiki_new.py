#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wiki 文档编辑器 - VS Code风格
"""

import os
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFileDialog, QApplication, QTextEdit, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QInputDialog, QMessageBox
from PyQt5.QtGui import QFont

from siui.components.page import SiPage
from siui.components.widgets import (
    SiDenseHContainer,
    SiDenseVContainer,
    SiLabel,
    SiPushButton,
)
from siui.core import SiGlobal

from src.core.config_manager import ConfigManager


class WikiPage(SiPage):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.config = ConfigManager()
        self.current_page_id = None
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(30000)  # 30秒自动保存
        
        # 主分割器 - 三栏布局
        self.main_splitter = QSplitter(Qt.Horizontal, self)
        self.main_splitter.setChildrenCollapsible(False)
        
        # 左侧文件列表
        self.left_panel = self._create_file_list_panel()
        
        # 中间编辑器
        self.editor_panel = self._create_editor_panel()
        
        # 右侧预览（默认隐藏，通过按钮切换）
        self.preview_panel = self._create_preview_panel()
        
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.editor_panel)
        self.main_splitter.addWidget(self.preview_panel)
        self.main_splitter.setSizes([250, 800, 400])
        
        self.setAttachment(self.main_splitter)
        self._refresh_file_list()
    
    def _create_file_list_panel(self):
        """创建文件列表面板"""
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 工具栏
        toolbar = SiDenseHContainer(panel)
        toolbar.setFixedHeight(40)
        toolbar.setSpacing(8)
        
        new_btn = SiPushButton(panel)
        new_btn.setFixedSize(80, 32)
        new_btn.attachment().setText("+ 新建")
        new_btn.clicked.connect(self._new_document)
        
        import_btn = SiPushButton(panel)
        import_btn.setFixedSize(80, 32)
        import_btn.attachment().setText("导入")
        import_btn.clicked.connect(self._import_markdown)
        
        toolbar.addWidget(new_btn)
        toolbar.addWidget(import_btn)
        
        # 文件列表
        self.file_list = QListWidget(panel)
        text_color = SiGlobal.siui.colors['TEXT_A']
        bg_color = SiGlobal.siui.colors['INTERFACE_BG_C']
        border_color = SiGlobal.siui.colors['INTERFACE_BG_D']
        self.file_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 4px;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background-color: {SiGlobal.siui.colors['INTERFACE_BG_D']};
            }}
            QListWidget::item:selected {{
                background-color: {SiGlobal.siui.colors['INTERFACE_BG_E']};
            }}
        """)
        self.file_list.itemClicked.connect(self._on_file_selected)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self._show_file_context_menu)
        
        layout.addWidget(toolbar)
        layout.addWidget(self.file_list)
        
        return panel
    
    def _create_editor_panel(self):
        """创建编辑器面板"""
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 工具栏
        toolbar = self._create_editor_toolbar()
        
        # 编辑器
        self.editor = QTextEdit(panel)
        self.editor.setPlaceholderText("在此输入 Markdown 内容...\n\n支持标准 Markdown 语法")
        
        text_color = SiGlobal.siui.colors['TEXT_A']
        bg_color = SiGlobal.siui.colors['INTERFACE_BG_C']
        border_color = SiGlobal.siui.colors['INTERFACE_BG_D']
        
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 16px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.6;
            }}
            QTextEdit:focus {{
                border-color: #0078D4;
            }}
        """)
        self.editor.textChanged.connect(self._on_text_changed)
        
        layout.addWidget(toolbar)
        layout.addWidget(self.editor)
        
        return panel
    
    def _create_editor_toolbar(self):
        """创建编辑器工具栏"""
        toolbar = SiDenseHContainer(self)
        toolbar.setFixedHeight(48)
        toolbar.setSpacing(12)
        
        # 文件名显示
        self.filename_label = SiLabel(self)
        self.filename_label.setText("未打开文档")
        text_color = SiGlobal.siui.colors['TEXT_B']
        self.filename_label.setStyleSheet(f"color: {text_color}; font-size: 13px;")
        
        # 保存按钮
        save_btn = SiPushButton(self)
        save_btn.resize(80, 36)
        save_btn.setUseTransition(True)
        save_btn.attachment().setText("💾 保存")
        save_btn.clicked.connect(self._save_content)
        
        # 导出按钮
        export_btn = SiPushButton(self)
        export_btn.resize(80, 36)
        export_btn.attachment().setText("📤 导出")
        export_btn.clicked.connect(self._export_markdown)
        
        # 预览切换按钮
        self.preview_toggle_btn = SiPushButton(self)
        self.preview_toggle_btn.resize(100, 36)
        self.preview_toggle_btn.attachment().setText("👁️ 预览")
        self.preview_toggle_btn.clicked.connect(self._toggle_preview)
        
        # Git同步按钮
        git_sync_btn = SiPushButton(self)
        git_sync_btn.resize(100, 36)
        git_sync_btn.attachment().setText("🔄 Git同步")
        git_sync_btn.clicked.connect(self._git_sync)
        
        toolbar.addWidget(self.filename_label)
        toolbar.addPlaceholder(12)
        toolbar.addWidget(save_btn, "right")
        toolbar.addWidget(export_btn, "right")
        toolbar.addWidget(self.preview_toggle_btn, "right")
        toolbar.addWidget(git_sync_btn, "right")
        
        return toolbar
    
    def _create_preview_panel(self):
        """创建预览面板"""
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 标题
        title_label = SiLabel(panel)
        title_label.setText("📖 Markdown 预览")
        title_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        text_color = SiGlobal.siui.colors['TEXT_A']
        title_label.setStyleSheet(f"color: {text_color}; padding: 8px;")
        
        # 预览区域
        self.preview_area = QTextEdit(panel)
        self.preview_area.setReadOnly(True)
        
        bg_color = SiGlobal.siui.colors['INTERFACE_BG_C']
        border_color = SiGlobal.siui.colors['INTERFACE_BG_D']
        
        self.preview_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 20px;
                font-family: 'Microsoft YaHei', sans-serif;
                font-size: 14px;
                line-height: 1.8;
            }}
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(self.preview_area)
        
        # 默认隐藏
        panel.setVisible(False)
        
        return panel
    
    def _refresh_file_list(self):
        """刷新文件列表"""
        self.file_list.clear()
        pages = self.config.get_wiki_pages()
        
        for page in pages:
            item = QListWidgetItem(f"📄 {page['title']}")
            item.setData(Qt.UserRole, page['id'])
            self.file_list.addItem(item)
    
    def _on_file_selected(self, item):
        """文件被选中"""
        page_id = item.data(Qt.UserRole)
        self._open_document(page_id)
    
    def _show_file_context_menu(self, pos):
        """显示文件右键菜单"""
        item = self.file_list.itemAt(pos)
        if not item:
            return
        
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        rename_action = menu.addAction("重命名")
        delete_action = menu.addAction("删除")
        
        action = menu.exec_(self.file_list.mapToGlobal(pos))
        page_id = item.data(Qt.UserRole)
        
        if action == rename_action:
            self._rename_document(page_id)
        elif action == delete_action:
            self._delete_document(page_id)
    
    def _new_document(self):
        """新建文档"""
        title, ok = QInputDialog.getText(self, "新建文档", "请输入文档标题:")
        if ok and title.strip():
            page_id = self.config.add_wiki_page(title.strip())
            self._refresh_file_list()
            self._show_message(f"已创建: {title}")
            self._open_document(page_id)
    
    def _open_document(self, page_id: str):
        """打开文档"""
        self.current_page_id = page_id
        content = self.config.get_wiki_content(page_id)
        
        self.editor.setPlainText(content)
        self._render_markdown(content)
        
        # 更新文件名显示
        pages = self.config.get_wiki_pages()
        for page in pages:
            if page['id'] == page_id:
                self.filename_label.setText(f"📝 {page['title']}")
                break
    
    def _rename_document(self, page_id: str):
        """重命名文档"""
        pages = self.config.get_wiki_pages()
        current_title = ""
        for page in pages:
            if page['id'] == page_id:
                current_title = page['title']
                break
        
        title, ok = QInputDialog.getText(self, "重命名", "请输入新标题:", text=current_title)
        if ok and title.strip():
            # 更新标题（需要在config_manager中添加方法）
            self._refresh_file_list()
            self._show_message("已重命名")
    
    def _delete_document(self, page_id: str):
        """删除文档"""
        reply = QMessageBox.question(self, "确认删除", "确定要删除这个文档吗？", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.config.delete_wiki_page(page_id)
            self._refresh_file_list()
            
            if self.current_page_id == page_id:
                self.current_page_id = None
                self.editor.clear()
                self.preview_area.clear()
                self.filename_label.setText("未打开文档")
            
            self._show_message("已删除")
    
    def _import_markdown(self):
        """导入Markdown文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "导入 Markdown 文件", "", "Markdown Files (*.md);;All Files (*.*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取标题
                title = os.path.splitext(os.path.basename(file_path))[0]
                lines = content.split('\n')
                if lines and lines[0].startswith('# '):
                    title = lines[0][2:].strip()
                
                page_id = self.config.add_wiki_page(title)
                self.config.save_wiki_content(page_id, content)
                self._refresh_file_list()
                self._open_document(page_id)
                self._show_message(f"已导入: {title}")
            except Exception as e:
                self._show_message(f"导入失败: {e}", msg_type=3)
    
    def _export_markdown(self):
        """导出为Markdown文件"""
        if not self.current_page_id:
            self._show_message("请先选择一个文档", msg_type=2)
            return
        
        # 获取文档标题
        pages = self.config.get_wiki_pages()
        title = "document"
        for page in pages:
            if page['id'] == self.current_page_id:
                title = page['title']
                break
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出 Markdown", f"{title}.md", "Markdown Files (*.md);;All Files (*.*)"
        )
        if file_path:
            try:
                content = self.editor.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._show_message(f"已导出: {os.path.basename(file_path)}")
            except Exception as e:
                self._show_message(f"导出失败: {e}", msg_type=3)
    
    def _on_text_changed(self):
        """文本改变时更新预览"""
        if self.preview_panel.isVisible():
            content = self.editor.toPlainText()
            self._render_markdown(content)
    
    def _render_markdown(self, content: str):
        """渲染Markdown预览"""
        if not content:
            self.preview_area.setPlainText("预览区域...")
            return
        
        # 简单的Markdown渲染
        lines = content.split('\n')
        html_lines = []
        in_code_block = False
        code_lines = []
        
        text_color = SiGlobal.siui.colors['TEXT_A']
        
        for line in lines:
            # 代码块
            if line.strip().startswith('```'):
                if in_code_block:
                    html_lines.append(f'<pre style="background: #2d2d2d; padding: 12px; border-radius: 4px; overflow-x: auto;"><code>{"<br>".join(code_lines)}</code></pre>')
                    code_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                continue
            
            if in_code_block:
                code_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))
                continue
            
            # 标题
            if line.startswith('# '):
                html_lines.append(f'<h1 style="color: {text_color}; font-size: 28px; margin: 16px 0 8px 0;">{line[2:]}</h1>')
            elif line.startswith('## '):
                html_lines.append(f'<h2 style="color: {text_color}; font-size: 24px; margin: 14px 0 7px 0;">{line[3:]}</h2>')
            elif line.startswith('### '):
                html_lines.append(f'<h3 style="color: {text_color}; font-size: 20px; margin: 12px 0 6px 0;">{line[4:]}</h3>')
            # 列表
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                html_lines.append(f'<li style="margin-left: 20px; color: {text_color};">{line.strip()[2:]}</li>')
            # 粗体和斜体
            else:
                formatted = line
                import re
                formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', formatted)
                formatted = re.sub(r'\*(.+?)\*', r'<em>\1</em>', formatted)
                formatted = re.sub(r'`(.+?)`', r'<code style="background: #3d3d3d; padding: 2px 6px; border-radius: 3px;">\1</code>', formatted)
                
                if formatted.strip():
                    html_lines.append(f'<p style="color: {text_color}; margin: 4px 0;">{formatted}</p>')
                else:
                    html_lines.append('<br>')
        
        html_content = ''.join(html_lines)
        self.preview_area.setHtml(html_content)
    
    def _toggle_preview(self):
        """切换预览面板"""
        is_visible = self.preview_panel.isVisible()
        self.preview_panel.setVisible(not is_visible)
        
        if not is_visible:
            # 显示预览时更新内容
            content = self.editor.toPlainText()
            self._render_markdown(content)
            self.preview_toggle_btn.attachment().setText("👁️ 隐藏预览")
        else:
            self.preview_toggle_btn.attachment().setText("👁️ 显示预览")
    
    def _auto_save(self):
        """自动保存"""
        if self.current_page_id and self.editor.toPlainText():
            content = self.editor.toPlainText()
            self.config.save_wiki_content(self.current_page_id, content)
    
    def _save_content(self):
        """保存内容"""
        if not self.current_page_id:
            self._show_message("请先选择或创建一个文档", msg_type=2)
            return
        
        content = self.editor.toPlainText()
        self.config.save_wiki_content(self.current_page_id, content)
        self._show_message("✓ 已保存", msg_type=1)
    
    def _git_sync(self):
        """Git同步"""
        try:
            # 这里实现Git同步逻辑
            # 示例：调用git命令或使用gitpython库
            self._show_message("Git同步功能开发中...", msg_type=2)
        except Exception as e:
            self._show_message(f"同步失败: {e}", msg_type=3)
    
    def _show_message(self, text: str, msg_type: int = 1):
        """显示消息"""
        try:
            window = self.window()
            if hasattr(window, 'LayerRightMessageSidebar'):
                window.LayerRightMessageSidebar().send(text=text, msg_type=msg_type, fold_after=2000)
        except Exception:
            pass
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        w, h = event.size().width(), event.size().height()
        if w > 0 and h > 0:
            self.main_splitter.setGeometry(0, 0, w, h)