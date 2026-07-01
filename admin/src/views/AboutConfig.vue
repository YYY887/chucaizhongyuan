<template>
  <section>
    <div class="page-header">
      <div>
        <h1 class="page-title">关于我们配置</h1>
        <p class="page-subtitle">维护前台关于我们信息，内容保存到共用后端配置表。</p>
      </div>
      <el-button type="primary" :loading="saving" @click="save">保存配置</el-button>
    </div>

    <div class="panel about-panel">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="10" />
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="form.contact" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getAbout, updateAbout } from '../api/admin'

const formRef = ref()
const saving = ref(false)
const form = reactive({
  title: '',
  content: '',
  contact: ''
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

async function loadData() {
  const res = await getAbout()
  Object.assign(form, res.data)
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    await updateAbout(form)
    ElMessage.success('保存成功')
  } finally {
    saving.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.about-panel {
  padding: 18px;
  max-width: 920px;
}
</style>
