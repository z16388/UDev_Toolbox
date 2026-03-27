#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用PyQt5生成应用图标 - 不需要额外依赖
"""

import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QLinearGradient, QPainterPath
from PyQt5.QtCore import Qt, QPointF, QRectF


def create_simple_icon():
    """创建简单的应用图标"""
    app = QApplication(sys.argv)
    
    # 创建256x256的图像
    size = 256
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    
    # 绘制圆角矩形背景（渐变色）
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor("#4A90E2"))
    gradient.setColorAt(1, QColor("#357ABD"))
    
    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, size, size), 48, 48)
    painter.fillPath(path, gradient)
    
    # 绘制Unity风格的立方体
    painter.save()
    painter.translate(size/2, size/2)
    
    # 立方体顶面
    top_points = [
        QPointF(-50, -25),
        QPointF(0, -50),
        QPointF(50, -25),
        QPointF(0, 0)
    ]
    painter.setBrush(QColor(255, 255, 255, 230))
    painter.setPen(Qt.NoPen)
    painter.drawPolygon(*top_points)
    
    # 立方体左面
    left_points = [
        QPointF(-50, -25),
        QPointF(-50, 37),
        QPointF(0, 62),
        QPointF(0, 0)
    ]
    painter.setBrush(QColor(220, 220, 220))
    painter.drawPolygon(*left_points)
    
    # 立方体右面
    right_points = [
        QPointF(50, -25),
        QPointF(50, 37),
        QPointF(0, 62),
        QPointF(0, 0)
    ]
    painter.setBrush(QColor(180, 180, 180))
    painter.drawPolygon(*right_points)
    
    # 绘制工具图标（扳手）
    painter.setPen(QPen(QColor("#F57C00"), 3))
    painter.setBrush(QColor("#FFB74D"))
    tool_rect = QRectF(15, 35, 25, 8)
    painter.drawRoundedRect(tool_rect, 3, 3)
    painter.drawEllipse(QPointF(35, 30), 5, 5)
    
    painter.restore()
    
    # 绘制字母 "U"
    font = QFont("Arial", 48, QFont.Bold)
    painter.setFont(font)
    painter.setPen(QColor(255, 255, 255, 230))
    text_rect = QRectF(0, size - 70, size, 60)
    painter.drawText(text_rect, Qt.AlignCenter, "U")
    
    painter.end()
    
    # 保存图标
    assets_dir = Path(__file__).parent
    png_path = assets_dir / "app_icon.png"
    
    if pixmap.save(str(png_path), "PNG"):
        print(f"✓ 图标已生成: {png_path}")
        return True
    else:
        print(f"✗ 保存图标失败")
        return False


if __name__ == "__main__":
    create_simple_icon()
