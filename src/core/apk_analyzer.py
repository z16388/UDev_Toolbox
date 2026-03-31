#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import struct
import zipfile
import hashlib
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class APKInfo:
    package_name: str = ""
    version_code: str = ""
    version_name: str = ""
    min_sdk: str = ""
    target_sdk: str = ""
    compile_sdk: str = ""  # compileSdkVersion
    app_name: str = ""
    permissions: List[str] = field(default_factory=list)
    abis: List[str] = field(default_factory=list)
    so_files: List[str] = field(default_factory=list)
    so_files_info: List[tuple] = field(default_factory=list)  # (path, size, aligned)
    is_16kb_aligned: bool = False
    has_x86: bool = False
    signature_info: Dict = field(default_factory=dict)
    file_size: int = 0
    aab_modules_size: Dict[str, int] = field(default_factory=dict)  # AAB各模块大小: {module_name: size}
    md5: str = ""
    sha1: str = ""
    sha256: str = ""
    file_type: str = "apk"

class APKAnalyzer:
    SUPPORTED_EXTENSIONS = ['.apk', '.aab']
    
    def __init__(self):
        self.aapt_path = self._find_aapt()
        self.bundletool_path = self._find_bundletool()
    
    def _find_aapt(self):
        android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        if android_home:
            build_tools = os.path.join(android_home, 'build-tools')
            if os.path.exists(build_tools):
                versions = sorted(os.listdir(build_tools), reverse=True)
                for version in versions:
                    aapt = os.path.join(build_tools, version, 'aapt.exe' if os.name == 'nt' else 'aapt')
                    if os.path.exists(aapt):
                        return aapt
        return None
    
    def _find_bundletool(self):
        """查找 bundletool.jar"""
        # 检查环境变量
        bundletool = os.environ.get('BUNDLETOOL_JAR')
        if bundletool and os.path.exists(bundletool):
            return bundletool
        # 检查常见位置
        possible_locations = [
            'bundletool.jar',
            'bundletool-all.jar',
            os.path.expanduser('~/bundletool.jar'),
            os.path.expanduser('~/.android/bundletool.jar'),
        ]
        for loc in possible_locations:
            if os.path.exists(loc):
                return loc
        try:
            subprocess.run(['aapt', 'version'], capture_output=True, check=True)
            return 'aapt'
        except:
            pass
        return None
    
    @staticmethod
    def is_supported_file(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        return ext in APKAnalyzer.SUPPORTED_EXTENSIONS
    
    def analyze(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported format: {ext}")
        info = APKInfo()
        info.file_size = os.path.getsize(file_path)
        info.file_type = ext[1:]
        info.md5, info.sha1, info.sha256 = self._calculate_hashes(file_path)
        # aapt 只能处理 APK，AAB 需要用 fallback
        if self.aapt_path and ext == '.apk':
            self._analyze_with_aapt(file_path, info)
        self._analyze_zip_contents(file_path, info)
        # 无 aapt 或 AAB 或 aapt 未获取到信息时，直接解析二进制 XML
        if not info.package_name:
            self._analyze_manifest_fallback(file_path, info)
        if ext == '.apk':
            info.is_16kb_aligned = all(a for _, _, a in info.so_files_info) if info.so_files_info else True
        return info
    
    def _calculate_hashes(self, file_path):
        md5_hash, sha1_hash, sha256_hash = hashlib.md5(), hashlib.sha1(), hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5_hash.update(chunk)
                sha1_hash.update(chunk)
                sha256_hash.update(chunk)
        return md5_hash.hexdigest(), sha1_hash.hexdigest(), sha256_hash.hexdigest()
    
    def _analyze_with_aapt(self, apk_path, info):
        try:
            result = subprocess.run([self.aapt_path, 'dump', 'badging', apk_path], capture_output=True, text=True, timeout=30)
            output = result.stdout
            m = re.search(r"package: name='([^']+)'", output)
            if m: info.package_name = m.group(1)
            m = re.search(r"versionCode='(\d+)'", output)
            if m: info.version_code = m.group(1)
            m = re.search(r"versionName='([^']+)'", output)
            if m: info.version_name = m.group(1)
            m = re.search(r"sdkVersion:'(\d+)'", output)
            if m: info.min_sdk = m.group(1)
            m = re.search(r"targetSdkVersion:'(\d+)'", output)
            if m: info.target_sdk = m.group(1)
            # 匹配本地化应用名，例如 application-label:'xxx' 或 application-label-zh-CN:'xxx'
            m = re.search(r"application-label(?:-[^:']+)?:'([^']+)'", output)
            if m: info.app_name = m.group(1)
            info.permissions = re.findall(r"uses-permission: name='([^']+)'", output)
            abis = re.findall(r"native-code: '([^']+)'", output)
            if abis: info.abis = abis[0].split("' '")
        except Exception as e:
            print(f"aapt failed: {e}")
    
    def _check_elf_alignment(self, so_data):
        """检查 ELF 文件的段对齐，返回是否所有 LOAD 段 p_align >= 16384"""
        if len(so_data) < 64:
            return False
        # 检查 ELF 魔数
        if so_data[:4] != b'\x7fELF':
            return False
        # so_data[4]: 1=32位, 2=64位
        is_64bit = (so_data[4] == 2)
        # so_data[5]: 1=小端, 2=大端
        is_little = (so_data[5] == 1)
        endian = '<' if is_little else '>'
        
        if is_64bit:
            # 64位: e_phoff在0x20, e_phentsize在0x36, e_phnum在0x38
            e_phoff, = struct.unpack(endian + 'Q', so_data[0x20:0x28])
            e_phentsize, e_phnum = struct.unpack(endian + 'HH', so_data[0x36:0x3a])
            ph_fmt = endian + 'IIQQQQQQ'  # p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align
        else:
            # 32位: e_phoff在0x1c, e_phentsize在0x2a, e_phnum在0x2c
            e_phoff, = struct.unpack(endian + 'I', so_data[0x1c:0x20])
            e_phentsize, e_phnum = struct.unpack(endian + 'HH', so_data[0x2a:0x2e])
            ph_fmt = endian + 'IIIIIIII'  # p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align
        
        # 遍历所有 Program Header，检查 PT_LOAD (type=1) 的对齐
        for i in range(e_phnum):
            ph_offset = e_phoff + i * e_phentsize
            if ph_offset + e_phentsize > len(so_data):
                break
            ph_data = so_data[ph_offset:ph_offset + e_phentsize]
            if is_64bit:
                p_type, _, _, _, _, _, _, p_align = struct.unpack(ph_fmt, ph_data[:56])
            else:
                p_type, _, _, _, _, _, _, p_align = struct.unpack(ph_fmt, ph_data[:32])
            # PT_LOAD 段必须 16KB 对齐
            if p_type == 1 and p_align < 16384:
                return False
        return True

    def _analyze_zip_contents(self, file_path, info):
        is_aab = file_path.lower().endswith('.aab')
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                so_files_info, abis_found = [], set()
                # AAB模块大小统计（排除元数据）
                if is_aab:
                    module_sizes = {}
                    # 排除的元数据目录和文件
                    excluded = {'BUNDLE-METADATA', 'META-INF', 'BundleConfig.pb'}
                    for fi in zf.infolist():
                        if not fi.is_dir():
                            parts = fi.filename.split('/')
                            if len(parts) > 0:
                                module_name = parts[0]  # base, feature1, etc.
                                # 跳过元数据
                                if module_name not in excluded:
                                    module_sizes[module_name] = module_sizes.get(module_name, 0) + fi.file_size
                    info.aab_modules_size = module_sizes
                
                for fi in zf.infolist():
                    name = fi.filename
                    if name.endswith('.so'):
                        size = fi.file_size
                        # 同时检测 ZIP 对齐和 ELF 对齐
                        zip_aligned = None
                        elf_aligned = None
                        
                        # AAB 和 APK 使用不同的对齐检测策略
                        # AAB: SO 文件可能被压缩，只检查 ELF 段对齐
                        # APK: 必须未压缩且 ZIP 对齐，同时检查 ELF 段对齐
                        
                        if not is_aab:
                            # 1. APK: 检测 ZIP 归档对齐（未压缩 + 数据偏移 % 16384 == 0）
                            try:
                                zf.fp.seek(fi.header_offset + 26)
                                local_fname_len, local_extra_len = struct.unpack('<HH', zf.fp.read(4))
                                data_offset = fi.header_offset + 30 + local_fname_len + local_extra_len
                                zip_aligned = (fi.compress_type == zipfile.ZIP_STORED) and (data_offset % 16384 == 0)
                            except:
                                zip_aligned = None
                        else:
                            # AAB: 不检查 ZIP 对齐（文件可能被压缩）
                            # Google Play 会在生成 APK 时处理对齐
                            zip_aligned = None
                        
                        # 2. 检测 ELF 内部段对齐（LOAD 段 p_align >= 16384）
                        # APK 和 AAB 都需要检查
                        try:
                            so_data = zf.read(name)
                            elf_aligned = self._check_elf_alignment(so_data)
                        except:
                            elf_aligned = None
                        
                        # 返回元组 (zip_aligned, elf_aligned)
                        so_files_info.append((name, size, (zip_aligned, elf_aligned)))
                        parts = name.split('/')
                        for i, part in enumerate(parts):
                            if part == 'lib' and i + 1 < len(parts):
                                abi = parts[i + 1]
                                if abi in ['arm64-v8a', 'armeabi-v7a', 'armeabi', 'x86', 'x86_64']:
                                    abis_found.add(abi)
                info.so_files_info = so_files_info
                info.so_files = [s[0] for s in so_files_info]
                if not info.abis:
                    info.abis = list(abis_found)
                info.has_x86 = 'x86' in info.abis or 'x86_64' in info.abis
        except Exception as e:
            print(f"ZIP failed: {e}")
    
    def _parse_binary_xml(self, data):
        """解析 Android 二进制 XML，返回 dict"""
        import struct
        result = {'package': '', 'versionCode': '', 'versionName': '',
                  'minSdkVersion': '', 'targetSdkVersion': '', 'compileSdkVersion': '',
                  'appLabel': '', 'permissions': []}
        try:
            print(f"  Binary XML size: {len(data)} bytes")
            if len(data) < 8 or data[0:2] != b'\x03\x00':
                print(f"  Invalid header: {data[0:2].hex()}")
                return result
            print(f"  Valid XML header")
            # --- 解析字符串池 ---
            sp_pos = 8
            if data[sp_pos:sp_pos+2] != b'\x01\x00':
                print(f"  Invalid string pool header: {data[sp_pos:sp_pos+2].hex()}")
                return result
            sp_header_size = struct.unpack_from('<H', data, sp_pos+2)[0]
            sp_size        = struct.unpack_from('<I', data, sp_pos+4)[0]
            str_count      = struct.unpack_from('<I', data, sp_pos+8)[0]
            flags          = struct.unpack_from('<I', data, sp_pos+16)[0]
            strs_start     = struct.unpack_from('<I', data, sp_pos+20)[0]
            is_utf8 = bool(flags & (1 << 8))
            print(f"  String pool: count={str_count}, utf8={is_utf8}")
            offsets_base = sp_pos + sp_header_size
            strs_base    = sp_pos + strs_start

            def read_str(i):
                if i < 0 or i >= str_count:
                    return ''
                off = struct.unpack_from('<I', data, offsets_base + i * 4)[0]
                p = strs_base + off
                try:
                    if is_utf8:
                        u16 = data[p]; p += 1
                        if u16 & 0x80: u16 = ((u16 & 0x7F) << 8) | data[p]; p += 1
                        u8 = data[p]; p += 1
                        if u8 & 0x80: u8 = ((u8 & 0x7F) << 8) | data[p]; p += 1
                        return data[p:p+u8].decode('utf-8', errors='replace')
                    else:
                        length = struct.unpack_from('<H', data, p)[0]; p += 2
                        return data[p:p+length*2].decode('utf-16-le', errors='replace')
                except Exception:
                    return ''

            # --- 遍历 XML 节点 ---
            pos = 8 + sp_size
            print(f"  Start parsing XML nodes from pos={pos}")
            element_count = 0
            while pos + 8 <= len(data):
                chunk_type   = struct.unpack_from('<H', data, pos)[0]
                chunk_hdr_sz = struct.unpack_from('<H', data, pos+2)[0]
                chunk_size   = struct.unpack_from('<I', data, pos+4)[0]
                if chunk_size == 0 or pos + chunk_size > len(data):
                    break
                if chunk_type == 0x0102:  # START_ELEMENT
                    name_idx   = struct.unpack_from('<i', data, pos+20)[0]
                    attr_size  = struct.unpack_from('<H', data, pos+26)[0]
                    attr_count = struct.unpack_from('<H', data, pos+28)[0]
                    if attr_size == 0:
                        attr_size = 20  # 标准大小
                    elem = read_str(name_idx)
                    element_count += 1
                    if element_count <= 10:  # 只显示前10个元素
                        print(f"    Element #{element_count}: '{elem}' (attrs={attr_count})")
                    attrs = {}
                    a_base = pos + chunk_hdr_sz
                    for ai in range(attr_count):
                        ap = a_base + ai * attr_size
                        if ap + 20 > len(data): break
                        a_ns_idx = struct.unpack_from('<i', data, ap)[0]
                        a_name_idx = struct.unpack_from('<i', data, ap+4)[0]
                        a_raw   = struct.unpack_from('<i', data, ap+8)[0]
                        a_dtype = data[ap+15]
                        a_data  = struct.unpack_from('<I', data, ap+16)[0]
                        # 读取属性名（可能包含命名空间）
                        a_name  = read_str(a_name_idx)
                        # 先通过 dataType 判断，避免 rawValue=0 时误读字符串
                        if a_dtype == 0x03:    # TYPE_STRING
                            a_val = read_str(a_raw) if a_raw >= 0 else ''
                        elif a_dtype == 0x10:  # INT_DEC
                            a_val = str(a_data)
                        elif a_dtype == 0x11:  # INT_HEX
                            a_val = hex(a_data)
                        elif a_dtype == 0x12:  # BOOLEAN
                            a_val = 'true' if a_data else 'false'
                        else:
                            # 引用类型等，尝试 rawValue 字符串
                            a_val = read_str(a_raw) if a_raw >= 0 else str(a_data)
                        if a_name:
                            # 同时存储带前缀和不带前缀的版本，以兼容不同格式
                            attrs[a_name] = a_val
                            # 如果属性名中有冒号，也存储冒号后的简短名
                            if ':' in a_name:
                                short_name = a_name.split(':')[-1]
                                attrs[short_name] = a_val
                    
                    # 调试：显示关键元素的属性
                    if elem in ['manifest', 'uses-sdk']:
                        print(f"  Element '{elem}' found, attrs count={len(attrs)}")
                        if attrs:
                            print(f"    attrs: {attrs}")
                    
                    # 辅助函数：尝试多种可能的属性名
                    def get_attr(attrs, *keys):
                        for key in keys:
                            if key in attrs and attrs[key]:
                                return attrs[key]
                        return ''
                    
                    if elem == 'manifest':
                        result['package']     = get_attr(attrs, 'package')
                        result['versionCode'] = get_attr(attrs, 'versionCode', 'android:versionCode')
                        result['versionName'] = get_attr(attrs, 'versionName', 'android:versionName')
                        result['compileSdkVersion'] = get_attr(attrs, 'compileSdkVersion', 'android:compileSdkVersion')
                    elif elem == 'uses-sdk':
                        result['minSdkVersion']    = get_attr(attrs, 'minSdkVersion', 'android:minSdkVersion')
                        result['targetSdkVersion'] = get_attr(attrs, 'targetSdkVersion', 'android:targetSdkVersion')
                    elif elem == 'application':
                        lbl = get_attr(attrs, 'label', 'android:label')
                        # 只取字符串值（非资源引用 @0x...）
                        if lbl and not lbl.startswith('@') and not lbl.startswith('0x'):
                            result['appLabel'] = lbl
                    elif elem == 'uses-permission':
                        perm = get_attr(attrs, 'name', 'android:name')
                        if perm and '.' in perm:
                            result['permissions'].append(perm)
                pos += chunk_size
            print(f"  Total elements parsed: {element_count}")
        except Exception as e:
            print(f"binary xml parse error: {e}")
            import traceback
            traceback.print_exc()
        return result

    def _analyze_manifest_fallback(self, apk_path, info):
        """无aapt时从 AndroidManifest.xml 二进制 XML 提取信息（APK/AAB均支持）"""
        # 根据文件类型确定manifest路径优先级
        # AAB: base/manifest/AndroidManifest.xml 优先
        # APK: AndroidManifest.xml 在根目录
        is_aab = apk_path.lower().endswith('.aab')
        if is_aab:
            manifest_paths = ['base/manifest/AndroidManifest.xml', 'AndroidManifest.xml']
        else:
            manifest_paths = ['AndroidManifest.xml', 'base/manifest/AndroidManifest.xml']
        
        data = None
        used_path = None
        try:
            with zipfile.ZipFile(apk_path, 'r') as zf:
                names = zf.namelist()
                print(f"Searching manifest in {'AAB' if is_aab else 'APK'}, available files: {len(names)}")
                
                # 对于 AAB，尝试多个可能的路径
                if is_aab:
                    # AAB 可能有多个 manifest 位置
                    possible_paths = [
                        'base/manifest/AndroidManifest.xml',
                        'AndroidManifest.xml',
                        'base/AndroidManifest.xml'
                    ]
                    # 也尝试查找未压缩的原始 manifest
                    for name in names:
                        if 'manifest' in name.lower() and name.endswith('.xml'):
                            if name not in possible_paths:
                                possible_paths.append(name)
                    manifest_paths = possible_paths
                    print(f"  Trying AAB manifest paths: {manifest_paths[:5]}")
                
                for mp in manifest_paths:
                    if mp in names:
                        data = zf.read(mp)
                        used_path = mp
                        print(f"Found manifest at: {used_path}")
                        
                        # 检查是否是文本 XML
                        if data[:5] == b'<?xml':
                            print("  Detected plain text XML, parsing...")
                            parsed_xml = self._parse_text_xml(data)
                            if parsed_xml:
                                self._apply_parsed_info(parsed_xml, info, data)
                                return
                        
                        # 检查是否是 Protobuf 格式 (AAB特有)
                        if data[:2] in [b'\x0a\xcb', b'\x0a\xc0', b'\x0a\xc8']:
                            print("  Detected Protobuf format (AAB manifest)")
                            # 尝试使用 bundletool
                            if self._analyze_aab_with_bundletool(apk_path, info):
                                return
                            # 如果没有 bundletool，尝试从资源文件中提取部分信息
                            print("  Bundletool not available, trying alternative methods...")
                            if self._analyze_aab_fallback(apk_path, info, zf):
                                return
                        
                        # 尝试传统二进制 XML 解析
                        break
                    else:
                        if len(manifest_paths) <= 5:
                            print(f"  {mp} not found")
        except Exception as e:
            print(f"manifest fallback open failed: {e}")
            return
        if not data:
            print("manifest not found in zip")
            return
        print(f"Parsing manifest from: {used_path}")
        parsed = self._parse_binary_xml(data)
        print(f"Parsed result: package={parsed.get('package')}, versionCode={parsed.get('versionCode')}, versionName={parsed.get('versionName')}")
        print(f"  minSdk={parsed.get('minSdkVersion')}, targetSdk={parsed.get('targetSdkVersion')}, compileSdk={parsed.get('compileSdkVersion')}")
        self._apply_parsed_info(parsed, info, data)
    
    def _parse_text_xml(self, data):
        """解析纯文本 XML 格式的 manifest"""
        try:
            import xml.etree.ElementTree as ET
            text = data.decode('utf-8')
            root = ET.fromstring(text)
            result = {'package': '', 'versionCode': '', 'versionName': '',
                      'minSdkVersion': '', 'targetSdkVersion': '', 'compileSdkVersion': '',
                      'appLabel': '', 'permissions': []}
            
            # 从 manifest 元素获取属性
            ns = {'android': 'http://schemas.android.com/apk/res/android'}
            result['package'] = root.get('package', '')
            result['versionCode'] = root.get('{http://schemas.android.com/apk/res/android}versionCode', '')
            result['versionName'] = root.get('{http://schemas.android.com/apk/res/android}versionName', '')
            result['compileSdkVersion'] = root.get('{http://schemas.android.com/apk/res/android}compileSdkVersion', '')
            
            # 查找 uses-sdk
            uses_sdk = root.find('uses-sdk')
            if uses_sdk is not None:
                result['minSdkVersion'] = uses_sdk.get('{http://schemas.android.com/apk/res/android}minSdkVersion', '')
                result['targetSdkVersion'] = uses_sdk.get('{http://schemas.android.com/apk/res/android}targetSdkVersion', '')
            
            # 查找 application label
            app = root.find('application')
            if app is not None:
                label = app.get('{http://schemas.android.com/apk/res/android}label', '')
                if label and not label.startswith('@'):
                    result['appLabel'] = label
            
            # 查找权限
            for perm in root.findall('uses-permission'):
                name = perm.get('{http://schemas.android.com/apk/res/android}name', '')
                if name and '.' in name:
                    result['permissions'].append(name)
            
            print(f"  Text XML parsed: package={result['package']}, versionCode={result['versionCode']}")
            return result
        except Exception as e:
            print(f"  Text XML parse error: {e}")
            return None
    
    def _analyze_aab_with_bundletool(self, aab_path, info):
        """使用 bundletool 分析 AAB"""
        if not self.bundletool_path:
            return False
        try:
            # 使用 bundletool dump manifest
            result = subprocess.run(
                ['java', '-jar', self.bundletool_path, 'dump', 'manifest', '--bundle=' + aab_path],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout:
                print("  Using bundletool to extract manifest...")
                parsed_xml = self._parse_text_xml(result.stdout.encode('utf-8'))
                if parsed_xml:
                    self._apply_parsed_info(parsed_xml, info, result.stdout.encode('utf-8'))
                    return True
        except Exception as e:
            print(f"  Bundletool error: {e}")
        return False
    
    def _analyze_aab_fallback(self, aab_path, info, zf):
        """AAB 的降级分析方案"""
        try:
            # 尝试从 BundleConfig.pb 或其他文件推断信息
            # 至少可以从 SO 文件路径推断一些信息
            print("  AAB Protobuf manifest detected.")
            print("  To fully analyze AAB files, please:")
            print("    1. Install bundletool: download from https://github.com/google/bundletool")
            print("    2. Set BUNDLETOOL_JAR environment variable to bundletool.jar path")
            print("    Or convert AAB to APK first using bundletool or Play Console")
            
            # 尝试从文件名或其他元数据推断包名
            # 查找是否有其他可读的 manifest
            for name in zf.namelist():
                if name.endswith('.xml') and 'manifest' in name.lower():
                    try:
                        data = zf.read(name)
                        if data[:5] == b'<?xml':
                            print(f"  Found alternative manifest: {name}")
                            parsed_xml = self._parse_text_xml(data)
                            if parsed_xml and parsed_xml.get('package'):
                                self._apply_parsed_info(parsed_xml, info, data)
                                return True
                    except:
                        pass
            
            # 设置一个提示性的文本
            info.app_name = "(AAB需要bundletool解析)"
            return False
        except Exception as e:
            print(f"  AAB fallback error: {e}")
            return False
    
    def _apply_parsed_info(self, parsed, info, data):
        if parsed['package']:
            info.package_name = parsed['package']
        if parsed['versionCode']:
            info.version_code = parsed['versionCode']
        if parsed['versionName']:
            info.version_name = parsed['versionName']
        if parsed['minSdkVersion']:
            info.min_sdk = parsed['minSdkVersion']
        if parsed['targetSdkVersion']:
            info.target_sdk = parsed['targetSdkVersion']
        if parsed.get('compileSdkVersion'):
            info.compile_sdk = parsed['compileSdkVersion']
        if parsed['appLabel']:
            info.app_name = parsed['appLabel']
        if parsed['permissions']:
            info.permissions = parsed['permissions']
        # 若二进制 XML 解析未取到权限，用字符串搜索兜底
        if not info.permissions:
            info.permissions = self._search_permissions_in_bytes(data)

    def _search_permissions_in_bytes(self, data):
        """在二进制数据中搜索 android 权限字符串（兜底方案）"""
        found, seen = [], set()
        # UTF-8 池（ASCII 字节直接可见）
        try:
            text8 = data.decode('latin-1')
            for m in re.finditer(r'android\.[a-z]+\.permission\.[A-Z_]+|android\.permission\.[A-Z_]+', text8):
                p = m.group()
                if p not in seen:
                    seen.add(p); found.append(p)
        except Exception:
            pass
        # UTF-16-LE 池
        try:
            text16 = data.decode('utf-16-le', errors='ignore')
            for m in re.finditer(r'android\.[a-z]+\.permission\.[A-Z_]+|android\.permission\.[A-Z_]+', text16):
                p = m.group()
                if p not in seen:
                    seen.add(p); found.append(p)
        except Exception:
            pass
        return found

    def _check_16kb_alignment(self, apk_path):
        try:
            with zipfile.ZipFile(apk_path, 'r') as zf:
                for fi in zf.infolist():
                    if fi.filename.endswith('.so') and fi.header_offset % 16384 != 0:
                        return False
                return True
        except:
            return False
    
    def extract_icon(self, apk_path, output_dir):
        try:
            with zipfile.ZipFile(apk_path, 'r') as zf:
                for name in zf.namelist():
                    if re.match(r'res/mipmap-.*hdpi.*/ic_launcher.*\.png', name) or re.match(r'res/drawable-.*hdpi.*/ic_launcher.*\.png', name):
                        output_path = os.path.join(output_dir, 'icon.png')
                        with zf.open(name) as src, open(output_path, 'wb') as dst:
                            dst.write(src.read())
                        return output_path
        except:
            pass
        return None
    
    def extract_manifest(self, apk_path, output_dir):
        if not self.aapt_path: return None
        try:
            result = subprocess.run([self.aapt_path, 'dump', 'xmltree', apk_path, 'AndroidManifest.xml'], capture_output=True, text=True, timeout=30)
            output_path = os.path.join(output_dir, 'AndroidManifest.txt')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            return output_path
        except:
            return None
    
    def compare_apks(self, apk1_path, apk2_path):
        info1, info2 = self.analyze(apk1_path), self.analyze(apk2_path)
        return {
            'version_changed': info1.version_code != info2.version_code,
            'version_code_diff': (info1.version_code, info2.version_code),
            'version_name_diff': (info1.version_name, info2.version_name),
            'size_diff': info2.file_size - info1.file_size,
            'permissions_added': list(set(info2.permissions) - set(info1.permissions)),
            'permissions_removed': list(set(info1.permissions) - set(info2.permissions)),
            'so_files_added': list(set(info2.so_files) - set(info1.so_files)),
            'so_files_removed': list(set(info1.so_files) - set(info2.so_files)),
            'abis_changed': info1.abis != info2.abis,
        }
