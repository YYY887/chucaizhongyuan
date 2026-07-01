<template>
  <el-container class="admin-page layout">
    <el-aside class="aside" width="232px">
      <div class="brand">
        <div class="brand-mark">
          <img v-if="site.site_logo" :src="site.site_logo" :alt="site.site_name" />
          <span v-else>{{ fallbackMark }}</span>
        </div>
        <div>
          <strong>{{ site.site_name || '出彩中原' }}</strong>
          <small>{{ site.site_subtitle || '管理后台' }}</small>
        </div>
      </div>
      <el-menu router :default-active="route.path" class="side-menu">
        <el-menu-item index="/dashboard"><el-icon><DataLine /></el-icon><span>访客统计</span></el-menu-item>
        <el-menu-item index="/site-config"><el-icon><Setting /></el-icon><span>站点配置</span></el-menu-item>
        <el-menu-item index="/banners"><el-icon><Picture /></el-icon><span>轮播图配置</span></el-menu-item>
        <el-menu-item index="/routes"><el-icon><Connection /></el-icon><span>路线管理</span></el-menu-item>
        <el-menu-item index="/points"><el-icon><Location /></el-icon><span>节点信息</span></el-menu-item>
        <el-menu-item index="/about"><el-icon><Document /></el-icon><span>关于我们</span></el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-title">{{ currentTitle }}</div>
        <div class="toolbar">
          <el-button :icon="themeIcon" plain @click="handleTheme">{{ themeText }}</el-button>
          <el-button plain @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Connection, DataLine, Document, Location, Moon, Picture, Setting, Sunny } from '@element-plus/icons-vue'
import { clearToken } from '../api/request'
import { getSiteConfig } from '../api/admin'
import { getTheme, toggleTheme } from '../stores/theme'

const route = useRoute()
const router = useRouter()
const theme = ref(getTheme())
const site = reactive({
  site_name: '出彩中原',
  site_subtitle: '管理后台',
  site_logo: '/logo.png'
})

const titles = {
  '/dashboard': '访客统计',
  '/site-config': '站点配置',
  '/banners': '轮播图配置',
  '/routes': '路线管理',
  '/points': '节点信息',
  '/about': '关于我们配置'
}

const currentTitle = computed(() => titles[route.path] || '管理后台')
const themeText = computed(() => (theme.value === 'dark' ? '日间' : '夜间'))
const themeIcon = computed(() => (theme.value === 'dark' ? Sunny : Moon))
const fallbackMark = computed(() => (site.site_name || '出').slice(0, 1))

async function loadSiteConfig() {
  try {
    const res = await getSiteConfig()
    Object.assign(site, res.data)
  } catch {
    // 保持默认配置，避免后台基础框架不可用
  }
}

function handleTheme() {
  theme.value = toggleTheme()
}

function logout() {
  clearToken()
  router.replace('/login')
}

onMounted(loadSiteConfig)
</script>

<style scoped>
.layout {
  min-height: 100dvh;
}

.aside {
  position: sticky;
  top: 0;
  height: 100dvh;
  overflow: hidden;
  border-right: 1px solid var(--admin-border);
  background: var(--admin-panel);
}

.brand {
  height: 72px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 18px;
  border-bottom: 1px solid var(--admin-border);
}

.brand-mark {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  color: var(--admin-accent);
  font-weight: 700;
  background: var(--admin-soft);
  overflow: hidden;
}

.brand-mark img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.brand strong,
.brand small {
  display: block;
}

.brand small {
  margin-top: 4px;
  color: var(--admin-muted);
}

.side-menu {
  height: calc(100dvh - 72px);
  overflow-y: auto;
  border-right: 0;
  background: transparent;
}

.header {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--admin-border);
  background: var(--admin-panel);
}

.header-title {
  font-size: 16px;
  font-weight: 650;
}

.main {
  padding: 22px;
}

@media (max-width: 760px) {
  .layout {
    display: block;
  }

  .aside {
    position: static;
    height: auto;
    width: 100% !important;
  }

  .side-menu {
    height: auto;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }

  .header {
    height: auto;
    align-items: flex-start;
    gap: 12px;
    padding: 14px;
    flex-direction: column;
  }

  .main {
    padding: 14px;
  }
}
</style>
