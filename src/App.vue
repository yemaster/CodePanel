<template>
  <div id="app">
    <el-container>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<style>
html,
body {
  margin: 0px;
}
</style>

<script>
import Menu from "./components/Menu.vue";

export default {
  name: "App",
  components: {
    Menu,
  },
};
</script>
