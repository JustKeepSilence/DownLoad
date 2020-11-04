#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/9/17 8:35
# Author  : He
# Github : https://github.com/JustKeepSilence

# 登陆接口的后台函数

import hashlib
import datetime

from aiohttp import web

from util import db
from util.decorator import method_dec
from util.data_structure import User, UserRole

__all__ = ('login', 'get_user_info')


# 登陆界面的接口
@method_dec("/login")
async def login(request):
    """用户登陆
       `username`: 用户民
       `password`: 密码
       `return`: dict{code: int, msg: str, username: str, token: str, avatar: str}
    """

    try:
        request_data = await request.json()
        username = request_data.get("username")  # 获取用户名
        password = request_data.get("password")  # 获取密码
        # 每次重新登陆的时候都会根据用户名和当前时间去重新生成特定的token,这样保证了用户只能单点登陆
        user_token = hashlib.md5((username[:-2] + str(datetime.datetime.now())).encode("utf-8")).hexdigest()
        query_data = [User(*item) async for item in await
                      db.get_data(f"select * from user_view where username='{username}'")]  # 从数据库获取用户信息
        if query_data[0].password == password:
            # 如果用户输入的密码正确
            await db.change_data(f"update user_cfg set {user_token=} where {username=}")  # 更新用户的token
            return web.json_response({"msg": "登陆成功!", "code": 200, "name": username,
                                      "token": user_token,
                                      "avatar": query_data[0].user_avatar})
        else:
            return web.json_response({"msg": "密码错误", "code": 500})
    except (IndexError, Exception):
        return web.json_response({"msg": "用户名错误", "code": 500})


@method_dec("/get_user_info", 'get')
async def get_user_info(request):
    """根据token获取用户信息
       `token`: 用户的token信息
       `return`: dict{code: int, data: dict{user_role: str}}
    """

    token = request.headers.get('Token')  # 获取token
    response_data = [{"role": item.role_name, "userName": item.username} for item in [UserRole(*item)
                                                                                      async for item in
                                                                                      await db.get_data(
                                                                                          f"select username, role_name from user_view where usertoken='{token}'")]]
    return web.json_response({"data": response_data[0], "msg": "success", "code": 200})
