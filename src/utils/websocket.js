/**
 * websocket连接
 */

const socketBaseUrl = 'ws://192.168.0.199:8082'  // websocket后台的url

// 连接搜索电影的websocket
const connectSearchMovieSocket = ()=>{
    return new WebSocket(socketBaseUrl + '/search_movie')
}

export {
    connectSearchMovieSocket
}