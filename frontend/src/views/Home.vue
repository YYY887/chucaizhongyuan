<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Location, Check, Search, Right, Phone, Message, IceCreamRound, Menu } from '@element-plus/icons-vue'
import { getRouteList, getRegionList } from '../api/route'
import { getPublicAbout, getPublicBanners, getPublicSiteConfig, getPublicVisitSummary } from '../api/config'
import AMap from '../components/AMap.vue'

const router = useRouter()

// 搜索结果状态
const searchActive = ref(false)
const filteredRoutes = ref([])
const filteredRegions = ref([])

const routes = ref([])
const regions = ref([])
const loading = ref(true)
const selectedRegion = ref('')
const selectedRoute = ref(null)
const hoveredRoute = ref(null)
const selectedAttraction = ref(null)

// 移动端抽屉状态
const showRoutesDrawer = ref(false)
const showRegionsDrawer = ref(false)
const showSearchDrawer = ref(false)
const showNavDrawer = ref(false)

// 路线规划
const planForm = ref({
  from: '',
  to: ''
})

// 所有景点和城市列表（用于自动补全）
const allLocations = ref([])

// 获取所有地点列表
const fetchAllLocations = async () => {
  try {
    // 从路线中提取所有景点和城市
    const locations = new Set()
    routes.value.forEach(route => {
      // 添加区域/城市
      locations.add(route.region)
      // 添加所有景点
      route.attractions?.forEach(attr => {
        locations.add(attr.name)
        if (attr.address) {
          // 从地址中提取城市名
          const cityMatch = attr.address.match(/(.+?市)/)
          if (cityMatch) locations.add(cityMatch[1])
        }
      })
    })
    allLocations.value = Array.from(locations).map(name => ({ value: name }))
  } catch (error) {
    console.error('获取地点列表失败:', error)
  }
}

// 地点搜索方法
const querySearchLocation = (queryString, cb) => {
  if (!queryString) {
    cb(allLocations.value)
    return
  }
  const results = allLocations.value.filter(item =>
    item.value.toLowerCase().includes(queryString.toLowerCase())
  )
  cb(results)
}

const banners = ref([])
const site = ref({
  site_name: '出彩中原',
  site_subtitle: '河南旅游路线导航平台',
  site_logo: '/logo.png'
})
const aboutInfo = ref({
  title: '关于我们',
  content: '出彩中原致力于推广河南旅游文化，为游客提供最优质的旅游路线规划服务。',
  contact: ''
})

const visitorCount = ref(0)

// 路线颜色配置
const routeColors = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
  '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2'
]

const fetchRoutes = async () => {
  loading.value = true
  try {
    const params = {}
    if (selectedRegion.value) params.region = selectedRegion.value
    routes.value = await getRouteList(params)
    // 获取路线后更新地点列表
    fetchAllLocations()
  } catch (error) {
    console.error('获取路线失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchRegions = async () => {
  try {
    regions.value = await getRegionList()
  } catch (error) {
    console.error('获取区域失败:', error)
  }
}

const fetchSiteConfig = async () => {
  try {
    site.value = await getPublicSiteConfig()
  } catch (error) {
    console.error('获取站点配置失败:', error)
  }
}

const fetchBanners = async () => {
  try {
    const list = await getPublicBanners()
    banners.value = list.map(item => ({
      id: item.id,
      title: item.title,
      desc: item.description || site.value.site_subtitle,
      image: item.image_url
    }))
  } catch (error) {
    console.error('获取轮播图失败:', error)
  }
}

const fetchAbout = async () => {
  try {
    aboutInfo.value = await getPublicAbout()
  } catch (error) {
    console.error('获取关于我们配置失败:', error)
  }
}

const fetchVisitSummary = async () => {
  try {
    const summary = await getPublicVisitSummary()
    visitorCount.value = summary.total || 0
  } catch (error) {
    console.error('获取访客统计失败:', error)
  }
}

const handleRegionClick = (region) => {
  selectedRegion.value = selectedRegion.value === region ? '' : region
  fetchRoutes()
}

const handleRouteClick = (route) => {
  router.push(`/route/${route.id}`)
}

const handlePlan = () => {
  console.log('规划路线:', planForm.value)

  if (!planForm.value.from || !planForm.value.to) {
    ElMessage.warning('请输入出发地和目的地')
    return
  }

  // 搜索包含出发地或目的地的路线
  const foundRoutes = routes.value.filter(route => {
    const routeText = `${route.name} ${route.description} ${route.region}`
    const attractions = route.attractions?.map(a => a.name).join(' ') || ''
    return routeText.includes(planForm.value.from) ||
           routeText.includes(planForm.value.to) ||
           attractions.includes(planForm.value.from) ||
           attractions.includes(planForm.value.to)
  })

  if (foundRoutes.length === 0) {
    ElMessage.info('未找到相关路线，请尝试其他地点')
    // 清除搜索状态
    searchActive.value = false
    filteredRoutes.value = []
    filteredRegions.value = []
    selectedRoute.value = null
  } else {
    ElMessage.success(`找到 ${foundRoutes.length} 条相关路线`)
    // 激活搜索状态
    searchActive.value = true
    filteredRoutes.value = foundRoutes

    // 筛选相关区域
    const relatedRegions = new Set(foundRoutes.map(r => r.region))
    filteredRegions.value = regions.value.filter(r => relatedRegions.has(r.region))

    // 高亮第一条匹配的路线
    selectedRoute.value = foundRoutes[0]
  }
}

const getRouteColor = (index) => {
  return routeColors[index % routeColors.length]
}

// 显示的路线列表（搜索时显示搜索结果，否则显示全部）
const displayRoutes = computed(() => {
  return searchActive.value ? filteredRoutes.value : routes.value
})

// 显示的区域列表（搜索时显示搜索结果，否则显示全部）
const displayRegions = computed(() => {
  return searchActive.value ? filteredRegions.value : regions.value
})

// 选择景点
const selectAttraction = (attraction) => {
  selectedAttraction.value = attraction
  console.log('选中景点:', attraction)
}

onMounted(() => {
  fetchSiteConfig()
  fetchBanners()
  fetchAbout()
  fetchVisitSummary()
  fetchRegions()
  fetchRoutes()
})
</script>

<template>
  <div class="home-page">
    <!-- 顶部导航栏 -->
    <header class="navbar">
      <div class="nav-content">
        <div class="logo">
          <img :src="site.site_logo" :alt="site.site_name" class="logo-image" />
          <span class="logo-text">{{ site.site_name }}</span>
        </div>

        <div class="nav-right desktop-only">
          <el-button text @click="router.push('/')">首页</el-button>
          <el-button text @click="router.push('/recommend')">路线推荐</el-button>
          <el-button text @click="router.push('/about')">关于我们</el-button>
          <el-button text>联系方式</el-button>
        </div>

        <!-- 移动端：导航菜单按钮 -->
        <button class="mobile-nav-btn" @click="showNavDrawer = true">
          <el-icon :size="24"><Menu /></el-icon>
        </button>
      </div>
    </header>

    <!-- 主要内容区域（可滚动） -->
    <div class="page-content">
      <!-- 轮播图区域 -->
      <section class="banner-section">
        <el-carousel height="700px" arrow="always" indicator-position="outside">
          <el-carousel-item v-for="banner in banners" :key="banner.id">
            <div class="banner-item" :style="{ backgroundImage: `url(${banner.image})` }">
              <div class="banner-overlay">
                <h2 class="banner-title">{{ banner.title }}</h2>
                <p class="banner-desc">{{ banner.desc }}</p>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </section>

      <!-- 路线规划区域 -->
      <section class="planner-section">
        <div class="planner-container">
          <div class="planner-form">
            <span class="planner-label">规划您的旅程：</span>
            <div class="planner-inputs">
              <el-autocomplete
                v-model="planForm.from"
                :fetch-suggestions="querySearchLocation"
                placeholder="请输入出发地"
                clearable
                size="large"
                class="planner-input"
                :trigger-on-focus="true"
              >
                <template #prefix><el-icon><Location /></el-icon></template>
              </el-autocomplete>
              <el-icon class="arrow-icon"><Right /></el-icon>
              <el-autocomplete
                v-model="planForm.to"
                :fetch-suggestions="querySearchLocation"
                placeholder="请输入目的地"
                clearable
                size="large"
                class="planner-input"
                :trigger-on-focus="true"
              >
                <template #prefix><el-icon><Location /></el-icon></template>
              </el-autocomplete>
              <el-button type="primary" size="large" @click="handlePlan">
                <el-icon style="margin-right: 8px;"><Search /></el-icon>
                搜索路线
              </el-button>
            </div>
          </div>
        </div>
      </section>

      <!-- 地图区域 -->
      <section class="map-section">
        <div class="map-wrapper">
          <!-- 移动端：左侧路线按钮 -->
          <button class="mobile-drawer-btn left" @click="showRoutesDrawer = true">
            <span>路线</span>
          </button>

          <!-- 移动端：右侧区域按钮 -->
          <button class="mobile-drawer-btn right" @click="showRegionsDrawer = true">
            <span>区域</span>
          </button>

          <!-- 移动端：底部搜索按钮 -->
          <button class="mobile-drawer-btn bottom" @click="showSearchDrawer = true">
            <el-icon :size="16"><Search /></el-icon>
            <span>搜索</span>
          </button>

          <!-- 桌面端：左侧路线列表 -->
          <aside class="routes-sidebar desktop-only">
            <div class="sidebar-header">
              <h2>河南旅游路线</h2>
              <p class="subtitle">{{ displayRoutes.length }} 条{{ searchActive ? '搜索结果' : '精选路线' }}</p>
            </div>

            <el-scrollbar class="routes-list">
              <div
                v-for="(route, index) in displayRoutes"
                :key="route.id"
                class="route-section"
              >
                <div
                  class="route-header"
                  :class="{ active: selectedRoute?.id === route.id }"
                  @click="handleRouteClick(route)"
                  @mouseenter="hoveredRoute = route"
                  @mouseleave="hoveredRoute = null"
                >
                  <div class="route-number" :style="{ background: getRouteColor(index) }">
                    {{ index + 1 }}
                  </div>
                  <div class="route-content">
                    <h3 class="route-name">{{ route.name }}</h3>
                    <div class="route-progress">
                      <div class="progress-bar" :style="{ background: getRouteColor(index), width: '100%' }"></div>
                    </div>
                  </div>
                </div>

                <!-- 景点缩略图列表（仅选中路线时显示） -->
                <div v-if="selectedRoute?.id === route.id && route.attractions?.length" class="attractions-thumbs">
                  <div
                    v-for="(attr, attrIndex) in route.attractions"
                    :key="attr.id"
                    class="thumb-item"
                    @click.stop="selectAttraction(attr)"
                  >
                    <img
                      :src="`https://picsum.photos/seed/${route.id}-${attr.id}/100/80`"
                      :alt="attr.name"
                      class="thumb-image"
                    />
                    <div class="thumb-info">
                      <span class="thumb-order" :style="{ color: getRouteColor(index) }">{{ attrIndex + 1 }}</span>
                      <span class="thumb-name">{{ attr.name }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </el-scrollbar>
          </aside>

          <!-- 中间地图区域 -->
          <main class="map-container">
            <AMap :routes="displayRoutes" :selected-route="selectedRoute" :selected-region="selectedRegion" :hovered-route="hoveredRoute" :selected-attraction="selectedAttraction" />
          </main>

          <!-- 右侧区域筛选 -->
          <aside class="regions-sidebar desktop-only">
            <div class="sidebar-header">
              <h2>选择区域</h2>
              <el-button v-if="selectedRegion || searchActive" text size="small" @click="selectedRegion = ''; searchActive = false; fetchRoutes()">
                清除筛选
              </el-button>
            </div>

            <el-scrollbar class="regions-list">
              <div
                v-for="region in displayRegions"
                :key="region.region"
                class="region-item"
                :class="{ active: selectedRegion === region.region }"
                @click="handleRegionClick(region.region)"
              >
                <div class="region-flag">
                  <el-icon :size="24"><Location /></el-icon>
                </div>
                <div class="region-info">
                  <h4>{{ region.region }}</h4>
                  <span class="count">{{ region.count }} 条路线</span>
                </div>
                <el-icon v-if="selectedRegion === region.region" class="check-icon" color="#3C5A78">
                  <Check />
                </el-icon>
              </div>
            </el-scrollbar>
          </aside>
        </div>
      </section>

      <!-- 页脚 -->
      <footer class="footer">
        <div class="footer-content">
          <div class="footer-row">
            <div class="footer-col">
              <div class="footer-logo">
                <img :src="site.site_logo" :alt="site.site_name" class="footer-logo-image" />
                <span class="footer-logo-text">{{ site.site_name }}</span>
              </div>
              <p>{{ aboutInfo.content || site.site_subtitle }}</p>
            </div>

            <div class="footer-col">
              <h3>联系方式</h3>
              <div class="contact-item">
                <el-icon><Message /></el-icon>
                <span>{{ aboutInfo.contact || '暂无联系方式' }}</span>
              </div>
            </div>

            <div class="footer-col">
              <h3>快速链接</h3>
              <a href="#" class="footer-link">首页</a>
              <a href="#" class="footer-link">路线推荐</a>
              <a href="#" class="footer-link">关于我们</a>
              <a href="#" class="footer-link">联系我们</a>
            </div>

            <div class="footer-col">
              <h3>统计信息</h3>
              <div class="stat-item">
                <el-icon><IceCreamRound /></el-icon>
                <span>访客总数：{{ visitorCount.toLocaleString() }}</span>
              </div>
            </div>
          </div>

          <el-divider style="background: rgba(255,255,255,0.1);" />

          <div class="footer-bottom">
            <p>© 2024 出彩中原旅游网 版权所有</p>
            <p>豫ICP备2024000000号 | 豫公网安备 41000000000000号</p>
          </div>
        </div>
      </footer>
    </div>

    <!-- 移动端：路线抽屉 -->
    <el-drawer v-model="showRoutesDrawer" direction="ltr" size="80%" title="河南旅游路线">
      <div class="drawer-content">
        <p class="drawer-subtitle">{{ displayRoutes.length }} 条{{ searchActive ? '搜索结果' : '精选路线' }}</p>
        <el-scrollbar height="calc(100vh - 120px)">
          <div
            v-for="(route, index) in displayRoutes"
            :key="route.id"
            class="route-section"
          >
            <div
              class="route-header"
              :class="{ active: selectedRoute?.id === route.id }"
              @click="handleRouteClick(route); showRoutesDrawer = false"
            >
              <div class="route-number" :style="{ background: getRouteColor(index) }">
                {{ index + 1 }}
              </div>
              <div class="route-content">
                <h3 class="route-name">{{ route.name }}</h3>
                <div class="route-progress">
                  <div class="progress-bar" :style="{ background: getRouteColor(index), width: '100%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </el-drawer>

    <!-- 移动端：区域抽屉 -->
    <el-drawer v-model="showRegionsDrawer" direction="rtl" size="80%" title="选择区域">
      <div class="drawer-content">
        <el-button v-if="selectedRegion || searchActive" text size="small" @click="selectedRegion = ''; searchActive = false; fetchRoutes(); showRegionsDrawer = false">
          清除筛选
        </el-button>
        <el-scrollbar height="calc(100vh - 120px)">
          <div
            v-for="region in displayRegions"
            :key="region.region"
            class="region-item"
            :class="{ active: selectedRegion === region.region }"
            @click="handleRegionClick(region.region); showRegionsDrawer = false"
          >
            <div class="region-flag">
              <el-icon :size="24"><Location /></el-icon>
            </div>
            <div class="region-info">
              <h4>{{ region.region }}</h4>
              <span class="count">{{ region.count }} 条路线</span>
            </div>
            <el-icon v-if="selectedRegion === region.region" class="check-icon" color="#3C5A78">
              <Check />
            </el-icon>
          </div>
        </el-scrollbar>
      </div>
    </el-drawer>

    <!-- 移动端：搜索抽屉 -->
    <el-drawer v-model="showSearchDrawer" direction="btt" size="auto" title="搜索路线">
      <div class="search-drawer-content">
        <div class="search-form">
          <el-autocomplete
            v-model="planForm.from"
            :fetch-suggestions="querySearchLocation"
            placeholder="请输入出发地"
            clearable
            size="large"
            class="search-input"
            :trigger-on-focus="true"
          >
            <template #prefix><el-icon><Location /></el-icon></template>
          </el-autocomplete>
          <el-icon class="search-arrow"><Right /></el-icon>
          <el-autocomplete
            v-model="planForm.to"
            :fetch-suggestions="querySearchLocation"
            placeholder="请输入目的地"
            clearable
            size="large"
            class="search-input"
            :trigger-on-focus="true"
          >
            <template #prefix><el-icon><Location /></el-icon></template>
          </el-autocomplete>
        </div>
        <el-button type="primary" size="large" @click="handlePlan(); showSearchDrawer = false" style="width: 100%; margin-top: 16px;">
          <el-icon style="margin-right: 8px;"><Search /></el-icon>
          搜索路线
        </el-button>
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
.home-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
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

/* 主要内容区域 */
.page-content {
  flex: 1;
}

/* 路线规划区域 */
.planner-section {
  padding: 30px 0;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);
}

.planner-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
}

.planner-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.planner-label {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.planner-inputs {
  display: flex;
  align-items: center;
  gap: 16px;
}

.planner-input {
  flex: 1;
}

.arrow-icon {
  font-size: 24px;
  color: var(--el-text-color-secondary);
  flex-shrink: 0;
}

.banner-item {
  width: 100%;
  height: 700px;
  background-size: cover;
  background-position: center;
  position: relative;
}

.banner-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.6));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.banner-title {
  margin: 0;
  font-size: 40px;
  font-weight: 700;
  color: white;
}

.banner-desc {
  margin: 0;
  font-size: 18px;
  color: rgba(255,255,255,0.9);
}

/* 地图区域 */
.map-section {
  padding: 40px 0 40px 0;
  background: var(--el-bg-color);
}

.map-wrapper {
  display: flex;
  height: 700px;
  width: 100%;
  margin: 0;
  border: 1px solid var(--el-border-color);
  border-left: none;
  border-radius: 0 8px 8px 0;
  overflow: hidden;
}

/* 中间地图 */
.routes-sidebar {
  width: 420px;
  min-width: 420px;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 24px 20px 16px;
  border-bottom: 1px solid var(--el-border-color);
}

.sidebar-header h2 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.routes-list {
  flex: 1;
  padding: 8px;
}

.route-section {
  margin-bottom: 8px;
}

.route-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 12px;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 8px;
}

.route-header:hover {
  background: var(--el-fill-color-light);
}

.route-header.active {
  background: var(--el-color-primary-light-9);
}

.route-number {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 18px;
  flex-shrink: 0;
}

.route-content {
  flex: 1;
  min-width: 0;
}

.route-name {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.route-progress {
  width: 100%;
  height: 4px;
  background: var(--el-fill-color);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 2px;
}

/* 查看详情按钮 */
.route-actions {
  padding: 8px 12px;
  text-align: center;
}

/* 景点缩略图 */
.attractions-thumbs {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 0 12px 12px 64px;
}

.thumb-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s;
}

.thumb-item:hover {
  background: var(--el-fill-color-light);
}

.thumb-image {
  width: 80px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
}

.thumb-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.thumb-order {
  font-size: 12px;
  font-weight: 700;
}

.thumb-name {
  font-size: 13px;
  color: var(--el-text-color-regular);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 中间地图 */
.map-container {
  flex: 1;
  position: relative;
}

/* 右侧区域筛选 */
.regions-sidebar {
  width: 280px;
  background: var(--el-bg-color);
  border-left: 1px solid var(--el-border-color);
  display: flex;
  flex-direction: column;
}

.regions-sidebar .sidebar-header {
  padding: 24px 20px 16px;
  border-bottom: 1px solid var(--el-border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.regions-sidebar .sidebar-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.regions-list {
  flex: 1;
  padding: 8px;
}

.region-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 6px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.region-item:hover {
  background: var(--el-fill-color-light);
}

.region-item.active {
  background: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary);
}

.region-flag {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  background: var(--el-fill-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.region-info h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
}

.count {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* 页脚 */
.footer {
  background: #2c3e50;
  color: white;
  padding: 60px 0 24px;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.footer-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 40px;
  margin-bottom: 40px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.footer-logo-image {
  width: 48px;
  height: 48px;
  object-fit: contain;
}

.footer-logo-text {
  font-size: 24px;
  font-weight: 700;
  color: white;
}

.footer-col h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
}

.footer-col p {
  margin: 0;
  line-height: 1.6;
  opacity: 0.8;
}

.contact-item,
.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  opacity: 0.8;
}

.footer-link {
  display: block;
  color: white;
  text-decoration: none;
  margin-bottom: 8px;
  opacity: 0.8;
  transition: opacity 0.3s;
}

.footer-link:hover {
  opacity: 1;
}

.footer-bottom {
  text-align: center;
  opacity: 0.6;
  font-size: 14px;
}

.footer-bottom p {
  margin: 4px 0;
}

/* 移动端抽屉按钮（默认隐藏） */
.mobile-drawer-btn {
  display: none;
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

/* 响应式设计 - 移动端适配 */
@media (max-width: 768px) {
  /* 隐藏桌面端侧边栏 */
  .desktop-only {
    display: none !important;
  }

  /* 显示移动端导航按钮 */
  .mobile-nav-btn {
    display: flex;
  }

  /* 移动端抽屉按钮 */
  .mobile-drawer-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    position: fixed;
    top: 50%;
    transform: translateY(-50%);
    z-index: 999;
    width: 48px;
    height: 120px;
    background: var(--el-color-primary);
    color: white;
    border: none;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
    writing-mode: vertical-rl;
    letter-spacing: 4px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: all 0.3s;
  }

  .mobile-drawer-btn:active {
    transform: translateY(-50%) scale(0.95);
  }

  .mobile-drawer-btn.left {
    left: 0;
    border-radius: 0 8px 8px 0;
  }

  .mobile-drawer-btn.right {
    right: 0;
    border-radius: 8px 0 0 8px;
  }

  .mobile-drawer-btn.bottom {
    top: auto;
    bottom: 80px;
    left: 50%;
    transform: translateX(-50%);
    width: 100px;
    height: 48px;
    border-radius: 24px;
    writing-mode: horizontal-tb;
    letter-spacing: 2px;
    display: flex;
    flex-direction: row;
    gap: 6px;
  }

  .mobile-drawer-btn.bottom:active {
    transform: translateX(-50%) scale(0.95);
  }

  /* 搜索抽屉样式 */
  .search-drawer-content {
    padding: 24px;
  }

  .search-form {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .search-input {
    width: 100%;
  }

  .search-arrow {
    align-self: center;
    font-size: 20px;
    color: var(--el-text-color-secondary);
  }

  /* 抽屉内容 */
  .drawer-content {
    padding: 0;
  }

  .drawer-subtitle {
    padding: 0 16px 16px;
    margin: 0;
    color: var(--el-text-color-secondary);
    font-size: 14px;
  }

  /* 导航栏 */
  .logo-text {
    font-size: 18px;
  }

  .nav-right {
    display: none;
  }

  /* 轮播图 */
  .banner-section {
    display: none;
  }

  /* 路线规划 */
  .planner-section {
    display: none;
  }

  /* 地图区域 */
  .map-section {
    position: fixed;
    top: 64px;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 0;
  }

  .map-wrapper {
    flex-direction: row;
    height: 100%;
  }

  .routes-sidebar,
  .regions-sidebar {
    display: none;
  }

  .map-container {
    width: 100%;
    height: 100%;
  }

  /* 页脚 */
  .footer {
    display: none;
  }

  .footer-row {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}
</style>
