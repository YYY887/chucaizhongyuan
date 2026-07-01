<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Location, Clock, Compass, Menu, Phone, Message } from '@element-plus/icons-vue'
import { getRouteDetail } from '../api/route'
import AMap from '../components/AMap.vue'

const route = useRoute()
const router = useRouter()

const routeDetail = ref(null)
const loading = ref(true)
const selectedAttraction = ref(null)

// 移动端抽屉状态
const showAttractionsDrawer = ref(false)
const showNavDrawer = ref(false)

// 路线颜色配置
const routeColors = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
  '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2'
]

const getAttractionColor = (index) => {
  if (!routeDetail.value) return routeColors[0]
  // 使用路线ID来保持颜色一致
  return routeColors[routeDetail.value.id % routeColors.length]
}

// 将路线详情转换为地图组件需要的格式
const mapRoutes = computed(() => {
  if (!routeDetail.value) return []
  return [{
    id: routeDetail.value.id,
    name: routeDetail.value.name,
    attractions: routeDetail.value.attractions || []
  }]
})

// 获取路线详情
const fetchRouteDetail = async () => {
  loading.value = true
  try {
    const id = route.params.id
    routeDetail.value = await getRouteDetail(id)
  } catch (error) {
    console.error('获取路线详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 返回首页
const goBack = () => {
  router.push('/')
}

// 选择景点
const selectAttraction = (attraction) => {
  selectedAttraction.value = attraction
  console.log('定位到景点:', attraction)
}

const getAttractionImage = (attraction) => attraction?.image_url || ''

onMounted(() => {
  fetchRouteDetail()
})
</script>

<template>
  <div class="detail-page">
    <!-- 顶部导航栏 -->
    <header class="navbar">
      <div class="nav-content">
        <div class="logo" @click="goBack" style="cursor: pointer;">
          <img src="/logo.png" alt="出彩中原" class="logo-image" />
          <span class="logo-text">出彩中原</span>
        </div>

        <div class="nav-right desktop-only">
          <el-button text>首页</el-button>
          <el-button text>路线推荐</el-button>
          <el-button text>关于我们</el-button>
          <el-button text>联系方式</el-button>
        </div>

        <!-- 移动端：导航菜单按钮 -->
        <button class="mobile-nav-btn" @click="showNavDrawer = true">
          <el-icon :size="24"><Menu /></el-icon>
        </button>
      </div>
    </header>

    <div class="detail-container">
    <!-- 加载状态 -->
    <el-skeleton v-if="loading" :rows="10" animated style="padding: 24px;" />

    <!-- 详情内容 -->
    <el-container v-else-if="routeDetail" class="detail-content">
      <!-- 移动端：景点列表按钮 -->
      <button class="mobile-attractions-btn" @click="showAttractionsDrawer = true">
        <el-icon :size="20"><Location /></el-icon>
        <span>景点列表</span>
      </button>

      <!-- 左侧信息面板 -->
      <el-aside width="420px" class="detail-sidebar desktop-only">
        <div class="sidebar-content">
          <!-- 返回按钮 -->
          <el-button :icon="ArrowLeft" text @click="goBack" class="back-button">
            返回首页
          </el-button>

          <!-- 路线标题 -->
          <div class="route-info">
            <h1 class="route-title">{{ routeDetail.name }}</h1>

            <el-space wrap>
              <el-tag
                :type="routeDetail.difficulty === '简单' ? 'success' : routeDetail.difficulty === '中等' ? 'warning' : 'danger'"
              >
                {{ routeDetail.difficulty }}
              </el-tag>

              <span class="info-item">
                <el-icon><Location /></el-icon>
                {{ routeDetail.region }}
              </span>

              <span class="info-item">
                <el-icon><Clock /></el-icon>
                {{ routeDetail.duration }}
              </span>

              <span class="info-item">
                <el-icon><Compass /></el-icon>
                {{ routeDetail.route_type }}
              </span>
            </el-space>

            <p class="route-description">{{ routeDetail.description }}</p>
          </div>

          <el-divider />

          <!-- 景点列表 -->
          <div class="attractions-section">
            <h3 class="section-title">
              景点列表 ({{ routeDetail.attractions.length }})
            </h3>

            <div class="attraction-list">
              <div
                v-for="(attraction, index) in routeDetail.attractions"
                :key="attraction.id"
                class="attraction-card"
                :class="{ active: selectedAttraction?.id === attraction.id }"
                :style="selectedAttraction?.id === attraction.id ? { '--route-color': getAttractionColor(index) } : {}"
                @click="selectAttraction(attraction)"
              >
                <div class="attraction-content">
                  <div class="attraction-image">
                    <img
                      v-if="getAttractionImage(attraction)"
                      :src="getAttractionImage(attraction)"
                      :alt="attraction.name"
                    />
                    <div v-else class="attraction-image-empty">暂无图片</div>
                    <div class="order-badge" :style="{ background: getAttractionColor(index) }">
                      {{ attraction.order }}
                    </div>
                  </div>
                  <div class="attraction-info">
                    <h4 class="attraction-name">{{ attraction.name }}</h4>
                    <p v-if="attraction.description" class="attraction-desc">
                      {{ attraction.description }}
                    </p>
                    <div v-if="attraction.address" class="attraction-address">
                      <el-icon><Location /></el-icon>
                      {{ attraction.address }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-aside>

      <!-- 右侧地图区域 -->
      <el-main class="map-container">
        <AMap :routes="mapRoutes" :selected-route="mapRoutes[0]" :selected-attraction="selectedAttraction" />
      </el-main>
    </el-container>

    <!-- 错误状态 -->
    <el-result
      v-else
      icon="error"
      title="路线不存在"
      sub-title="请返回首页重新选择"
    >
      <template #extra>
        <el-button type="primary" @click="goBack">返回首页</el-button>
      </template>
    </el-result>
  </div>

  <!-- 移动端：景点列表抽屉 -->
  <el-drawer v-model="showAttractionsDrawer" direction="ltr" size="85%" :title="`${routeDetail?.name || ''} - 景点列表`">
    <div v-if="routeDetail" class="drawer-content">
      <!-- 路线信息摘要 -->
      <div class="route-summary">
        <el-space :size="8" wrap>
          <el-tag
            :type="routeDetail.difficulty === '简单' ? 'success' : routeDetail.difficulty === '中等' ? 'warning' : 'danger'"
            size="small"
          >
            {{ routeDetail.difficulty }}
          </el-tag>
          <span class="summary-item">
            <el-icon><Location /></el-icon>
            {{ routeDetail.region }}
          </span>
          <span class="summary-item">
            <el-icon><Clock /></el-icon>
            {{ routeDetail.duration }}
          </span>
        </el-space>
      </div>

      <el-divider />

      <!-- 景点列表 -->
      <el-scrollbar height="calc(100vh - 200px)">
        <div
          v-for="(attraction, index) in routeDetail.attractions"
          :key="attraction.id"
          class="attraction-card"
          :class="{ active: selectedAttraction?.id === attraction.id }"
          :style="selectedAttraction?.id === attraction.id ? { '--route-color': getAttractionColor(index) } : {}"
          @click="selectAttraction(attraction); showAttractionsDrawer = false"
        >
          <div class="attraction-content">
            <div class="attraction-image">
              <img
                v-if="getAttractionImage(attraction)"
                :src="getAttractionImage(attraction)"
                :alt="attraction.name"
              />
              <div v-else class="attraction-image-empty">暂无图片</div>
              <div class="order-badge" :style="{ background: getAttractionColor(index) }">
                {{ attraction.order }}
              </div>
            </div>
            <div class="attraction-info">
              <h4 class="attraction-name">{{ attraction.name }}</h4>
              <p v-if="attraction.description" class="attraction-desc">
                {{ attraction.description }}
              </p>
              <div v-if="attraction.address" class="attraction-address">
                <el-icon><Location /></el-icon>
                {{ attraction.address }}
              </div>
            </div>
          </div>
        </div>
      </el-scrollbar>
    </div>
  </el-drawer>

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
.detail-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
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

.detail-container {
  flex: 1;
  height: calc(100vh - 64px);
  overflow: hidden;
}

.detail-content {
  height: 100%;
  overflow: hidden;
}

.detail-sidebar {
  width: 380px;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color);
  overflow-y: auto;
  height: 100%;
}

.sidebar-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.back-button {
  align-self: flex-start;
  padding-left: 0;
}

.route-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.route-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1.3;
}

.info-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.route-description {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
  line-height: 1.6;
}

.attractions-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.attraction-list {
  position: relative;
  padding-left: 32px;
}

/* 垂直时间线 */
.attraction-list::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--el-border-color);
}

.attraction-card {
  position: relative;
  margin-bottom: 24px;
  cursor: pointer;
  transition: all 0.3s;
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
}

.attraction-card:hover {
  transform: translateX(4px);
}

.attraction-card.active .attraction-content {
  background: var(--el-color-primary-light-9);
  border-left-color: var(--route-color, #3C5A78);
}

/* 时间线节点 */
.attraction-card::before {
  content: '';
  position: absolute;
  left: -25px;
  top: 8px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--el-bg-color);
  border: 2px solid var(--el-border-color);
  z-index: 1;
}

.attraction-card.active::before {
  background: #3C5A78;
  border-color: #3C5A78;
  box-shadow: 0 0 0 4px rgba(60, 90, 120, 0.1);
}

.attraction-content {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  border-left: 3px solid transparent;
  background: var(--el-fill-color-light);
  transition: all 0.3s;
}

.attraction-image {
  position: relative;
  flex-shrink: 0;
  width: 120px;
  height: 100px;
  border-radius: 6px;
  overflow: hidden;
}

.attraction-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.attraction-image-empty {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  background: var(--el-fill-color-light);
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.order-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  background: #3C5A78;
  color: white;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.attraction-info {
  flex: 1;
  min-width: 0;
}

.attraction-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.attraction-desc {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

.attraction-address {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

.map-container {
  flex: 1;
  padding: 0;
  background: var(--el-bg-color-page);
  height: 100%;
  overflow: hidden;
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

/* 移动端景点列表按钮 */
.mobile-attractions-btn {
  display: none;
}

/* 响应式设计 - 移动端适配 */
@media (max-width: 768px) {
  .nav-right {
    display: none;
  }

  .mobile-nav-btn {
    display: flex;
  }

  .detail-content {
    flex-direction: column;
  }

  .detail-sidebar {
    display: none !important;
  }

  /* 移动端景点按钮 */
  .mobile-attractions-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    position: fixed;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    z-index: 999;
    width: 48px;
    height: 120px;
    background: var(--el-color-primary);
    color: white;
    border: none;
    border-radius: 0 8px 8px 0;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
    writing-mode: vertical-rl;
    letter-spacing: 4px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: all 0.3s;
    gap: 6px;
  }

  .mobile-attractions-btn:active {
    transform: translateY(-50%) scale(0.95);
  }

  .map-container {
    height: calc(100vh - 64px) !important;
  }

  .route-title {
    font-size: 20px;
  }

  .attraction-image {
    width: 80px;
    height: 66px;
  }
}
</style>
