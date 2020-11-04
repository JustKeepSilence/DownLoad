#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/7/18 23:05
# Author  : He
# Github : https://github.com/JustKeepSilence


# 获取文件的图标


import os
import win32api
import win32con
import win32ui
import win32gui

from PIL import Image
from win32com.shell import shell, shellcon


def get_icon(PATH, size):
    SHGFI_ICON = 0x000000100
    SHGFI_ICONLOCATION = 0x000001000
    if size == "small":
        SHIL_SIZE = 0x00001
    elif size == "large":
        SHIL_SIZE = 0x00002
    else:
        raise TypeError("Invalid argument for 'size'. Must be equal to 'small' or 'large'")
    ret, info = shell.SHGetFileInfo(PATH, 0, SHGFI_ICONLOCATION | SHGFI_ICON | SHIL_SIZE)
    hIcon, iIcon, dwAttr, name, typeName = info
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_x)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(hbmp)
    hdc.DrawIcon((0, 0), hIcon)
    win32gui.DestroyIcon(hIcon)

    bmpinfo = hbmp.GetInfo()
    bmpstr = hbmp.GetBitmapBits(True)
    img = Image.frombuffer(
        "RGBA",
        (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
        bmpstr, "raw", "BGRA", 0, 1
    )

    if size == "small":
        img = img.resize((16, 16), Image.ANTIALIAS)
    return img


def get_icons(tasks: list):

    """获取已经完成任务的图标"""

    for task in tasks:
        image_name = f"./images/{task['fileName']}.png"
        if not os.path.exists(image_name):
            # 如果该图片不存在则重新读取并保存
            img = get_icon(rf"{task['filePath']}\{task['fileName']}", "large")
            img.save(image_name)  # 保存图片
        task["image"] = f"{task['fileName']}.png"  # 图片的名称
    return tasks
