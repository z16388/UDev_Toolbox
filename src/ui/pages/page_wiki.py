#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wiki 文档编辑器
"""

import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QApplication, QTextEdit
from PyQt5.QtGui import QFont

from siui.components.option_card import SiOptionCardPlane, SiOptionCardLinear
from siui.components.page import SiPage
from siui.components.titled_widget_group import SiTitledWidgetGroup
from siui.components.widgets import (
    SiDenseHContainer,
    SiDenseVContainer,
    SiLabel,
    SiLineEdit,
    SiPushButton,
    SiSimpleButton,
)
from siui.core import Si, SiColor, SiGlobal

from src.core.config_manager import ConfigManager


class WikiPage(SiPage):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.config = ConfigManager()
        self.current_page_id = None
        self.current_file_path = None
        self.page_cards = []
        
        # 主容器 - 使用水平分割
        self.main_container = SiDenseHContainer(self)
        self.main_container.setSpacing(16)
        
        # 左侧：文件列表
        self.left_panel = self._create_left_panel()
        
        # 右侧：编辑器和预览
        self.right_panel = self._create_right_panel()
        
        self.main_container.addWidget(self.left_panel)
        self.main_container.addWidget(self.right_panel)
        
        self.setAttachment(self.main_container)
        self._refresh_page_list()
    
    def _create_left_panel(self):
        """创建左侧文件管理面板"""
        container = SiDenseVContainer(self)
        container.setFixedWidth(280)
        container.setSpacing(12)
        
        # 标题
        title = SiLabel(self)
        title.setText("📚 Wiki 文档")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        text_color = SiGlobal.siui.colors['TEXT_A']
        title.setStyleSheet(f"color: {text_color}; padding: 12px;")
        
        # 新建按钮
        new_btn = SiPushButton(self)
        new_btn.setFixedHeight(40)
        new_btn.setUseTransition(True)
        new_btn.attachment().setText("+ 新建文档")
        new_btn.clicked.connect(self._create_new_page)
        
        # 导入按钮
        import_btn = SiPushButton(self)
        import_btn.setFixedHeight(36)
        import_btn.attachment().setText("📂 导入 .md 文件")
        import_btn.clicked.connect(self._import_markdown)
        
        # 文件列表容器
        self.page_list_container = SiDenseVContainer(self)
        self.page_list_container.setSpacing(6)
        
        container.addWidget(title)
        container.addWidget(new_btn)
        container.addWidget(import_btn)
        container.addPlaceholder(12)
        container.addWidget(self.page_list_container)
        
        return container
    
    def _create_right_panel(self):
        """创建右侧编辑器面板"""
        container = SiDenseVContainer(self)
        container.setSpacing(12)
        
        # 工具栏
        toolbar = self._create_toolbar()
        
        # 编辑器区域（使用QTextEdit支持多行）
        self.editor = QTextEdit(self)
        self.editor.setMinimumHeight(300)
        self.editor.setPlaceholderText("在此输入 Markdown 内容...\n\n支持标准 Markdown 语法:\n# 一级标题\n##  二级标题\n- 列表项\n**粗体** *斜体*\n```代码块```")
        
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
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                line-height: 1.6;
            }}
            QTextEdit:focus {{
                border-color: #0078D4;
            }}
        """)
        self.editor.textChanged.connect(self._on_text_changed)
        
        # 预览区域
        preview_label = SiLabel(self)
        preview_label.setText("📖 实时预览")
        preview_label.setStyleSheet(f"color: {text_color}; font-weight: bold; padding: 8px 0;")
        
        self.preview_area = QTextEdit(self)
        self.preview_area.setReadOnly(True)
        self.preview_area.setMinimumHeight(200)
        self.preview_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 16px;
                font-family: 'Microsoft YaHei', sans-serif;
                font-size: 14px;
                line-height: 1.8;
            }}
        """)
        
        container.addWidget(toolbar)
        container.addWidget(self.editor)
        container.addWidget(preview_label)
        container.addWidget(self.preview_area)
        
        return container
    
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = SiDenseHContainer(self)
        toolbar.setFixedHeight(48)
        toolbar.setSpacing(8)
        
        # 文件名显示
        self.filename_label = SiLabel(self)
        self.filename_label.setText("未打开文档")
        text_color = SiGlobal.siui.colors['TEXT_B']
        self.filename_label.setStyleSheet(f"color: {text_color}; font-size: 13px;")
        
        save_btn = SiPushButton(self)
        save_btn.resize(80, 36)
        save_btn.setUseTransition(True)
        save_btn.attachment().setText("💾 保存")
        save_btn.clicked.connect(self._save_content)
        
        export_btn = SiPushButton(self)
        export_btn.resize(100, 36)
        export_btn.attachment().setText("📤 导出")
        export_btn.clicked.connect(self._export_markdown)
        
        toolbar.addWidget(self.filename_label)
        toolbar.addPlaceholder(12)
        toolbar.addWidget(save_btn, "right")
        toolbar.addWidget(export_btn, "right")
        
        return toolbar
    
    def _refresh_page_list(self):
        """刷新页面列表"""
        for card in self.page_cards:
            card.setParent(None)
            card.deleteLater()
        self.page_cards.clear()
        
        pages = self.config.get_wiki_pages()
        
        if not pages:
            empty_label = SiLabel(self)
            empty_label.setText("暂无文档\n点击上方按钮创建")
            text_color = SiGlobal.siui.colors['TEXT_C']
            empty_label.setStyleSheet(f"color: {text_color}; padding: 20px; text-align: center;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.page_list_container.addWidget(empty_label)
            self.page_cards.append(empty_label)
        else:
            for page in pages:
                card = self._create_page_card(page)
                self.page_list_container.addWidget(card)
                self.page_cards.append(card)
    
    def _create_page_card(self, page: dict):
        """创建页面卡片"""
        card = SiPushButton(self)
        card.setFixedHeight(48)
        card.attachment().setText(f"📄 {page['title']}")
        card.clicked.connect(lambda: self._edit_page(page['id']))
        
        # 右键菜单
        card.setContextMenuPolicy(Qt.CustomContextMenu)
        card.customContextMenuRequested.connect(lambda pos, pid=page['id']: self._show_page_context_menu(card, pos, pid))
        
        return card
    
    def _show_page_context_menu(self, widget, pos, page_id):
        """显示页面右键菜单"""
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        delete_action = menu.addAction("删除")
        
        action = menu.exec_(widget.mapToGlobal(pos))
        if action == delete_action:
            self._delete_page(page_id)
    
    def _on_text_changed(self):
        """文本改变时更新预览"""
        content = self.editor.toPlainText()
        self._render_markdown(content)
    
    def _render_markdown(self, content: str):
        """渲染Markdown预览"""
        if not content:
            self.preview_area.setPlainText("预览区域将在此显示...")
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
                    # 结束代码块
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
                # 粗体 **text**
                import re
                formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', formatted)
                # 斜体 *text*
                formatted = re.sub(r'\*(.+?)\*', r'<em>\1</em>', formatted)
                # 行内代码 `code`
                formatted = re.sub(r'`(.+?)`', r'<code style="background: #3d3d3d; padding: 2px 6px; border-radius: 3px;">\1</code>', formatted)
                
                if formatted.strip():
                    html_lines.append(f'<p style="color: {text_color}; margin: 4px 0;">{formatted}</p>')
                else:
                    html_lines.append('<br>')
        
        html_content = ''.join(html_lines)
        self.preview_area.setHtml(html_content)
    
    def _create_new_page(self):
        """创建新文档"""
        from PyQt5.QtWidgets import QInputDialog
        title, ok = QInputDialog.getText(self, "新建文档", "请输入文档标题:")
        if ok and title.strip():
            page_id = self.config.add_wiki_page(title.strip())
            self._refresh_page_list()
            self._show_message(f"已创建: {title}")
            self._edit_page(page_id)
    
    def _edit_page(self, page_id: str):
        """编辑页面"""
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
    
    def _delete_page(self, page_id: str):
        """删除页面"""
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "确认删除", "确定要删除这个文档吗？", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.config.delete_wiki_page(page_id)
            self._refresh_page_list()
            
            if self.current_page_id == page_id:
                self.current_page_id = None
                self.editor.clear()
                self.preview_area.clear()
                self.filename_label.setText("未打开文档")
            
            self._show_message("已删除")
    
    def _save_content(self):
        """保存内容"""
        if not self.current_page_id:
            self._show_message("请先选择或创建一个文档", msg_type=2)
            return
        
        content = self.editor.toPlainText()
        self.config.save_wiki_content(self.current_page_id, content)
        self._show_message("✓ 已保存", msg_type=1)
    
    def _import_markdown(self):
        """导入Markdown文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "导入 Markdown 文件", "", "Markdown Files (*.md);;All Files (*.*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取标题（如果有）
                title = os.path.splitext(os.path.basename(file_path))[0]
                lines = content.split('\n')
                if lines and lines[0].startswith('# '):
                    title = lines[0][2:].strip()
                
                page_id = self.config.add_wiki_page(title)
                self.config.save_wiki_content(page_id, content)
                self._refresh_page_list()
                self._edit_page(page_id)
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
        self.main_container.setGeometry(32, 32, w - 64, h - 64)
        
        # 调整右侧面板宽度
        right_width = w - 64 - 280 - 16 - 64
        if right_width > 400:
            self.right_panel.setFixedWidth(right_width)
