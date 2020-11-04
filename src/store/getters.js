/*
所有vuex的getters属性
*/

const getters = {
    userToken: state=>state.user.userToken,  // 用户的token
    userRole: state=>state.user.userRole,  // 用户的role
    userName: state=>state.user.userName,  // 用户的名称
    asyncRoutes: state=>state.routes.asyncRoutes  // 异步路由
}

export default getters