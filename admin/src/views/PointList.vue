<template>
  <section>
    <div class="page-header">
      <div>
        <h1 class="page-title">节点信息</h1>
        <p class="page-subtitle">维护景点节点坐标与描述，支持手动录入和 Excel 批量导入。</p>
      </div>
      <div class="toolbar">
        <el-input v-model="keyword" clearable placeholder="搜索名称、地址、标签" style="width: 240px" @keyup.enter="loadData" />
        <el-button plain @click="loadData">查询</el-button>
        <el-upload :http-request="handleImport" :show-file-list="false" accept=".xlsx,.xlsm">
          <el-button plain>Excel 导入</el-button>
        </el-upload>
        <el-button type="primary" @click="openDialog()">新增节点</el-button>
      </div>
    </div>

    <div class="panel">
      <el-table :data="items" v-loading="loading" style="width: 100%">
        <el-table-column label="图片" width="110">
          <template #default="{ row }">
            <el-image v-if="row.image_url" class="point-thumb" :src="row.image_url" fit="cover" />
            <el-empty v-else :image-size="30" description="无图" />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="170" show-overflow-tooltip />
        <el-table-column prop="address" label="地址" min-width="220" show-overflow-tooltip />
        <el-table-column prop="longitude" label="经度" width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="single-line-cell">{{ row.longitude }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="latitude" label="纬度" width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="single-line-cell">{{ row.latitude }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="tags" label="标签" width="180" show-overflow-tooltip />
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          layout="total, prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page="page"
          @current-change="handlePage"
        />
      </div>
    </div>

    <el-dialog v-model="visible" :title="form.id ? '编辑节点' : '新增节点'" width="720px">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <div class="form-grid">
          <el-form-item label="名称" prop="name">
            <el-input v-model="form.name" />
          </el-form-item>
          <el-form-item label="标签">
            <el-input v-model="form.tags" placeholder="多个标签用英文逗号分隔" />
          </el-form-item>
          <el-form-item label="经度" prop="longitude">
            <el-input-number v-model="form.longitude" :min="-180" :max="180" :precision="6" style="width: 100%" />
          </el-form-item>
          <el-form-item label="纬度" prop="latitude">
            <el-input-number v-model="form.latitude" :min="-90" :max="90" :precision="6" style="width: 100%" />
          </el-form-item>
          <el-form-item label="地址" class="form-grid-full">
            <el-input v-model="form.address" />
          </el-form-item>
          <el-form-item label="地图选点" class="form-grid-full">
            <el-button plain @click="openMap">打开地图搜索选点</el-button>
          </el-form-item>
          <el-form-item label="图片地址" class="form-grid-full">
            <el-input v-model="form.image_url" placeholder="可手动输入，或使用下方上传" />
          </el-form-item>
          <el-form-item label="图片预览" class="form-grid-full">
            <div class="dialog-image-preview">
              <el-image v-if="form.image_url" :src="form.image_url" fit="cover" class="dialog-preview-image" />
              <div v-else class="dialog-preview-empty">暂无图片</div>
            </div>
          </el-form-item>
          <el-form-item label="上传图片" class="form-grid-full">
            <el-upload :http-request="handleUpload" :show-file-list="false" accept="image/*">
              <el-button plain>选择图片</el-button>
            </el-upload>
          </el-form-item>
          <el-form-item label="描述" class="form-grid-full">
            <el-input v-model="form.description" type="textarea" :rows="5" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="mapVisible" title="地图搜索选点" width="960px">
      <AdminAmapPicker v-model="form" mode="picker" />
      <template #footer>
        <el-button @click="mapVisible = false">关闭</el-button>
        <el-button type="primary" @click="mapVisible = false">确定</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminAmapPicker from '../components/AdminAmapPicker.vue'
import { createPoint, deletePoint, getPoints, importPoints, updatePoint, uploadImage } from '../api/admin'

const loading = ref(false)
const saving = ref(false)
const visible = ref(false)
const mapVisible = ref(false)
const formRef = ref()
const keyword = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const items = ref([])
const form = reactive(defaultForm())

const rules = {
  name: [{ required: true, message: '请输入节点名称', trigger: 'blur' }],
  longitude: [{ required: true, message: '请输入经度', trigger: 'blur' }],
  latitude: [{ required: true, message: '请输入纬度', trigger: 'blur' }]
}

function defaultForm() {
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

async function loadData() {
  loading.value = true
  try {
    const res = await getPoints({
      keyword: keyword.value || undefined,
      skip: (page.value - 1) * pageSize,
      limit: pageSize
    })
    items.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function handlePage(nextPage) {
  page.value = nextPage
  loadData()
}

function openDialog(row) {
  Object.assign(form, defaultForm(), row || {})
  visible.value = true
}

function openMap() {
  mapVisible.value = true
}

async function handleUpload(option) {
  const data = new FormData()
  data.append('file', option.file)
  const res = await uploadImage(data)
  form.image_url = res.data.url
  ElMessage.success('上传成功')
}

async function handleImport(option) {
  const data = new FormData()
  data.append('file', option.file)
  const res = await importPoints(data)
  const result = res.data
  ElMessage.success(`导入完成，新增 ${result.created} 条，跳过 ${result.skipped} 条`)
  page.value = 1
  await loadData()
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (form.id) {
      await updatePoint(form.id, form)
    } else {
      await createPoint(form)
    }
    visible.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除「${row.name}」？`, '删除确认', { type: 'warning' })
  await deletePoint(row.id)
  await loadData()
}

onMounted(loadData)
</script>

<style scoped>
.point-thumb {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  border: 1px solid var(--admin-border);
}

.single-line-cell {
  display: inline-block;
  max-width: 100%;
  white-space: nowrap;
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

.pager {
  display: flex;
  justify-content: flex-end;
  padding: 14px;
  border-top: 1px solid var(--admin-border);
}
</style>
