import Vue from 'vue'
import Router from 'vue-router'
import DownLoad from '@/view/download'   // DownLoad组件中包含了所有页面公共的侧边栏

Vue.use(Router)

// 不需要用户权限的静态路由, path: 路由的路径,redirect: 重定向路由的路径
// component: 跳转的组件, meta:元数据{title: 页面的标题, icon: 侧边栏的按钮,
// hidden: 该路由是否在侧边栏被隐藏, 默认为false}
const constantRoutes = [
  {
    path: '/',
    redirect: '/login',
    meta: { hidden: true }
  },
  {
    path: '/login',  // 登陆界面
    name: 'Login',
    component: () => import('@/view/login'),
    meta: { title: '登陆', hidden: true }
  },
  {
    path: '',
    component: DownLoad,
    meta: { hidden: false },
    children: [
      {
        path: '/firstPage',
        name: 'FirstPage',
        component: () => import('@/view/firstPage'),
        meta: { title: 'DownLoad', icon: 'el-icon-download', hidden: false },
        
      }
    ]
  },
  {
    path: '/search',
    component: DownLoad,
    name: 'Search',
    meta: { title: '资源搜索', icon: 'el-icon-search', hidden: false },
    children: [
      {
        path: '/movie',
        name: 'Movie',
        component: () => import('@/view/search/movie'),
        meta: { title: '电影搜索', icon: 'el-icon-film', hidden: false },
      },
      {
        path: '/music',
        name: 'Music',
        component: () => import('@/view/search/music'),
        meta: { title: '音乐搜索', icon: 'el-icon-headset', hidden: false },
        children: [
          {
            path: '/test',
            name: 'Test',
            component: () => import('@/view/test'),
            meta: {title: '测试页', icon: 'el-icon-edit', hidden: false}
          }
        ]
      },
      {
        path: '/picture',
        name: 'Picture',
        component: () => import('@/view/search/image'),
        meta: { title: '图片搜索', icon: 'el-icon-picture', hidden: false }
      }
    ]
  },
  {
    path: '/news',
    component: DownLoad,
    name: 'News',
    meta: { title: '新闻头条', icon: 'el-icon-news', hidden: false },
    children: [
      {
        path: '/weibo',
        name: 'WeiBo',
        component: () => import('@/view/news/weibo'),
        meta: { title: '微博热搜', icon: 'weibo', hidden: false },
      },
      {
        path: '/today',
        name: 'Today',
        component: () => import('@/view/news/today'),
        meta: { title: '今日头条', icon: 'today', hidden: false }
      },
      {
        path: '/tecentNews',
        name: 'TecentNews',
        component: () => import('@/view/news/tencentNews'),
        meta: { title: '腾讯新闻', icon: 'tecent', hidden: false }
      }
    ]
  },
  {
    path: '/video',
    component: DownLoad,
    name: 'Video',
    meta: { title: '热门视频', icon: 'el-icon-video-play', hidden: false },
    children: [
      {
        path: '/hotVideo',
        name: 'HotVideo',
        component: () => import('@/view/video/'),
        meta: { title: '热门视频', icon: 'el-icon-video-play', hidden: false },
        
      }
    ]
  }
]

const asyncRoutes = [
  {
    path: '/user',
    component: DownLoad,
    name: 'User',
    meta: { title: '用户中心', role: ['developer', 'super_user', 'common_user'], icon: 'el-icon-user-solid', hidden: false },
    children:[
      {
        path: '/api',
        name: 'Api',
        component: () => import('@/view/user/api'),
        meta: { title: '接口管理', role: ['developer'], icon: 'el-icon-menu', hidden: false} ,
        
      },
      {
        path: '/downloadCneter',
        name: 'DownLoadCenter',
        component: () => import('@/view/user/downloadCenter'),
        meta: { title: '下载中心', role: ['developer', 'super_user', 'common_user'], icon: 'el-icon-download', hidden: false }  // 路由元数据
      },
      {
        path: '/spiderLog',
        name: 'SpiderLog',
        component: () => import('@/view/user/spiderLog'),
        meta: { title: '爬虫日志', role: ['developer', 'super_user', 'common_user'], icon: 'bug', hidden: false }  // 路由元数据
      },
      {
        path: '/userManagement',
        name: 'UserManagement',
        component: () => import('@/view/user/userManagement'),
        meta: { title: '用户管理', role: ['developer', 'super_user'], icon: 'el-icon-user-solid', hidden: false }  // 路由元数据
      },
    ]
  },
  {
    path: '*',
    name: 'Page404',
    component: () => import('@/view/404'),
    meta: { role: ['developer', 'super_user', 'common_user'], hidden: true }
  }
]

// 解决VUE路由跳转出现Redirected when going from "/xxx" to "/yyy" via a navigation guard.报错
const originalPush = Router.prototype.push
Router.prototype.push = function push(location, onResolve, onReject) {
  if (onResolve || onReject) return originalPush.call(this, location, onResolve, onReject)
  return originalPush.call(this, location).catch(err => err)
}

const router = new Router({
  routes: constantRoutes,
  mode: 'history'
})

const createRouter= () => {
  return new Router({
    routes: constantRoutes,
    mode: 'history'
  })
}

// addRoutes 方法仅仅是帮你注入新的路由，并没有帮你剔除其它路由,所以需要手动清空路由
// 为了确保其完成，需要使用async异步操作
const resetRouter = async() =>{
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}


export default router
export { constantRoutes, asyncRoutes, resetRouter }