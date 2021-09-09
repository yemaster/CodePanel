<template>
  <div>
    <el-row :gutter="20" v-loading="loading">
      <el-col :span="20" :offset="2">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span id="logo">CodePanel</span>
          </div>
          <div class="text item">
            <el-row :gutter="20">
              <el-col :span="12">
                <editor
                  v-model="codeForm.content"
                  @init="editorInit"
                  :lang="codeParser[codeForm.lang]"
                  theme="tomorrow"
                  height="500"
                ></editor>
              </el-col>
              <el-col :span="12">
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
                      maxlength="200"
                      show-word-limit
                    >
                    </el-input>
                  </el-form-item>
                  <el-form-item label="输出数据">
                    <el-tag :type="statusTranslate[codeForm.status].type">{{ statusTranslate[codeForm.status].info }}</el-tag>
                    <el-input
                      type="textarea"
                      :rows="3"
                      placeholder="输出数据"
                      v-model="codeForm.outputFile"
                    >
                    </el-input>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="onSubmit" :disabled="codeForm.isOK || loading">
                      运行
                    </el-button>
                  </el-form-item>
                </el-form>
              </el-col>
            </el-row>
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
import io from 'socket.io-client'

export default {
  name: "Home",
  data() {
    return {
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
          type: "info"
        },
        "0": {
          info: "运行成功",
          type: "success"
        },
        "1": {
          info: "运行时错误",
          type: "danger"
        },
        "2": {
          info: "运行超时",
          type: "warning"
        },
        "3": {
          info: "系统错误",
          type: "danger"
        },
        "4": {
          info: "提交中",
          type: "warning"
        },
        "801": {
          info: "编译错误",
          type: "danger"
        },
        "802": {
          info: "编译超时",
          type: "warning"
        },
        "803": {
          info: "系统错误",
          type: "danger"
        },
      }
    };
  },
  mounted() {
    let _t = this
    _t.sked = io()
    _t.sked.on('connect', () => {
      _t.loading = false
    })
    _t.sked.on('disconnect', () => {
      _t.loading = true
    })
    _t.sked.on('res', (data) => {
      _t.codeForm.isOK = false
      _t.codeForm.status = data.code
      _t.codeForm.outputFile = data.outputFile
    })
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
      const _t = this
      _t.codeForm.isOK = true
      _t.codeForm.status = 4
      _t.sked.emit('run_code', {
        code: _t.codeForm.content,
        lang: _t.codeForm.lang,
        inputData: _t.codeForm.inputFile
      })
    },
  },
  components: {
    editor: require("vue2-ace-editor"),
  },
};
</script>
