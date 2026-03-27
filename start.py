#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unity Developer Toolbox - 主入口文件
一个为Unity开发者设计的多功能工具箱
"""

import sys
import os

# 添加路径以便导入PyQt-SiliconUI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PyQt-SiliconUI'))

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import UDevToolbox

import siui
from siui.core import SiGlobal


def show_welcome_message(window):
    """显示欢迎消息"""
    window.LayerRightMessageSidebar().send(
        title="欢迎使用 Unity 开发者工具箱",
        text="当前版本 v1.0.0\n"
             "包含APK分析、字符串工具、文件工具等多种实用功能。",
        msg_type=1,
        icon=SiGlobal.siui.iconpack.get("ic_fluent_hand_wave_filled"),
        fold_after=5000,
    )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = UDevToolbox()
    window.show()
    
    # 延迟显示欢迎消息
    timer = QTimer(window)
    timer.singleShot(500, lambda: show_welcome_message(window))
    
    sys.exit(app.exec_())
