# download

> Python-based real-time crawler project

## JS Environment

``` bash
# install dependencies

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build

# build for production and view the bundle analyzer report
npm run build --report

# run unit tests
npm run unit

# run all tests
npm test
```

For a detailed explanation on how things work, check out the [guide](http://vuejs-templates.github.io/webpack/) and [docs for vue-loader](http://vuejs.github.io/vue-loader).


## Python Environment
```bash
packages            version
python               >=3.8
aiofiles             0.5.0
aiohttp              3.6.2
aiohttp-cors         0.7.0
aiohttp-proxy        0.1.2
aiomysql             0.0.20
scrapy               2.3.0
```

## 2020-11-4 update
```bash
1.整个前端界面重写,完善了路由权限验证，侧边栏
2.websocket改用websocket.io
3.电影搜索界面基本完成
(1) 可以进行搜索,如果数据库中不存在,则可以调用爬虫进行搜索
(2) 电影的收藏，删除功能已经实现
(3) 爬虫日志可以实时查看
4.存在的问题
(1) 多个爬虫同时爬取,并行爬取
(2) RPC调用aria2下载时界面的完善
(3) 后续可能考虑使用go重构来进行爬虫的并发爬取，以及RPC进行并发下载
```
