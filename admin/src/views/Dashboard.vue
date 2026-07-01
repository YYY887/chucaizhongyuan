<template>
  <section class="dashboard-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">访客统计</h1>
        <p class="page-subtitle">按访问路径统计前台访问行为，观察近期流量趋势与热门页面。</p>
      </div>
      <el-button plain @click="loadData">刷新</el-button>
    </div>

    <div class="metric-grid dashboard-metrics">
      <div class="metric metric-primary">
        <div class="metric-label">累计访问</div>
        <div class="metric-value">{{ stats.total }}</div>
        <div class="metric-footnote">全站累计访问量</div>
      </div>
      <div class="metric">
        <div class="metric-label">今日访问</div>
        <div class="metric-value">{{ stats.today }}</div>
        <div class="metric-footnote">今日新增访问</div>
      </div>
      <div class="metric">
        <div class="metric-label">统计路径</div>
        <div class="metric-value">{{ pathSummary.length }}</div>
        <div class="metric-footnote">已追踪页面路径数</div>
      </div>
      <div class="metric">
        <div class="metric-label">近 7 日访问</div>
        <div class="metric-value">{{ weekTotal }}</div>
        <div class="metric-footnote">最近一周累计</div>
      </div>
    </div>

    <div class="dashboard-grid">
      <div class="panel chart-panel">
        <div class="panel-head">
          <div>
            <h3>访问趋势</h3>
            <p>按日期汇总最近访问走势</p>
          </div>
        </div>
        <div ref="trendChartRef" class="chart-box"></div>
      </div>

      <div class="panel chart-panel">
        <div class="panel-head">
          <div>
            <h3>路径分布</h3>
            <p>访问量最高的页面路径</p>
          </div>
        </div>
        <div ref="pathChartRef" class="chart-box"></div>
      </div>
    </div>

    <div class="panel table-panel">
      <div class="panel-head">
        <div>
          <h3>访问明细</h3>
          <p>保留原始明细，便于继续排查</p>
        </div>
      </div>
      <el-table :data="tableItems" v-loading="loading" style="width: 100%">
        <el-table-column prop="visit_date" label="日期" width="150" />
        <el-table-column prop="path_label" label="访问页面" min-width="220" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="访问 IP" min-width="160" />
        <el-table-column prop="location" label="大致归属地" min-width="220" show-overflow-tooltip />
        <el-table-column prop="count" label="访问次数" width="140" />
      </el-table>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { getTheme } from '../stores/theme'
import { getRoutes, getVisitStats } from '../api/admin'

const loading = ref(false)
const trendChartRef = ref()
const pathChartRef = ref()
const stats = reactive({
  total: 0,
  today: 0,
  items: []
})
const routeNameMap = ref({})

let trendChart
let pathChart

const dailySummary = computed(() => {
  const map = new Map()
  stats.items.forEach((item) => {
    map.set(item.visit_date, (map.get(item.visit_date) || 0) + item.count)
  })
  return [...map.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([date, count]) => ({ date, count }))
})

const pathSummary = computed(() => {
  const map = new Map()
  stats.items.forEach((item) => {
    map.set(item.path, (map.get(item.path) || 0) + item.count)
  })
  return [...map.entries()]
    .map(([path, count]) => ({
      path,
      count,
      label: formatPathLabel(path)
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6)
})

const weekTotal = computed(() => dailySummary.value.slice(-7).reduce((sum, item) => sum + item.count, 0))
const tableItems = computed(() => stats.items.map((item) => ({
  ...item,
  path_label: formatPathLabel(item.path)
})))

function getChartColors() {
  if (getTheme() === 'dark') {
    return {
      axis: '#8f9bb3',
      split: '#1f2937',
      line: '#409eff',
      lineSoft: 'rgba(64, 158, 255, 0.16)',
      bar: '#79bbff',
      text: '#f3f4f6'
    }
  }
  return {
    axis: '#6b7280',
    split: '#e5e7eb',
    line: '#409eff',
    lineSoft: 'rgba(64, 158, 255, 0.14)',
    bar: '#66b1ff',
    text: '#111827'
  }
}

function formatPathLabel(path) {
  if (!path || path === '/') {
    return '首页'
  }
  if (path === '/recommend') {
    return '路线推荐'
  }
  if (path === '/about') {
    return '关于我们'
  }

  const routeMatch = path.match(/^\/route\/(\d+)$/)
  if (routeMatch) {
    const routeId = Number(routeMatch[1])
    return routeNameMap.value[routeId] || `路线 ${routeId}`
  }

  return path
}

function initCharts() {
  if (!trendChartRef.value || !pathChartRef.value) {
    return
  }
  trendChart = echarts.init(trendChartRef.value)
  pathChart = echarts.init(pathChartRef.value)
  renderCharts()
}

function renderCharts() {
  if (!trendChart || !pathChart) {
    return
  }

  const colors = getChartColors()
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 18, right: 18, top: 24, bottom: 24, containLabel: true },
    xAxis: {
      type: 'category',
      data: dailySummary.value.map((item) => item.date),
      axisLine: { lineStyle: { color: colors.split } },
      axisLabel: { color: colors.axis }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: colors.split } },
      axisLabel: { color: colors.axis }
    },
    series: [{
      data: dailySummary.value.map((item) => item.count),
      type: 'line',
      smooth: true,
      symbolSize: 8,
      lineStyle: { color: colors.line, width: 3 },
      itemStyle: { color: colors.line },
      areaStyle: { color: colors.lineSoft }
    }]
  })

  pathChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 18, right: 18, top: 24, bottom: 24, containLabel: true },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: colors.split } },
      axisLabel: { color: colors.axis }
    },
    yAxis: {
      type: 'category',
      data: pathSummary.value.map((item) => item.label),
      axisLine: { lineStyle: { color: colors.split } },
      axisLabel: { color: colors.axis }
    },
    series: [{
      data: pathSummary.value.map((item) => item.count),
      type: 'bar',
      barWidth: 16,
      itemStyle: {
        color: colors.bar,
        borderRadius: [0, 8, 8, 0]
      }
    }]
  })
}

async function loadData() {
  loading.value = true
  try {
    const [visitRes, routeRes] = await Promise.all([
      getVisitStats(),
      getRoutes()
    ])
    routeNameMap.value = Object.fromEntries((routeRes.data || []).map((item) => [item.id, item.name]))
    Object.assign(stats, visitRes.data)
    await nextTick()
    if (!trendChart || !pathChart) {
      initCharts()
    } else {
      renderCharts()
    }
  } finally {
    loading.value = false
  }
}

function handleResize() {
  trendChart?.resize()
  pathChart?.resize()
}

watch(() => getTheme(), () => {
  renderCharts()
})

onMounted(async () => {
  await loadData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pathChart?.dispose()
})
</script>

<style scoped>
.dashboard-page {
  display: grid;
  gap: 18px;
}

.dashboard-metrics {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-bottom: 0;
}

.metric-primary {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.16), rgba(64, 158, 255, 0.04));
}

.metric-footnote {
  margin-top: 12px;
  font-size: 12px;
  color: var(--admin-muted);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.95fr);
  gap: 18px;
}

.chart-panel,
.table-panel {
  padding: 18px;
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.panel-head h3 {
  margin: 0;
  font-size: 16px;
}

.panel-head p {
  margin: 6px 0 0;
  color: var(--admin-muted);
  font-size: 12px;
}

.chart-box {
  width: 100%;
  height: 320px;
}

@media (max-width: 1180px) {
  .dashboard-metrics,
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>
