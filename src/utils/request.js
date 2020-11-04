/**
 * 使用axios发送get和post请求
 */

import axios from 'axios'
import { getCookie } from '@/utils/cookie'
import {Message} from 'element-ui'

const requestBaseUrl = 'http://192.168.0.199:8082'  // 后台接口的url

const request = axios.create({
    baseURL: requestBaseUrl,  // 请求的baseurl
    timeout: 5000  // 设置请求的超时时间
})

// 添加请求拦截器
request.interceptors.request.use(
    config => {
        // 在发送请求之前进行的配置
        const userToken = getCookie('token') // 获取cookie中的用户token
        if(userToken){
            // 如果有token,则所有的请求都必须携带上token信息
            config.headers['token'] = userToken
        }
        return config
    },
    error=>{
        return Promise.reject(error)
    }
)

// 添加响应拦截器
request.interceptors.response.use(
    response=>{
        const res = response.data // 获取响应的数据
        const code = res.code  // 响应的状态码
        if (code !== 200){
            if(code === 503){
                Message({
                    message: '接口不可用',
                    type: 'error'
                })
            }
            else if(code === 404){
                Message({
                    message: '接口不存在',
                    type: 'error'
                })
            }
            else{
            Message({
                message: res.msg || 'Error',  // 错误的信息
                type: 'error'  // Message的类型
            })
        }
        return new Promise.reject(new Error(res.msg || 'Error'))
        }
        else{
            return  res  // 返回响应的数据
        }
    },
    error=>{
        console.log(error)
        Message({
            message: error.data || 'Error',
            type: 'error'
        })
        return Promise.reject(error)
    }
)

export default request
