#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
时间工具页面
"""

from datetime import datetime
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication

from siui.components.option_card import SiOptionCardPlane
from siui.components.page import SiPage
from siui.components.titled_widget_group import SiTitledWidgetGroup
from siui.components.widgets import (
    SiDenseHContainer,
    SiLabel,
    SiLineEdit,
    SiPushButton,
)
from siui.core import Si, SiGlobal

from src.core.time_utils import TimeUtils


class TimeToolsPage(SiPage):
    """时间工具页面"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.scroll_container = SiTitledWidgetGroup(self)
        
        self.body_area = SiLabel(self)
        self.body_area.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.body_area.resized.connect(lambda _: self.scroll_container.adjustSize())
        
        self.titled_widget_group = SiTitledWidgetGroup(self.body_area)
        self.titled_widget_group.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.titled_widget_group.resized.connect(lambda size: self.body_area.setFixedHeight(size[1]))
        self.titled_widget_group.move(64, 32)
        
        self.titled_widget_group.setSpacing(16)
        
        # 当前时间
        self.titled_widget_group.addTitle("当前时间")
        self.titled_widget_group.addWidget(self._create_current_time_panel())
        
        # 时间戳转换
        self.titled_widget_group.addTitle("时间戳转换")
        self.titled_widget_group.addWidget(self._create_timestamp_panel())
        
        # 日期时间转时间戳
        self.titled_widget_group.addTitle("日期时间转时间戳")
        self.titled_widget_group.addWidget(self._create_datetime_panel())
        
        # Cron表达式
        self.titled_widget_group.addTitle("Cron 表达式解析")
        self.titled_widget_group.addWidget(self._create_cron_panel())
        
        # 倒计时
        self.titled_widget_group.addTitle("倒计时计算")
        self.titled_widget_group.addWidget(self._create_countdown_panel())
        
        # 时间间隔计算
        self.titled_widget_group.addTitle("时间间隔计算")
        self.titled_widget_group.addWidget(self._create_duration_panel())
        
        self.titled_widget_group.addPlaceholder(64)
        
        self.body_area.setFixedHeight(self.titled_widget_group.height())
        self.scroll_container.addWidget(self.body_area)
        
        self.setAttachment(self.scroll_container)
        
        # 启动定时器更新当前时间
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_current_time)
        self.timer.start(1000)
    
    def _create_current_time_panel(self):
        """创建当前时间面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("实时显示当前时间和时间戳")
        
        self.current_time_label = SiLabel(self)
        self.current_time_label.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.current_time_label.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']}; font-family: Consolas, monospace; font-size: 16px;")
        self._update_current_time()
        
        action_row = SiDenseHContainer(self)
        action_row.setFixedHeight(36)
        action_row.setSpacing(8)
        
        copy_ts_btn = SiPushButton(self)
        copy_ts_btn.resize(120, 32)
        copy_ts_btn.attachment().setText("复制时间戳(秒)")
        copy_ts_btn.clicked.connect(lambda: self._copy_timestamp(False))
        
        copy_ts_ms_btn = SiPushButton(self)
        copy_ts_ms_btn.resize(130, 32)
        copy_ts_ms_btn.attachment().setText("复制时间戳(毫秒)")
        copy_ts_ms_btn.clicked.connect(lambda: self._copy_timestamp(True))
        
        action_row.addWidget(copy_ts_btn)
        action_row.addWidget(copy_ts_ms_btn)
        
        panel.body().addWidget(self.current_time_label)
        panel.body().addWidget(action_row)
        panel.adjustSize()
        
        return panel
    
    def _create_timestamp_panel(self):
        """创建时间戳转换面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("将时间戳转换为日期时间")
        
        input_row = SiDenseHContainer(self)
        input_row.setFixedHeight(36)
        input_row.setSpacing(8)
        
        self.ts_input = SiLineEdit(self)
        self.ts_input.setFixedHeight(32)
        self.ts_input.lineEdit().setPlaceholderText("输入时间戳 (秒或毫秒)")
        
        convert_btn = SiPushButton(self)
        convert_btn.resize(80, 32)
        convert_btn.setUseTransition(True)
        convert_btn.attachment().setText("转换")
        convert_btn.clicked.connect(self._convert_timestamp)
        
        input_row.addWidget(self.ts_input)
        input_row.addWidget(convert_btn, "right")
        
        self.ts_result = SiLabel(self)
        self.ts_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.ts_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']};")
        self.ts_result.setText("输入时间戳进行转换")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(input_row)
        panel.body().addWidget(self.ts_result)
        panel.adjustSize()
        
        return panel
    
    def _create_datetime_panel(self):
        """创建日期时间转时间戳面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("将日期时间转换为时间戳")
        
        input_row = SiDenseHContainer(self)
        input_row.setFixedHeight(36)
        input_row.setSpacing(8)
        
        self.dt_input = SiLineEdit(self)
        self.dt_input.setFixedHeight(32)
        self.dt_input.lineEdit().setPlaceholderText("格式: YYYY-MM-DD HH:MM:SS")
        
        convert_btn = SiPushButton(self)
        convert_btn.resize(80, 32)
        convert_btn.setUseTransition(True)
        convert_btn.attachment().setText("转换")
        convert_btn.clicked.connect(self._convert_datetime)
        
        input_row.addWidget(self.dt_input)
        input_row.addWidget(convert_btn, "right")
        
        self.dt_result = SiLabel(self)
        self.dt_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.dt_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']};")
        self.dt_result.setText("输入日期时间进行转换")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(input_row)
        panel.body().addWidget(self.dt_result)
        panel.adjustSize()
        
        return panel
    
    def _create_cron_panel(self):
        """创建Cron表达式面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("解析Cron表达式 (分 时 日 月 周)")
        
        input_row = SiDenseHContainer(self)
        input_row.setFixedHeight(36)
        input_row.setSpacing(8)
        
        self.cron_input = SiLineEdit(self)
        self.cron_input.setFixedHeight(32)
        self.cron_input.lineEdit().setPlaceholderText("如: 0 0 * * * (每天午夜)")
        
        parse_btn = SiPushButton(self)
        parse_btn.resize(80, 32)
        parse_btn.setUseTransition(True)
        parse_btn.attachment().setText("解析")
        parse_btn.clicked.connect(self._parse_cron)
        
        input_row.addWidget(self.cron_input)
        input_row.addWidget(parse_btn, "right")
        
        # 常用Cron示例
        examples_row = SiDenseHContainer(self)
        examples_row.setFixedHeight(36)
        examples_row.setSpacing(8)
        
        examples = [
            ("每分钟", "* * * * *"),
            ("每小时", "0 * * * *"),
            ("每天0点", "0 0 * * *"),
            ("每周一", "0 0 * * 1"),
        ]
        
        for label, cron in examples:
            btn = SiPushButton(self)
            btn.resize(80, 32)
            btn.attachment().setText(label)
            btn.clicked.connect(lambda checked, c=cron: self.cron_input.lineEdit().setText(c))
            examples_row.addWidget(btn)
        
        self.cron_result = SiLabel(self)
        self.cron_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.cron_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']};")
        self.cron_result.setText("输入Cron表达式进行解析")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(input_row)
        panel.body().addWidget(examples_row)
        panel.body().addWidget(self.cron_result)
        panel.adjustSize()
        
        return panel
    
    def _create_countdown_panel(self):
        """创建倒计时面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("计算距离目标时间的倒计时")
        
        input_row = SiDenseHContainer(self)
        input_row.setFixedHeight(36)
        input_row.setSpacing(8)
        
        self.countdown_input = SiLineEdit(self)
        self.countdown_input.setFixedHeight(32)
        self.countdown_input.lineEdit().setPlaceholderText("目标时间: YYYY-MM-DD HH:MM:SS")
        
        calc_btn = SiPushButton(self)
        calc_btn.resize(80, 32)
        calc_btn.setUseTransition(True)
        calc_btn.attachment().setText("计算")
        calc_btn.clicked.connect(self._calc_countdown)
        
        input_row.addWidget(self.countdown_input)
        input_row.addWidget(calc_btn, "right")
        
        self.countdown_result = SiLabel(self)
        self.countdown_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.countdown_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']};")
        self.countdown_result.setText("输入目标时间计算倒计时")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(input_row)
        panel.body().addWidget(self.countdown_result)
        panel.adjustSize()
        
        return panel
    
    def _create_duration_panel(self):
        """创建时间间隔面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("计算两个时间之间的间隔")
        
        input_row = SiDenseHContainer(self)
        input_row.setFixedHeight(36)
        input_row.setSpacing(8)
        
        self.duration_start = SiLineEdit(self)
        self.duration_start.setFixedHeight(32)
        self.duration_start.lineEdit().setPlaceholderText("开始时间")
        
        self.duration_end = SiLineEdit(self)
        self.duration_end.setFixedHeight(32)
        self.duration_end.lineEdit().setPlaceholderText("结束时间")
        
        calc_btn = SiPushButton(self)
        calc_btn.resize(80, 32)
        calc_btn.setUseTransition(True)
        calc_btn.attachment().setText("计算")
        calc_btn.clicked.connect(self._calc_duration)
        
        input_row.addWidget(self.duration_start)
        input_row.addWidget(self.duration_end)
        input_row.addWidget(calc_btn, "right")
        
        self.duration_result = SiLabel(self)
        self.duration_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.duration_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']};")
        self.duration_result.setText("输入两个时间计算间隔")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(input_row)
        panel.body().addWidget(self.duration_result)
        panel.adjustSize()
        
        return panel
    
    # 功能方法
    def _update_current_time(self):
        now = datetime.now()
        ts = TimeUtils.get_current_timestamp()
        ts_ms = TimeUtils.get_current_timestamp(milliseconds=True)
        
        week_info = TimeUtils.get_week_info(now)
        
        text = f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')} {week_info['weekday_name']}\n"
        text += f"时间戳(秒): {int(ts)}\n"
        text += f"时间戳(毫秒): {int(ts_ms)}\n"
        text += f"今年第 {week_info['day_of_year']} 天, 第 {week_info['iso_week']} 周"
        
        self.current_time_label.setText(text)
    
    def _copy_timestamp(self, milliseconds: bool):
        ts = TimeUtils.get_current_timestamp(milliseconds)
        QApplication.clipboard().setText(str(int(ts)))
        self._show_message("已复制时间戳")
    
    def _convert_timestamp(self):
        try:
            ts_text = self.ts_input.lineEdit().text().strip()
            ts = float(ts_text)
            
            # 自动检测秒/毫秒
            is_ms = ts > 10000000000
            
            dt = TimeUtils.timestamp_to_datetime(ts, is_milliseconds=is_ms)
            
            result = f"时间戳: {ts_text} {'(毫秒)' if is_ms else '(秒)'}\n\n"
            result += f"UTC+8: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # 转换到其他时区
            for tz_name in ['UTC', 'UTC+9', 'UTC-5']:
                dt_tz = TimeUtils.convert_timezone(dt, 'UTC+8', tz_name)
                result += f"{tz_name}: {dt_tz.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            self.ts_result.setText(result)
        except Exception as e:
            self.ts_result.setText(f"转换失败: {e}")
    
    def _convert_datetime(self):
        try:
            dt_text = self.dt_input.lineEdit().text().strip()
            dt = TimeUtils.parse_datetime(dt_text)
            
            ts = TimeUtils.datetime_to_timestamp(dt)
            ts_ms = TimeUtils.datetime_to_timestamp(dt, to_milliseconds=True)
            
            result = f"日期时间: {dt_text}\n\n"
            result += f"时间戳(秒): {int(ts)}\n"
            result += f"时间戳(毫秒): {int(ts_ms)}"
            
            self.dt_result.setText(result)
        except Exception as e:
            self.dt_result.setText(f"转换失败: {e}\n\n请使用格式: YYYY-MM-DD HH:MM:SS")
    
    def _parse_cron(self):
        cron = self.cron_input.lineEdit().text().strip()
        if not cron:
            self._show_message("请输入Cron表达式", msg_type=2)
            return
        
        result = TimeUtils.parse_cron(cron)
        
        if 'error' in result:
            self.cron_result.setText(f"解析失败: {result['error']}")
        else:
            text = f"Cron表达式: {cron}\n\n"
            text += f"描述: {result['description']}\n\n"
            text += "字段解析:\n"
            for field, info in result['fields'].items():
                text += f"  {field}: {info['expression']}\n"
            
            self.cron_result.setText(text)
    
    def _calc_countdown(self):
        try:
            target_text = self.countdown_input.lineEdit().text().strip()
            target = TimeUtils.parse_datetime(target_text)
            target = target.replace(tzinfo=TimeUtils.TIMEZONES['UTC+8'])
            
            countdown = TimeUtils.calculate_countdown(target)
            
            if countdown['expired']:
                self.countdown_result.setText(f"目标时间已过去 {abs(countdown['total_seconds'])} 秒")
            else:
                result = f"距离 {target_text} 还有:\n\n"
                result += f"{countdown['days']} 天 {countdown['hours']} 小时 "
                result += f"{countdown['minutes']} 分钟 {countdown['seconds']} 秒\n"
                result += f"(共 {countdown['total_seconds']} 秒)"
                self.countdown_result.setText(result)
        except Exception as e:
            self.countdown_result.setText(f"计算失败: {e}")
    
    def _calc_duration(self):
        try:
            start_text = self.duration_start.lineEdit().text().strip()
            end_text = self.duration_end.lineEdit().text().strip()
            
            start = TimeUtils.parse_datetime(start_text)
            end = TimeUtils.parse_datetime(end_text)
            
            duration = TimeUtils.calculate_duration(start, end)
            
            result = f"从 {start_text} 到 {end_text}:\n\n"
            result += f"{duration['human_readable']}\n"
            result += f"(共 {duration['total_seconds']} 秒)"
            
            self.duration_result.setText(result)
        except Exception as e:
            self.duration_result.setText(f"计算失败: {e}")
    
    def _show_message(self, text: str, msg_type: int = 1):
        try:
            window = self.window()
            if hasattr(window, 'LayerRightMessageSidebar'):
                window.LayerRightMessageSidebar().send(text=text, msg_type=msg_type, fold_after=2000)
        except Exception:
            pass
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = event.size().width()
        if w > 200:
            self.body_area.setFixedWidth(w)
            self.titled_widget_group.setFixedWidth(min(w - 128, 1200))
