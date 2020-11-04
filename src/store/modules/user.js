/**
 * 和用户信息有关的vuex
 */

import { getUserRole } from '@/api/login'
import { setCookie, removeCookie } from '@/utils/cookie'

const state = {
    userName: '',  // 用户名称
    userRole: '',  // 用户角色
    userToken: ''  // 用户的token
}

const mutations = {
    setToken(state, token) {
        state.userToken = token  // 设置token
    },
    clearUserInfo(state) {
        removeCookie('token')  // 清除cookie里的token
        state.userRole = ''  // 清除用户名
        state.userToken = ''  // 清除token
    },
    setRole(state, data) {
        const { role, userName } = data  // 获取用户的role信息和userName
        state.userRole = role  // 设置role
        state.userName = userName  // 设置用户名称
    }
}

const getters = {
    userToken: state => state.userToken,  // 用户的token
    userRole: state => state.userRole,  // 用户的role
    userName: state => state.userName,  // 用户的名称
}

const actions = {
    setToken({ commit }, token) {
        // 设置cookie,每次刷新之后vuex中的state都会被浏览器释放掉,所以对于token需要存储在
        // cookie当中,每次权限验证的时候都需要根据token去重新获取用户的信息
        setCookie({ key: 'token', value: token })
        commit('setToken', token)  // 设置token
    },
    clearUserInfo({ commit }) {
        return new Promise((resolve, reject) => {
            commit('clearUserInfo')
            const code = 200
            resolve({ code })
        })
    },
    setRole({ commit }, token) {
        // 先根据token从数据库获取用户的role
        return new Promise((resolve, reject) => {
            getUserRole(token).then(({ data }) => {
                commit('setRole', data)
                const { role } = data
                resolve({ role })  // 返回role
            }).catch(error => {
                reject(error)
            })
        })

    }
}

export default {
    namespaced: true,
    state,
    mutations,
    actions,
    getters
}
