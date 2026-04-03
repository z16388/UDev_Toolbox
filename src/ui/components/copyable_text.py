#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QTextEdit, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QSizePolicy)
from siui.core import SiGlobal


def _get_colors():
    return {
        'text': SiGlobal.siui.colors['TEXT_A'],
        'label': SiGlobal.siui.colors['TEXT_B'],
        'bg': SiGlobal.siui.colors['INTERFACE_BG_C'],
        'border': SiGlobal.siui.colors['INTERFACE_BG_D'],
    }


class CopyableTextArea(QWidget):
    """多行可选中文本框，支持鼠标选中复制"""
    def __init__(self, parent=None, monospace=True, rows=8, min_height=None, max_height=None, auto_expand=False):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._auto_expand = auto_expand
        self._line_height = 22
        c = _get_colors()
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        line_height = 22
        if auto_expand:
            fixed_h = line_height + 20  # 初始占位高度，setText 时会动态扩展
        elif min_height is not None:
            fixed_h = min_height
        else:
            fixed_h = rows * line_height + 20
        self.text_edit.setFixedHeight(fixed_h)
        self.setFixedHeight(fixed_h)
        font_family = "Consolas, monospace" if monospace else "Microsoft YaHei"
        self.text_edit.setStyleSheet(
            f"QTextEdit {{ background-color: {c['bg']}; color: {c['text']}; "
            f"border: 1px solid {c['border']}; border-radius: 6px; padding: 8px; "
            f"font-family: {font_family}; font-size: 13px; "
            f"selection-background-color: #264F78; selection-color: #FFFFFF; }}"
            f"QScrollBar:vertical {{ background: transparent; width: 6px; margin: 4px 2px; border-radius: 3px; }}"
            f"QScrollBar::handle:vertical {{ background: {c['border']}; border-radius: 3px; min-height: 24px; }}"
            f"QScrollBar::handle:vertical:hover {{ background: #555; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}"
            f"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}"
        )
        if auto_expand:
            self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._layout.addWidget(self.text_edit)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.text_edit.setFixedWidth(self.width())

    def setText(self, text):
        self.text_edit.setPlainText(text)
        if self._auto_expand:
            lines = text.count('\n') + 1 if text.strip() else 1
            h = lines * self._line_height + 20
            self.text_edit.setFixedHeight(h)
            self.setFixedHeight(h)
            # 通知父容器尺寸已变化
            self.updateGeometry()

    def text(self):
        return self.text_edit.toPlainText()


class CopyableLineEdit(QWidget):
    """单行/多行可选中文本框，支持鼠标选中复制"""
    def __init__(self, parent=None, label="", monospace=True, multiline_height=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        c = _get_colors()
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

        if label:
            lbl = QLabel(label, self)
            lbl.setFixedWidth(120)
            lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            lbl.setStyleSheet(f"color: {c['label']}; font-size: 13px;")
            self._layout.addWidget(lbl)

        font_family = "Consolas, monospace" if monospace else "Microsoft YaHei"
        self.line_edit = QTextEdit(self)
        self.line_edit.setReadOnly(True)
        self.line_edit.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        self.line_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.line_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.line_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        h = multiline_height if multiline_height else 36
        self.line_edit.setFixedHeight(h)
        self.line_edit.setStyleSheet(
            f"QTextEdit {{ background-color: {c['bg']}; color: {c['text']}; "
            f"border: 1px solid {c['border']}; border-radius: 4px; padding: 4px 8px; "
            f"font-family: {font_family}; font-size: 13px; "
            f"selection-background-color: #264F78; }}"
        )
        self._layout.addWidget(self.line_edit, 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        label_w = 120 + 8  # label width + spacing
        new_edit_w = max(self.width() - label_w, 60)
        self.line_edit.setFixedWidth(new_edit_w)

    def setText(self, text):
        self.line_edit.setPlainText(text)

    def text(self):
        return self.line_edit.toPlainText()

    def setFixedHeight(self, h):
        super().setFixedHeight(h)
        self.line_edit.setFixedHeight(max(h - 4, 28))


class SoFileList(QWidget):
    """SO文件列表，显示路径、大小、16KB对齐状态，可鼠标选中"""
    def __init__(self, parent=None, rows=8):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        c = _get_colors()
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # 表头
        # 路径列52字符(ASCII) + 2间距 + 大小列10字符 + 2间距 + 对齐列
        # 中文字符在等宽字体中占2个ASCII宽，故用空格补偿
        # "  文件路径"=10视觉宽，需补至路径列起始56位 → 46空格；"大小"结束60，需补至68 → 8空格
        header = QLabel("  文件路径" + " " * 48 + "大小" + " " * 8 + "16KB对齐", self)
        header.setStyleSheet(
            f"color: {c['label']}; font-family: Consolas, monospace; "
            f"font-size: 12px; padding: 2px 8px;"
        )
        self._layout.addWidget(header)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        self.text_edit.setLineWrapMode(QTextEdit.NoWrap)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        line_height = 22
        fixed_h = rows * line_height + 12
        self.text_edit.setFixedHeight(fixed_h)
        # header 高度约 22px，总高度 = 表头 + 文本区
        self.setFixedHeight(fixed_h + 22)
        self.text_edit.setStyleSheet(
            f"QTextEdit {{ background-color: {c['bg']}; color: {c['text']}; "
            f"border: 1px solid {c['border']}; border-radius: 6px; padding: 4px 8px; "
            f"font-family: Consolas, monospace; font-size: 12px; "
            f"selection-background-color: #264F78; selection-color: #FFFFFF; }}"
            f"QScrollBar:vertical {{ background: transparent; width: 6px; margin: 4px 2px; border-radius: 3px; }}"
            f"QScrollBar::handle:vertical {{ background: {c['border']}; border-radius: 3px; min-height: 24px; }}"
            f"QScrollBar::handle:vertical:hover {{ background: #555; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}"
            f"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}"
            f"QScrollBar:horizontal {{ background: transparent; height: 6px; margin: 2px 4px; border-radius: 3px; }}"
            f"QScrollBar::handle:horizontal {{ background: {c['border']}; border-radius: 3px; min-width: 24px; }}"
            f"QScrollBar::handle:horizontal:hover {{ background: #555; }}"
            f"QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}"
            f"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: transparent; }}"
        )
        self._layout.addWidget(self.text_edit)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.text_edit.setFixedWidth(self.width())

    _ABI_SHORT = {
        'armeabi-v7a': 'armeabi-v7a',
        'armeabi':     'armeabi',
        'arm64-v8a':   'arm64-v8a',
        'x86':         'x86',
        'x86_64':      'x86_64',
        'mips':        'mips',
        'mips64':      'mips64',
    }

    def setSoFiles(self, so_files_info):
        """
        so_files_info: list of (path, size_bytes, (zip_aligned, elf_aligned))
        """
        if not so_files_info:
            self.text_edit.setPlainText("无原生库")
            return
        lines = []
        for path, size, alignment in so_files_info:
            parts = path.split('/')
            # APK:  lib/armeabi-v7a/libxxx.so  → lib 在 index 0
            # AAB:  base/lib/armeabi-v7a/libxxx.so → lib 在 index 1
            # 通用：找到 'lib' 的位置，下一段就是 ABI
            raw_abi = ''
            for i, p in enumerate(parts):
                if p == 'lib' and i + 1 < len(parts):
                    raw_abi = parts[i + 1]
                    break
            abi = self._ABI_SHORT.get(raw_abi, raw_abi)
            name = parts[-1]
            size_str = self._fmt_size(size)
            
            # alignment = (zip_aligned, elf_aligned)
            # 32位 ABI 不需要 16KB 对齐
            if raw_abi in ('armeabi-v7a', 'armeabi', 'x86'):
                align_str = "-"
            elif alignment is None or not isinstance(alignment, tuple):
                align_str = "- 检测失败"
            else:
                zip_aligned, elf_aligned = alignment
                
                # AAB 特殊处理：zip_aligned 为 None（不检查 ZIP 对齐）
                if zip_aligned is None:
                    # AAB 只检查 ELF 对齐
                    if elf_aligned is True:
                        align_str = "✓ 16KB对齐"
                    elif elf_aligned is False:
                        align_str = "✗ ELF未对齐"
                    else:
                        align_str = "- 检测失败"
                # APK 完整检查：ZIP + ELF
                elif zip_aligned is True and elf_aligned is True:
                    align_str = "✓ 16KB对齐"
                elif zip_aligned is False and elf_aligned is False:
                    align_str = "✗ ZIP+ELF未对齐"
                elif zip_aligned is False and elf_aligned is True:
                    align_str = "✗ ZIP未对齐"
                elif zip_aligned is True and elf_aligned is False:
                    align_str = "✗ ELF未对齐"
                elif elf_aligned is None:
                    align_str = "- 检测失败"
                else:
                    align_str = "- 未知状态"
            
            full_path = f"{abi}/{name}"
            lines.append(f"  {full_path:<52}  {size_str:<10}  {align_str}")
        self.text_edit.setPlainText('\n'.join(lines))

    def setText(self, text):
        self.text_edit.setPlainText(text)

    @staticmethod
    def _fmt_size(b):
        if b < 1024: return f"{b}B"
        if b < 1024 * 1024: return f"{b/1024:.1f}KB"
        return f"{b/1024/1024:.2f}MB"
