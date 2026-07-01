<template>
  <section>
    <div class="page-header">
      <div>
        <h1 class="page-title">轮播图配置</h1>
        <p class="page-subtitle">支持真实图片上传、启停控制和拖拽排序，前台首页实时读取。</p>
      </div>
      <div class="toolbar">
        <el-input v-model="keyword" clearable placeholder="搜索标题" style="width: 220px" @keyup.enter="loadData" />
        <el-button plain @click="loadData">查询</el-button>
        <el-button type="primary" @click="openDialog()">新增轮播图</el-button>
      </div>
    </div>

    <div class="panel banner-panel">
      <div class="drag-tip">
        直接拖动左侧排序手柄即可调整轮播顺序，松开后自动保存。
      </div>
      <el-table ref="tableRef" :data="items" v-loading="loading" row-key="id" style="width: 100%">
        <el-table-column label="排序" width="92">
          <template #default="{ row }">
            <div class="sort-cell">
              <span class="drag-handle">::</span>
              <span>{{ row.order }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="图片" width="140">
          <template #default="{ row }">
            <el-image class="thumb" :src="row.image_url" fit="cover" />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="180" />
        <el-table-column prop="link_url" label="跳转链接" min-width="220" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'primary' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="visible" :title="form.id ? '编辑轮播图' : '新增轮播图'" width="620px">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <div class="form-grid">
          <el-form-item label="标题" prop="title">
            <el-input v-model="form.title" />
          </el-form-item>
          <el-form-item label="排序" prop="order">
            <el-input-number v-model="form.order" :min="0" style="width: 100%" />
          </el-form-item>
          <el-form-item label="图片地址" prop="image_url" class="form-grid-full">
            <el-input v-model="form.image_url" placeholder="可手动输入，或使用下方上传" />
          </el-form-item>
          <el-form-item label="图片预览" class="form-grid-full">
            <div class="banner-preview">
              <el-image v-if="form.image_url" :src="form.image_url" fit="cover" class="banner-preview-image" />
              <div v-else class="banner-preview-empty">暂无图片</div>
            </div>
          </el-form-item>
          <el-form-item label="上传图片" class="form-grid-full">
            <el-upload :http-request="handleUpload" :show-file-list="false" accept="image/*">
              <el-button plain>选择图片</el-button>
            </el-upload>
          </el-form-item>
          <el-form-item label="跳转链接" class="form-grid-full">
            <el-input v-model="form.link_url" />
          </el-form-item>
          <el-form-item label="是否启用">
            <el-switch v-model="form.is_active" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import Sortable from 'sortablejs'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createBanner, deleteBanner, getBanners, saveBannerOrder, updateBanner, uploadImage } from '../api/admin'

const loading = ref(false)
const saving = ref(false)
const visible = ref(false)
const formRef = ref()
const tableRef = ref()
const keyword = ref('')
const items = ref([])
const form = reactive(defaultForm())
let sortableInstance

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  image_url: [{ required: true, message: '请上传或输入图片地址', trigger: 'blur' }]
}

function defaultForm() {
  return { id: null, title: '', image_url: '', link_url: '', order: 0, is_active: true }
}

async function loadData() {
  loading.value = true
  try {
    const res = await getBanners({ keyword: keyword.value || undefined })
    items.value = res.data
    await nextTick()
    initSortable()
  } finally {
    loading.value = false
  }
}

function openDialog(row) {
  Object.assign(form, defaultForm(), row || {})
  visible.value = true
}

async function handleUpload(option) {
  const data = new FormData()
  data.append('file', option.file)
  const res = await uploadImage(data)
  form.image_url = res.data.url
  ElMessage.success('上传成功')
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (form.id) {
      await updateBanner(form.id, form)
    } else {
      await createBanner(form)
    }
    visible.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除「${row.title}」？`, '删除确认', { type: 'warning' })
  await deleteBanner(row.id)
  await loadData()
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
    onEnd: async ({ oldIndex, newIndex }) => {
      if (oldIndex === undefined || newIndex === undefined || oldIndex === newIndex) {
        return
      }
      const nextItems = [...items.value]
      const [moved] = nextItems.splice(oldIndex, 1)
      nextItems.splice(newIndex, 0, moved)
      nextItems.forEach((item, index) => {
        item.order = index
      })
      items.value = nextItems
      try {
        await saveBannerOrder({
          items: nextItems.map((item, index) => ({ id: item.id, order: index }))
        })
        ElMessage.success('排序已保存')
      } catch (error) {
        await loadData()
        throw error
      }
    }
  })
}

onMounted(loadData)

onBeforeUnmount(() => {
  sortableInstance?.destroy()
})
</script>

<style scoped>
.banner-panel {
  overflow: hidden;
}

.drag-tip {
  padding: 14px 18px 0;
  color: var(--admin-muted);
  font-size: 13px;
}

.sort-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.drag-handle {
  cursor: grab;
  color: var(--admin-accent);
  font-weight: 700;
  letter-spacing: 1px;
  user-select: none;
}

.thumb {
  width: 96px;
  height: 54px;
  border-radius: 8px;
  border: 1px solid var(--admin-border);
}

.banner-preview {
  width: 220px;
  height: 124px;
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  background: var(--admin-soft);
  overflow: hidden;
}

.banner-preview-image {
  width: 100%;
  height: 100%;
}

.banner-preview-empty {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: var(--admin-muted);
  font-size: 13px;
}
</style>
