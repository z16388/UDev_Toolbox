#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成应用图标 - 从SVG转换为PNG
需要安装：pip install pillow cairosvg
"""

import os
from pathlib import Path

def generate_icon():
    """从SVG生成PNG图标"""
    try:
        import cairosvg
        from PIL import Image
        import io
        
        # 获取当前脚本目录
        current_dir = Path(__file__).parent
        svg_path = current_dir / "app_icon.svg"
        png_path = current_dir / "app_icon.png"
        
        if not svg_path.exists():
            print(f"错误: SVG文件不存在: {svg_path}")
            return False
        
        # 转换SVG到PNG (256x256)
        print(f"正在从 {svg_path} 生成图标...")
        png_data = cairosvg.svg2png(url=str(svg_path), output_width=256, output_height=256)
        
        # 保存PNG
        with open(png_path, 'wb') as f:
            f.write(png_data)
        
        print(f"✓ PNG图标已生成: {png_path}")
        
        # 如果需要，还可以生成ICO格式（Windows图标）
        try:
            img = Image.open(io.BytesIO(png_data))
            ico_path = current_dir / "app_icon.ico"
            img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"✓ ICO图标已生成: {ico_path}")
        except Exception as e:
            print(f"生成ICO时出错（可选）: {e}")
        
        return True
        
    except ImportError as e:
        print("缺少必要的库，请运行以下命令安装：")
        print("pip install pillow cairosvg")
        return False
    except Exception as e:
        print(f"生成图标时出错: {e}")
        return False


if __name__ == "__main__":
    generate_icon()
