<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Menu, Phone, Message } from '@element-plus/icons-vue'
import { getPublicAbout, getPublicSiteConfig } from '../api/config'

const router = useRouter()
const showNavDrawer = ref(false)
const site = ref({
  site_name: '出彩中原',
  site_subtitle: '河南旅游路线导航平台',
  site_logo: '/logo.png'
})
const aboutInfo = ref({
  title: '关于我们',
  content: '',
  contact: ''
})

const goHome = () => {
  router.push('/')
}

const features = ref([
  {
    title: '精选路线',
    desc: '精心策划河南省内多条旅游路线，涵盖历史文化、自然风光、特色体验等多种主题'
  },
  {
    title: '智能规划',
    desc: '根据您的出发地和目的地，智能推荐最适合的旅游路线，让您的旅程更加便捷'
  },
  {
    title: '地图导航',
    desc: '集成高德地图，实时显示景点位置和路线规划，为您的出行提供精准导航'
  },
  {
    title: '详细信息',
    desc: '每个景点都配有详细的介绍、地址、图片等信息，帮助您更好地了解河南文化'
  }
])

const team = ref([
  { name: '出彩中原团队', role: '致力于推广河南旅游文化' }
])

const fetchPageConfig = async () => {
  try {
    site.value = await getPublicSiteConfig()
    aboutInfo.value = await getPublicAbout()
  } catch (error) {
    console.error('获取关于页配置失败:', error)
  }
}

onMounted(() => {
  fetchPageConfig()
})
</script>

<template>
  <div class="about-page">
    <!-- 顶部导航栏 -->
    <header class="navbar">
      <div class="nav-content">
        <div class="logo" @click="goHome" style="cursor: pointer;">
          <img :src="site.site_logo" :alt="site.site_name" class="logo-image" />
          <span class="logo-text">{{ site.site_name }}</span>
        </div>

        <div class="nav-right desktop-only">
          <el-button text @click="router.push('/')">首页</el-button>
          <el-button text @click="router.push('/recommend')">路线推荐</el-button>
          <el-button text>关于我们</el-button>
          <el-button text>联系方式</el-button>
        </div>

        <!-- 移动端：导航菜单按钮 -->
        <button class="mobile-nav-btn" @click="showNavDrawer = true">
          <el-icon :size="24"><Menu /></el-icon>
        </button>
      </div>
    </header>

    <!-- 主要内容 -->
    <div class="about-content">
      <!-- 返回按钮 -->
      <div class="back-section">
        <el-button :icon="ArrowLeft" text @click="goHome">
          返回首页
        </el-button>
      </div>

      <!-- 品牌介绍区域 -->
      <section class="hero-section">
        <div class="hero-content">
          <div class="brand-identity">
            <img :src="site.site_logo" :alt="site.site_name" class="hero-logo" />
            <h1 class="hero-title">{{ site.site_name }}</h1>
            <p class="hero-subtitle">{{ site.site_subtitle }}</p>
          </div>
          <p class="hero-desc">{{ aboutInfo.content }}</p>
        </div>
      </section>

      <!-- 特色功能 -->
      <section class="features-section">
        <h2 class="section-title">我们的特色</h2>
        <div class="features-grid">
          <div v-for="(feature, index) in features" :key="index" class="feature-card">
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-desc">{{ feature.desc }}</p>
          </div>
        </div>
      </section>

      <!-- 团队介绍 -->
      <section class="team-section">
        <h2 class="section-title">关于团队</h2>
        <div class="team-content">
          <p class="team-intro">
            我们是一支热爱河南文化、专注旅游服务的团队。通过整合河南省内优质旅游资源，
            结合现代化的技术手段，为广大游客提供便捷、专业的旅游路线规划服务。
            我们相信，每一次旅行都是一次文化的探索，每一个景点都承载着中原大地的历史记忆。
          </p>
        </div>
      </section>

      <!-- 联系方式 -->
      <section class="contact-section">
        <h2 class="section-title">联系我们</h2>
        <div class="contact-grid">
          <div class="contact-item">
            <div class="contact-label">邮箱</div>
            <div class="contact-value">{{ aboutInfo.contact || '暂无联系方式' }}</div>
          </div>
        </div>
      </section>
    </div>

    <footer class="about-footer">
      <div class="about-footer-content">
        <div class="about-footer-brand">
          <img :src="site.site_logo" :alt="site.site_name" class="about-footer-logo" />
          <div>
            <div class="about-footer-name">{{ site.site_name }}</div>
            <p>{{ aboutInfo.content || site.site_subtitle }}</p>
          </div>
        </div>
        <div class="about-footer-contact">
          <h3>联系方式</h3>
          <div class="footer-item">
            <el-icon><Message /></el-icon>
            <span>{{ aboutInfo.contact || '暂无联系方式' }}</span>
          </div>
        </div>
      </div>
    </footer>

    <!-- 移动端：导航菜单抽屉 -->
    <el-drawer v-model="showNavDrawer" direction="rtl" size="75%" title="菜单">
      <div class="nav-drawer-content">
        <div class="nav-drawer-items">
          <el-button text size="large" @click="router.push('/'); showNavDrawer = false" class="nav-drawer-item">
            首页
          </el-button>
          <el-button text size="large" @click="router.push('/recommend'); showNavDrawer = false" class="nav-drawer-item">
            路线推荐
          </el-button>
          <el-button text size="large" @click="router.push('/about'); showNavDrawer = false" class="nav-drawer-item">
            关于我们
          </el-button>
          <el-button text size="large" class="nav-drawer-item">
            联系方式
          </el-button>
        </div>

        <!-- 页脚信息 -->
        <div class="drawer-footer">
          <div class="drawer-footer-section">
            <h4>联系方式</h4>
            <div class="footer-item">
              <el-icon><Message /></el-icon>
              <span>{{ aboutInfo.contact || '暂无联系方式' }}</span>
            </div>
          </div>
          <div class="drawer-footer-bottom">
            <p>&copy; 2024 出彩中原. All rights reserved.</p>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped>
.about-page {
  min-height: 100vh;
  background: var(--el-bg-color-page);
}

/* 顶部导航栏 */
.navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  height: 64px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);
  backdrop-filter: blur(10px);
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-image {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 主要内容 */
.about-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px 80px;
}

.back-section {
  margin-bottom: 32px;
}

/* 品牌介绍 */
.hero-section {
  text-align: center;
  padding: 60px 0;
  margin-bottom: 80px;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.brand-identity {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 32px;
}

.hero-logo {
  width: 120px;
  height: 120px;
  object-fit: contain;
  margin-bottom: 24px;
}

.hero-title {
  margin: 0 0 12px 0;
  font-size: 48px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.hero-subtitle {
  margin: 0;
  font-size: 20px;
  color: var(--el-text-color-secondary);
}

.hero-desc {
  margin: 0;
  font-size: 16px;
  line-height: 1.8;
  color: var(--el-text-color-regular);
  text-align: left;
}

/* 特色功能 */
.features-section {
  margin-bottom: 80px;
}

.section-title {
  margin: 0 0 40px 0;
  font-size: 32px;
  font-weight: 700;
  text-align: center;
  color: var(--el-text-color-primary);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.feature-card {
  padding: 32px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 12px;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.feature-title {
  margin: 0 0 16px 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.feature-desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
}

/* 团队介绍 */
.team-section {
  margin-bottom: 80px;
}

.team-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 12px;
}

.team-intro {
  margin: 0;
  font-size: 16px;
  line-height: 1.8;
  color: var(--el-text-color-regular);
}

/* 联系方式 */
.contact-section {
  margin-bottom: 40px;
}

.contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.contact-item {
  padding: 32px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 12px;
  text-align: center;
}

.contact-label {
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.contact-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.about-footer {
  border-top: 1px solid var(--el-border-color);
  background: var(--el-bg-color);
}

.about-footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.about-footer-brand {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  max-width: 720px;
}

.about-footer-logo {
  width: 40px;
  height: 40px;
  object-fit: contain;
  flex-shrink: 0;
}

.about-footer-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.about-footer-brand p {
  margin: 8px 0 0;
  color: var(--el-text-color-regular);
  line-height: 1.7;
}

.about-footer-contact h3 {
  margin: 0 0 12px;
  font-size: 16px;
  color: var(--el-text-color-primary);
}

/* 响应式设计 - 移动端适配 */
@media (max-width: 768px) {
  .nav-right {
    display: none;
  }

  .mobile-nav-btn {
    display: flex;
  }

  .about-content {
    padding: 24px 16px 40px;
  }

  .hero-logo {
    width: 80px;
    height: 80px;
  }

  .hero-title {
    font-size: 32px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .section-title {
    font-size: 24px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .contact-grid {
    grid-template-columns: 1fr;
  }

  .about-footer-content {
    flex-direction: column;
  }
}

/* 移动端导航按钮 */
.mobile-nav-btn {
  display: none;
  align-items: center;
  justify-content: center;
  padding: 8px;
  background: transparent;
  border: none;
  color: var(--el-text-color-primary);
  cursor: pointer;
  transition: all 0.3s;
}

.mobile-nav-btn:hover {
  background: var(--el-fill-color-light);
  border-radius: 8px;
}

.mobile-nav-btn:active {
  transform: scale(0.95);
}

/* 导航抽屉内容 */
.nav-drawer-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  justify-content: space-between;
}

.nav-drawer-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 0;
}

.nav-drawer-item {
  width: 100%;
  justify-content: flex-start;
  padding: 16px 20px;
  font-size: 16px;
  border-radius: 8px;
  transition: all 0.3s;
}

.nav-drawer-item:hover {
  background: var(--el-fill-color-light);
}

/* 抽屉页脚 */
.drawer-footer {
  padding: 24px 0;
  border-top: 1px solid var(--el-border-color);
}

.drawer-footer-section {
  margin-bottom: 20px;
}

.drawer-footer-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
}

.footer-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.drawer-footer-bottom {
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
  text-align: center;
}

.drawer-footer-bottom p {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}
</style>
