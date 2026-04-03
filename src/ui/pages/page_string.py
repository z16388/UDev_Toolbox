#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""字符串工具页面"""
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QTextEdit
from siui.components.option_card import SiOptionCardPlane
from siui.components.page import SiPage
from siui.components.titled_widget_group import SiTitledWidgetGroup
from siui.components.widgets import SiDenseHContainer, SiLabel, SiLineEdit, SiPushButton, SiSwitch
from siui.core import Si, SiGlobal
from src.core.string_utils import StringUtils
from src.core.config_manager import ConfigManager
from src.ui.components.copyable_text import CopyableTextArea

class StringToolsPage(SiPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = ConfigManager()
        self.scroll_container = SiTitledWidgetGroup(self)
        self.body_area = SiLabel(self)
        self.body_area.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.body_area.resized.connect(lambda _: self.scroll_container.adjustSize())
        self.titled_widget_group = SiTitledWidgetGroup(self.body_area)
        self.titled_widget_group.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.titled_widget_group.resized.connect(lambda size: self.body_area.setFixedHeight(size[1]))
        self.titled_widget_group.move(64, 32)
        self.titled_widget_group.setSpacing(16)
        self.titled_widget_group.addTitle("随机字符串生成")
        self.titled_widget_group.addWidget(self._create_random_string_panel())
        self.titled_widget_group.addTitle("随机字符串组合生成")
        self.titled_widget_group.addWidget(self._create_combo_string_panel())
        self.titled_widget_group.addTitle("字符串哈希计算")
        self.titled_widget_group.addWidget(self._create_hash_panel())
        self.titled_widget_group.addPlaceholder(64)
        self.body_area.setFixedHeight(self.titled_widget_group.height())
        self.scroll_container.addWidget(self.body_area)
        self.setAttachment(self.scroll_container)

    def _create_random_string_panel(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("生成随机字符串")
        
        # 长度和数量输入行
        length_row = SiDenseHContainer(self)
        length_row.setFixedHeight(40)
        length_row.setSpacing(12)
        length_label = SiLabel(self)
        length_label.setText("长度:")
        length_label.setFixedWidth(50)
        text_color = SiGlobal.siui.colors['TEXT_A']
        length_label.setStyleSheet(f"color: {text_color};")
        self.random_length_edit = SiLineEdit(self)
        self.random_length_edit.setFixedSize(120, 36)
        self.random_length_edit.lineEdit().setText("16")
        count_label = SiLabel(self)
        count_label.setText("数量:")
        count_label.setFixedWidth(50)
        count_label.setStyleSheet(f"color: {text_color};")
        self.random_count_edit = SiLineEdit(self)
        self.random_count_edit.setFixedSize(120, 36)
        self.random_count_edit.lineEdit().setText("1")
        length_row.addWidget(length_label)
        length_row.addWidget(self.random_length_edit)
        length_row.addWidget(count_label)
        length_row.addWidget(self.random_count_edit)
        
        # 字符类型选项 - 垂直排列
        # 第一行：大写字母和小写字母
        options_row1 = SiDenseHContainer(self)
        options_row1.setFixedHeight(40)
        options_row1.setSpacing(16)
        uppercase_label = SiLabel(self)
        uppercase_label.setText("大写字母")
        uppercase_label.setFixedWidth(80)
        uppercase_label.setStyleSheet(f"color: {text_color};")
        self.use_uppercase = SiSwitch(self)
        self.use_uppercase.setFixedHeight(32)
        self.use_uppercase.setChecked(True)
        lowercase_label = SiLabel(self)
        lowercase_label.setText("小写字母")
        lowercase_label.setFixedWidth(80)
        lowercase_label.setStyleSheet(f"color: {text_color};")
        self.use_lowercase = SiSwitch(self)
        self.use_lowercase.setFixedHeight(32)
        self.use_lowercase.setChecked(True)
        options_row1.addWidget(uppercase_label)
        options_row1.addWidget(self.use_uppercase)
        options_row1.addWidget(lowercase_label)
        options_row1.addWidget(self.use_lowercase)
        
        # 第二行：数字和特殊符号
        options_row2 = SiDenseHContainer(self)
        options_row2.setFixedHeight(40)
        options_row2.setSpacing(16)
        digits_label = SiLabel(self)
        digits_label.setText("数字")
        digits_label.setFixedWidth(80)
        digits_label.setStyleSheet(f"color: {text_color};")
        self.use_digits = SiSwitch(self)
        self.use_digits.setFixedHeight(32)
        self.use_digits.setChecked(True)
        special_label = SiLabel(self)
        special_label.setText("特殊符号")
        special_label.setFixedWidth(80)
        special_label.setStyleSheet(f"color: {text_color};")
        self.use_special = SiSwitch(self)
        self.use_special.setFixedHeight(32)
        options_row2.addWidget(digits_label)
        options_row2.addWidget(self.use_digits)
        options_row2.addWidget(special_label)
        options_row2.addWidget(self.use_special)
        
        # 第三行：数字范围（仅当只使用数字时有效）
        number_range_row = SiDenseHContainer(self)
        number_range_row.setFixedHeight(40)
        number_range_row.setSpacing(12)
        range_label = SiLabel(self)
        range_label.setText("数字范围:")
        range_label.setFixedWidth(80)
        range_label.setStyleSheet(f"color: {text_color};")
        self.number_min_edit = SiLineEdit(self)
        self.number_min_edit.setFixedSize(100, 36)
        self.number_min_edit.lineEdit().setPlaceholderText("最小值")
        range_separator = SiLabel(self)
        range_separator.setText("-")
        range_separator.setStyleSheet(f"color: {text_color};")
        range_separator.setFixedWidth(20)
        self.number_max_edit = SiLineEdit(self)
        self.number_max_edit.setFixedSize(100, 36)
        self.number_max_edit.lineEdit().setPlaceholderText("最大值")
        range_hint = SiLabel(self)
        range_hint.setText("(仅当只选择数字时生效)")
        range_hint.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_B']}; font-size: 11px;")
        number_range_row.addWidget(range_label)
        number_range_row.addWidget(self.number_min_edit)
        number_range_row.addWidget(range_separator)
        number_range_row.addWidget(self.number_max_edit)
        number_range_row.addWidget(range_hint)
        
        # 生成按钮
        
        action_row = SiDenseHContainer(self)
        action_row.setFixedHeight(40)
        generate_btn = SiPushButton(self)
        generate_btn.resize(120, 36)
        generate_btn.setUseTransition(True)
        generate_btn.attachment().setText("生成")
        generate_btn.clicked.connect(self._generate_random_string)
        action_row.addWidget(generate_btn)
        
        # 结果显示区域 - 自动扩展
        self.random_result = CopyableTextArea(self, monospace=True, auto_expand=True)
        self.random_result.setText("点击生成按钮生成随机字符串")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(length_row)
        panel.body().addWidget(options_row1)
        panel.body().addWidget(options_row2)
        panel.body().addWidget(number_range_row)
        panel.body().addWidget(action_row)
        panel.body().addWidget(self.random_result)
        panel.adjustSize()
        self.random_panel = panel  # 保存引用以便后续调整布局
        return panel

    def _create_combo_string_panel(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("生成自定义格式的字符串组合")
        text_color = SiGlobal.siui.colors['TEXT_A']
        hint_color = SiGlobal.siui.colors['TEXT_B']
        bg_color = SiGlobal.siui.colors['INTERFACE_BG_D']
        border_color = SiGlobal.siui.colors['INTERFACE_BG_D']
        
        # 标签行
        label_row = SiDenseHContainer(self)
        label_row.setFixedHeight(28)
        label_row.setSpacing(12)
        pattern_label = SiLabel(self)
        pattern_label.setText("格式模板 (每行一个模式):")
        pattern_label.setStyleSheet(f"color: {text_color}; font-weight: bold;")
        label_row.addWidget(pattern_label)
        
        # 多行模板输入框
        self.combo_template_edit = QTextEdit(self)
        self.combo_template_edit.setFixedHeight(120)
        self.combo_template_edit.setPlaceholderText("每行一个格式，如:\n{UL:8}-{D:4}\n订单号:{U:4}{N:10000-99999}\n{N:100-999}")
        # 从配置加载模板
        saved_template = self.config.get('string_settings', {}).get('combo_template', '{UL:8}-{D:4}-{D:4}\n订单号:{U:4}{N:10000-99999}\n会员卡:{N:100000-999999}')
        self.combo_template_edit.setPlainText(saved_template)
        self.combo_template_edit.setStyleSheet(
            f"QTextEdit {{ background-color: {bg_color}; color: {text_color}; "
            f"border: 1px solid {border_color}; border-radius: 6px; padding: 8px; "
            f"font-family: Consolas, monospace; font-size: 13px; }}"
        )
        # 监听文本变化以保存配置
        self.combo_template_edit.textChanged.connect(self._save_combo_template)
        
        # 占位符说明（第一组）
        hint_row1 = SiDenseHContainer(self)
        hint_row1.setFixedHeight(28)
        hint_row1.setSpacing(8)
        hint_label1 = SiLabel(self)
        hint_label1.setText("占位符:")
        hint_label1.setFixedWidth(80)
        hint_label1.setStyleSheet(f"color: {text_color}; font-weight: bold;")
        hint_text1 = SiLabel(self)
        hint_text1.setText("U=大写字母  L=小写字母  D=十进制数字  S=特殊符号")
        hint_text1.setStyleSheet(f"color: {hint_color}; font-size: 12px;")
        hint_row1.addWidget(hint_label1)
        hint_row1.addWidget(hint_text1)
        
        # 占位符说明（第二组）
        hint_row2 = SiDenseHContainer(self)
        hint_row2.setFixedHeight(28)
        hint_row2.setSpacing(8)
        hint_spacer = SiLabel(self)
        hint_spacer.setFixedWidth(80)
        hint_text2 = SiLabel(self)
        hint_text2.setText("O=八进制数字  H=大写十六进制  h=小写十六进制")
        hint_text2.setStyleSheet(f"color: {hint_color}; font-size: 12px;")
        hint_row2.addWidget(hint_spacer)
        hint_row2.addWidget(hint_text2)
        
        # 扩展格式说明
        hint_row3 = SiDenseHContainer(self)
        hint_row3.setFixedHeight(28)
        hint_row3.setSpacing(8)
        hint_label3 = SiLabel(self)
        hint_label3.setText("扩展格式:")
        hint_label3.setFixedWidth(80)
        hint_label3.setStyleSheet(f"color: {text_color}; font-weight: bold;")
        hint_text3 = SiLabel(self)
        hint_text3.setText("{类型:长度} 如: {UL:8}=8个大小写混合  {N:min-max} 如: {N:100-999}=100到999的数字")
        hint_text3.setStyleSheet(f"color: {hint_color}; font-size: 12px;")
        hint_row3.addWidget(hint_label3)
        hint_row3.addWidget(hint_text3)
        
        # 示例说明
        example_row = SiDenseHContainer(self)
        example_row.setFixedHeight(28)
        example_row.setSpacing(8)
        example_label = SiLabel(self)
        example_label.setText("示例:")
        example_label.setFixedWidth(80)
        example_label.setStyleSheet(f"color: {text_color}; font-weight: bold;")
        example_text = SiLabel(self)
        example_text.setText("{UL:8}-{D:4} → aBcD-1234   {N:100-999} → 567   订单:{U:4}{N:10000-99999} → 订单:ABCD45678")
        example_text.setStyleSheet(f"color: {hint_color}; font-size: 12px;")
        example_row.addWidget(example_label)
        example_row.addWidget(example_text)
        
        # 生成按钮
        action_row = SiDenseHContainer(self)
        action_row.setFixedHeight(40)
        generate_btn = SiPushButton(self)
        generate_btn.resize(120, 36)
        generate_btn.setUseTransition(True)
        generate_btn.attachment().setText("生成")
        generate_btn.clicked.connect(self._generate_combo_string)
        action_row.addWidget(generate_btn)
        
        # 结果显示区域 - 自动扩展
        self.combo_result = CopyableTextArea(self, monospace=True, auto_expand=True)
        self.combo_result.setText("点击生成按钮生成字符串组合\n\n提示: 使用 {类型:长度} 格式灵活定义每个部分")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(label_row)
        panel.body().addWidget(self.combo_template_edit)
        panel.body().addWidget(hint_row1)
        panel.body().addWidget(hint_row2)
        panel.body().addWidget(hint_row3)
        panel.body().addWidget(example_row)
        panel.body().addWidget(action_row)
        panel.body().addWidget(self.combo_result)
        panel.adjustSize()
        self.combo_panel = panel  # 保存引用以便后续调整布局
        return panel

    def _create_hash_panel(self):
        panel = SiOptionCardPlane(self)
        panel.setTitle("字符串哈希计算")
        self.hash_input = SiLineEdit(self)
        self.hash_input.setFixedHeight(36)
        self.hash_input.lineEdit().setPlaceholderText("输入要计算哈希的文本...")
        action_row = SiDenseHContainer(self)
        action_row.setFixedHeight(40)
        calc_btn = SiPushButton(self)
        calc_btn.resize(120, 36)
        calc_btn.setUseTransition(True)
        calc_btn.attachment().setText("计算哈希")
        calc_btn.clicked.connect(self._calc_hash)
        action_row.addWidget(calc_btn)
        self.hash_result = CopyableTextArea(self, monospace=True, min_height=80, max_height=150)
        self.hash_result.setText("-")
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(self.hash_input)
        panel.body().addWidget(action_row)
        panel.body().addWidget(self.hash_result)
        panel.adjustSize()
        return panel

    def _generate_random_string(self):
        try:
            length = int(self.random_length_edit.lineEdit().text() or "16")
            count = int(self.random_count_edit.lineEdit().text() or "1")
            
            # 获取数字范围（如果设置了）
            number_min = None
            number_max = None
            min_text = self.number_min_edit.lineEdit().text().strip()
            max_text = self.number_max_edit.lineEdit().text().strip()
            if min_text and max_text:
                try:
                    number_min = int(min_text)
                    number_max = int(max_text)
                except ValueError:
                    pass  # 如果转换失败，忽略范围
            
            results = StringUtils.generate_multiple_strings(
                count=count, 
                length=length, 
                use_uppercase=self.use_uppercase.isChecked(), 
                use_lowercase=self.use_lowercase.isChecked(), 
                use_digits=self.use_digits.isChecked(), 
                use_special=self.use_special.isChecked(),
                number_min=number_min,
                number_max=number_max
            )
            self.random_result.setText("\n".join(results))
            # 使用短延迟确保 setText 和 updateGeometry 已生效
            QTimer.singleShot(10, self._update_layout)
        except Exception as e: 
            self.random_result.setText(f"错误: {e}")
            QTimer.singleShot(10, self._update_layout)
    
    def _generate_combo_string(self):
        """生成字符串组合"""
        try:
            template = self.combo_template_edit.toPlainText() or "{UL:8}-{D:4}-{D:4}"
            
            result = StringUtils.generate_combo_strings(template=template)
            self.combo_result.setText(result)
            # 使用短延迟确保 setText 和 updateGeometry 已生效
            QTimer.singleShot(10, self._update_layout_combo)
        except Exception as e:
            self.combo_result.setText(f"错误: {e}")
            QTimer.singleShot(10, self._update_layout_combo)
    
    def _save_combo_template(self):
        """保存组合字符串模板到配置"""
        template = self.combo_template_edit.toPlainText()
        if 'string_settings' not in self.config.config:
            self.config.config['string_settings'] = {}
        self.config.config['string_settings']['combo_template'] = template
        self.config.save()
    
    def _update_layout(self):
        """更新布局以支持滚动"""
        self.random_panel.body().adjustSize()
        self.random_panel.adjustSize()
        self.titled_widget_group.adjustSize()
        new_height = self.titled_widget_group.height()
        self.body_area.setFixedHeight(new_height)
        self.scroll_container.adjustSize()
    
    def _update_layout_combo(self):
        """更新组合字符串面板布局以支持滚动"""
        self.combo_panel.body().adjustSize()
        self.combo_panel.adjustSize()
        self.titled_widget_group.adjustSize()
        new_height = self.titled_widget_group.height()
        self.body_area.setFixedHeight(new_height)
        self.scroll_container.adjustSize()

    def _calc_hash(self):
        text = self.hash_input.lineEdit().text()
        self.hash_result.setText(f"MD5:    {StringUtils.hash_md5(text)}\nSHA1:   {StringUtils.hash_sha1(text)}\nSHA256: {StringUtils.hash_sha256(text)}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = event.size().width()
        if w > 200:
            self.body_area.setFixedWidth(w)
            self.titled_widget_group.setFixedWidth(min(w - 128, 1200))
