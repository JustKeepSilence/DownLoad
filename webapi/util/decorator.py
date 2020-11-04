#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/9/17 8:39
# Author  : He
# Github : https://github.com/JustKeepSilence

# 装饰器函数,用于将所有后台函数的信息写入到param_list全局变量中

import re
from functools import wraps
from typing import Optional, Callable

from util.config import *

def method_dec(url: str, method: Optional[str] = "post",
               register: Optional[bool] = True, ) -> Callable:
  """函数的装饰器函数,用来获得接口函数的相关信息"""

  def decorate(func: Callable):
    @wraps(func)
    def inner_func(*args, **kwargs):
      docs = func.__doc__
      descriptions = re.search(r"(.*?)`", docs, re.DOTALL).group(1).replace(" ", "")  # 函数的描述
      input_params = re.search(r"`(.*)return`", docs, re.DOTALL).group(1).replace("`", "").replace(" ", "")  # 输入
      output_params = re.search(r"return\s*`:(.*)", docs, re.DOTALL).group(1).replace("`", "").replace(" ", "")  # 输出
      PARAM_LIST.append({"name": func.__name__, "method": method, "url": url,
                         "full_url": f"{IP}:{PORT}{url}",
                         "register": register, "func": func, "descriptions": descriptions,
                         "input_params": input_params, "output_params": output_params})
    inner_func()
    return func
  return decorate
