#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APK/AAB分析工具"""
import os
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QApplication
from siui.components.option_card import SiOptionCardPlane
from siui.components.page import SiPage
from siui.components.titled_widget_group import SiTitledWidgetGroup
from siui.components.widgets import SiDenseHContainer, SiLabel, SiLineEdit, SiPushButton
from siui.core import Si, SiGlobal
from src.core.apk_analyzer import APKAnalyzer, APKInfo
from src.ui.components.copyable_text import CopyableTextArea, CopyableLineEdit

class APKAnalyzeThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    def __init__(self, path): super().__init__(); self.path = path
    def run(self):
        try: self.finished.emit(APKAnalyzer().analyze(self.path))
        except Exception as e: self.error.emit(str(e))

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
        self.titled_widget_group.addTitle("文件哈希 (可复制)")
        self.titled_widget_group.addWidget(self._create_hash_panel())
        self.titled_widget_group.addTitle("权限列表")
        self.titled_widget_group.addWidget(self._create_permissions_panel())
        self.titled_widget_group.addTitle("原生库 (SO文件)")
        self.titled_widget_group.addWidget(self._create_so_panel())
        self.titled_widget_group.addTitle("操作")
        self.titled_widget_group.addWidget(self._create_actions_panel())
        self.titled_widget_group.addPlaceholder(64)
        self.body_area.setFixedHeight(self.titled_widget_group.height())
        self.scroll_container.addWidget(self.body_area)
        self.setAttachment(self.scroll_container)
    
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls() and e.mimeData().urls()[0].toLocalFile().lower().endswith((".apk",".aab")): e.acceptProposedAction()
        else: e.ignore()
    
    def dropEvent(self, e):
        path = e.mimeData().urls()[0].toLocalFile()
        if path.lower().endswith((".apk",".aab")):
            self.path_edit.lineEdit().setText(path)
            e.acceptProposedAction()
            self._analyze()
    
    def _create_file_selector(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("拖拽或选择APK/AAB文件")
        row = SiDenseHContainer(self)
        row.setFixedHeight(40)
        row.setSpacing(8)
        self.path_edit = SiLineEdit(self)
        self.path_edit.setFixedHeight(36)
        self.path_edit.lineEdit().setPlaceholderText("拖拽或选择APK/AAB文件...")
        browse_btn = SiPushButton(self)
        browse_btn.resize(100, 36)
        browse_btn.attachment().setText("浏览")
        browse_btn.clicked.connect(self._browse)
        self.analyze_btn = SiPushButton(self)
        self.analyze_btn.resize(100, 36)
        self.analyze_btn.setUseTransition(True)
        self.analyze_btn.attachment().setText("分析")
        self.analyze_btn.clicked.connect(self._analyze)
        row.addWidget(self.path_edit)
        row.addWidget(browse_btn, "right")
        row.addWidget(self.analyze_btn, "right")
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(row)
        panel.adjustSize()
        return panel
    
    def _create_info_panel(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("应用信息")
        self.info = {}
        for key, label in [("app_name","应用名"),("package_name","包名"),("version_name","版本"),("version_code","版本码"),("file_size","大小"),("file_type","类型"),("min_sdk","最低SDK"),("target_sdk","目标SDK"),("abis","架构"),("is_16kb_aligned","16KB对齐")]:
            row = CopyableLineEdit(self, label=label+":", monospace=(key in ["package_name"]))
            row.setText("-")
            row.setFixedHeight(36)
            self.info[key] = row
            panel.body().addWidget(row)
        panel.adjustSize()
        return panel
    
    def _create_hash_panel(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("文件哈希")
        for key, label in [("md5","MD5"),("sha1","SHA1"),("sha256","SHA256")]:
            row = CopyableLineEdit(self, label=label+":", monospace=True)
            row.setText("-")
            row.setFixedHeight(36)
            self.info[key] = row
            panel.body().addWidget(row)
        panel.adjustSize()
        return panel
    
    def _create_permissions_panel(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("权限")
        self.perm_text = CopyableTextArea(self, monospace=False, min_height=120, max_height=400)
        self.perm_text.setText("请选择文件分析")
        panel.body().addWidget(self.perm_text)
        panel.adjustSize()
        return panel
    
    def _create_so_panel(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("原生库")
        self.so_text = CopyableTextArea(self, monospace=True, min_height=120, max_height=400)
        self.so_text.setText("请选择文件分析")
        panel.body().addWidget(self.so_text)
        panel.adjustSize()
        return panel
    
    def _create_actions_panel(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("操作")
        row = SiDenseHContainer(self)
        row.setFixedHeight(40)
        row.setSpacing(12)
        for text, func in [("提取图标",self._extract_icon),("提取Manifest",self._extract_manifest),("对比安装包",self._compare),("导出报告",self._export)]:
            btn = SiPushButton(self)
            btn.resize(120, 36)
            btn.attachment().setText(text)
            btn.clicked.connect(func)
            row.addWidget(btn)
        panel.body().addWidget(row)
        panel.adjustSize()
        return panel
    
    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择安装包", "", "Android安装包 (*.apk *.aab)")
        if path: self.path_edit.lineEdit().setText(path)
    
    def _analyze(self):
        path = self.path_edit.lineEdit().text().strip()
        if not path or not os.path.exists(path): self._msg("请选择有效文件", 2); return
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
        self.info["file_size"].setText(self._fmt_size(info.file_size))
        self.info["file_type"].setText(info.file_type.upper())
        self.info["min_sdk"].setText(f"API {info.min_sdk}" if info.min_sdk else "-")
        self.info["target_sdk"].setText(f"API {info.target_sdk}" if info.target_sdk else "-")
        self.info["abis"].setText(", ".join(info.abis) if info.abis else "-")
        self.info["is_16kb_aligned"].setText("是" if info.is_16kb_aligned else "否")
        self.info["md5"].setText(info.md5 or "-")
        self.info["sha1"].setText(info.sha1 or "-")
        self.info["sha256"].setText(info.sha256 or "-")
        self.perm_text.setText("\n".join(["* "+p.split(".")[-1] for p in info.permissions]) if info.permissions else "无权限")
        self.so_text.setText("\n".join(["* "+s for s in info.so_files]) if info.so_files else "无原生库")
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.attachment().setText("分析")
        self._msg(f"{info.file_type.upper()} 分析完成")
    
    def _on_error(self, err):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.attachment().setText("分析")
        self._msg(f"失败: {err}", 3)
    
    def _extract_icon(self):
        if not self.current_info: return self._msg("请先分析", 2)
        out = QFileDialog.getExistingDirectory(self, "选择目录")
        if out:
            r = APKAnalyzer().extract_icon(self.path_edit.lineEdit().text(), out)
            self._msg(f"已保存: {r}" if r else "提取失败", 1 if r else 2)
    
    def _extract_manifest(self):
        if not self.current_info: return self._msg("请先分析", 2)
        out = QFileDialog.getExistingDirectory(self, "选择目录")
        if out:
            r = APKAnalyzer().extract_manifest(self.path_edit.lineEdit().text(), out)
            self._msg(f"已保存: {r}" if r else "需要aapt", 1 if r else 2)
    
    def _compare(self):
        if not self.current_info: return self._msg("请先分析", 2)
        path, _ = QFileDialog.getOpenFileName(self, "选择对比文件", "", "Android安装包 (*.apk *.aab)")
        if path:
            d = APKAnalyzer().compare_apks(self.path_edit.lineEdit().text(), path)
            self._msg(f"版本: {d['version_code_diff'][0]}{d['version_code_diff'][1]}")
    
    def _export(self):
        if not self.current_info: return self._msg("请先分析", 2)
        path, _ = QFileDialog.getSaveFileName(self, "保存报告", f"{self.current_info.package_name}_report.txt", "文本 (*.txt)")
        if path:
            i = self.current_info
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"应用: {i.app_name}\n包名: {i.package_name}\n版本: {i.version_name}\nMD5: {i.md5}\nSHA1: {i.sha1}\nSHA256: {i.sha256}\n\n权限:\n"+"\n".join(i.permissions))
            self._msg(f"已保存: {path}")
    
    def _fmt_size(self, s):
        for u in ["B","KB","MB","GB"]:
            if s < 1024: return f"{s:.2f} {u}"
            s /= 1024
        return f"{s:.2f} TB"
    
    def _msg(self, text, t=1):
        try: self.window().LayerRightMessageSidebar().send(text=text, msg_type=t, fold_after=3000)
        except: pass
    
    def resizeEvent(self, e):
        super().resizeEvent(e)
        w = e.size().width()
        if w > 200:
            self.body_area.setFixedWidth(w)
            self.titled_widget_group.setFixedWidth(min(w - 128, 1200))
