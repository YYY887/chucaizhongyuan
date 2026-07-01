<template>
  <main class="admin-page login-page">
    <section class="login-shell">
      <article class="login-brand panel">
        <div class="brand-top">
          <div class="brand-badge">ADMIN CONSOLE</div>
          <div class="brand-logo-box">
            <div class="brand-logo">
              <img v-if="site.site_logo" :src="site.site_logo" :alt="site.site_name || '站点 Logo'" />
              <span v-else>{{ fallbackMark }}</span>
            </div>
            <div class="brand-title">
              <p class="login-kicker">{{ site.site_name || '出彩中原' }}</p>
              <h1>统一管理路线内容、站点配置与访客数据</h1>
              <p class="brand-text">
                保持 Element Plus 原始蓝色体系，集中维护轮播图、节点信息、关于我们和访问统计。
              </p>
            </div>
          </div>
        </div>

        <div class="brand-metrics">
          <div class="metric-card">
            <span class="metric-label">站点内容</span>
            <strong>Logo、名称、页脚与轮播图统一维护</strong>
          </div>
          <div class="metric-card">
            <span class="metric-label">路线管理</span>
            <strong>节点拖拽、地图选点、线路预览集中处理</strong>
          </div>
          <div class="metric-card">
            <span class="metric-label">统计看板</span>
            <strong>访客趋势、访问路径与真实统计同步查看</strong>
          </div>
        </div>
      </article>

      <section class="login-panel panel">
        <div class="panel-head">
          <p class="panel-kicker">管理员登录</p>
          <h2>进入后台控制台</h2>
          <p class="panel-text">使用管理员账号登录后，可继续维护前台展示内容与路线数据。</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleLogin">
          <el-form-item label="账号" prop="username">
            <el-input
              v-model="form.username"
              autocomplete="off"
              name="admin-login-username"
              size="large"
              spellcheck="false"
            />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              autocomplete="new-password"
              name="admin-login-password"
              size="large"
              show-password
            />
          </el-form-item>
          <el-button type="primary" size="large" :loading="loading" native-type="submit" class="login-button">
            登录后台
          </el-button>
        </el-form>

        <div class="panel-foot">
          <span class="foot-dot"></span>
          <span>当前服务端口为 6567，登录后默认进入访客统计页。</span>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getSiteConfig, login } from '../api/admin'
import { setToken } from '../api/request'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = reactive({
  username: '',
  password: ''
})
const site = reactive({
  site_name: '出彩中原',
  site_logo: '/logo.png'
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const fallbackMark = computed(() => (site.site_name || '出').slice(0, 1))

async function loadSiteConfig() {
  try {
    const res = await getSiteConfig()
    site.site_name = res.data.site_name || '出彩中原'
    site.site_logo = res.data.site_logo || '/logo.png'
  } catch {
    site.site_name = '出彩中原'
    site.site_logo = '/logo.png'
  }
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

onMounted(loadSiteConfig)
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px 24px;
  background:
    radial-gradient(circle at top left, rgba(64, 158, 255, 0.18), transparent 24%),
    radial-gradient(circle at right center, rgba(64, 158, 255, 0.1), transparent 20%),
    linear-gradient(180deg, rgba(64, 158, 255, 0.05), transparent 36%),
    var(--admin-bg);
}

.login-shell {
  width: min(1180px, 100%);
  display: grid;
  grid-template-columns: 1.08fr 0.92fr;
  gap: 24px;
  align-items: stretch;
}

.login-brand,
.login-panel {
  padding: 40px;
  border-radius: 24px;
  border: 1px solid var(--admin-border);
  background:
    linear-gradient(180deg, rgba(64, 158, 255, 0.06), transparent 32%),
    var(--admin-panel);
}

.login-brand {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 640px;
}

.brand-top {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.brand-badge,
.panel-kicker {
  width: fit-content;
  margin: 0;
  padding: 7px 12px;
  border-radius: 999px;
  border: 1px solid rgba(64, 158, 255, 0.22);
  background: rgba(64, 158, 255, 0.08);
  color: var(--el-color-primary);
  font-size: 12px;
  letter-spacing: 0.08em;
}

.brand-logo-box {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.brand-logo {
  width: 88px;
  height: 88px;
  display: grid;
  place-items: center;
  flex: none;
  border-radius: 22px;
  border: 1px solid var(--admin-border);
  background: rgba(64, 158, 255, 0.08);
  overflow: hidden;
  color: var(--el-color-primary);
  font-size: 32px;
  font-weight: 700;
}

.brand-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.brand-title {
  min-width: 0;
}

.login-kicker {
  margin: 0 0 12px;
  color: var(--admin-muted);
  font-family: "JetBrains Mono", "Consolas", monospace;
  font-size: 13px;
}

.brand-title h1 {
  margin: 0;
  max-width: 520px;
  color: var(--admin-text);
  font-size: 52px;
  line-height: 1.08;
  font-weight: 700;
  letter-spacing: -0.03em;
}

.brand-text,
.panel-text {
  margin: 18px 0 0;
  color: var(--admin-muted);
  line-height: 1.8;
  font-size: 15px;
}

.brand-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.metric-card {
  padding: 18px 16px;
  border-radius: 18px;
  border: 1px solid var(--admin-border);
  background: rgba(255, 255, 255, 0.58);
}

:global(.dark) .metric-card {
  background: rgba(255, 255, 255, 0.03);
}

.metric-label {
  display: block;
  margin-bottom: 10px;
  color: var(--admin-muted);
  font-size: 12px;
}

.metric-card strong {
  display: block;
  color: var(--admin-text);
  font-size: 15px;
  line-height: 1.65;
  font-weight: 600;
}

.login-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 30px;
  min-height: 640px;
}

.panel-head h2 {
  margin: 16px 0 0;
  color: var(--admin-text);
  font-size: 34px;
  line-height: 1.15;
  font-weight: 700;
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}

:deep(.el-form-item__label) {
  color: var(--admin-text);
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  min-height: 48px;
  border-radius: 14px;
}

.login-button {
  width: 100%;
  min-height: 48px;
  margin-top: 6px;
  border-radius: 14px;
}

.panel-foot {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--admin-muted);
  font-size: 13px;
}

.foot-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--el-color-primary);
  flex: none;
}

@media (max-width: 1100px) {
  .login-shell {
    grid-template-columns: 1fr;
  }

  .login-brand,
  .login-panel {
    min-height: auto;
  }

  .brand-title h1 {
    max-width: none;
    font-size: 40px;
  }
}

@media (max-width: 760px) {
  .login-page {
    padding: 18px;
  }

  .login-brand,
  .login-panel {
    padding: 26px;
  }

  .brand-logo-box {
    flex-direction: column;
  }

  .brand-title h1,
  .panel-head h2 {
    font-size: 28px;
  }

  .brand-metrics {
    grid-template-columns: 1fr;
  }
}
</style>
