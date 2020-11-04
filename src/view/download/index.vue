<template>
  <div class="box">
    <el-container style="height: 100%; border: 1px solid #eee">
      <!-- 侧边栏区域 -->
      <el-aside :width="asideWidth">
        <el-menu
          router
          :default-active="this.$route.path"
          background-color="#304156"
          text-color="#fff"
          :collapse="isCollapse"
        >
          <!-- 当含有子路由且子路由的长度>1的时候使用递归组件去渲染，因为如果想渲染没有
            子路由的组件的时候，由于子组件的内容必须要写在整个父级组件的router-view
            中，所以此时有也必须将该路由写成只有一个子路由的形成，此时就不能使用递归
          路由去渲染，而是应该直接渲染-->
          <el-submenu
            v-for="(route, index) in routes"
            :index="index.toString()"
            :key="index"
            v-if="!route.meta.hidden && route.children && route.children.length > 1"
          >
            <!-- 渲染第一个template -->
            <template slot="title">
              <i :class="route.meta.icon" v-if="route.meta.icon.indexOf('el-icon') > -1"></i>
              <icon-svg v-else :iconClass="route.meta.icon" />
              <span>{{route.meta.title}}</span>
            </template>
            <MultiMenu :routes="route.children" />
          </el-submenu>
          <!-- 子路由的长度为1，则直接渲染,需要注意的是必须要先有route.children的判断 -->
          <el-menu-item
            :index="route.children[0].path"
            :key="index"
            v-else-if="!route.meta.hidden && route.children && route.children.length === 1"
            :name="route.children[0].path.replace('/', '')"
          >
            <i
              :class="route.children[0].meta.icon"
              v-if="route.children[0].meta.icon.indexOf('el-icon') > -1"
            ></i>
            <icon-svg v-else :iconClass="route.children[0].meta.icon" />
            <span slot="title">{{route.children[0].meta.title}}</span>
          </el-menu-item>
          <!-- 没有子路由，此时也直接渲染，但是点击侧边栏会直接跳转，因为不在整个父级的router-view中 -->
          <Menu v-else-if="!route.meta.hidden" :route="route" />
        </el-menu>
      </el-aside>
      <el-container>
        <!-- 头部区域 -->
        <el-header>
          <el-row>
            <!-- 折叠展开按钮区域 -->
            <el-col :span="1">
              <icon-svg iconClass="hamburger" name="folder" @click="changeCollapse" />
            </el-col>
            <!-- 面包屑导航区域 -->
            <el-col :span="19">
              <el-breadcrumb>
                <el-breadcrumb-item
                  v-for="(item, index) in breadItems"
                  :key="index"
                  v-if="item.path"
                  :to="{ path: item.path }"
                >{{item.title}}</el-breadcrumb-item>
                <el-breadcrumb-item :key="index" v-else>{{item.title}}</el-breadcrumb-item>
              </el-breadcrumb>
            </el-col>
            <el-col :span="4">
              <el-dropdown>
                <i class="el-icon-user-solid" style="float: left"></i>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item>个人中心</el-dropdown-item>
                  <el-dropdown-item @click.native="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </el-dropdown>
              <span>{{userName}}</span>
            </el-col>
            <el-col :span="24">
              <el-tag
                v-for="tag in tags"
                :key="tag.name"
                :closable="tag.closable === undefined ? true: false"
                :effect="tag.effect"
                @close="handleTagClose(tag)"
                @click="handleTagClick(tag)"
                :type="tag.type"
              >{{tag.name}}</el-tag>
            </el-col>
          </el-row>
          <el-divider></el-divider>
        </el-header>
        <!-- 右侧内容区域 -->
        <el-main>
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { removeCookie, getCookie } from "@/utils/cookie";
import Menu from "./components/menu";
import MultiMenu from "./components/multimenu";
import "@/assets/el-submenu-title.css";
import { setCookie } from "@/utils/cookie";

export default {
  name: "DownLoad",
  created() {
    // 实例挂载完成之后获取用户路由
    this.routes = this.$store.getters["routes/asyncRoutes"];
    this.initialBread(this.$route.path); // 初始化面包屑
    if (this.$route.path === "/firstPage") {
      // 如果一开始就是首页
      this.tags[0].effect = "dark";
    } else {
      // 如果不是首页则将路由信息加入tags中
      this.tags.push({
        name: this.$route.meta.title,
        path: this.$route.path,
        effect: "dark",
      });
    }
  },
  mounted() {},
  computed: {},
  methods: {
    // 退出登陆的函数
    async logout() {
      const { code } = await this.$store.dispatch("user/clearUserInfo"); // 清空用户信息
      if (code === 200) {
        this.$router.push("/login"); // 如果清空成功则跳转到登陆页
      } else {
        this.$message({
          type: "danger",
          message: "退出登陆发生错误!",
        });
      }
    },
    // 侧边栏展开或者收缩的函数
    changeCollapse() {
      this.isCollapse = !this.isCollapse;
    },
    // 计算指定路由在路由表中的位置
    getRouteIndex(routePath) {
      return this.routes.findIndex((item) => {
        if (item.path === routePath) {
          return true;
        } else if (item.children) {
          this.checkChildrenRoute(item.children, routePath);
          return this.flag;
        } else {
          return false;
        }
      });
    },
    // 用于重新生成面包屑
    reInitialBread(routePath, indexPath) {
      this.breadItems = [{ path: "/firstPage", title: "首页" }]; // 初始化面包屑的数据
      // routePath即为路由的url,indexPath的第一个参数即为父级路由在整个路由表中的位置
      // 如果没有的话则说明父级路由被隐藏，此时的indexPath只有一个元素即routePath,此时直接寻找即可
      if (routePath !== "/firstPage") {
        // 不是首页
        const routeIndex = indexPath[0]; // 获取url的下标
        const reg = /\d+/; // 判断indexPath的第一个值是否是纯数字
        if (reg.test(routeIndex)) {
          // 如果routeIndex是下标,则一定有>1的子路由
          const route = this.routes[routeIndex]; // 从路由表中获取该路由
          this.addBreadItem(route, false); // 将该级路由信息加入到面包屑中,父级不包括path
          // 递归向面包屑中增加路由信息
          this.addBreadItems(routePath, route.children);
        } else {
          // index不是下标,则意味着父级路由被隐藏，只有一级子路由
          const temp = this.routes.filter((item) => {
            if (item.children) {
              return item.children[0].path === routePath; // 直接搜索找到该级路由
            }
          });
          this.addBreadItem(temp[0].children[0], true); // 添加该级元素,最终的子路由
        }
      }
    },
    // 递归增加面包削中的内容, routePath为待寻找的路由,routes为子路由列表
    addBreadItems(routePath, routes) {
      for (let i = 0; i < routes.length; i++) {
        const item = routes[i];
        if (item.path === routePath) {
          // 找到了该级路由
          this.addBreadItem(item, true); // 添加该级元素,最终的子路由
          break; // 结束整个循环
        } else if (item.children) {
          // 有子路由并且该子路由中含有待寻找的路由则继续递归
          // 如果不做这个逻辑判断就会出现点击图片搜索的时候
          // 面包屑的内容是首页/音乐搜索/图片搜索的bug
          this.checkChildrenRoute(item.children, routePath);
          if (this.flag) {
            this.addBreadItem(item, false); // 首先添加父级元素,并且不添加path
            // 这样在面包屑永远只能点击首页和最后一级可以点击的路由
            this.flag = false; // 设置成false
            this.addBreadItems(routePath, item.children); // 递归调用
          }
        } else {
          // 没有子路由或者该级路由不匹配
          continue; // 结束此次循环
        }
      }
    },
    // 向breaditem中增加一个元素, includePath: 是都将该级路由添加进去,默认为true
    addBreadItem(item, inclduePath = true) {
      if (inclduePath) {
        const { path } = item; // 获取该级path
        const { title } = item.meta; // 获取该级的title
        this.breadItems.push({ path, title }); // 添加该级的路径
      } else {
        const { title } = item.meta; // 该级的title
        this.breadItems.push({ title });
      }
    },
    checkChildrenRoute(routes, routePath) {
      // 检查子路由中是否含有指定的routePath
      for (let i = 0; i < routes.length; i++) {
        const item = routes[i];
        if (item.path === routePath) {
          // 如果有的话将flag的值设置成true
          this.flag = true;
        } else if (item.children) {
          this.checkChildrenRoute(item.children, routePath);
        } else {
          continue;
        }
      }
    },
    // 初始化面包屑，页面刚加载成功或者是路由变化的时候调用, routePath为将要进入的路由
    initialBread(routePath) {
      // 获取默认展开的路由在路由表中的index,由于每个路由的路径都是唯一的
      // 所以可以使用findIndex来进行查找
      this.defaultRouteIndex = this.getRouteIndex(routePath);
      this.flag = false; // 重新设置成false
      if (this.routes[this.defaultRouteIndex].children.length === 1) {
        // 只有一级子路由
        this.reInitialBread(routePath, [routePath]);
      } else {
        // 多级子路由
        this.reInitialBread(routePath, [
          this.defaultRouteIndex.toString(),
          routePath,
        ]);
      }
    },
    handleTagClose(tag) {
      // 关闭tag标签
      this.tags.splice(this.tags.indexOf(tag), 1);
      this.$router.push(this.tags[this.tags.length - 1].path); // 路由跳转
    },
    // 点击tag标签时进行路由跳转
    handleTagClick({ path }) {
      this.$router.push(path);
    },
  },
  data() {
    return {
      routes: [], // 用户的动态路由
      userName: this.$store.getters["user/userName"], // 用户的姓名
      isCollapse: false, // 侧边栏是否展开
      asideWidth: "200px", // 侧边栏的宽度
      breadItems: [{ path: "/firstPage", title: "首页" }], // 初始化面包屑里面的数据
      defaultRouteIndex: 0, // 一开始进来的时候默认展开的路由在路由表中的index
      flag: false, // 子路由中是否含有this.$route.path,用于一开始面包屑的生成
      tags: [
        { name: "首页", path: "/firstPage", effect: "plain", closable: false },
      ], // tags标签,首页不能关闭
    };
  },
  watch: {
    // 监听isCollapse的变化来实现侧边栏的动态响应
    isCollapse(n, o) {
      this.asideWidth = n ? "60px" : "220px";
    },
    // 监听路由的变化
    $route(to, from) {
      if (to.path === "/firstPage") {
        this.breadItems = [{ path: "/firstPage", title: "首页" }]; // 初始化面包屑的数据
      } else {
        this.initialBread(to.path); // 初始化面包屑
      }
      const res = this.tags.some((item) => {
        return item.name === to.meta.title;
      });
      if (res) {
        // 该路由已经添加到tags中
        this.tags.forEach((item) => {
          if (item.name === to.meta.title) {
            item["effect"] = "dark"; // 现在的路由深色显示
          }
          if (item.name === from.meta.title || item.name === "首页") {
            item["effect"] = "plain"; //去除原先的路由的深色显示的效果
          }
        });
      } else {
        if (to.meta.title === "DownLoad") {
          // 进入首页
          this.tags.forEach((item) => {
            if (item.name === "首页") {
              item["effect"] = "dark"; // 首页路由深色显示
            }
            if (item.name === from.meta.title) {
              item["effect"] = "plain"; //去除原先的路由的深色显示的效果
            }
          });
        } else {
          this.tags.push({
            name: to.meta.title,
            path: to.path,
            effect: "dark",
          });
          this.tags.forEach((item) => {
            if (item.name === from.meta.title || item.name === "首页") {
              item["effect"] = "plain"; //去除原先的路由的深色显示的效果
            }
          });
        }
      }
    },
  },
  components: {
    Menu,
    MultiMenu,
  },
};
</script>
<style>
/* 设置头部样式 */
.el-header {
  background-color: #ffffff;
  line-height: 60px;
  border-bottom: 1px solid #dcdfe6;
  text-align: right;
  align-items: center;
  height: 60px;
  padding-left: 0px;
}

/* 设置侧边栏样式 */
.el-aside {
  color: #333;
  margin-left: -20px;
  background-color: #304156;
  border-right: none;
  overflow-x: hidden;
}

/* 设置每一个菜单的样式 */
.el-menu {
  border-right: none;
}

/* 设置每一个菜单标题的样式 */
.el-submenu__title {
  margin-left: -40px;
}

/* 设置每一个子菜单的样式 */
.el-menu-item {
  margin-left: 5px;
}

/* 当只有一级子菜单的时候样式需要单独设置,因为其实是有el-menu-item,但是展现出来的必须
和el-submenu__title的效果一样 */
[name="hotVideo"] {
  margin-left: -40px;
}

/*设置收缩时的样式*/
ul.el-menu--collapse li.el-menu-item[name="hotVideo"] {
  margin-left: 0px;
}

/* 设置首页侧边栏菜单的样式 */
[name="firstPage"] {
  margin-left: -5px;
  font-size: 1.2em;
}

/*设置收缩时的样式*/
ul.el-menu--collapse li.el-menu-item[name="firstPage"] {
  margin-left: 0px;
}

/* 设置侧边栏收缩时菜单标题的样式 */
ul.el-menu--collapse div.el-submenu__title {
  margin-left: 0px;
}

/* 让布局占满整个屏幕 */
.box {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.el-breadcrumb {
  margin-top: 25px;
  font-size: 15px !important;
}

/* 右侧区域的样式 */
.el-main {
  margin-top: 50px;
}

/* tag标签的样式 */
.el-tag {
  float: left;
  margin-top: 5px;
  margin-left: 5px;
  cursor: pointer;
}

/* 设置分割线的样式 */
.el-divider--horizontal {
  width: 120%;
  margin-top: 5px;
  overflow-x: hidden;
}

/* 设置container的样式 */
.el-container.is-vertical {
  overflow-x: hidden;
}

/* 设置内容区域的样式 */
.el-main{
  padding-left: 5px;
  padding-top: 10px;
  overflow-x: hidden;
}

/* 设置弹窗中的标题靠左 */
.el-dialog__title{
  float: left;
}
</style>
