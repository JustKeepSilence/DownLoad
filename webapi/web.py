#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/7/5 14:33
# Author  : He
# Github : https://github.com/JustKeepSilence

import aiohttp_cors

from api.login import *
from api.movie import *
from api.download import *
from util.config import *

app = web.Application()
sio.attach(app)


@sio.event(namespace="/")
async def connect(sid, environ):
    # 连接socketio
    pass

@sio.event(namespace="/movie")
async def disconnect(sid):
    # 断开连接
    pass


if __name__ == "__main__":
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    for parm in PARAM_LIST:
        if parm["register"]:
            app.router.add_route(parm["method"], parm["url"], parm["func"])
    for route in list(app.router.routes()):
        try:
            cors.add(route)
        except ValueError:
            pass
    web.run_app(app, host=IP, port=PORT)
