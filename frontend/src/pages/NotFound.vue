<template>
  <div class="not-found-container">
    <div class="content">
      <h1>404</h1>
      <p>页面未找到</p>
      <router-link to="/">返回首页</router-link>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped lang="scss">
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

  .content {
    text-align: center;
    color: white;

    h1 {
      font-size: 80px;
      margin: 0;
    }

    p {
      font-size: 24px;
      margin: 20px 0;
    }

    a {
      display: inline-block;
      margin-top: 20px;
      padding: 10px 20px;
      background: white;
      color: #667eea;
      text-decoration: none;
      border-radius: 4px;
      font-weight: bold;

      &:hover {
        background: #f0f0f0;
      }
    }
  }
}
</style>
