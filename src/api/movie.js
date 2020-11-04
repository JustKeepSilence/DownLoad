/**
 * 和电影搜索界面相关的请求
 */


import request from '@/utils/request'


const getWebsiteLists = (data) => {
    return request({
        url: 'get_website_list',
        method: 'post',
        data
    })
}

const getSearchHistoryLists = (data) => {
    return request({
        url: 'get_search_history_list',
        method: 'post',
        data
    })
}

const deleteItem = (data) => {
    return request({
        url: 'delete_movie_item',
        method: 'post',
        data
    })
}

// 获取所有的电影数据
const getAllMovieData = (data)=>{
    return request({
        url: 'get_all_movie_data',
        method: 'post',
        data
    })
}

export{
    getWebsiteLists,
    getSearchHistoryLists,
    deleteItem,
    getAllMovieData
}
