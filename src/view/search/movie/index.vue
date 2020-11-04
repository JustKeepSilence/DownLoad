<template>
  <div>
    <!-- 头部搜索框区域 -->
    <el-row :gutter="10">
      <el-col :span="4">
        <el-input v-model="keyWord" placeholder="请输入搜索内容"></el-input>
      </el-col>
      <el-col :span="4">
        <el-select v-model="selectedWebSite" placeholder="请选择搜索网站">
          <el-option v-for="(item, index) in webSites" :key="index" :label="item" :value="item"></el-option>
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-autocomplete
          v-model="searchHistory"
          :fetch-suggestions="querySearch"
          placeholder="从历史中搜索"
        ></el-autocomplete>
      </el-col>
      <el-col :span="2">
        <el-button type="primary" icon="el-icon-search" @click="beginSearchMovie">开始搜索</el-button>
      </el-col>
      <el-col :span="2">
        <el-button type="success" icon="el-icon-document">日志查看</el-button>
      </el-col>
      <el-col :span="2">
        <el-button
          type="success"
          icon="el-icon-refresh"
          v-show="showCurrentLogButton"
          @click="currentLogDiagVisible=true"
        >实时日志</el-button>
      </el-col>
      <el-col :span="2">
        <el-button type="success" icon="el-icon-download" @click="downloadData">数据下载</el-button>
      </el-col>
      <el-col :span="2">
        <el-button type="danger" icon="el-icon-delete">清空历史</el-button>
      </el-col>
    </el-row>
    <!-- 中间电影表格区域 -->
    <el-row style="margin-top: 20px">
      <el-table
        :data="movieTableData"
        v-loading="loadingMovie"
        :element-loading-text="loadingText"
        border
        fit
        highlight-current-row
        style="width: 100%;"
        @sort-change="sortChange"
      >
        <el-table-column align="left">
          <template slot="header" slot-scope="scope">
            <el-input
              placeholder="表格搜索(请输入搜索关键字)"
              v-model="movieTableSearchKeyWord"
              prefix-icon="el-icon-search"
              class="input-with-select"
              style="width: 400px"
              @input="searchMovieTableContent"
            ></el-input>
          </template>
          <el-table-column
            label="ID"
            prop="id"
            align="center"
            width="80"
            sortable
            :class-name="getSortClass('id')"
          ></el-table-column>
          <el-table-column label="电影名称" width="150px" prop="name" align="center"></el-table-column>
          <el-table-column label="导演" min-width="150px" prop="director" align="center"></el-table-column>
          <el-table-column
            label="评分"
            width="110px"
            prop="score"
            align="center"
            sortable
            :sort-method="orderByScore"
          ></el-table-column>
          <el-table-column label="电影类型" min-width="150px" prop="movie_type" align="center"></el-table-column>
          <el-table-column
            label="电影评论"
            min-width="250px"
            prop="synopsis"
            align="center"
            show-overflow-tooltip
          ></el-table-column>
          <el-table-column
            label="操作"
            align="center"
            fixed="right"
            min-width="200"
            class-name="small-padding fixed-width"
            :filters="[{text: '有资源', value: '有资源'}]"
            :filter-method="handleMovieSourceFilter"
          >
            <template slot-scope="{row,$index}">
              <el-button type="success" size="mini" :icon="collected(row)" @click="collect(row)">收藏</el-button>
              <el-button
                size="mini"
                type="danger"
                icon="el-icon-delete"
                @click="handleMovieDelete(row)"
              >删除</el-button>
              <el-tooltip
                placement="top"
                :content="JSON.parse(row.download_link).length !== 0 ? `有${JSON.parse(row.download_link).length}个资源`: '暂无资源'"
              >
                <el-button
                  type="primary"
                  size="mini"
                  @click="handleSourceDownLoad(row)"
                  icon="el-icon-download"
                >资源下载</el-button>
              </el-tooltip>
            </template>
          </el-table-column>
        </el-table-column>
      </el-table>
    </el-row>
    <!-- 底部电影表格分页区域 -->
    <el-row style="margin-top: 10px">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="movieNumber"
        :current-page.sync="movieCurrentPage"
        @size-change="handleMovieTablePageSizeChange"
        @current-change="handleMovieTableCurrentPageChange"
        :page-sizes="[5, 10, 15]"
        :page-size="5"
      ></el-pagination>
    </el-row>
    <!-- 点击资源下载的弹窗区域 -->
    <el-dialog
      title="资源下载"
      :visible.sync="sourceDownLoadDialogVisibility"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      width="30%"
    >
      <!-- 下载资源表格区域 -->
      <!-- 通过row-key来标识每行数据是通过哪个属性来进行识别的, reserve-selection的作用是在数据更新之后保留之前选中的数据 -->
      <el-table
        :data="sourceTableData"
        ref="sourceTable"
        @selection-change="handleSelection"
        row-key="id"
      >
        <el-table-column type="selection" min-width="50" :reserve-selection="true"></el-table-column>
        <el-table-column property="id" label="ID" width="150"></el-table-column>
        <el-table-column property="link" label="下载链接" show-overflow-tooltip min-width="150"></el-table-column>
        <el-table-column property="linkType" label="链接来源" min-width="100"></el-table-column>
      </el-table>
      <!-- 分页区域 -->
      <el-pagination
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="sourceNumber"
        @current-change="handleSourceTableCurrentPageChange"
        :page-sizes="[8]"
        :page-size="sourcePageSizes"
      ></el-pagination>
      <!-- 底部按钮区域 -->
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="handleDownLoad">下载</el-button>
      </span>
    </el-dialog>
    <!-- 点击实时查看的弹窗区域 -->
    <el-dialog
      :title="logTitle"
      :visible.sync="currentLogDiagVisible"
      width="800px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <el-input type="textarea" :autosize="{ minRows: 2, maxRows: 15}" v-model="currentLog"></el-input>
      <div slot="footer" class="dialog-footer">
        <el-button @click="currentLogDiagVisible = false">关闭</el-button>
      </div>
    </el-dialog>
  </div>
</template>
<script>
import {
  getWebsiteLists,
  getSearchHistoryLists,
  deleteItem,
  getAllMovieData,
} from "@/api/movie"; // 导入请求的接口
import { connectSearchMovieSocket } from "@/utils/websocket";
import { parseDownLoadUrl } from "@/utils/parseDownloadUrls";
import { addDownloadItems } from "@/api/download";
import { exportDataToExcel } from "@/utils/excel";

export default {
  name: "Movie",
  data: () => {
    return {
      keyWord: "", // 搜索的关键字
      webSites: [], // 进行爬虫搜索的网站
      searchHistory: "", // 搜索历史,输入框的v-model
      movieTableData: [], // 电影表格中的数据
      loadingText: "", // 表格数据加载时显示的text
      movieTableSearchKeyWord: "", // 电影表格搜索框的输入
      selectedWebSite: "", // 选中的搜索网站
      searchHistoryList: [], // 搜索历史列表
      movieNumber: 0, // 搜索到的电影的总数目
      moviePageSizes: 5, // 电影表格每页的总条数
      movieCurrentPage: 1, // 电影表格当前页码
      loadingMovie: true, // 电影表格页面是否显示加载动画，默认显示
      sourceDownLoadDialogVisibility: false, // 资源搜索弹窗是否显示
      sourceTableData: [], // 资源下载弹窗表格中的数据源
      sourcePageSizes: 8, // 资源表格每页的总条数
      sourceCurrentPage: 1, // 资源表格当前的页码
      sourceNumber: 0, // 资源表格的总数目
      download_links: [], // 资源下载链接
      download_links_type: [], // 资源下载链接类型
      selectedSource: [], // 选中的下载资源表格的行
      showCurrentLogButton: false, // 是否显示实时查看按钮
      currentLogDiagVisible: false, // 实时日志弹窗是否显示
      currentLog: "", // 实时日志弹窗中textarea里面的内容
      logTitle: "实时日志查看", // 实时日志查看弹窗
    };
  },
  created() {
    // 页面实例挂载完之后执行
    this.getWebsiteList(); // 获取搜索网站
    this.getSearchHistory(); // 获取搜索历史
    this.searchMovie(this.movieCurrentPage, this.moviePageSizes); // 搜索电影,一开始进来展示所有的内容
    // 监听后台返回的数据,movie就是emit的第一个参数,第二个参数是回调函数,函数的参数
    // 就是后台接口返回的值,监听搜索电影后台接口的返回结果
    this.$socket.on("movie", ({ code, data: { result, total } }) => {
      switch (code) {
        case 200:
          // 返回200说明查询成功
          this.movieTableData = result; // result就是后台返回的数据
          this.movieNumber = total;
          this.loadingMovie = false; // 去除动画
          this.showCurrentLogButton = false; // 隐藏实时查看按钮
          this.currentLog = ""; // 清空实时弹窗中的内容
          this.currentLogDiagVisible = false  //关闭弹窗
          break;
        case 204:
          // 返回204说明调用爬虫正在爬取数据
          this.showCurrentLogButton = true; // 显示实时查看按钮
          this.movieTableData = []; // 清空表格中的数据
          this.loadingText = "正在爬取数据...";
          this.loadingMovie = true; // 显示爬取动画
          this.currentLog = result; // 实时日志弹窗中的内容
          break;
        default:
          // 返回500说明爬虫爬取失败
          this.loadingMovie = false; // 取消爬取动画
          this.showCurrentLogButton = false; // 隐藏实时查看按钮
          this.currentLog = ""; // 清空实时弹窗中的内容
          this.$message.error("爬虫爬取失败,详情请查看日志!");
          this.keyWord = ""; // 搜索关键字设置为空
          this.movieTableSearchKeyWord = ""; // 设置电影表格搜索关键字为空
          this.movieTableData = []
      }
    });
    // 监听电影某一行的收藏事件
    this.$socket.on(
      "update_movie_item_collection_status",
      ({ code, data: { table_id, is_collected } }) => {
        this.movieTableData[table_id - 1].is_collected = is_collected; // 根据index去根据表格中的数据
      }
    );
  },
  methods: {
    sortChange() {},
    getSortClass(id) {},
    // 搜索电影表格中的内容
    searchMovieTableContent() {
      this.searchMovie(this.movieCurrentPage, this.moviePageSizes); // 搜索电影
    },
    // 对电影表格按照评分进行排序,其行为需要和array.sort表现的一致, a, b为表格的row
    orderByScore(a, b) {
      a = a.score === "暂无" ? 0 : a.score;
      b = b.score === "暂无" ? 0 : b.score;
      return parseFloat(a) - parseFloat(b);
      return parseFloat(a) - parseFloat(b);
    },
    // 获取搜索网站列表
    getWebsiteList() {
      getWebsiteLists({ type_name: "movie" }).then(({ data }) => {
        this.webSites = data.result;
      });
    },
    // 获取搜索历史
    getSearchHistory() {
      getSearchHistoryLists({ type_name: "movie" }).then(({ data }) => {
        this.searchHistoryList = data.result;
      });
    },
    // 带有输入建议输入框的方法属性，第一个参数为输入的字符串
    // 第二个参数为回调函数，通过回调函数去返回对应的数据
    querySearch(queryString, callback) {
      const history = queryString
        ? this.searchHistoryList.filter((item) => {
            return (
              item.value.toLowerCase().indexOf(queryString.toLowerCase()) > -1
            );
          })
        : this.searchHistoryList;
      callback(history);
    },
    // 调用后台接口搜索或者爬取电影,page为当前的页码,limit为每一页显示的数目
    searchMovie(page, limit) {
      this.$socket.emit("search_movie", {
        keyword: this.keyWord,
        search_keyword: this.movieTableSearchKeyWord,
        web_site_id:
          this.webSites.findIndex((item) => {
            return item === this.selectedWebSite; // vue中的index和数据库中的index差1
          }) + 1,
        page,
        limit,
      });
    },
    // 判断每一行的数据是否被收藏
    collected(row) {
      return row.is_collected ? "el-icon-star-on" : "el-icon-star-off";
    },
    // 收藏电影表格中的某一行数据, item_id即为该行数据在数据库中的id, id为其在当前
    // 表格数据中的index,需要根据这个index去更新表格中的数据
    collect({ is_collected, item_id: movie_id, id: table_id }) {
      is_collected = !is_collected;
      this.$socket.emit("update_movie_item_collection_status", {
        table_id,
        is_collected,
        movie_id,
      });
    },
    // 电影表格每页总数发生改变时的回调函数
    handleMovieTablePageSizeChange(pageSizes) {
      this.moviePageSizes = pageSizes;
      this.searchMovie(this.movieCurrentPage, this.moviePageSizes); // 搜索电影
    },
    // 电影表格当前页码发生改变时的回调函数
    handleMovieTableCurrentPageChange(currentPage) {
      this.movieCurrentPage = currentPage; // 赋值
      this.searchMovie(this.movieCurrentPage, this.moviePageSizes); // 搜索电影
    },
    // 点击搜索电影按钮
    beginSearchMovie() {
      if (this.selectedWebSite) {
        // 选择了搜索的网站
        this.movieCurrentPage = 1; // 重置当前页码
        // this.moviePageSizes = 5; // 重置每页显示的数目
        this.movieTableSearchKeyWord = ""; // 重置表格中的搜索数据
        this.searchMovie(this.movieCurrentPage, this.moviePageSizes); // 搜索电影
      } else {
        this.$message.warning("请选择要搜索的网站");
      }
    },
    // 删除电影表格中的某一行数据
    handleMovieDelete({ item_id: movie_id, id: table_id }) {
      deleteItem(JSON.stringify({ movie_id })).then(({ code }) => {
        if (code === 200) {
          this.movieTableData.splice(table_id - 1, 1); // 删除表格中对应的数据
          this.movieTableData = this.movieTableData.map((item) => {
            if (item.id > table_id) {
              // 所有在待删除这一行数据后面的数据的id都减1,如果不进行这一步
              // 那在删除之后的表格中的ID将不再是依次排序,下一次删除或者收藏
              // 操作时获取到的id将发生错误
              item.id -= 1;
            }
            return item;
          });
        } else {
          this.$message.error("调取后台接口失败");
        }
      });
    },
    // 获取资源弹窗表格的全部数据
    getSourceTableData() {
      let temp = [];
      for (let i = 0; i < this.download_links.length; i++) {
        temp.push({
          id: i + 1,
          link: this.download_links[i],
          linkType: this.download_links_type[i],
        }); // 添加数据
      }
      this.sourceNumber = temp.length; // 计算总数目
      return temp;
    },
    // 点击资源下载时触发的事件,弹出弹窗
    handleSourceDownLoad({ download_link, download_link_type }) {
      this.download_links = JSON.parse(download_link); // 下载的链接
      if (this.download_links.length === 0) {
        // 数组为空说明没有下载资源
        this.$message.warning("该电影暂无下载资源");
      } else {
        this.sourceDownLoadDialogVisibility = true; // 显示弹窗
        this.download_links_type = JSON.parse(download_link_type);
        const temp = this.getSourceTableData(); // 获取整个资源列表表格的数据
        this.sourceTableData = temp.filter((item) => {
          return item.id - 1 < this.sourcePageSizes; // 选择出前sourcePageSizes个数据
        });
      }
    },
    // 资源表格界面分页的页码改变
    handleSourceTableCurrentPageChange(currentPage) {
      const temp = this.getSourceTableData(); // 获取所有的下载数据
      this.sourceTableData = temp.filter((item) => {
        // 获取分页的数据
        return (
          item.id - 1 >= this.sourcePageSizes * (currentPage - 1) &&
          item.id - 1 < this.sourcePageSizes * currentPage
        );
      });
    },
    // 资源下载页面点击下载按钮的函数
    handleDownLoad() {
      let download_urls = []; // 下载链接
      for (let i = 0; i < this.selectedSource.length; i++) {
        const { link } = this.selectedSource[i]; // 下载链接
        download_urls.push(parseDownLoadUrl(link)); // 将下载链接解析成aria2可以下载的链接
      }
      addDownloadItems(
        JSON.stringify({
          download_urls,
          typename: "movie",
        })
      ).then(({ code, data: { result } }) => {
        if (code === 200) {
          if (result.length === 0) {
            //  所有的下载都已经存在
            this.$message.warning("所有的下载链接都已存在!");
          } else {
            this.$message.success("成功加入下载列表");
            this.sourceDownLoadDialogVisibility = false; // 关闭弹窗
          }
        }
      });
    },
    // 电影表格资源筛选的函数,传入三个参数分别是选择的value,row, colum
    handleMovieSourceFilter(value, { download_link }) {
      return JSON.parse(download_link).length > 0;
    },
    // 当资源下载表格中的checkbox选项发生变化时的回调函数, selection是包含了所有选中
    // 数据的一个list,如果切换页码那么selection的值就是[]
    handleSelection(selection) {
      this.selectedSource = selection; // 赋值
    },

    // 下载表格中的数据
    downloadData() {
      this.$prompt("请输入保存的文件名称", "提示", {
        confirmButtonText: "确定", // 确定按钮的名称
        cancelButtonText: "取消", // 取消按钮的名称
        inputPattern: /.*/, // 输入内容的正则匹配
        inputErrorMessage: "文件名格式不正确", // 匹配错误信息
      }).then(({ value }) => {
        // 获取输入， value即为文件名
        getAllMovieData(
          JSON.stringify({
            keyword: this.keyWord,
            search_keyword: this.movieTableSearchKeyWord,
          })
        ).then(({ code, data: { result } }) => {
          if (code === 200) {
            // 成功,async返回的也是promise
            exportDataToExcel(result, value).catch((e)=>{
              this.$message.error(e.message)  // message中存储了错误的信息
            }).then(()=>{
              this.$$message.success('下载成功')
            })
          } else {
            this.$message.error(`请求出错:${resul}`);
          }
        });
      }).catch(()=>{
        this.$message.info('取消下载')
      })
    },
  },
};
</script>
<style scoped>
.el-select {
  width: 100%;
}
.el-autocomplete {
  width: 100%;
}
/* 设置分页的样式 */
.el-pagination {
  float: left;
}
</style>