<template>
  <main class="admin-page login-page">
    <section class="login-panel panel">
      <div>
        <p class="login-kicker">ADMIN</p>
        <h1>出彩中原管理后台</h1>
        <p>配置轮播图、节点信息、关于我们和访客统计。</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleLogin">
        <el-form-item label="账号" prop="username">
          <el-input v-model="form.username" autocomplete="username" size="large" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" autocomplete="current-password" size="large" show-password />
        </el-form-item>
        <el-button type="primary" size="large" :loading="loading" native-type="submit" class="login-button">
          登录
        </el-button>
      </el-form>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api/admin'
import { setToken } from '../api/request'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = reactive({
  username: 'admin',
  password: 'admin123'
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await login(form)
    setToken(res.data.token)
    ElMessage.success('登录成功')
    router.replace('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: grid;
  place-items: center;
  padding: 24px;
}

.login-panel {
  width: min(920px, 100%);
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 48px;
  padding: 46px;
}

.login-kicker {
  margin: 0 0 26px;
  color: var(--admin-accent);
  font-family: "JetBrains Mono", "Consolas", monospace;
  letter-spacing: 0;
}

h1 {
  margin: 0;
  max-width: 420px;
  font-size: 42px;
  line-height: 1.08;
  font-weight: 700;
}

p {
  margin: 16px 0 0;
  color: var(--admin-muted);
  line-height: 1.8;
}

.login-button {
  width: 100%;
  margin-top: 8px;
}

@media (max-width: 760px) {
  .login-panel {
    grid-template-columns: 1fr;
    padding: 28px;
    gap: 28px;
  }

  h1 {
    font-size: 30px;
  }
}
</style>
