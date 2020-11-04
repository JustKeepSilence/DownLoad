<template>
  <div class="container">
    <el-form :model="ruleForm" status-icon :rules="rules" ref="ruleForm" label-width="100px">
      <el-form-item prop="userName">
        <el-input
          v-model="ruleForm.userName"
          autocomplete="off"
          prefix-icon="el-icon-user-solid"
          placeholder="请输入用户名"
        ></el-input>
      </el-form-item>
      <el-form-item prop="passWord">
        <el-input
          type="password"
          v-model="ruleForm.passWord"
          autocomplete="off"
          prefix-icon="el-icon-key"
          placeholder="请输入密码"
        ></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm" style="width: 100%">登陆</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
<script>
import { userLogin, passWordValidator } from "@/api/login";
export default {
  name: "Login",
  data() {
    return {
      ruleForm: {
        userName: "",  // 用户名
        passWord: "",  // 密码
      },
      rules: {
        userName: [{ required: true, trigger: "blur", message: '用户名不能为空' }],  // 用户名的验证
        passWord: [
          {
            required: true,
            tigger: "blur",
            min: 6,
            validator: passWordValidator,  // 自定义验证函数
          },
        ],
      },
    };
  },
  methods: {
    submitForm() {
      userLogin(
        JSON.stringify({
          username: this.ruleForm.userName,
          password: this.ruleForm.passWord,
        })
      ).then(({ token, name }) => {
        // 当登陆成功以后将token写入cookie
        this.$store.dispatch("user/setToken", token).then(() => {
          this.$router.push("/firstPage"); // 跳转到首页
        });
      });
    },
  },
};
</script>
<style scoped>
.container {
  width: 400px;
  margin-left: 600px;
  margin-top: 370px;
}
</style>