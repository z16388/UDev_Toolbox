#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextEdit, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from siui.core import SiGlobal

class CopyableTextArea(QWidget):
    def __init__(self, parent=None, monospace=True, min_height=80, max_height=600):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(False)
        self.text_edit.setMinimumHeight(min_height)
        self.text_edit.setMaximumHeight(max_height)
        self.text_edit.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard | Qt.TextEditorInteraction)
        text_color = SiGlobal.siui.colors['TEXT_A']
        bg_color = SiGlobal.siui.colors['INTERFACE_BG_C']
        border_color = SiGlobal.siui.colors['INTERFACE_BG_D']
        font_family = "Consolas, monospace" if monospace else "Microsoft YaHei"
        self.text_edit.setStyleSheet(f"QTextEdit {{ background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 6px; padding: 10px; font-family: {font_family}; font-size: 13px; selection-background-color: #264F78; selection-color: #FFFFFF; }} QTextEdit:focus {{ border-color: #0078D4; }}")
        self._layout.addWidget(self.text_edit)
    def setText(self, text): self.text_edit.setPlainText(text)
    def text(self): return self.text_edit.toPlainText()
    def setMinimumHeight(self, h): self.text_edit.setMinimumHeight(h)
    def setMaximumHeight(self, h): self.text_edit.setMaximumHeight(h)

class CopyableLineEdit(QWidget):
    def __init__(self, parent=None, label="", monospace=True):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)
        text_color = SiGlobal.siui.colors['TEXT_A']
        label_color = SiGlobal.siui.colors['TEXT_B']
        bg_color = SiGlobal.siui.colors['INTERFACE_BG_C']
        if label:
            self.label = QLabel(label)
            self.label.setFixedWidth(80)
            self.label.setStyleSheet(f"color: {label_color}; font-size: 13px;")
            self._layout.addWidget(self.label)
        # 使用QTextEdit替代QLineEdit以支持多行显示
        self.line_edit = QTextEdit(self)
        self.line_edit.setMaximumHeight(60)
        self.line_edit.setMinimumHeight(32)
        self.line_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.line_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.line_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        font_family = "Consolas, monospace" if monospace else "Microsoft YaHei"
        self.line_edit.setStyleSheet(f"QTextEdit {{ background-color: {bg_color}; color: {text_color}; border: 1px solid #333; border-radius: 4px; padding: 4px 8px; font-family: {font_family}; font-size: 13px; selection-background-color: #264F78; }} QTextEdit:focus {{ border-color: #0078D4; }}")
        self._layout.addWidget(self.line_edit, 1)
    def setText(self, text):
        self.line_edit.setPlainText(text)
    def text(self): return self.line_edit.toPlainText()
    def setMinimumHeight(self, h): 
        super().setMinimumHeight(h)
        self.line_edit.setMinimumHeight(h)
    def setFixedHeight(self, h): 
        super().setFixedHeight(h)
        self.line_edit.setMaximumHeight(h)
