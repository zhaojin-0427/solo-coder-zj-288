<template>
  <div class="emergency-page">
    <div class="page-header">
      <h1 class="page-title">🆘 应急联系人</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showAddDialog = true" :icon="Plus">
          添加联系人
        </el-button>
      </div>
    </div>

    <div class="emergency-tip">
      <el-alert
        title="突发情况处理提示"
        type="warning"
        :closable="false"
        show-icon
      >
        <template #default>
          遇到突发情况时，请第一时间联系<span style="color: #f56c6c; font-weight: 600;">主要联系人</span>，
          并在任务看板中快速调整分工，确保婚礼顺利进行。
        </template>
      </el-alert>
    </div>

    <div v-if="primaryContact" class="primary-contact">
      <div class="primary-badge">⭐ 主要联系人</div>
      <div class="contact-card primary">
        <div class="contact-avatar">👩‍💼</div>
        <div class="contact-info">
          <h3 class="contact-name">{{ primaryContact.name }}</h3>
          <p class="contact-role">{{ primaryContact.role }}</p>
        </div>
        <div class="contact-actions">
          <el-button type="primary" size="large" @click="callPhone(primaryContact.phone)">
            📞 立即拨打
          </el-button>
        </div>
      </div>
    </div>

    <div class="contacts-list">
      <h3 class="list-title">📒 全部联系人</h3>
      <div class="contacts-grid">
        <div
          v-for="contact in otherContacts"
          :key="contact.id"
          class="contact-card"
        >
          <div class="contact-avatar">{{ getAvatar(contact.role) }}</div>
          <div class="contact-info">
            <h4 class="contact-name">{{ contact.name }}</h4>
            <p class="contact-role">{{ contact.role }}</p>
            <p class="contact-phone">📱 {{ contact.phone }}</p>
          </div>
          <div class="contact-actions">
            <el-button type="success" size="small" @click="callPhone(contact.phone)">
              拨打
            </el-button>
            <el-button type="primary" size="small" @click="editContact(contact)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="deleteContact(contact)">
              删除
            </el-button>
          </div>
          <div class="set-primary">
            <el-link type="primary" @click="setPrimary(contact)" v-if="!contact.is_primary">
              设为主要联系人
            </el-link>
          </div>
        </div>
      </div>
    </div>

    <div class="quick-actions">
      <h3 class="list-title">⚡ 快速求助</h3>
      <div class="quick-action-grid">
        <div class="quick-action-card" @click="emergencyAdjust">
          <div class="action-icon">🔄</div>
          <div class="action-title">快速调整分工</div>
          <div class="action-desc">突发情况时重新分配任务</div>
        </div>
        <div class="quick-action-card" @click="goToTimeline">
          <div class="action-icon">📅</div>
          <div class="action-title">查看流程表</div>
          <div class="action-desc">确认当前流程节点状态</div>
        </div>
        <div class="quick-action-card" @click="goToTasks">
          <div class="action-icon">📋</div>
          <div class="action-title">任务看板</div>
          <div class="action-desc">查看和调整任务进度</div>
        </div>
        <div class="quick-action-card" @click="showEmergencyList">
          <div class="action-icon">🩹</div>
          <div class="action-title">应急物品清单</div>
          <div class="action-desc">查看应急包内物品</div>
        </div>
      </div>
    </div>

    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑联系人' : '添加联系人'" width="450px">
      <el-form :model="contactForm" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="contactForm.name" placeholder="请输入联系人姓名" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="contactForm.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="身份/角色">
          <el-input v-model="contactForm.role" placeholder="如：新娘母亲、婚礼主持人等" />
        </el-form-item>
        <el-form-item label="主要联系人">
          <el-switch v-model="contactForm.is_primary" />
          <span style="margin-left: 10px; color: #909399; font-size: 13px;">
            设为主要紧急联系人
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveContact">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEmergencyItems" title="应急物品清单" width="500px">
      <div class="emergency-items">
        <el-checkbox-group v-model="checkedItems">
          <div class="item-row" v-for="item in emergencyItems" :key="item.id">
            <el-checkbox :value="item.id" :label="item.id">
              {{ item.name }}
            </el-checkbox>
            <span class="item-desc">{{ item.desc }}</span>
          </div>
        </el-checkbox-group>
      </div>
      <template #footer>
        <el-button @click="showEmergencyItems = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { getContacts, createContact, updateContact, deleteContact as apiDeleteContact } from '@/api/emergency'

const WEDDING_ID = 1
const router = useRouter()

const contacts = ref([])
const showAddDialog = ref(false)
const showEmergencyItems = ref(false)
const isEdit = ref(false)
const editingId = ref(null)

const contactForm = ref({
  name: '',
  phone: '',
  role: '',
  is_primary: false
})

const checkedItems = ref([])

const emergencyItems = ref([
  { id: 1, name: '创可贴', desc: '处理小伤口' },
  { id: 2, name: '止痛药', desc: '缓解头痛、牙痛' },
  { id: 3, name: '肠胃药', desc: '应对肠胃不适' },
  { id: 4, name: '晕车药', desc: '防晕车晕船' },
  { id: 5, name: '碘伏棉签', desc: '消毒伤口' },
  { id: 6, name: '补妆口红', desc: '新娘补妆用' },
  { id: 7, name: '粉饼', desc: '控油补妆' },
  { id: 8, name: '吸油纸', desc: '面部控油' },
  { id: 9, name: '发胶', desc: '固定发型' },
  { id: 10, name: '充电宝', desc: '手机充电' },
  { id: 11, name: '针线包', desc: '衣服开线应急' },
  { id: 12, name: '安全别针', desc: '固定衣物' },
  { id: 13, name: '纸巾/湿巾', desc: '清洁用' },
  { id: 14, name: '薄荷糖', desc: '清新口气' },
  { id: 15, name: '饮用水', desc: '补充水分' }
])

const primaryContact = computed(() => {
  return contacts.value.find(c => c.is_primary)
})

const otherContacts = computed(() => {
  return contacts.value.filter(c => !c.is_primary)
})

const getAvatar = (role) => {
  if (role && role.includes('妈妈')) return '👩'
  if (role && role.includes('爸爸')) return '👨'
  if (role && role.includes('主持')) return '🎤'
  if (role && role.includes('摄影')) return '📷'
  if (role && role.includes('伴娘')) return '👰'
  return '👤'
}

const loadContacts = async () => {
  try {
    const res = await getContacts({ wedding_id: WEDDING_ID })
    contacts.value = res || []
  } catch (e) {
    useMockData()
  }
}

const useMockData = () => {
  contacts.value = [
    { id: 1, name: '王小雨', phone: '13800138001', role: '伴娘团长', is_primary: true },
    { id: 2, name: '张妈妈', phone: '13900139001', role: '新娘母亲', is_primary: false },
    { id: 3, name: '李爸爸', phone: '13700137001', role: '新郎父亲', is_primary: false },
    { id: 4, name: '陈司仪', phone: '13600136001', role: '婚礼主持人', is_primary: false },
    { id: 5, name: '赵摄影', phone: '13500135001', role: '婚礼摄影师', is_primary: false },
    { id: 6, name: '酒店经理', phone: '13400134001', role: '酒店对接人', is_primary: false }
  ]
}

const callPhone = (phone) => {
  ElMessage.info(`正在拨打 ${phone}...`)
  window.location.href = `tel:${phone}`
}

const editContact = (contact) => {
  isEdit.value = true
  editingId.value = contact.id
  contactForm.value = {
    name: contact.name,
    phone: contact.phone,
    role: contact.role || '',
    is_primary: contact.is_primary
  }
  showAddDialog.value = true
}

const saveContact = async () => {
  if (!contactForm.value.name || !contactForm.value.phone) {
    ElMessage.warning('请填写姓名和电话')
    return
  }
  
  try {
    const data = {
      wedding_id: WEDDING_ID,
      ...contactForm.value
    }
    
    if (isEdit.value) {
      await updateContact(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createContact(data)
      ElMessage.success('添加成功')
    }
    
    showAddDialog.value = false
    loadContacts()
    resetForm()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const resetForm = () => {
  contactForm.value = {
    name: '',
    phone: '',
    role: '',
    is_primary: false
  }
  isEdit.value = false
  editingId.value = null
}

const deleteContact = async (contact) => {
  try {
    await ElMessageBox.confirm(`确定要删除联系人"${contact.name}"吗？`, '提示', {
      type: 'warning'
    })
    await apiDeleteContact(contact.id)
    contacts.value = contacts.value.filter(c => c.id !== contact.id)
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const setPrimary = async (contact) => {
  try {
    await updateContact(contact.id, { is_primary: true })
    ElMessage.success(`已将 ${contact.name} 设为主要联系人`)
    loadContacts()
  } catch (e) {
    ElMessage.error('设置失败')
  }
}

const emergencyAdjust = () => {
  router.push('/tasks')
}

const goToTimeline = () => {
  router.push('/timeline')
}

const goToTasks = () => {
  router.push('/tasks')
}

const showEmergencyList = () => {
  showEmergencyItems.value = true
}

onMounted(() => {
  loadContacts()
})
</script>

<style scoped>
.emergency-page {
  min-height: 100%;
}

.emergency-tip {
  margin-bottom: 24px;
}

.primary-contact {
  margin-bottom: 24px;
}

.primary-badge {
  display: inline-block;
  background: linear-gradient(90deg, #ff6b6b, #feca57);
  color: white;
  padding: 6px 16px;
  border-radius: 20px 20px 20px 0;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 10px;
}

.contact-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: all 0.3s;
}

.contact-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.contact-card.primary {
  background: linear-gradient(135deg, #fff5f5 0%, #fff0f0 100%);
  border: 2px solid #ffb3b3;
}

.contact-avatar {
  font-size: 40px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 50%;
  flex-shrink: 0;
}

.contact-info {
  flex: 1;
  min-width: 0;
}

.contact-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.contact-role {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.contact-phone {
  font-size: 14px;
  color: #606266;
}

.contact-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.set-primary {
  margin-top: 8px;
}

.list-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #303133;
}

.contacts-list {
  margin-bottom: 24px;
}

.contacts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.quick-actions {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.quick-action-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.quick-action-card {
  background: #fafafa;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.quick-action-card:hover {
  background: #ecf5ff;
  border-color: #409eff;
  transform: translateY(-4px);
}

.action-icon {
  font-size: 36px;
  margin-bottom: 10px;
}

.action-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.action-desc {
  font-size: 12px;
  color: #909399;
}

.emergency-items {
  max-height: 400px;
  overflow-y: auto;
}

.item-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.item-desc {
  margin-left: 10px;
  color: #909399;
  font-size: 13px;
}
</style>
