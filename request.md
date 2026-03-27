做好代码的管理，一个py文件不要有太多行，一个小功能独立成一个目录，形成类似于下方的结构（不一定要用我举例子的名字）：
core
apk
time
string
unity
util


1. APK 工具（重点模块）

读取 APK 信息，包括不限于：

包名

versionCode / versionName

签名信息

最低SDK

查看 ABI（armv7 / arm64）

查看权限列表

查看 so 文件列表

APK 对比（版本差异）

检测：

是否开启 16KB 对齐

是否包含 x86

提取 icon / manifest

2. 字符串 & 编码工具

随机字符串生成

可以指定个数，提供选项确定由哪些字符组成：大写字母、小写字母、数字、特殊符号

可以指定长度

可以指定字符集

Base64 编码/解码

URL 编码

JSON 格式化 / 压缩

Unicode 转换

GUID 生成（Unity常用）

正则测试工具

3. 加密 & 哈希
拖文件计算计算，也可多文件比较
MD5

SHA1 / SHA256 / SHA512

HMAC（进阶）

文件 Hash

4. 文件工具

文件对比（diff）

批量重命名

文件搜索（支持正则）

文本 diff（类似 Beyond Compare 简化版）这部分在wiki功能中也可以提供和github上版本比较时复用

5. Unity 专用工具

PlayerPrefs 查看/编辑

GUID 查找（资源定位）

AssetBundle 信息查看

Addressables 分析

资源体积排行

日志查看器（adb logcat 简化UI）

Unity log 解析

6. 网络工具

IP 查询

HTTP 请求测试（类似 Postman Lite）

JSON API 测试

7. 时间工具

时间戳转换（秒 / 毫秒 / 时区）

cron 表达式解析和生成（高级）

倒计时计算

8. 计算工具

进制转换（2/8/10/16）

单位转换

表达式计算

9. wiki功能

默认提供一个范例wiki切页

玩家可以在第一级切页中不限制增加自定义的wiki切页（要做好切页过多时的显示优化）

自定义wiki切页提供icon自定义，希望有30个以上的可选项

使用markdown，要美化显示

支持git存档、同步和对比，需要支持常见的git平台，比如github，gitee等