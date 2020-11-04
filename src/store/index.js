import Vue from 'vue'
import Vuex from 'vuex'
// import getters from '@/store/getters'
import user from '@/store/modules/user'
import routes from '@/store/modules/routes'

Vue.use(Vuex)

const store = new Vuex.Store({
    modules: {
        user,
        routes
    },
})

export default store