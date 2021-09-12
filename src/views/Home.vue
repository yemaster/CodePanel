<template>
  <div>
    <el-row :gutter="20" v-loading="loading">
      <el-col :span="20" :offset="2">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span id="logo">CodePanel</span>
          </div>
          <div class="text item">
            <el-tabs v-model="activeName" @tab-click="handleClick">
              <el-tab-pane label="单文件模式" name="first">
                <el-row :gutter="20">
                  <el-col :span="15">
                    <editor
                      v-model="codeForm.content"
                      @init="editorInit"
                      :lang="codeParser[codeForm.lang]"
                      theme="tomorrow"
                      height="500"
                    ></editor>
                  </el-col>
                  <el-col :span="9">
                    <el-form label-position="top" :model="codeForm">
                      <el-form-item label="语言">
                        <el-select v-model="codeForm.lang" placeholder="请选择">
                          <el-option
                            v-for="item in options"
                            :key="item.value"
                            :label="item.label"
                            :value="item.value"
                          >
                          </el-option>
                        </el-select>
                      </el-form-item>
                      <el-form-item label="输入数据">
                        <el-input
                          type="textarea"
                          :rows="3"
                          placeholder="输入数据"
                          v-model="codeForm.inputFile"
                        >
                        </el-input>
                      </el-form-item>
                      <el-form-item label="输出数据">
                        <el-tag :type="statusTranslate[codeForm.status].type">{{
                          statusTranslate[codeForm.status].info
                        }}</el-tag>
                        <el-input
                          type="textarea"
                          :rows="3"
                          placeholder="输出数据"
                          v-model="codeForm.outputFile"
                        >
                        </el-input>
                      </el-form-item>
                      <el-form-item>
                        <el-button
                          type="primary"
                          @click="onSubmit"
                          :disabled="codeForm.isOK || loading"
                        >
                          运行
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </el-col>
                </el-row>
              </el-tab-pane>
              <el-tab-pane label="项目模式" name="second">
                <template v-if="opened_project == ''">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <h3>新建项目</h3>
                      <el-form label-position="top" :model="new_project">
                        <el-form-item label="项目名称">
                          <el-input v-model="new_project.title"> </el-input>
                        </el-form-item>
                        <el-form-item label="保存文件夹名称">
                          <el-input v-model="new_project.work_dir"> </el-input>
                        </el-form-item>
                        <el-form-item>
                          <el-button
                            type="primary"
                            @click="createProject"
                            :disabled="new_project.isSubmit"
                          >
                            提交
                          </el-button>
                        </el-form-item>
                      </el-form>
                    </el-col>
                    <el-col :span="12">
                      <h3>
                        打开项目
                        <el-button
                          type="primary"
                          icon="el-icon-refresh"
                          circle
                          @click="sendFre"
                        ></el-button>
                      </h3>
                      
                    </el-col>
                  </el-row>
                </template>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
#logo {
  line-height: 1;
  font-weight: 300px;
  font-size: 28px;
}
@font-face {
  font-family: "Jetbrains Mono";
  src: url("~@/assets/fonts/woff2/JetBrainsMono-Medium.woff2") format("woff2");
}
.ace_editor {
  font-family: "Jetbrains Mono";
}
</style>

<script>
import io from "socket.io-client";

export default {
  name: "Home",
  data() {
    return {
      activeName: "first",
      content: "",
      options: [
        {
          value: "C++",
          label: "C++",
        },
        {
          value: "Python3",
          label: "Python3",
        },
        {
          value: "Nodejs",
          label: "JavaScript",
        },
      ],
      codeForm: {
        lang: "C++",
        content: "",
        inputFile: "",
        outputFile: "",
        isOK: false,
        status: -1,
        sked: "",
      },
      loading: true,
      codeParser: {
        "C++": "c_cpp",
        Python3: "python",
        Nodejs: "javascript",
      },
      statusTranslate: {
        "-1": {
          info: "未提交",
          type: "info",
        },
        0: {
          info: "运行成功",
          type: "success",
        },
        1: {
          info: "运行时错误",
          type: "danger",
        },
        2: {
          info: "运行超时",
          type: "warning",
        },
        3: {
          info: "系统错误",
          type: "danger",
        },
        4: {
          info: "提交中",
          type: "warning",
        },
        801: {
          info: "编译错误",
          type: "danger",
        },
        802: {
          info: "编译超时",
          type: "warning",
        },
        803: {
          info: "系统错误",
          type: "danger",
        },
      },
      opened_project: "",
      new_project: {
        title: "New Project",
        work_dir: "newproject",
        isSubmit: false,
      },
    };
  },
  mounted() {
    let _t = this;
    _t.sked = io("http://127.0.0.1:3000");
    _t.sked.on("connect", () => {
      _t.loading = false;
    });
    _t.sked.on("disconnect", () => {
      _t.loading = true;
    });
    _t.sked.on("res", (data) => {
      _t.codeForm.isOK = false;
      _t.codeForm.status = data.code;
      _t.codeForm.outputFile = data.outputFile;
    });
    _t.sked.on("mes", (data) => {
      _t.$message(data);
    });
    _t.sked.on("handle_new_project", (data) => {
      _t.new_project.isSubmit = false;
    });
    _t.sked.on("enter_project", (data) => {
      _t.opened_project = data;
      console.log(data);
    });
  },
  methods: {
    editorInit: function (editor) {
      require("brace/ext/language_tools"); //language extension prerequsite...
      require("brace/mode/python");
      require("brace/mode/javascript"); //language
      require("brace/mode/c_cpp");
      require("brace/theme/tomorrow");
      require("brace/snippets/javascript"); //snippet
      editor.setFontSize(14);
    },
    onSubmit() {
      const _t = this;
      _t.codeForm.isOK = true;
      _t.codeForm.status = 4;
      _t.sked.emit("run_code", {
        code: _t.codeForm.content,
        lang: _t.codeForm.lang,
        inputData: _t.codeForm.inputFile,
      });
    },
    createProject() {
      const _t = this;
      _t.new_project.isSubmit = true;
      _t.sked.emit("new_project", {
        title: _t.new_project.title,
        dir: _t.new_project.work_dir,
      });
    },
    handleClick(tab, event) {
      console.log(tab, event);
    },
  },
  components: {
    editor: require("vue2-ace-editor"),
  },
};
</script>
