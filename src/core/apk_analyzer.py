#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
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
    app_name: str = ""
    permissions: List[str] = field(default_factory=list)
    abis: List[str] = field(default_factory=list)
    so_files: List[str] = field(default_factory=list)
    is_16kb_aligned: bool = False
    has_x86: bool = False
    signature_info: Dict = field(default_factory=dict)
    file_size: int = 0
    md5: str = ""
    sha1: str = ""
    sha256: str = ""
    file_type: str = "apk"

class APKAnalyzer:
    SUPPORTED_EXTENSIONS = ['.apk', '.aab']
    
    def __init__(self):
        self.aapt_path = self._find_aapt()
    
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
        if ext == '.apk' and self.aapt_path:
            self._analyze_with_aapt(file_path, info)
        self._analyze_zip_contents(file_path, info)
        if ext == '.apk':
            info.is_16kb_aligned = self._check_16kb_alignment(file_path)
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
            m = re.search(r"application-label:'([^']+)'", output)
            if m: info.app_name = m.group(1)
            info.permissions = re.findall(r"uses-permission: name='([^']+)'", output)
            abis = re.findall(r"native-code: '([^']+)'", output)
            if abis: info.abis = abis[0].split("' '")
        except Exception as e:
            print(f"aapt failed: {e}")
    
    def _analyze_zip_contents(self, file_path, info):
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                so_files, abis_found = [], set()
                for name in zf.namelist():
                    if name.endswith('.so'):
                        so_files.append(name)
                        parts = name.split('/')
                        for i, part in enumerate(parts):
                            if part == 'lib' and i + 1 < len(parts):
                                abi = parts[i + 1]
                                if abi in ['arm64-v8a', 'armeabi-v7a', 'armeabi', 'x86', 'x86_64']:
                                    abis_found.add(abi)
                info.so_files = so_files
                if not info.abis: info.abis = list(abis_found)
                info.has_x86 = 'x86' in info.abis or 'x86_64' in info.abis
        except Exception as e:
            print(f"ZIP failed: {e}")
    
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
