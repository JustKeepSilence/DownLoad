/**
 * 和动态路由相关的vuex
 */

import { constantRoutes, asyncRoutes } from '@/router'

const state = {
    asyncRoutes: []  // 异步路由

}

const getters = {
    asyncRoutes: state => state.asyncRoutes  // 最终用户的异步路由
}

const mutations = {
    getAsyncRoutes: (state, dynamicRoutes) => {
        state.asyncRoutes = constantRoutes.concat(dynamicRoutes)  // 最终的路由
        // 是由没有权限的路由的动态生成的路由所组合而成
    }
}

const actions = {
    getAsyncRoutes: ({ commit }, userRole) => {
        return new Promise((resolve, reject) => {
            let dynamicRoutes = []
            checkPermission(asyncRoutes, userRole, dynamicRoutes)
            commit('getAsyncRoutes', dynamicRoutes)  // 根据用户角色筛选路由
            resolve({ dynamicRoutes })  // 该异步操作返回的是动态路由,通过addRoutes
            // 去进行动态的挂载
        })
    },
    clearRoutes: ({commit}) => {
        // 清空用户的路由
        
    }

}


// 检查给定路由的权限
// 检查的逻辑为如果含有子路由，则进行递归检查,此时的route参数是包含了路由对象的列表
// dynamicRoutes为根据权限生成的动态路由
const checkPermission = (route, userRole, dynamicRoutes = []) => {
    route.forEach(item => {
        const { meta: { role } } = item  // 整个父级路由的权限
        if (role.indexOf(userRole) === -1) {
            // 没有权限则直接结束,forEach中不可使用continue
            return true
        }
        else {
            // 有父级路由的权限
            if (item.children && item.children.length > 0) {
                // 有子路由的时候则进行递归调用
                let temp = Object.assign({}, item)  // 深复制,不可以使用JSON.parse
                // 因为组件对象使用parse页面会出现错误,首先通过深复制获得该路由对象
                temp.children = []  // 将该对象的子路由设置为空
                dynamicRoutes.push(temp)  // 在动态路由中加入该级路由
                // 进行下一次递归的时候第一个参数即为该及路由的子路由列表，第三个参数及为dynamicRoutes中
                // 刚刚加入的路由对象的children
                checkPermission(item.children, userRole, dynamicRoutes[dynamicRoutes.length - 1].children)
            }
            else {
                // 没有子路由或者子路由为空
                dynamicRoutes.push(item)  // 直接添加子路由
            }


        }
    })
}

export default {
    namespaced: true,
    state,
    mutations,
    actions,
    getters
}
