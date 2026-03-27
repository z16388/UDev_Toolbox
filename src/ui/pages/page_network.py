#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具页面
"""

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication

from siui.components.option_card import SiOptionCardPlane
from siui.components.page import SiPage
from siui.components.titled_widget_group import SiTitledWidgetGroup
from siui.components.widgets import (
    SiDenseHContainer,
    SiDenseVContainer,
    SiLabel,
    SiLineEdit,
    SiPushButton,
)
from siui.core import Si, SiGlobal

from src.core.network_utils import NetworkUtils


class HTTPRequestThread(QThread):
    """HTTP请求线程"""
    finished = pyqtSignal(object)
    
    def __init__(self, url, method, headers, body):
        super().__init__()
        self.url = url
        self.method = method
        self.headers = headers
        self.body = body
    
    def run(self):
        result = NetworkUtils.http_request(self.url, self.method, self.headers, self.body)
        self.finished.emit(result)


class NetworkToolsPage(SiPage):
    """网络工具页面"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.request_thread = None
        
        self.scroll_container = SiTitledWidgetGroup(self)
        
        self.body_area = SiLabel(self)
        self.body_area.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.body_area.resized.connect(lambda _: self.scroll_container.adjustSize())
        
        self.titled_widget_group = SiTitledWidgetGroup(self.body_area)
        self.titled_widget_group.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.titled_widget_group.resized.connect(lambda size: self.body_area.setFixedHeight(size[1]))
        self.titled_widget_group.move(64, 32)
        
        self.titled_widget_group.setSpacing(16)
        
        # IP查询
        self.titled_widget_group.addTitle("IP 查询")
        self.titled_widget_group.addWidget(self._create_ip_panel())
        
        # DNS查询
        self.titled_widget_group.addTitle("DNS 查询")
        self.titled_widget_group.addWidget(self._create_dns_panel())
        
        # HTTP请求测试
        self.titled_widget_group.addTitle("HTTP 请求测试")
        self.titled_widget_group.addWidget(self._create_http_panel())
        
        # Ping测试
        self.titled_widget_group.addTitle("Ping 测试")
        self.titled_widget_group.addWidget(self._create_ping_panel())
        
        self.titled_widget_group.addPlaceholder(64)
        
        self.body_area.setFixedHeight(self.titled_widget_group.height())
        self.scroll_container.addWidget(self.body_area)
        
        self.setAttachment(self.scroll_container)
    
    def _create_ip_panel(self):
        """创建IP查询面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("查询本机IP和公网IP信息")
        
        action_row = SiDenseHContainer(self)
        action_row.setFixedHeight(36)
        action_row.setSpacing(8)
        
        local_ip_btn = SiPushButton(self)
        local_ip_btn.resize(100, 32)
        local_ip_btn.attachment().setText("本机IP")
        local_ip_btn.clicked.connect(self._get_local_ip)
        
        public_ip_btn = SiPushButton(self)
        public_ip_btn.resize(100, 32)
        public_ip_btn.setUseTransition(True)
        public_ip_btn.attachment().setText("公网IP")
        public_ip_btn.clicked.connect(self._get_public_ip)
        
        action_row.addWidget(local_ip_btn)
        action_row.addWidget(public_ip_btn)
        
        # IP查询输入
        query_row = SiDenseHContainer(self)
        query_row.setFixedHeight(36)
        query_row.setSpacing(8)
        
        self.ip_query_edit = SiLineEdit(self)
        self.ip_query_edit.setFixedHeight(32)
        self.ip_query_edit.lineEdit().setPlaceholderText("输入IP地址查询详情...")
        
        query_btn = SiPushButton(self)
        query_btn.resize(80, 32)
        query_btn.attachment().setText("查询")
        query_btn.clicked.connect(self._lookup_ip)
        
        query_row.addWidget(self.ip_query_edit)
        query_row.addWidget(query_btn, "right")
        
        self.ip_result = SiLabel(self)
        self.ip_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.ip_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']};")
        self.ip_result.setText("点击按钮查询IP信息")
        
        panel.body().addWidget(action_row)
        panel.body().addWidget(query_row)
        panel.body().addWidget(self.ip_result)
        panel.adjustSize()
        
        return panel
    
    def _create_dns_panel(self):
        """创建DNS查询面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("DNS域名解析")
        
        query_row = SiDenseHContainer(self)
        query_row.setFixedHeight(36)
        query_row.setSpacing(8)
        
        self.dns_edit = SiLineEdit(self)
        self.dns_edit.setFixedHeight(32)
        self.dns_edit.lineEdit().setPlaceholderText("输入域名 (如: www.google.com)")
        
        dns_btn = SiPushButton(self)
        dns_btn.resize(80, 32)
        dns_btn.setUseTransition(True)
        dns_btn.attachment().setText("解析")
        dns_btn.clicked.connect(self._dns_lookup)
        
        query_row.addWidget(self.dns_edit)
        query_row.addWidget(dns_btn, "right")
        
        self.dns_result = SiLabel(self)
        self.dns_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.dns_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']};")
        self.dns_result.setText("输入域名进行DNS解析")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(query_row)
        panel.body().addWidget(self.dns_result)
        panel.adjustSize()
        
        return panel
    
    def _create_http_panel(self):
        """创建HTTP请求面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("HTTP请求测试 (类似Postman)")
        
        url_row = SiDenseHContainer(self)
        url_row.setFixedHeight(36)
        url_row.setSpacing(8)
        
        method_label = SiLabel(self)
        method_label.setText("GET")
        method_label.setFixedWidth(40)
        
        self.http_url_edit = SiLineEdit(self)
        self.http_url_edit.setFixedHeight(32)
        self.http_url_edit.lineEdit().setPlaceholderText("输入URL...")
        
        self.send_btn = SiPushButton(self)
        self.send_btn.resize(80, 32)
        self.send_btn.setUseTransition(True)
        self.send_btn.attachment().setText("发送")
        self.send_btn.clicked.connect(self._send_http_request)
        
        url_row.addWidget(method_label)
        url_row.addWidget(self.http_url_edit)
        url_row.addWidget(self.send_btn, "right")
        
        self.http_result = SiLabel(self)
        self.http_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.http_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']}; font-family: Consolas, monospace;")
        self.http_result.setText("输入URL后发送请求")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(url_row)
        panel.body().addWidget(self.http_result)
        panel.adjustSize()
        
        return panel
    
    def _create_ping_panel(self):
        """创建Ping测试面板"""
        panel = SiOptionCardPlane(self)
        panel.setTitle("Ping主机")
        
        ping_row = SiDenseHContainer(self)
        ping_row.setFixedHeight(36)
        ping_row.setSpacing(8)
        
        self.ping_edit = SiLineEdit(self)
        self.ping_edit.setFixedHeight(32)
        self.ping_edit.lineEdit().setPlaceholderText("输入主机地址...")
        
        ping_btn = SiPushButton(self)
        ping_btn.resize(80, 32)
        ping_btn.setUseTransition(True)
        ping_btn.attachment().setText("Ping")
        ping_btn.clicked.connect(self._ping_host)
        
        ping_row.addWidget(self.ping_edit)
        ping_row.addWidget(ping_btn, "right")
        
        self.ping_result = SiLabel(self)
        self.ping_result.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.ping_result.setStyleSheet(f"color: {SiGlobal.siui.colors['TEXT_A']}; font-family: Consolas, monospace;")
        self.ping_result.setText("输入主机地址进行Ping测试")
        
        panel.body().setAdjustWidgetsSize(True)
        panel.body().addWidget(ping_row)
        panel.body().addWidget(self.ping_result)
        panel.adjustSize()
        
        return panel
    
    # 功能方法
    def _get_local_ip(self):
        ip = NetworkUtils.get_local_ip()
        self.ip_result.setText(f"本机IP: {ip}")
    
    def _get_public_ip(self):
        info = NetworkUtils.get_public_ip()
        if 'error' in info:
            self.ip_result.setText(f"获取失败: {info['error']}")
        else:
            result = "公网IP信息:\n\n"
            for key, value in info.items():
                result += f"{key}: {value}\n"
            self.ip_result.setText(result)
    
    def _lookup_ip(self):
        ip = self.ip_query_edit.lineEdit().text().strip()
        if not ip:
            self._show_message("请输入IP地址", msg_type=2)
            return
        
        info = NetworkUtils.lookup_ip(ip)
        if 'error' in info:
            self.ip_result.setText(f"查询失败: {info['error']}")
        else:
            result = f"IP {ip} 信息:\n\n"
            for key, value in info.items():
                result += f"{key}: {value}\n"
            self.ip_result.setText(result)
    
    def _dns_lookup(self):
        hostname = self.dns_edit.lineEdit().text().strip()
        if not hostname:
            self._show_message("请输入域名", msg_type=2)
            return
        
        info = NetworkUtils.dns_lookup(hostname)
        if info['error']:
            self.dns_result.setText(f"解析失败: {info['error']}")
        else:
            result = f"DNS解析 - {hostname}:\n\n"
            result += f"IP地址: {', '.join(info['addresses'])}\n"
            if info['aliases']:
                result += f"别名: {', '.join(info['aliases'])}\n"
            self.dns_result.setText(result)
    
    def _send_http_request(self):
        url = self.http_url_edit.lineEdit().text().strip()
        if not url:
            self._show_message("请输入URL", msg_type=2)
            return
        
        if not url.startswith('http'):
            url = 'https://' + url
        
        self.send_btn.setEnabled(False)
        self.send_btn.attachment().setText("请求中...")
        
        self.request_thread = HTTPRequestThread(url, 'GET', {}, None)
        self.request_thread.finished.connect(self._on_http_response)
        self.request_thread.start()
    
    def _on_http_response(self, response):
        result = f"HTTP响应:\n\n"
        result += f"状态码: {response.status_code}\n"
        result += f"耗时: {response.elapsed_ms:.2f} ms\n\n"
        
        if response.error:
            result += f"错误: {response.error}\n\n"
        
        result += "响应头:\n"
        for key, value in list(response.headers.items())[:10]:
            result += f"  {key}: {value}\n"
        
        result += f"\n响应体 (前1000字符):\n{response.body[:1000]}"
        
        self.http_result.setText(result)
        
        self.send_btn.setEnabled(True)
        self.send_btn.attachment().setText("发送")
    
    def _ping_host(self):
        host = self.ping_edit.lineEdit().text().strip()
        if not host:
            self._show_message("请输入主机地址", msg_type=2)
            return
        
        self.ping_result.setText("Ping中...")
        
        result = NetworkUtils.ping(host, count=4)
        if result['success']:
            self.ping_result.setText(f"Ping {host} 成功:\n\n{result['output']}")
        else:
            self.ping_result.setText(f"Ping {host} 失败:\n\n{result['error']}")
    
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
