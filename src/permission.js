/**
 * 整个页面的权限验证,在每次进入一个页面之前都验证对应的权限
 * 并且动态的生成路由
 */

import NProgress from 'nprogress'  // 导入进度条
import 'nprogress/nprogress.css'  // 导入样式

NProgress.configure({ showSpinner: false })  // 不显示加载指示器
NProgress.configure({ ease: 'ease', speed: 500 })  // 配置动画效果

import router from './router'
import store from './store'
import { getCookie } from '@/utils/cookie'
import { Message } from 'element-ui'
import {resetRouter} from './router'

// 每次进入一个路由之前进行权限验证
// 验证的规则为如果是登陆页面则直接跳转,否则根据token去获取用户权限,再根据用户权限去动态
// 挂载路由,如果没有token或者是获取用户权限失败则跳转到登陆页面
router.beforeEach(async (to, from, next) => {
        document.title = to.meta.title || '404'  // 设置页面的标题
        if (to.path === '/login') {
            next()  // 如果是登陆页则直接跳转
        }
        else {
            const token = getCookie('token') // 获取cookie中的用户token
            if(token){
            // 如果有token则根据token去获取用户信息,否则跳转到登陆也页面
            let userName = store.getters['user/userRole']  // 获取用户的角色
            if (!userName) {
                // 如果用户名为空则根据token去重新获取用户的权限信息
                store.dispatch('user/setRole', { token }).then(({ role }) => {
                    store.dispatch('routes/getAsyncRoutes', role).then(async ({ dynamicRoutes }) => {
                        await resetRouter()  // 清空路由
                        router.addRoutes(dynamicRoutes)  // 动态挂载路由
                        if(from.path === '/login'){
                            // 登陆成功以后提示登陆成功
                            Message({
                                message: '登陆成功',
                                type: 'success'
                            })
                        }
                        next({...to, replace: true})  // 确保addRoutes方法被调用
                    })
                }).catch((error) => {
                    Message({
                        message: '获取用户权限失败' + error,
                        type: 'error'
                    })
                    next('/')  // 跳转到登陆界面
                })
            }
            else {
                NProgress.start()  // 开始
                next()
            }
        }
        else{
            next('/')
        }
        }
})


router.afterEach((to, from)=>{
    NProgress.done()  // 结束
})
