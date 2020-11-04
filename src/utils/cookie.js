/**
 * 读写cookie,使用的是js-cookie
 * https://github.com/js-cookie/js-cookie
 */

 import Cookies from 'js-cookie'

const setCookie = ({key, value})=>{
    // 设置cookie,key为键,value为值
    Cookies.set(key, value)
}

const getCookie = (key)=>{
    // 获取cookie
    return Cookies.get(key)
}

const removeCookie = async (key)=>{
    Cookies.remove(key)
}

export {
    setCookie,
    getCookie,
    removeCookie
}