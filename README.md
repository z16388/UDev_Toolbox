# Unity 开发者工具箱 (UDev Toolbox)

一个为Unity开发者打造的全能工具箱，基于 PyQt5 + PyQt-SiliconUI 构建。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 功能特性

### 📱 APK 分析工具
- 分析APK包信息（包名、版本、SDK等）
- 查看权限列表和Native库（SO文件）
- 检测16KB页面对齐和x86架构
- 计算文件哈希值（MD5/SHA1/SHA256）
- APK版本对比功能
- 提取图标和AndroidManifest

### 🔤 字符串工具
- 随机字符串生成（支持自定义字符集）
- GUID/UUID生成（Unity常用格式）
- Base64/URL编解码
- JSON格式化和验证
- 正则表达式测试
- 字符串哈希计算

### 📁 文件工具
- 文件哈希计算（MD5/SHA1/SHA256/SHA512）
- 多文件哈希对比
- 文件搜索（支持正则）
- 批量重命名
- 文本/文件Diff对比

### 🎮 Unity 专用工具
- PlayerPrefs文件查看和搜索
- GUID资源查找和引用追踪
- AssetBundle头信息分析
- 项目资源体积分析
- Unity日志解析

### 🌐 网络工具
- 本机/公网IP查询
- IP地址信息查询
- DNS域名解析
- HTTP请求测试（类似Postman）
- Ping主机测试

### ⏰ 时间工具
- 实时时间戳显示
- 时间戳与日期转换
- 多时区支持
- Cron表达式解析
- 倒计时和时间间隔计算

### 📝 Wiki 文档
- Markdown格式笔记
- 自定义图标
- Git仓库同步（可选）
- 导入导出功能

## 🚀 快速开始

### 安装依赖

```bash
pip install PyQt5 numpy
```

### 运行程序

```bash
python start.py
```

## 📦 项目结构

```
UDev_Toolbox/
├── start.py                 # 程序入口
├── PyQt-SiliconUI/          # UI框架
├── src/
│   ├── core/                # 核心功能模块
│   │   ├── apk_analyzer.py  # APK分析
│   │   ├── string_utils.py  # 字符串工具
│   │   ├── file_utils.py    # 文件工具
│   │   ├── unity_utils.py   # Unity工具
│   │   ├── network_utils.py # 网络工具
│   │   ├── time_utils.py    # 时间工具
│   │   └── config_manager.py# 配置管理
│   ├── ui/
│   │   ├── main_window.py   # 主窗口
│   │   └── pages/           # 功能页面
│   └── icons/               # 图标资源
├── config/                  # 配置文件目录
│   ├── settings.json        # 应用设置
│   └── wiki/                # Wiki内容
└── assets/                  # 资源文件
```

## ⚙️ 配置说明

### APK分析配置
- 自动检测Android SDK中的aapt工具
- 也可在设置中手动指定aapt路径

### Git同步配置
Wiki内容支持同步到Git仓库：
1. 在设置页面配置仓库URL和分支
2. 开启自动同步或手动同步

## 🔧 开发说明

本项目使用 PyQt-SiliconUI 作为UI框架，具有：
- 现代化的暗色主题
- 流畅的动画效果
- 丰富的组件库

## 📄 许可证

MIT License

## 🙏 致谢

- [PyQt-SiliconUI](https://github.com/ChinaIceF/PyQt-SiliconUI) - 优秀的PyQt5 UI框架
- [Fluent Icons](https://github.com/microsoft/fluentui-system-icons) - 图标资源
