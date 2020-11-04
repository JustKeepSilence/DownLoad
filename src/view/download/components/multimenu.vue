<template>
  <div>
    <!-- 第一次传进来的是一个对象，如果该对象包含了不为空的children，则使用MultiMenuItem递归
    组件进行迭代-->
    <el-submenu
      v-for="(route, index) in routes"
      :index="route.path"
      :key="index"
      v-if="!route.meta.hidden && route.children && route.children.length > 0"
    >
      <!-- 渲染第一个template -->
      <template slot="title">
        <i :class="route.meta.icon" v-if="route.meta.icon.indexOf('el-icon') > -1"></i>
        <icon-svg v-else :iconClass="route.meta.icon" />
        {{route.meta.title}}
      </template>
      <MultiMenu :routes="route.children" />
    </el-submenu>
    <el-menu-item :index="route.path" v-else-if="!route.meta.hidden" :key="index">
      <i :class="route.meta.icon" v-if="route.meta.icon.indexOf('el-icon') > -1"></i>
      <icon-svg v-else :iconClass="route.meta.icon"/>
      <span slot="title">{{route.meta.title}}</span>
    </el-menu-item>
  </div>
</template>

<script>
import Menu from "./menu";

export default {
  name: "MultiMenu",
  props: ["routes"], // 子路由
};
</script>
