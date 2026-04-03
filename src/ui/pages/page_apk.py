#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APK/AAB分析工具"""
import os
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from siui.components.option_card import SiOptionCardPlane
from siui.components.page import SiPage
from siui.components.titled_widget_group import SiTitledWidgetGroup
from siui.components.widgets import SiLabel, SiPushButton, SiDenseHContainer, SiLineEdit
from siui.core import Si, SiGlobal
from src.core.apk_analyzer import APKAnalyzer
from src.ui.components.copyable_text import CopyableTextArea, CopyableLineEdit, SoFileList


class APKAnalyzeThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            self.finished.emit(APKAnalyzer().analyze(self.path))
        except Exception as e:
            self.error.emit(str(e))


class APKToolsPage(SiPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.current_info = None
        self.thread = None
        self.scroll_container = SiTitledWidgetGroup(self)
        self.body_area = SiLabel(self)
        self.body_area.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.body_area.resized.connect(lambda _: self.scroll_container.adjustSize())
        self.titled_widget_group = SiTitledWidgetGroup(self.body_area)
        self.titled_widget_group.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.titled_widget_group.resized.connect(lambda size: self.body_area.setFixedHeight(size[1]))
        self.titled_widget_group.move(64, 32)
        self.titled_widget_group.setSpacing(16)
        self.titled_widget_group.addTitle("选择安装包 (支持APK和AAB)")
        self.titled_widget_group.addWidget(self._create_file_selector())
        self.titled_widget_group.addTitle("基本信息")
        self.titled_widget_group.addWidget(self._create_info_panel())
        self.titled_widget_group.addTitle("文件哈希")
        self.titled_widget_group.addWidget(self._create_hash_panel())
        self.titled_widget_group.addTitle("权限列表")
        self.titled_widget_group.addWidget(self._create_permissions_panel())
        self.titled_widget_group.addTitle("SO文件")
        self.titled_widget_group.addWidget(self._create_so_panel())
        self.titled_widget_group.addTitle("操作")
        self.titled_widget_group.addWidget(self._create_actions_panel())
        self.titled_widget_group.addPlaceholder(64)
        self.body_area.setFixedHeight(self.titled_widget_group.height())
        self.scroll_container.addWidget(self.body_area)
        self.setAttachment(self.scroll_container)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls() and e.mimeData().urls()[0].toLocalFile().lower().endswith((".apk", ".aab")):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e):
        path = e.mimeData().urls()[0].toLocalFile()
        if path.lower().endswith((".apk", ".aab")):
            self.path_edit.lineEdit().setText(path)
            self.path_edit.lineEdit().setCursorPosition(len(path))
            e.acceptProposedAction()
            self._analyze()

    def _create_file_selector(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("拖拽或选择APK/AAB文件")

        # 第一行：SiLineEdit 路径框，直接加入 body，由 setAdjustWidgetsSize 拉满宽度
        self.path_edit = SiLineEdit(self)
        self.path_edit.setFixedHeight(36)
        self.path_edit.lineEdit().setPlaceholderText("拖拽或选择APK/AAB文件...")
        self.path_edit.lineEdit().setReadOnly(True)

        # 第二行：浏览 + 分析按钮
        btn_row = SiDenseHContainer(self)
        btn_row.setFixedHeight(40)
        btn_row.setSpacing(12)
        browse_btn = SiPushButton(self)
        browse_btn.resize(120, 36)
        browse_btn.attachment().setText("浏览文件")
        browse_btn.clicked.connect(self._browse)
        self.analyze_btn = SiPushButton(self)
        self.analyze_btn.resize(120, 36)
        self.analyze_btn.setUseTransition(True)
        self.analyze_btn.attachment().setText("开始分析")
        self.analyze_btn.clicked.connect(self._analyze)
        btn_row.addWidget(browse_btn)
        btn_row.addWidget(self.analyze_btn)

        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(self.path_edit)
        panel.body().addWidget(btn_row)
        panel.adjustSize()
        return panel

    def _create_info_panel(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("应用信息")
        self.info = {}
        for key, label in [
            ("app_name",    "应用名"),
            ("package_name","包名"),
            ("version_name","versionName"),
            ("version_code","versionCode"),
            ("file_size",   "大小"),
            ("file_type",   "类型"),
            ("min_sdk",     "minSdkVersion"),
            ("target_sdk",  "targetSdkVersion"),
            ("compile_sdk", "compileSdkVersion"),
            ("abis",        "架构"),
        ]:
            mono = key in ("package_name",)
            row = CopyableLineEdit(self, label=label + ":", monospace=mono)
            row.setText("-")
            row.setFixedHeight(36)
            self.info[key] = row
            panel.body().addWidget(row)
        panel.body().setAdjustWidgetsSize(True)
        panel.adjustSize()
        self.info_panel = panel
        return panel

    def _create_hash_panel(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("文件哈希")
        for key, label, h in [("md5", "MD5", 52), ("sha1", "SHA1", 52), ("sha256", "SHA256", 72)]:
            row = CopyableLineEdit(self, label=label + ":", monospace=True, multiline_height=h)
            row.setText("-")
            row.setFixedHeight(h + 4)
            self.info[key] = row
            panel.body().addWidget(row)
        panel.body().setAdjustWidgetsSize(True)
        panel.adjustSize()
        return panel

    def _create_permissions_panel(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("权限列表")
        self.perm_text = CopyableTextArea(self, monospace=False, auto_expand=True)
        self.perm_text.setText("请选择文件分析")
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(self.perm_text)
        panel.adjustSize()
        self.perm_panel = panel
        return panel

    def _create_so_panel(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("原生库 (路径 / 大小 / 16KB对齐)")
        self.so_list = SoFileList(self, rows=12)
        self.so_list.setText("请选择文件分析")
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(self.so_list)
        panel.adjustSize()
        return panel

    def _create_actions_panel(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("操作")
        
        # 导出报告
        row = SiDenseHContainer(self)
        row.setFixedHeight(40)
        row.setSpacing(12)
        export_btn = SiPushButton(self)
        export_btn.resize(120, 36)
        export_btn.attachment().setText("导出报告")
        export_btn.clicked.connect(self._export)
        row.addWidget(export_btn)
        
        panel.body().addWidget(row)
        panel.adjustSize()
        return panel

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择安装包", "", "Android安装包 (*.apk *.aab)")
        if path:
            self.path_edit.lineEdit().setText(path)
            self.path_edit.lineEdit().setCursorPosition(len(path))

    def _analyze(self):
        path = self.path_edit.lineEdit().text().strip()
        if not path or not os.path.exists(path):
            self._msg("请选择有效文件", 2)
            return
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.attachment().setText("分析中...")
        self.thread = APKAnalyzeThread(path)
        self.thread.finished.connect(self._on_done)
        self.thread.error.connect(self._on_error)
        self.thread.start()

    def _on_done(self, info):
        self.current_info = info
        self.info["app_name"].setText(info.app_name or "-")
        self.info["package_name"].setText(info.package_name or "-")
        self.info["version_name"].setText(info.version_name or "-")
        self.info["version_code"].setText(info.version_code or "-")
        # AAB 显示模块分包大小
        if info.file_type == 'aab' and info.aab_modules_size:
            modules_str_parts = []
            modules_total = 0
            for module_name, size in sorted(info.aab_modules_size.items()):
                modules_str_parts.append(f"{module_name}: {self._fmt_size(size)}")
                modules_total += size
            total_str = f"总计 {self._fmt_size(modules_total)}\n" + "\n".join(modules_str_parts)
            self.info["file_size"].setText(total_str)
            self.info["file_size"].setFixedHeight(72 + len(info.aab_modules_size) * 20)
            # 动态高度改变后需要重新布局
            self.info_panel.body().adjustSize()
            self.info_panel.adjustSize()
        else:
            self.info["file_size"].setText(self._fmt_size(info.file_size))
            self.info["file_size"].setFixedHeight(36)
        self.info["file_type"].setText(info.file_type.upper())
        self.info["min_sdk"].setText(f"API {info.min_sdk}" if info.min_sdk else "-")
        self.info["target_sdk"].setText(f"API {info.target_sdk}" if info.target_sdk else "-")
        self.info["compile_sdk"].setText(f"API {info.compile_sdk}" if info.compile_sdk else "-")
        self.info["abis"].setText(", ".join(info.abis) if info.abis else "-")
        self.info["md5"].setText(info.md5 or "-")
        self.info["sha1"].setText(info.sha1 or "-")
        self.info["sha256"].setText(info.sha256 or "-")
        if info.permissions:
            self.perm_text.setText("\n".join(f"• {p}" for p in info.permissions))
        else:
            self.perm_text.setText("无权限")
        # 权限数量不定，动态扩展后重新布局
        self.perm_panel.body().adjustSize()
        self.perm_panel.adjustSize()
        self.titled_widget_group.adjustSize()
        self.body_area.setFixedHeight(self.titled_widget_group.height())
        self.scroll_container.adjustSize()
        so_info = getattr(info, 'so_files_info', [])
        if so_info:
            self.so_list.setSoFiles(so_info)
        elif info.so_files:
            self.so_list.setText("\n".join(f"• {s}" for s in info.so_files))
        else:
            self.so_list.setText("无原生库")
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.attachment().setText("开始分析")
        self._msg(f"{info.file_type.upper()} 分析完成")

    def _on_error(self, err):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.attachment().setText("开始分析")
        self._msg(f"失败: {err}", 3)

    def _export(self):
        if not self.current_info: return self._msg("请先分析", 2)
        i = self.current_info
        default_name = f"{i.package_name or 'report'}_report.txt"
        path, _ = QFileDialog.getSaveFileName(self, "保存报告", default_name, "文本 (*.txt)")
        if path:
            # AAB 模块大小显示
            if i.file_type == 'aab' and i.aab_modules_size:
                modules_total = sum(i.aab_modules_size.values())
                size_lines = [f"大小:   {self._fmt_size(modules_total)} (模块总计)"]
                for module_name, size in sorted(i.aab_modules_size.items()):
                    size_lines.append(f"  - {module_name}: {self._fmt_size(size)}")
                size_str = "\n".join(size_lines)
            else:
                size_str = f"大小:   {self._fmt_size(i.file_size)}"
            
            lines = [
                "===== APK/AAB 分析报告 =====",
                f"文件路径: {self.path_edit.lineEdit().text()}", "",
                "[应用信息]",
                f"应用名: {i.app_name or '-'}",
                f"包名:   {i.package_name or '-'}",
                f"版本:   {i.version_name or '-'} ({i.version_code or '-'})",
                f"类型:   {i.file_type.upper()}",
                size_str,
                f"最低SDK: API {i.min_sdk or '-'}",
                f"目标SDK: API {i.target_sdk or '-'}",
            ]
            # 添加编译SDK（如果有）
            if i.compile_sdk:
                lines.append(f"编译SDK: API {i.compile_sdk}")
            
            lines.extend([
                f"架构:   {', '.join(i.abis) if i.abis else '-'}", "",
                "[哈希值]",
                f"MD5:    {i.md5}",
                f"SHA1:   {i.sha1}",
                f"SHA256: {i.sha256}", "",
                f"[权限列表] ({len(i.permissions)} 项)",
            ])
            lines += i.permissions + [
                "", f"[SO文件] ({len(i.so_files)} 项)",
            ]
            so_info = getattr(i, 'so_files_info', [])
            if so_info:
                for p, sz, alignment in so_info:
                    # alignment 是 tuple (zip_aligned, elf_aligned) 或旧的 boolean
                    if isinstance(alignment, tuple):
                        zip_aligned, elf_aligned = alignment
                        # 判断 ABI 是否为 32 位（不需要 16KB 对齐）
                        is_32bit = any(abi in p for abi in ['armeabi-v7a', 'armeabi', 'x86'])
                        
                        if is_32bit:
                            status = "-"  # 32位不需要对齐
                        elif zip_aligned is None:
                            # AAB: 只检查 ELF 对齐
                            if elf_aligned is True:
                                status = "✓ 16KB对齐"
                            elif elf_aligned is False:
                                status = "✗ ELF未对齐"
                            else:
                                status = "?"
                        elif zip_aligned is True and elf_aligned is True:
                            status = "✓ 16KB对齐"
                        elif zip_aligned is False and elf_aligned is False:
                            status = "✗ ZIP+ELF未对齐"
                        elif zip_aligned is False:
                            status = "✗ ZIP未对齐"
                        elif elf_aligned is False:
                            status = "✗ ELF未对齐"
                        else:
                            status = "?"
                    else:
                        status = "✓" if alignment else "✗"
                    lines.append(f"  [{status:12s}]  {sz:>10}B  {p}")
            else:
                lines += [f"  {s}" for s in i.so_files]
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            self._msg(f"已保存: {path}")

    def _fmt_size(self, s):
        for u in ["B", "KB", "MB", "GB"]:
            if s < 1024: return f"{s:.2f} {u}"
            s /= 1024
        return f"{s:.2f} TB"

    def _msg(self, text, t=1):
        try:
            self.window().LayerRightMessageSidebar().send(text=text, msg_type=t, fold_after=3000)
        except:
            pass

    def resizeEvent(self, e):
        super().resizeEvent(e)
        w = e.size().width()
        if w > 200:
            self.body_area.setFixedWidth(w)
            self.titled_widget_group.setFixedWidth(min(w - 128, 1200))

