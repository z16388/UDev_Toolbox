#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主页
"""

from PyQt5.QtCore import Qt

from siui.components.option_card import SiOptionCardPlane
from siui.components.page import SiPage
from siui.components.titled_widget_group import SiTitledWidgetGroup
from siui.components.widgets import (
    SiDenseHContainer,
    SiDenseVContainer,
    SiLabel,
)
from siui.core import GlobalFont, Si, SiColor, SiGlobal
from siui.gui import SiFont


class HomePage(SiPage):
    """主页"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 滚动区域
        self.scroll_container = SiTitledWidgetGroup(self)
        
        # 顶部区域
        self.head_area = SiLabel(self)
        self.head_area.setFixedHeight(280)
        
        # 创建大标题
        self.title = SiLabel(self.head_area)
        self.title.setGeometry(64, 40, 600, 64)
        self.title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.title.setText("Unity 开发者工具箱")
        self.title.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']}")
        self.title.setFont(SiFont.tokenized(GlobalFont.XL_MEDIUM))
        
        # 副标题
        self.subtitle = SiLabel(self.head_area)
        self.subtitle.setGeometry(64, 100, 800, 32)
        self.subtitle.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.subtitle.setText("为Unity开发者打造的全能工具集 - APK分析、字符串处理、文件工具、网络调试等")
        self.subtitle.setStyleSheet(f"color: {SiColor.trans(SiGlobal.siui.colors['TEXT_A'], 0.7)}")
        self.subtitle.setFont(SiFont.tokenized(GlobalFont.S_NORMAL))
        
        # 功能卡片容器
        self.cards_container = SiDenseHContainer(self.head_area)
        self.cards_container.move(64, 150)
        self.cards_container.setFixedHeight(100)
        self.cards_container.setSpacing(16)
        
        # 快捷功能卡片
        self._create_quick_cards()
        
        # 添加到滚动区域
        self.scroll_container.addWidget(self.head_area)
        
        # 下方区域
        self.body_area = SiLabel(self)
        self.body_area.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.body_area.resized.connect(lambda _: self.scroll_container.adjustSize())
        
        # 功能组
        self.titled_widget_group = SiTitledWidgetGroup(self.body_area)
        self.titled_widget_group.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.titled_widget_group.resized.connect(lambda size: self.body_area.setFixedHeight(size[1]))
        self.titled_widget_group.move(64, 0)
        
        # 创建功能面板
        self.titled_widget_group.setSpacing(16)
        self.titled_widget_group.addTitle("核心功能")
        self.titled_widget_group.addWidget(self._create_features_panel())
        
        self.titled_widget_group.addTitle("快速开始")
        self.titled_widget_group.addWidget(self._create_quick_start_panel())
        
        self.titled_widget_group.addPlaceholder(64)
        
        # 添加到滚动区域
        self.body_area.setFixedHeight(self.titled_widget_group.height())
        self.scroll_container.addWidget(self.body_area)
        
        self.setAttachment(self.scroll_container)
    
    def _create_quick_cards(self):
        """创建快捷功能卡片"""
        cards_data = [
            ("📱 APK分析", "#6366f1"),
            ("🔤 字符串工具", "#8b5cf6"),
            ("📁 文件工具", "#ec4899"),
            ("🎮 Unity工具", "#f59e0b"),
        ]
        
        for title, color in cards_data:
            card = self._create_mini_card(title, color)
            self.cards_container.addWidget(card)
    
    def _create_mini_card(self, title: str, color: str):
        """创建迷你功能卡片"""
        card = SiLabel(self)
        card.setFixedSize(140, 80)
        card.setStyleSheet(f"""
            background-color: {SiColor.trans(color, 0.15)};
            border-radius: 8px;
        """)
        
        # 标题
        title_label = SiLabel(card)
        title_label.setGeometry(16, 30, 120, 24)
        title_label.setText(title)
        title_label.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']}; background: transparent;")
        
        return card
    
    def _create_features_panel(self):
        """创建功能面板"""
        panel = SiDenseVContainer(self)
        panel.setAdjustWidgetsSize(True)
        panel.setSpacing(12)
        
        # 功能列表
        features = [
            ("📱 APK 分析工具", "分析APK包信息、签名、权限、ABI等，支持版本对比"),
            ("🔤 字符串工具", "随机字符串生成、Base64编解码、JSON格式化、正则测试等"),
            ("📁 文件工具", "文件Hash计算、批量重命名、文件搜索、文本Diff对比"),
            ("🎮 Unity 专用工具", "PlayerPrefs查看编辑、GUID查找、AssetBundle分析"),
            ("🌐 网络工具", "IP查询、HTTP请求测试、JSON API调试"),
            ("⏰ 时间工具", "时间戳转换、Cron表达式解析、倒计时计算"),
        ]
        
        for title, desc in features:
            card = self._create_feature_card(title, desc)
            panel.addWidget(card)
        
        return panel
    
    def _create_feature_card(self, title: str, description: str):
        """创建功能卡片"""
        from siui.components.option_card import SiOptionCardLinear
        
        card = SiOptionCardLinear(self)
        card.setTitle(title, description)
        
        return card
    
    def _create_quick_start_panel(self):
        """创建快速开始面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("使用提示")
        
        tips_label = SiLabel(self)
        tips_label.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        tips_label.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_B']}")
        tips_label.setText(
            "• 使用左侧导航栏切换不同功能模块\n"
            "• 拖拽文件到相应区域可快速分析\n"
            "• Wiki功能支持Markdown语法，可记录开发笔记\n"
            "• 在设置页面可自定义功能页面顺序\n"
            "• 支持Git同步Wiki内容到远程仓库"
        )
        
        panel.body().addWidget(tips_label)
        panel.adjustSize()
        
        return panel
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = event.size().width()
        if w > 200:
            self.body_area.setFixedWidth(w)
            self.titled_widget_group.setFixedWidth(min(w - 128, 1200))
