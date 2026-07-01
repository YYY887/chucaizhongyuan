<template>
  <section>
    <div class="page-header">
      <div>
        <h1 class="page-title">路线管理</h1>
        <p class="page-subtitle">使用 Element Plus 原生布局查看路线、维护路线信息，并直接编辑节点与拖拽排序。</p>
      </div>
      <div class="toolbar">
        <el-input v-model="keyword" clearable placeholder="搜索路线、区域、类型" style="width: 240px" @keyup.enter="loadRoutes" />
        <el-button plain @click="loadRoutes">查询</el-button>
      </div>
    </div>

    <el-card shadow="never" class="route-card detail-card" v-loading="loadingRoutes || loadingPoints">
      <div class="route-select-bar">
        <div class="route-select-main">
          <span class="route-select-label">选择路线</span>
          <el-select
            :model-value="selectedRoute?.id ?? null"
            placeholder="请选择路线"
            filterable
            class="route-select"
            @change="handleRouteChange"
          >
            <el-option
              v-for="route in routes"
              :key="route.id"
              :label="route.name"
              :value="route.id"
            />
          </el-select>
        </div>
        <el-tag type="info">{{ routes.length }} 条</el-tag>
      </div>
      <div v-if="selectedRoute" class="route-select-meta">
        {{ selectedRoute.region }} / {{ selectedRoute.route_type || '未分类' }}
      </div>

      <template v-if="!routes.length && !loadingRoutes">
        <el-empty description="暂无路线" />
      </template>

      <template v-else>
        <div v-if="selectedRoute" class="card-head detail-head detail-panel-head">
          <div>
            <div class="detail-title">{{ selectedRoute.name }}</div>
            <div class="detail-subtitle">{{ selectedRoute.region }} / {{ selectedRoute.route_type || '未分类' }}</div>
          </div>
          <div class="toolbar">
            <el-button plain @click="openRoutePreview">预览地图</el-button>
            <el-button plain @click="openRouteDialog">编辑路线</el-button>
            <el-button type="primary" :loading="savingOrder" @click="saveOrder">保存顺序</el-button>
          </div>
        </div>
        <div v-else class="card-head detail-panel-head">
          <span>路线详情</span>
        </div>

        <template v-if="selectedRoute">
          <div class="cover-panel">
            <div class="cover-preview">
              <el-image v-if="selectedRoute.cover_image" class="route-cover" :src="selectedRoute.cover_image" fit="cover" />
              <div v-else class="route-cover route-cover-empty">暂无封面</div>
            </div>
            <div class="cover-content">
              <div class="cover-title">路线封面</div>
              <div class="cover-text">可在“编辑路线”中上传封面图，前台路线卡片会同步更新。</div>
            </div>
          </div>

          <div class="point-table-wrap">
            <div class="table-tip">拖动右侧手柄可以直接调整节点顺序，节点信息可在本页直接编辑。</div>
            <el-table ref="tableRef" :data="routePoints" row-key="id" style="width: 100%">
              <el-table-column label="排序" width="90">
                <template #default="{ row }">
                  <div class="sort-cell">
                    <span>{{ row.order }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="图片" width="110">
                <template #default="{ row }">
                  <el-image v-if="row.image_url" class="point-thumb" :src="row.image_url" fit="cover" />
                  <el-empty v-else :image-size="32" description="无图" />
                </template>
              </el-table-column>
              <el-table-column prop="name" label="节点名称" min-width="180" show-overflow-tooltip>
                <template #default="{ row }">
                  <span class="table-single-line">{{ row.name }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="address" label="地址" min-width="260" show-overflow-tooltip>
                <template #default="{ row }">
                  <span class="table-single-line">{{ row.address }}</span>
                </template>
              </el-table-column>
              <el-table-column label="纬度" width="150" show-overflow-tooltip>
                <template #default="{ row }">
                  <span class="table-single-line">{{ formatCoordinate(row.latitude) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="经度" width="150" show-overflow-tooltip>
                <template #default="{ row }">
                  <span class="table-single-line">{{ formatCoordinate(row.longitude) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="170" fixed="right">
                <template #default="{ row }">
                  <div class="row-actions">
                    <el-button link type="primary" @click="openPointDialog(row)">编辑节点</el-button>
                    <span class="drag-handle" title="拖拽排序">::</span>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <el-empty v-if="!routePoints.length" description="该路线暂无节点" />
        </template>
        <el-empty v-else description="请选择路线" />
      </template>
    </el-card>

    <el-dialog v-model="routeDialogVisible" title="编辑路线" width="720px">
      <el-form ref="routeFormRef" :model="routeForm" :rules="routeRules" label-position="top">
        <div class="form-grid">
          <el-form-item label="路线名称" prop="name">
            <el-input v-model="routeForm.name" />
          </el-form-item>
          <el-form-item label="区域" prop="region">
            <el-input v-model="routeForm.region" />
          </el-form-item>
          <el-form-item label="路线类型">
            <el-input v-model="routeForm.route_type" />
          </el-form-item>
          <el-form-item label="游玩时长">
            <el-input v-model="routeForm.duration" />
          </el-form-item>
          <el-form-item label="难度">
            <el-input v-model="routeForm.difficulty" />
          </el-form-item>
          <el-form-item label="封面图地址" class="form-grid-full">
            <el-input v-model="routeForm.cover_image" placeholder="可手动输入，或使用下方上传" />
          </el-form-item>
          <el-form-item label="上传封面" class="form-grid-full">
            <el-upload :http-request="handleCoverUpload" :show-file-list="false" accept="image/*">
              <el-button plain>选择图片</el-button>
            </el-upload>
          </el-form-item>
          <el-form-item label="路线描述" class="form-grid-full">
            <el-input v-model="routeForm.description" type="textarea" :rows="5" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="routeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingRoute" @click="saveRoute">保存路线</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="pointDialogVisible" title="编辑节点" width="760px">
      <el-form ref="pointFormRef" :model="pointForm" :rules="pointRules" label-position="top">
        <div class="form-grid">
          <el-form-item label="名称" prop="name">
            <el-input v-model="pointForm.name" />
          </el-form-item>
          <el-form-item label="标签">
            <el-input v-model="pointForm.tags" placeholder="多个标签用英文逗号分隔" />
          </el-form-item>
          <el-form-item label="经度" prop="longitude">
            <el-input-number v-model="pointForm.longitude" :min="-180" :max="180" :precision="6" style="width: 100%" />
          </el-form-item>
          <el-form-item label="纬度" prop="latitude">
            <el-input-number v-model="pointForm.latitude" :min="-90" :max="90" :precision="6" style="width: 100%" />
          </el-form-item>
          <el-form-item label="地址" class="form-grid-full">
            <el-input v-model="pointForm.address" />
          </el-form-item>
          <el-form-item label="地图选点" class="form-grid-full">
            <el-button plain @click="openPointMap">打开地图搜索选点</el-button>
          </el-form-item>
          <el-form-item label="图片地址" class="form-grid-full">
            <el-input v-model="pointForm.image_url" placeholder="可手动输入，或使用下方上传" />
          </el-form-item>
          <el-form-item label="图片预览" class="form-grid-full">
            <div class="dialog-image-preview">
              <el-image v-if="pointForm.image_url" :src="pointForm.image_url" fit="cover" class="dialog-preview-image" />
              <div v-else class="dialog-preview-empty">暂无图片</div>
            </div>
          </el-form-item>
          <el-form-item label="上传图片" class="form-grid-full">
            <el-upload :http-request="handlePointUpload" :show-file-list="false" accept="image/*">
              <el-button plain>选择图片</el-button>
            </el-upload>
          </el-form-item>
          <el-form-item label="描述" class="form-grid-full">
            <el-input v-model="pointForm.description" type="textarea" :rows="5" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="pointDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingPoint" @click="savePoint">保存节点</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="pointMapVisible" title="地图搜索选点" width="960px">
      <AdminAmapPicker v-model="pointForm" mode="picker" />
      <template #footer>
        <el-button @click="pointMapVisible = false">关闭</el-button>
        <el-button type="primary" @click="pointMapVisible = false">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="routePreviewVisible" title="路线地图预览" width="1100px">
      <AdminAmapPicker mode="preview" :route-points="routePoints" />
      <template #footer>
        <el-button type="primary" @click="routePreviewVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import Sortable from 'sortablejs'
import { ElMessage } from 'element-plus'
import AdminAmapPicker from '../components/AdminAmapPicker.vue'
import { getPointDetail, getRoutePoints, getRoutes, saveRoutePointOrder, updatePoint, updateRoute, uploadImage } from '../api/admin'

const keyword = ref('')
const routes = ref([])
const selectedRoute = ref(null)
const routePoints = ref([])
const loadingRoutes = ref(false)
const loadingPoints = ref(false)
const savingOrder = ref(false)
const savingRoute = ref(false)
const savingPoint = ref(false)
const routeDialogVisible = ref(false)
const pointDialogVisible = ref(false)
const pointMapVisible = ref(false)
const routePreviewVisible = ref(false)
const routeFormRef = ref()
const pointFormRef = ref()
const tableRef = ref()
let sortableInstance

const routeForm = reactive(defaultRouteForm())
const pointForm = reactive(defaultPointForm())

const routeRules = {
  name: [{ required: true, message: '请输入路线名称', trigger: 'blur' }],
  region: [{ required: true, message: '请输入区域', trigger: 'blur' }]
}

const pointRules = {
  name: [{ required: true, message: '请输入节点名称', trigger: 'blur' }],
  longitude: [{ required: true, message: '请输入经度', trigger: 'blur' }],
  latitude: [{ required: true, message: '请输入纬度', trigger: 'blur' }]
}

function defaultRouteForm() {
  return {
    id: null,
    name: '',
    description: '',
    region: '',
    route_type: '',
    cover_image: '',
    duration: '',
    difficulty: ''
  }
}

function defaultPointForm() {
  return {
    id: null,
    name: '',
    description: '',
    address: '',
    longitude: 113.625,
    latitude: 34.7466,
    image_url: '',
    tags: ''
  }
}

async function loadRoutes() {
  loadingRoutes.value = true
  try {
    const res = await getRoutes({ keyword: keyword.value || undefined })
    routes.value = res.data
    if (routes.value.length === 0) {
      selectedRoute.value = null
      routePoints.value = []
      return
    }
    const current = selectedRoute.value
      ? routes.value.find((item) => item.id === selectedRoute.value.id)
      : routes.value[0]
    await selectRoute(current || routes.value[0])
  } finally {
    loadingRoutes.value = false
  }
}

async function selectRoute(route) {
  selectedRoute.value = route
  loadingPoints.value = true
  try {
    const res = await getRoutePoints(route.id)
    routePoints.value = res.data
    await nextTick()
    initSortable()
  } finally {
    loadingPoints.value = false
  }
}

function handleRouteChange(routeId) {
  const route = routes.value.find((item) => item.id === routeId)
  if (route) {
    selectRoute(route)
  }
}

function normalizePointOrder(items) {
  items.forEach((item, index) => {
    item.order = index + 1
  })
}

function movePointOrder(oldIndex, newIndex) {
  if (oldIndex === undefined || newIndex === undefined || oldIndex === newIndex) {
    return
  }
  const nextItems = [...routePoints.value]
  const [moved] = nextItems.splice(oldIndex, 1)
  nextItems.splice(newIndex, 0, moved)
  normalizePointOrder(nextItems)
  routePoints.value = nextItems
}

function formatCoordinate(value) {
  if (value === null || value === undefined || value === '') {
    return '--'
  }
  return Number(value).toFixed(6)
}

function initSortable() {
  const tbody = tableRef.value?.$el?.querySelector('.el-table__body-wrapper tbody')
  if (!tbody) {
    return
  }
  sortableInstance?.destroy()
  sortableInstance = Sortable.create(tbody, {
    animation: 180,
    handle: '.drag-handle',
    ghostClass: 'route-sort-ghost',
    chosenClass: 'route-sort-chosen',
    dragClass: 'route-sort-drag',
    onChange: ({ oldIndex, newIndex }) => {
      movePointOrder(oldIndex, newIndex)
    },
    onEnd: ({ oldIndex, newIndex }) => {
      movePointOrder(oldIndex, newIndex)
    }
  })
}

async function saveOrder() {
  if (!selectedRoute.value) {
    return
  }
  savingOrder.value = true
  try {
    await saveRoutePointOrder(selectedRoute.value.id, {
      items: routePoints.value.map((item, index) => ({
        attraction_id: item.id,
        order: index + 1
      }))
    })
    ElMessage.success('顺序已保存')
    await selectRoute(selectedRoute.value)
  } finally {
    savingOrder.value = false
  }
}

function openRouteDialog() {
  Object.assign(routeForm, defaultRouteForm(), selectedRoute.value || {})
  routeDialogVisible.value = true
}

async function openPointDialog(row) {
  if (!row?.id) {
    Object.assign(pointForm, defaultPointForm())
    pointDialogVisible.value = true
    return
  }

  try {
    const res = await getPointDetail(row.id)
    Object.assign(pointForm, defaultPointForm(), res.data || {})
  } catch (error) {
    Object.assign(pointForm, defaultPointForm(), row || {})
    ElMessage.warning('节点详情读取失败，已使用列表数据回填')
  }
  pointDialogVisible.value = true
}

function openPointMap() {
  pointMapVisible.value = true
}

function openRoutePreview() {
  routePreviewVisible.value = true
}

async function handleCoverUpload(option) {
  const data = new FormData()
  data.append('file', option.file)
  const res = await uploadImage(data)
  routeForm.cover_image = res.data.url
  ElMessage.success('上传成功')
}

async function handlePointUpload(option) {
  const data = new FormData()
  data.append('file', option.file)
  const res = await uploadImage(data)
  pointForm.image_url = res.data.url
  ElMessage.success('上传成功')
}

async function saveRoute() {
  await routeFormRef.value.validate()
  savingRoute.value = true
  try {
    const res = await updateRoute(routeForm.id, routeForm)
    selectedRoute.value = res.data
    const index = routes.value.findIndex((item) => item.id === routeForm.id)
    if (index > -1) {
      routes.value[index] = res.data
    }
    routeDialogVisible.value = false
    ElMessage.success('路线已保存')
  } finally {
    savingRoute.value = false
  }
}

async function savePoint() {
  await pointFormRef.value.validate()
  savingPoint.value = true
  try {
    const res = await updatePoint(pointForm.id, pointForm)
    const index = routePoints.value.findIndex((item) => item.id === pointForm.id)
    if (index > -1) {
      routePoints.value[index] = {
        ...routePoints.value[index],
        ...res.data,
        order: routePoints.value[index].order
      }
    }
    pointDialogVisible.value = false
    ElMessage.success('节点已保存')
  } finally {
    savingPoint.value = false
  }
}

onMounted(loadRoutes)

onBeforeUnmount(() => {
  sortableInstance?.destroy()
})
</script>

<style scoped>
.route-card {
  border-radius: 12px;
}

.route-select-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.route-select-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.route-select-label {
  flex-shrink: 0;
  color: var(--admin-muted);
  font-size: 13px;
}

.route-select {
  max-width: 520px;
  width: 100%;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.detail-head {
  align-items: flex-start;
}

.detail-panel-head {
  margin-bottom: 16px;
}

.detail-title {
  font-size: 20px;
  font-weight: 650;
}

.detail-subtitle {
  margin-top: 6px;
  color: var(--admin-muted);
  font-size: 13px;
}

.route-select-meta {
  margin: -4px 0 16px 84px;
  color: var(--admin-muted);
  font-size: 12px;
  line-height: 1.4;
}

.cover-panel {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding: 16px 18px;
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  background: var(--admin-panel);
}

.cover-preview {
  flex-shrink: 0;
}

.route-cover {
  width: 140px;
  height: 84px;
  border-radius: 10px;
  border: 1px solid var(--admin-border);
}

.route-cover-empty {
  display: grid;
  place-items: center;
  color: var(--admin-muted);
  background: var(--admin-soft);
  font-size: 13px;
}

.cover-content {
  min-width: 0;
}

.cover-title {
  font-size: 15px;
  font-weight: 650;
}

.cover-text {
  margin-top: 6px;
  color: var(--admin-muted);
  font-size: 13px;
  line-height: 1.6;
}

.point-table-wrap {
  margin-top: 16px;
}

.table-tip {
  margin-bottom: 12px;
  color: var(--admin-muted);
  font-size: 13px;
}

:deep(.el-dialog .map-box) {
  height: 460px;
}

.sort-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.table-single-line {
  display: inline-block;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.drag-handle {
  cursor: grab;
  color: var(--admin-accent);
  font-weight: 700;
  letter-spacing: 1px;
  user-select: none;
  padding: 0 6px;
}

.row-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.point-thumb {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  border: 1px solid var(--admin-border);
}

.dialog-image-preview {
  width: 160px;
  height: 110px;
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  background: var(--admin-soft);
  overflow: hidden;
}

.dialog-preview-image {
  width: 100%;
  height: 100%;
}

.dialog-preview-empty {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: var(--admin-muted);
  font-size: 13px;
}

@media (max-width: 900px) {
  .route-select-bar,
  .route-select-main {
    align-items: stretch;
    flex-direction: column;
  }

  .route-select {
    max-width: none;
  }

  .route-select-meta {
    margin-left: 0;
  }

  .cover-panel {
    align-items: flex-start;
    flex-direction: column;
  }
}

:global(.route-sort-ghost > td) {
  background: var(--el-color-primary-light-9) !important;
}

:global(.route-sort-chosen > td) {
  background: var(--el-fill-color-light) !important;
}

:global(.route-sort-drag) {
  opacity: 0.92;
}
</style>
