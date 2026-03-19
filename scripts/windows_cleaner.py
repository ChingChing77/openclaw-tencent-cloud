#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 系统清理 Bot
功能：自动清理 Windows 系统垃圾文件
"""

import os
import shutil
import glob
from datetime import datetime

# Windows 垃圾文件路径
CLEAN_PATHS = {
    # 临时文件
    "Windows临时文件": [
        os.path.expandvars(r"%WINDIR%\Temp"),
        os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
    ],
    # 用户临时文件
    "用户缓存": [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\INetCache"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer"),
    ],
    # 浏览器缓存
    "浏览器缓存": [
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache"),
    ],
    # Windows 更新缓存
    "更新缓存": [
        os.path.expandvars(r"%WINDIR%\SoftwareDistribution\Download"),
    ],
    # 回收站
    "回收站": ["$Recycle.Bin"],
    # 日志文件
    "日志文件": [
        os.path.expandvars(r"%WINDIR%\Logs"),
        os.path.expandvars(r"%WINDIR%\Panther"),
    ],
}

def get_folder_size(path):
    """获取文件夹大小"""
    total_size = 0
    try:
        if os.path.exists(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total_size += os.path.getsize(fp)
                    except:
                        pass
    except:
        pass
    return total_size

def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def clean_folder(path, category_name):
    """清理指定文件夹"""
    if not os.path.exists(path):
        return 0, 0
    
    file_count = 0
    freed_size = 0
    
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    os.remove(item_path)
                    file_count += 1
                    freed_size += size
                elif os.path.isdir(item_path):
                    size = get_folder_size(item_path)
                    shutil.rmtree(item_path)
                    file_count += 1
                    freed_size += size
            except Exception as e:
                pass  # 跳过无法删除的文件
    except Exception as e:
        pass
    
    return file_count, freed_size

def run_cleaner(dry_run=False):
    """运行清理程序"""
    print("=" * 50)
    print("🧹 Windows 系统清理 Bot")
    print("=" * 50)
    print(f"🕐 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    if dry_run:
        print("⚠️ 演示模式 (dry-run)，不会实际删除文件")
        print("-" * 50)
    
    total_files = 0
    total_freed = 0
    
    for category, paths in CLEAN_PATHS.items():
        print(f"\n📂 正在清理: {category}")
        cat_files = 0
        cat_size = 0
        
        for path in paths:
            if dry_run:
                if os.path.exists(path):
                    size = get_folder_size(path)
                    print(f"   {path}: {format_size(size)}")
                    cat_size += size
            else:
                files, size = clean_folder(path, category)
                cat_files += files
                cat_size += size
        
        print(f"   → {cat_files} 个文件, {format_size(cat_size)}")
        total_files += cat_files
        total_freed += cat_size
    
    print("\n" + "=" * 50)
    print(f"✅ 清理完成!")
    print(f"   总计: {total_files} 个文件")
    print(f"   释放空间: {format_size(total_freed)}")
    print("=" * 50)
    
    if dry_run:
        print("\n💡 实际运行请使用: python windows_cleaner.py")

if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    run_cleaner(dry_run=dry_run)
