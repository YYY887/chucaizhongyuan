<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Location, Clock, Compass, Menu, Phone, Message, View } from '@element-plus/icons-vue'
import { getRouteList } from '../api/route'

const router = useRouter()
const routes = ref([])
const loading = ref(true)
const showNavDrawer = ref(false)

// 路线颜色配置
const routeColors = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
  '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2'
]

const getRouteColor = (index) => {
  return routeColors[index % routeColors.length]
}

const fetchRoutes = async () => {
  loading.value = true
  try {
    routes.value = await getRouteList({})
  } catch (error) {
    console.error('获取路线失败:', error)
  } finally {
    loading.value = false
  }
}

const goHome = () => {
  router.push('/')
}

const viewDetail = (routeId) => {
  router.push(`/route/${routeId}`)
}

const getPreviewPoints = (route) => route.attractions?.slice(0, 5) || []

onMounted(() => {
  fetchRoutes()
})
</script>

<template>
  <div class="recommend-page">
    <!-- 顶部导航栏 -->
    <header class="navbar">
      <div class="nav-content">
        <div class="logo" @click="goHome" style="cursor: pointer;">
          <img src="/logo.png" alt="出彩中原" class="logo-image" />
          <span class="logo-text">出彩中原</span>
        </div>

        <div class="nav-right desktop-only">
          <el-button text @click="router.push('/')">首页</el-button>
          <el-button text>路线推荐</el-button>
          <el-button text @click="router.push('/about')">关于我们</el-button>
          <el-button text>联系方式</el-button>
        </div>

        <!-- 移动端：导航菜单按钮 -->
        <button class="mobile-nav-btn" @click="showNavDrawer = true">
          <el-icon :size="24"><Menu /></el-icon>
        </button>
      </div>
    </header>

    <!-- 主要内容 -->
    <div class="recommend-content">
      <!-- 返回按钮 -->
      <div class="back-section">
        <el-button :icon="ArrowLeft" text @click="goHome">
          返回首页
        </el-button>
      </div>

      <!-- 标题区域 -->
      <section class="header-section">
        <h1 class="page-title">精选旅游路线</h1>
        <p class="page-subtitle">探索河南，发现中原文化之美</p>
      </section>

      <!-- 路线列表 -->
      <el-skeleton v-if="loading" :rows="5" animated style="padding: 24px;" />

      <el-empty v-else-if="!routes.length" description="暂无路线数据" />

      <section v-else class="routes-section">
        <div class="routes-grid">
          <div
            v-for="(route, index) in routes"
            :key="route.id"
            class="route-card"
            @click="viewDetail(route.id)"
          >
            <div class="route-cover-wrap">
              <div
                class="route-cover"
                :style="route.cover_image
                  ? { backgroundImage: `linear-gradient(rgba(15, 23, 42, 0.12), rgba(15, 23, 42, 0.36)), url(${route.cover_image})` }
                  : { background: `linear-gradient(135deg, ${getRouteColor(index)}1f, ${getRouteColor(index)}47)` }"
                "
                :class="{ 'route-cover-image': !!route.cover_image }"
              >
                <div class="route-cover-badge">
                  <span class="route-cover-index" :style="{ background: getRouteColor(index) }">
                    {{ index + 1 }}
                  </span>
                  <span class="route-cover-count">
                    <el-icon><View /></el-icon>
                    {{ route.attractions?.length || 0 }} 个景点
                  </span>
                </div>
              </div>
            </div>

            <div class="route-body">
              <div class="route-info">
                <h3 class="route-name">{{ route.name }}</h3>
                <p class="route-description">{{ route.description }}</p>

                <div class="route-meta">
                  <span class="meta-item">
                    <el-icon><Location /></el-icon>
                    {{ route.region }}
                  </span>
                  <span class="meta-item">
                    <el-icon><Clock /></el-icon>
                    {{ route.duration }}
                  </span>
                  <span class="meta-item">
                    <el-icon><Compass /></el-icon>
                    {{ route.route_type }}
                  </span>
                </div>

                <div class="route-tags">
                  <el-tag
                    :type="route.difficulty === '简单' ? 'success' : route.difficulty === '中等' ? 'warning' : 'danger'"
                    size="small"
                  >
                    {{ route.difficulty }}
                  </el-tag>
                </div>
              </div>

              <div v-if="route.attractions?.length" class="attractions-preview">
                <div class="preview-title">途经景点</div>
                <div class="preview-list">
                  <span
                    v-for="(attr, attrIndex) in getPreviewPoints(route)"
                    :key="attr.id"
                    class="preview-item"
                  >
                    {{ attrIndex + 1 }}. {{ attr.name }}
                  </span>
                  <span v-if="route.attractions.length > 5" class="preview-more">
                    继续查看剩余 {{ route.attractions.length - 5 }} 个景点
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

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
              <el-icon><Phone /></el-icon>
              <span>00000</span>
            </div>
            <div class="footer-item">
              <el-icon><Message /></el-icon>
              <span>3449837914@qq.com</span>
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
.recommend-page {
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
.recommend-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 24px 80px;
}

.back-section {
  margin-bottom: 32px;
}

/* 标题区域 */
.header-section {
  text-align: center;
  padding: 40px 0 60px;
}

.page-title {
  margin: 0 0 16px 0;
  font-size: 48px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.page-subtitle {
  margin: 0;
  font-size: 18px;
  color: var(--el-text-color-secondary);
}

/* 路线列表 */
.routes-section {
  margin-top: 40px;
}

.routes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 32px;
}

.route-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.28s ease, border-color 0.28s ease;
  display: grid;
}

.route-card:hover {
  transform: translateY(-6px);
  border-color: var(--el-color-primary-light-5);
}

.route-cover-wrap {
  padding: 18px 18px 0;
}

.route-cover {
  min-height: 220px;
  position: relative;
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-light);
}

.route-cover-image::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(15,23,42,0.12));
}

.route-cover-badge {
  position: absolute;
  inset: 18px 18px auto 18px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  z-index: 1;
}

.route-cover-index {
  min-width: 56px;
  height: 56px;
  padding: 0 14px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 700;
  color: white;
}

.route-cover-count {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  color: #1f2937;
  font-size: 13px;
  line-height: 1;
}

.route-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 172px;
  align-items: stretch;
}

.route-info {
  padding: 24px;
}

.route-name {
  margin: 0 0 12px 0;
  font-size: 22px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.route-description {
  margin: 0 0 16px 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
}

.route-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.route-tags {
  display: flex;
  align-items: center;
  gap: 12px;
}

.attractions-preview {
  border-left: 1px solid var(--el-border-color-light);
  background: linear-gradient(180deg, var(--el-fill-color-blank), var(--el-fill-color-light));
  padding: 22px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transform: translateX(22px);
  opacity: 0;
  transition: transform 0.28s ease, opacity 0.28s ease;
}

.route-card:hover .attractions-preview {
  transform: translateX(0);
  opacity: 1;
}

.preview-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.preview-item {
  font-size: 13px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

.preview-more {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

@media (max-width: 1080px) {
  .route-body {
    grid-template-columns: 1fr;
  }

  .attractions-preview {
    border-left: 0;
    border-top: 1px solid var(--el-border-color-light);
    transform: none;
    opacity: 1;
    padding: 18px 24px 24px;
  }
}

/* 响应式设计 - 移动端适配 */
@media (max-width: 768px) {
  .nav-right {
    display: none;
  }

  .mobile-nav-btn {
    display: flex;
  }

  .recommend-content {
    padding: 24px 16px 40px;
  }

  .page-title {
    font-size: 32px;
  }

  .page-subtitle {
    font-size: 16px;
  }

  .routes-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .route-name {
    font-size: 18px;
  }

  .route-cover-wrap {
    padding: 14px 14px 0;
  }

  .route-cover {
    min-height: 184px;
  }

  .route-info {
    padding: 18px;
  }

  .attractions-preview {
    padding: 16px 18px 18px;
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
