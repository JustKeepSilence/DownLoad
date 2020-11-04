<template>
  <div>
    <el-menu-item :index="route.path" :key="index">
      <i :class="route.meta.icon" v-if="route.meta.icon.indexOf('el-icon') > -1"></i>
        <icon-svg v-else :iconClass="route.meta.icon" />
      <span slot="title">{{route.meta.title}}</span>
    </el-menu-item>
  </div>
</template>
<script>
export default {
  name: "Menu",
  props: ["route"],
  created: ()=>{
      this.index = new Date()  // 通过设定key值为当前的时间来个给每个key不同的index
  },
  data(){
    return {
      index: '',
      margin: route.meta.title === '热门视频' ? '30px': '0px'
    }
  }
}
</script>
<style>
  
</style>