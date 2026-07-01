<template>
  <section>
    <div class="page-header">
      <div>
        <h1 class="page-title">站点配置</h1>
        <p class="page-subtitle">维护前台与后台共用的站点名称、副标题和 Logo。</p>
      </div>
      <el-button type="primary" :loading="saving" @click="save">保存配置</el-button>
    </div>

    <div class="panel site-panel">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <div class="form-grid">
          <el-form-item label="站点名称" prop="site_name">
            <el-input v-model="form.site_name" maxlength="80" show-word-limit />
          </el-form-item>
          <el-form-item label="站点副标题">
            <el-input v-model="form.site_subtitle" maxlength="120" show-word-limit />
          </el-form-item>
          <el-form-item label="Logo 地址" prop="site_logo" class="form-grid-full">
            <el-input v-model="form.site_logo" placeholder="可手动输入，或使用下方上传" />
          </el-form-item>
          <el-form-item label="上传 Logo" class="form-grid-full">
            <div class="upload-row">
              <el-upload :http-request="handleUpload" :show-file-list="false" accept="image/*">
                <el-button plain>选择图片</el-button>
              </el-upload>
              <div class="logo-preview" v-if="form.site_logo">
                <img :src="form.site_logo" :alt="form.site_name || '站点 Logo'" />
              </div>
            </div>
          </el-form-item>
        </div>
      </el-form>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getSiteConfig, updateSiteConfig, uploadImage } from '../api/admin'

const formRef = ref()
const saving = ref(false)
const form = reactive({
  site_name: '',
  site_subtitle: '',
  site_logo: ''
})

const rules = {
  site_name: [{ required: true, message: '请输入站点名称', trigger: 'blur' }],
  site_logo: [{ required: true, message: '请上传或输入 Logo 地址', trigger: 'blur' }]
}

async function loadData() {
  const res = await getSiteConfig()
  Object.assign(form, res.data)
}

async function handleUpload(option) {
  const data = new FormData()
  data.append('file', option.file)
  const res = await uploadImage(data)
  form.site_logo = res.data.url
  ElMessage.success('上传成功')
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    await updateSiteConfig(form)
    ElMessage.success('保存成功')
  } finally {
    saving.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.site-panel {
  padding: 18px;
  max-width: 920px;
}

.upload-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.logo-preview {
  width: 120px;
  height: 120px;
  border: 1px solid var(--admin-border);
  border-radius: 12px;
  background: var(--admin-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.logo-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
