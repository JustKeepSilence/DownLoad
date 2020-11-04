#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/6/28 19:36
# Author  : He
# Github : https://github.com/JustKeepSilence


# 异步操作数据库的模块


import typing
import pymysql
from databases import Database


_SQL_IP = "192.168.0.199"  # 数据库的IP
_SQL_PORT = 3306  # 数据库的端口号
_SQL_USERNAME = "sa"  # 用户名
_SQL_PASSWORD = "admin@123"  # 密码
_SQL_DATABASE = "download"  # 数据库的名称
_CONNECTION_URL = f"mysql://{_SQL_USERNAME}:{_SQL_PASSWORD}@{_SQL_IP}:{_SQL_PORT}/{_SQL_DATABASE}"


async def get_data(command: str) -> typing.AsyncGenerator[typing.Mapping, None]:

    """从数据库查询数据"""

    db = Database(_CONNECTION_URL)
    await db.connect()
    return db.iterate(query=command)


async def change_data(command: str) -> bool:

    """增加,删除或者改变数据库中的数据
       insert, delete, update
    """

    db = Database(_CONNECTION_URL)
    await db.connect()
    res = await db.execute(command)
    return res


def change_data_sync(command: str) -> bool:
    connection = pymysql.Connect(host=_SQL_IP, user=_SQL_USERNAME, password=_SQL_PASSWORD,
                                 database=_SQL_DATABASE, port=_SQL_PORT)
    try:
        cursor = connection.cursor()
        cursor.execute(command)
        connection.commit()
        return True
    except pymysql.err.ProgrammingError:
        # SQL语句出现错误
        return False
    except Exception as e:
        print("aaa")
    finally:
        connection.close()
