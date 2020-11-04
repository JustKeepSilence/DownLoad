/**
 * 和下载有关的后台请求函数接口
 */

import request from '@/utils/request'

// 向aria2中添加下载内容
 const addDownloadItems = (data)=>{
    return request({
        url: 'add_download_items',
        method: 'post',
        data
    })
 }

 export {
     addDownloadItems
 }