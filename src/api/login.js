/**
 * 登陆时候的密码表单规则验证
 * 验证的规则为用户输入的密码必须得包含数字和字母的组合
 */

import request from '@/utils/request'

const passWordValidator = (rule, value, callback) => {
    const numberReg = /^[\d|\.]*$/  // 验证字符串是否全为数字
    const stringReg = /[0-9]/  // 验证字符串中是否含有数字
    if (numberReg.test(value)) {
        callback(new Error('密码不能全为数字'))
    }
    else if (stringReg.test(value)) {
        callback()
    }
    else {
        callback(new Error('密码不能全为字母'))
    }
}

/**
 * 验证用户登陆，返回用户的token
 */

const userLogin = (data) => {
    return request({
        url: '/login',
        method: 'post',
        data
    })
}

const getUserRole = (data) => {
    return request({
        url: '/get_user_info',
        method: 'get',
        params: data
    })
}

export {
    passWordValidator,
    userLogin,
    getUserRole
}
