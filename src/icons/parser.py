#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图标解析器 - 复用PyQt-SiliconUI的图标资源
"""

import numpy
import os

# 使用Gallery示例中的图标数据
current_module_path = os.path.dirname(os.path.abspath(__file__))
gallery_icons_path = os.path.join(
    current_module_path, 
    '../../PyQt-SiliconUI/examples/Gallery for siui/icons/icons.dat'
)


class IconDictionary:
    """图标字典类，用于加载和获取SVG图标"""
    
    def __init__(self, library_path=gallery_icons_path, color=None):
        """
        初始化图标字典
        
        Args:
            library_path: 图标库文件路径
            color: SVG填充颜色
        """
        # 读取数据并解密
        with open(library_path, 'rb') as f:
            library_raw = f.read()
        
        library_list = list(library_raw)
        library = bytes(
            list((numpy.array(library_list) + numpy.array(range(len(library_list))) * 17) % 255)
        ).decode()

        # 整理成字典
        items = library.split('!!!')
        names = []
        datas = []
        for item in items[1:]:
            name, data = item.split('###')
            if color:
                data = data.replace('/>', f' fill="{color}" />')
            names.append(name)
            datas.append(data.encode())
        
        self.icons = dict(zip(names, datas))

    def get(self, name):
        """获取指定名称的图标SVG数据"""
        svg_data = self.icons.get(name)
        if svg_data:
            return svg_data if isinstance(svg_data, bytes) else svg_data.encode()
        return None
