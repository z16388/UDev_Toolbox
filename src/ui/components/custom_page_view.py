#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自定义PageView - 支持展开/简略模式切换
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from siui.core import SiGlobal, SiColor
from siui.components.widgets import SiLabel, SiToggleButton, SiSvgLabel, SiPushButton
from siui.components.widgets.abstracts import ABCSiNavigationBar
from siui.components.widgets import SiDenseHContainer, SiDenseVContainer, SiStackedContainer


class PageButtonWithText(SiToggleButton):
    """带文本标签的页面按钮 - 支持展开/简略模式"""
    activated = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.is_expanded = True  # 默认展开

        # 设置自身样式
        self.setBorderRadius(6)
        self.colorGroup().assign(SiColor.BUTTON_OFF, "#00FFFFFF")
        self.colorGroup().assign(SiColor.BUTTON_ON, "#10FFFFFF")

        # 创建容器
        self.container = SiDenseHContainer(self)
        self.container.setSpacing(10)
        self.container.setFixedHeight(48)
        self.container.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)  # 垂直居中、水平左对齐
        
        # 高光指示条 - 垂直居中
        self.active_indicator = SiLabel(self)
        self.active_indicator.setFixedStyleSheet("border-radius: 2px")
        self.active_indicator.resize(4, 36)
        self.active_indicator.setOpacity(0)

        # 图标
        self.icon_label = SiSvgLabel(self)
        self.icon_label.resize(24, 24)
        self.icon_label.setSvgSize(20, 20)
        
        # 文本标签
        self.text_label = SiLabel(self)
        self.text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.text_label.setFont(QFont("Microsoft YaHei", 10))
        self.text_label.setMinimumWidth(100)
        
        # 添加到容器
        self.container.addPlaceholder(8)
        self.container.addWidget(self.icon_label)
        self.container.addWidget(self.text_label)
        self.container.addPlaceholder(8)

        # 绑定点击事件
        self.clicked.connect(self._on_clicked)

        # 索引
        self.index_ = -1
        
        # 保存按钮文本，用于收缩时的提示
        self.button_text = ""

    def reloadStyleSheet(self):
        super().reloadStyleSheet()
        self.active_indicator.setStyleSheet(
            f"background-color: {self.getColor(SiColor.THEME)}"
        )
        text_color = self.getColor(SiColor.TEXT_A) if self.isChecked() else self.getColor(SiColor.TEXT_B)
        self.text_label.setStyleSheet(f"color: {text_color};")

    def setText(self, text: str):
        """设置文本"""
        self.text_label.setText(text)
        self.button_text = text
        # 如果当前是收缩状态，更新提示
        if not self.is_expanded:
            self.setHint(text)

    def setIconSvg(self, svg_data):
        """设置图标"""
        self.icon_label.load(svg_data)
    
    def setExpanded(self, expanded: bool):
        """设置展开/简略模式"""
        self.is_expanded = expanded
        self.text_label.setVisible(expanded)
        if expanded:
            self.setFixedWidth(200)
            # 展开模式：容器左对齐，显示图标和文本
            self.container.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            # 展开时清除提示（因为已经显示文本了）
            self.setHint("")
        else:
            self.setFixedWidth(56)
            # 收起模式：容器居中对齐，只显示图标
            self.container.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            # 收起时显示提示
            if self.button_text:
                self.setHint(self.button_text)
        
        # 手动更新容器布局
        self.updateGeometry()
        self.update()

    def setActive(self, state):
        """设置激活状态"""
        self.setChecked(state)
        self.active_indicator.setOpacityTo(1 if state is True else 0)
        
        # 更新背景和文本颜色 - 增强选中效果
        if state:
            self.colorGroup().assign(SiColor.BUTTON_ON, "#18FFFFFF")
            text_color = self.getColor(SiColor.TEXT_A)
        else:
            self.colorGroup().assign(SiColor.BUTTON_ON, "#10FFFFFF")
            text_color = self.getColor(SiColor.TEXT_B)
        
        self.text_label.setStyleSheet(f"color: {text_color};")
        self.reloadStyleSheet()
        
        if state is True:
            self.activated.emit()

    def setIndex(self, index: int):
        """设置索引"""
        self.index_ = index

    def index(self):
        """获取索引"""
        return self.index_

    def on_index_changed(self, index):
        if index == self.index():
            self.setChecked(True)
            self.active_indicator.setOpacityTo(1)
            # 设置选中状态的背景和文本颜色
            self.colorGroup().assign(SiColor.BUTTON_ON, "#18FFFFFF")
            text_color = self.getColor(SiColor.TEXT_A)
            self.text_label.setStyleSheet(f"color: {text_color};")
            self.reloadStyleSheet()
        else:
            self.setChecked(False)
            self.active_indicator.setOpacityTo(0)
            # 设置未选中状态的背景和文本颜色
            self.colorGroup().assign(SiColor.BUTTON_ON, "#10FFFFFF")
            text_color = self.getColor(SiColor.TEXT_B)
            self.text_label.setStyleSheet(f"color: {text_color};")
            self.reloadStyleSheet()

    def _on_clicked(self):
        # 触发activated信号，由连接的func_when_active处理页面切换
        # func_when_active会调用setPage，进而发送indexChanged信号更新所有按钮状态
        self.activated.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.active_indicator.move(0, (self.height() - self.active_indicator.height()) // 2)
        w = event.size().width()
        if w > 0:
            if self.is_expanded:
                # 展开模式：容器左侧留4px给指示条
                self.container.setGeometry(4, 0, w - 4, event.size().height())
            else:
                # 收起模式：容器占满整个按钮宽度，图标会居中显示
                self.container.setGeometry(0, 0, w, event.size().height())


class PageNavigatorWithText(ABCSiNavigationBar):
    """带文本的页面导航栏 - 支持展开/简略切换"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 清空样式表
        self.setStyleSheet("")
        
        self.is_expanded = True  # 默认展开

        # 切换按钮 - 使用左右箭头图标
        self.toggle_btn = SiPushButton(self)
        self.toggle_btn.setFixedSize(200, 40)  # 初始宽度
        self.toggle_btn.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_chevron_left_filled"))
        self.toggle_btn.attachment().setSvgSize(20, 20)
        self.toggle_btn.clicked.connect(self._toggle_expanded)
        
        # 顶部按钮容器
        self.container_top = SiDenseVContainer(self)
        self.container_top.setSpacing(4)
        self.container_top.setShrinking(True)
        
        # 底部按钮容器
        self.container_bottom = SiDenseVContainer(self)
        self.container_bottom.setSpacing(4)
        self.container_bottom.setShrinking(True)
        self.container_bottom.setMinimumHeight(52)  # 确保至少能显示一个按钮（48px + 4px spacing）

        # 按钮列表
        self.buttons = []

    def _toggle_expanded(self):
        """切换展开/简略模式"""
        self.is_expanded = not self.is_expanded
        
        # 更新所有按钮
        for button in self.buttons:
            button.setExpanded(self.is_expanded)
        
        # 更新导航栏宽度和切换按钮图标
        if self.is_expanded:
            self.setFixedWidth(200)
            self.toggle_btn.setFixedWidth(200)
            self.toggle_btn.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_chevron_left_filled"))
            self.container_top.setFixedWidth(200)
            self.container_bottom.setFixedWidth(200)
        else:
            self.setFixedWidth(56)
            self.toggle_btn.setFixedWidth(56)
            self.toggle_btn.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_chevron_right_filled"))
            self.container_top.setFixedWidth(56)
            self.container_bottom.setFixedWidth(56)
        
        # 调整容器大小
        self.container_top.adjustSize()
        self.container_bottom.adjustSize()
        
        # 通知父容器（CustomPageView）更新布局
        if self.parent():
            parent = self.parent()
            # 直接更新父容器中导航栏和stacked_container的布局
            if hasattr(parent, 'stacked_container') and hasattr(parent, 'page_navigator'):
                w, h = parent.width(), parent.height()
                nav_width = self.width()
                # 更新导航栏位置和大小
                parent.page_navigator.setGeometry(0, 0, nav_width, h - 8)
                # 更新内容区域位置和大小
                parent.stacked_container.setGeometry(nav_width, 0, w - nav_width, h)

    def addPageButton(self, svg_data, text, func_when_active, side="top", index=None):
        """添加页面按钮"""
        # 根据side选择容器
        container = self.container_top if side == "top" else self.container_bottom
        
        # 如果没有传入index，则使用按钮总数作为索引
        if index is None:
            index = len(self.buttons)
        
        new_button = PageButtonWithText(container)
        new_button.setIndex(index)
        new_button.setFixedHeight(48)
        new_button.setText(text)
        new_button.setIconSvg(svg_data)
        new_button.setExpanded(self.is_expanded)
        new_button.activated.connect(func_when_active)
        new_button.show()

        # 绑定索引切换信号
        self.indexChanged.connect(new_button.on_index_changed)

        # 添加到对应的容器
        container.addWidget(new_button)
        container.adjustSize()
        self.setMaximumIndex(self.maximumIndex() + 1)

        self.buttons.append(new_button)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = event.size()
        if size.height() > 0:
            # 切换按钮固定在顶部
            self.toggle_btn.move(0, 0)
            
            # 顶部按钮容器（从切换按钮下方+8px间距开始）
            top_container_y = self.toggle_btn.height() + 8
            self.container_top.move(0, top_container_y)
            self.container_top.setFixedWidth(size.width())
            self.container_top.adjustSize()  # 根据内容调整高度
            
            # 底部按钮容器 - 手动计算所需高度
            self.container_bottom.setFixedWidth(size.width())
            # 计算底部容器需要的高度：按钮数量 * (按钮高度 + 间距)
            bottom_button_count = len([w for w in self.container_bottom.widgets()])
            if bottom_button_count > 0:
                # 每个按钮48px，间距4px，但最后一个按钮后面不需要间距
                bottom_height = bottom_button_count * 48 + (bottom_button_count - 1) * 4
            else:
                bottom_height = 0
            
            # 设置固定高度并定位（从导航栏底部向上计算，留足够的边距）
            if bottom_height > 0:
                self.container_bottom.setFixedHeight(bottom_height)
                # 留更多底部边距（28px）确保按钮完整显示
                bottom_container_y = size.height() - bottom_height - 28
                self.container_bottom.move(0, bottom_container_y)
                self.container_bottom.show()
            else:
                self.container_bottom.hide()


class StackedContainerWithAnimation(SiStackedContainer):
    """带动画的堆叠容器"""
    def setCurrentIndex(self, index: int):
        if 0 <= index < len(self.widgets):
            super().setCurrentIndex(index)
            self.widgets[index].animationGroup().fromToken("move").setFactor(1 / 5)
            self.widgets[index].move(0, 64)
            self.widgets[index].moveTo(0, 0)


class CustomPageView(SiDenseHContainer):
    """自定义页面视图 - 支持展开/简略侧边栏"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 清空样式表
        self.setStyleSheet("")

        self.setSpacing(0)
        self.setAdjustWidgetsSize(True)

        # 创建导航栏 - 默认展开(200px)
        self.page_navigator = PageNavigatorWithText(self)
        self.page_navigator.setFixedWidth(200)

        # 创建堆叠容器
        self.stacked_container = StackedContainerWithAnimation(self)
        self.stacked_container.setObjectName("stacked_container")

        # 添加到布局
        self.addWidget(self.page_navigator)
        self.addWidget(self.stacked_container)

    def _get_page_toggle_method(self, index):
        return lambda: self.setPage(index)

    def addPage(self, page, icon, text, side="top"):
        """添加页面"""
        self.stacked_container.addWidget(page)
        page_index = self.stacked_container.widgetsAmount() - 1
        self.page_navigator.addPageButton(
            icon,
            text,
            self._get_page_toggle_method(page_index),
            side,
            index=page_index  # 传递页面索引，确保按钮索引和页面索引一致
        )

    def setPage(self, index):
        """设置当前页面"""
        self.stacked_container.setCurrentIndex(index)
        # 触发导航栏的索引变化信号，使对应按钮显示选中状态
        self.page_navigator.indexChanged.emit(index)

    def reloadStyleSheet(self):
        super().reloadStyleSheet()
        self.stacked_container.setStyleSheet(
            f"""
            #stacked_container {{
                border-top-left-radius:6px; border-bottom-right-radius: 8px;
                background-color: {SiGlobal.siui.colors["INTERFACE_BG_B"]}; 
                border:1px solid {SiGlobal.siui.colors["INTERFACE_BG_C"]};
            }}
            """
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = event.size().width(), event.size().height()
        if h > 0 and w > 0:
            nav_width = self.page_navigator.width()
            # 明确设置导航栏的位置和大小，从顶部开始，留出底部间距
            self.page_navigator.setGeometry(0, 0, nav_width, h - 8)
            self.stacked_container.setGeometry(nav_width, 0, w - nav_width, h)
