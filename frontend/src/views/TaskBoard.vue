<template>
  <div class="task-board-page">
    <div class="page-header">
      <h1 class="page-title">📋 任务看板</h1>
      <div class="header-actions">
        <el-select v-model="filterCategory" placeholder="按类别筛选" clearable style="width: 160px; margin-right: 12px;">
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
        <el-button type="primary" @click="showAddDialog = true" :icon="Plus">
          新建任务
        </el-button>
      </div>
    </div>

    <div class="board-columns">
      <div class="board-column">
        <div class="column-header pending">
          <span class="column-title">待认领</span>
          <span class="column-count">{{ pendingTasks.length }}</span>
        </div>
        <div class="task-list">
          <div v-for="task in pendingTasks" :key="task.id" class="task-card" @click="openTaskDetail(task)">
            <div class="task-category" :style="{ background: getCategoryColor(task.category) }">
              {{ getCategoryName(task.category) }}
            </div>
            <h4 class="task-title">{{ task.title }}</h4>
            <p class="task-desc">{{ task.description }}</p>
            <div class="task-footer">
              <span class="priority" :class="`priority-${task.priority}`">
                {{ getPriorityText(task.priority) }}
              </span>
              <span v-if="task.due_date" class="due-date">
                📅 {{ task.due_date }}
              </span>
            </div>
            <el-button size="small" type="success" class="claim-btn" @click.stop="claimTask(task)">
              认领任务
            </el-button>
          </div>
        </div>
      </div>

      <div class="board-column">
        <div class="column-header in-progress">
          <span class="column-title">进行中</span>
          <span class="column-count">{{ inProgressTasks.length }}</span>
        </div>
        <div class="task-list">
          <div v-for="task in inProgressTasks" :key="task.id" class="task-card" @click="openTaskDetail(task)">
            <div class="task-category" :style="{ background: getCategoryColor(task.category) }">
              {{ getCategoryName(task.category) }}
            </div>
            <h4 class="task-title">{{ task.title }}</h4>
            <p class="task-desc">{{ task.description }}</p>
            <div class="task-assignee">
              👤 {{ task.assigned_name || '未分配' }}
            </div>
            <el-progress :percentage="task.progress" :stroke-width="6" />
            <div class="task-footer">
              <span class="priority" :class="`priority-${task.priority}`">
                {{ getPriorityText(task.priority) }}
              </span>
              <span v-if="task.due_date" class="due-date">
                📅 {{ task.due_date }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="board-column">
        <div class="column-header completed">
          <span class="column-title">已完成</span>
          <span class="column-count">{{ completedTasks.length }}</span>
        </div>
        <div class="task-list">
          <div v-for="task in completedTasks" :key="task.id" class="task-card completed-card" @click="openTaskDetail(task)">
            <div class="task-category" :style="{ background: getCategoryColor(task.category) }">
              {{ getCategoryName(task.category) }}
            </div>
            <h4 class="task-title"><s>{{ task.title }}</s></h4>
            <div class="task-assignee">
              👤 {{ task.assigned_name || '未分配' }}
            </div>
            <el-progress :percentage="100" :stroke-width="6" status="success" />
            <div v-if="task.photo_proof" class="photo-proof">
              <el-image :src="task.photo_proof" fit="cover" style="width: 100%; height: 80px; border-radius: 4px;" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="showAddDialog" title="新建任务" width="500px">
      <el-form :model="newTask" label-width="80px">
        <el-form-item label="任务标题">
          <el-input v-model="newTask.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-form-item label="任务类别">
          <el-select v-model="newTask.category" placeholder="请选择类别" style="width: 100%;">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="newTask.priority">
            <el-radio value="high">高</el-radio>
            <el-radio value="medium">中</el-radio>
            <el-radio value="low">低</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="newTask.due_date" type="date" placeholder="选择日期" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input v-model="newTask.description" type="textarea" :rows="3" placeholder="请输入任务描述" />
        </el-form-item>
        <el-form-item label="分配给">
          <el-select v-model="newTask.assigned_to" placeholder="选择伴娘（可选）" clearable style="width: 100%;">
            <el-option v-for="bm in bridesmaids" :key="bm.id" :label="bm.name" :value="bm.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="createTask">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="任务详情" width="560px">
      <div v-if="selectedTask" class="task-detail">
        <div class="detail-header">
          <span class="task-category" :style="{ background: getCategoryColor(selectedTask.category) }">
            {{ getCategoryName(selectedTask.category) }}
          </span>
          <span class="status-tag" :class="`status-${selectedTask.status}`">
            {{ getStatusText(selectedTask.status) }}
          </span>
        </div>
        <h2 class="detail-title">{{ selectedTask.title }}</h2>
        <p class="detail-desc">{{ selectedTask.description }}</p>
        
        <div class="detail-info">
          <div class="info-item">
            <span class="info-label">负责人：</span>
            <span>{{ selectedTask.assigned_name || '未分配' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">优先级：</span>
            <span :class="`priority-${selectedTask.priority}`">
              {{ getPriorityText(selectedTask.priority) }}
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">截止日期：</span>
            <span>{{ selectedTask.due_date || '暂无' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">进度：</span>
          </div>
        </div>

        <div class="progress-section">
          <el-slider v-model="progressValue" :show-tooltip="true" @change="handleProgressChange" />
          <div style="text-align: right; margin-top: -10px;">
            <el-button size="small" type="primary" @click="updateTaskProgress">更新进度</el-button>
          </div>
        </div>

        <div v-if="selectedTask.notes" class="notes-section">
          <div class="section-title">备注</div>
          <p>{{ selectedTask.notes }}</p>
        </div>

        <div class="photo-section">
          <div class="section-title">照片凭证</div>
          <div v-if="selectedTask.photo_proof" class="photo-preview">
            <el-image :src="selectedTask.photo_proof" fit="cover" style="width: 200px; height: 150px; border-radius: 8px;" />
          </div>
          <el-upload
            action=""
            :show-file-list="false"
            :before-upload="beforePhotoUpload"
            accept="image/*"
          >
            <el-button size="small" type="success">📷 上传照片</el-button>
          </el-upload>
        </div>

        <div class="adjustment-section">
          <div class="section-title">快速调整分工</div>
          <el-select v-model="newAssignee" placeholder="重新分配给..." style="width: 200px; margin-right: 12px;">
            <el-option v-for="bm in bridesmaids" :key="bm.id" :label="bm.name" :value="bm.id" />
          </el-select>
          <el-input v-model="adjustReason" placeholder="调整原因" style="width: 200px; margin-right: 12px;" />
          <el-button type="warning" @click="adjustTask">调整</el-button>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="showClaimDialog" title="认领任务" width="400px">
      <div v-if="claimingTask" style="margin-bottom: 20px;">
        <p><strong>任务：</strong>{{ claimingTask.title }}</p>
        <p style="color: #909399; font-size: 13px; margin-top: 6px;">{{ claimingTask.description }}</p>
      </div>
      <el-form label-width="80px">
        <el-form-item label="选择伴娘">
          <el-select v-model="claimBridesmaidId" placeholder="请选择认领的伴娘" style="width: 100%;">
            <el-option v-for="bm in bridesmaids" :key="bm.id" :label="bm.name" :value="bm.id">
              <span>{{ bm.avatar || '👩' }} {{ bm.name }}</span>
              <span v-if="bm.role === 'leader'" style="color: #e6a23c; margin-left: 8px; font-size: 12px;">团长</span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showClaimDialog = false">取消</el-button>
        <el-button type="success" @click="confirmClaim">确认认领</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getTasks, getCategories, createTask as apiCreateTask, claimTask as apiClaimTask, updateProgress, assignTask, uploadPhoto } from '@/api/task'
import { getBridesmaids } from '@/api/bridesmaid'

const WEDDING_ID = 1

const tasks = ref([])
const categories = ref([])
const bridesmaids = ref([])
const filterCategory = ref('')

const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const showClaimDialog = ref(false)
const selectedTask = ref(null)
const claimingTask = ref(null)
const claimBridesmaidId = ref(null)
const progressValue = ref(0)
const newAssignee = ref(null)
const adjustReason = ref('')

const newTask = ref({
  title: '',
  description: '',
  category: '',
  priority: 'medium',
  due_date: null,
  assigned_to: null
})

const pendingTasks = computed(() => {
  return tasks.value.filter(t => t.status === 'pending' && (!filterCategory.value || t.category === filterCategory.value))
})

const inProgressTasks = computed(() => {
  return tasks.value.filter(t => t.status === 'in_progress' && (!filterCategory.value || t.category === filterCategory.value))
})

const completedTasks = computed(() => {
  return tasks.value.filter(t => t.status === 'completed' && (!filterCategory.value || t.category === filterCategory.value))
})

const getCategoryName = (catId) => {
  const cat = categories.value.find(c => c.id === catId)
  return cat ? cat.name : catId
}

const getCategoryColor = (catId) => {
  const cat = categories.value.find(c => c.id === catId)
  return cat ? cat.color : '#ccc'
}

const getPriorityText = (p) => {
  const map = { high: '高优先级', medium: '中优先级', low: '低优先级' }
  return map[p] || p
}

const getStatusText = (s) => {
  const map = { pending: '待认领', in_progress: '进行中', completed: '已完成' }
  return map[s] || s
}

const loadTasks = async () => {
  try {
    const res = await getTasks({ wedding_id: WEDDING_ID })
    tasks.value = res || []
  } catch (e) {
    console.error('加载任务失败', e)
    useMockData()
  }
}

const loadCategories = async () => {
  try {
    const res = await getCategories()
    categories.value = res || []
  } catch (e) {
    categories.value = [
      { id: 'door_game', name: '堵门游戏', icon: '🎮', color: '#ff6b6b' },
      { id: 'photo_props', name: '拍照道具', icon: '📸', color: '#4ecdc4' },
      { id: 'emergency_kit', name: '应急包', icon: '🩹', color: '#ffe66d' },
      { id: 'route_check', name: '接亲路线踩点', icon: '🗺️', color: '#95e1d3' },
      { id: 'decoration', name: '场地布置', icon: '💐', color: '#f38181' },
      { id: 'logistics', name: '物资采购', icon: '🛍️', color: '#aa96da' },
      { id: 'reception', name: '接待宾客', icon: '👥', color: '#fcbad3' },
      { id: 'other', name: '其他任务', icon: '📋', color: '#a8d8ea' }
    ]
  }
}

const loadBridesmaids = async () => {
  try {
    const res = await getBridesmaids({ wedding_id: WEDDING_ID })
    bridesmaids.value = res || []
  } catch (e) {
    bridesmaids.value = [
      { id: 1, name: '王小雨', role: 'leader' },
      { id: 2, name: '刘思琪', role: 'member' },
      { id: 3, name: '陈梦瑶', role: 'member' },
      { id: 4, name: '杨雪婷', role: 'member' },
      { id: 5, name: '赵嘉怡', role: 'member' }
    ]
  }
}

const useMockData = () => {
  tasks.value = [
    { id: 1, title: '设计堵门游戏方案', description: '准备3-5个有趣的堵门游戏', category: 'door_game', status: 'in_progress', priority: 'high', progress: 60, due_date: '2025-09-20', assigned_name: '王小雨' },
    { id: 2, title: '准备堵门红包', description: '准备不同面额的堵门红包', category: 'door_game', status: 'pending', priority: 'medium', progress: 0, due_date: '2025-09-28' },
    { id: 3, title: '采购拍照道具', description: '气球、手持拍照道具等', category: 'photo_props', status: 'completed', priority: 'medium', progress: 100, due_date: '2025-09-25', assigned_name: '刘思琪' },
    { id: 4, title: '准备应急医药包', description: '创可贴、止痛药等', category: 'emergency_kit', status: 'completed', priority: 'high', progress: 100, due_date: '2025-09-26', assigned_name: '杨雪婷' },
    { id: 5, title: '接亲路线踩点', description: '提前走一遍接亲路线', category: 'route_check', status: 'completed', priority: 'high', progress: 100, due_date: '2025-09-15', assigned_name: '王小雨' }
  ]
}

const createTask = async () => {
  if (!newTask.value.title || !newTask.value.category) {
    ElMessage.warning('请填写任务标题和类别')
    return
  }
  try {
    const data = {
      wedding_id: WEDDING_ID,
      title: newTask.value.title,
      description: newTask.value.description,
      category: newTask.value.category,
      priority: newTask.value.priority,
      due_date: newTask.value.due_date ? new Date(newTask.value.due_date).toISOString().split('T')[0] : null
    }
    const res = await apiCreateTask(data)
    if (newTask.value.assigned_to) {
      await assignTask(res.id, newTask.value.assigned_to)
    }
    ElMessage.success('任务创建成功')
    showAddDialog.value = false
    loadTasks()
    newTask.value = { title: '', description: '', category: '', priority: 'medium', due_date: null, assigned_to: null }
  } catch (e) {
    ElMessage.error('创建任务失败')
    console.error(e)
  }
}

const claimTask = (task) => {
  claimingTask.value = task
  claimBridesmaidId.value = null
  showClaimDialog.value = true
}

const confirmClaim = async () => {
  if (!claimBridesmaidId.value) {
    ElMessage.warning('请选择认领的伴娘')
    return
  }
  try {
    await apiClaimTask(claimingTask.value.id, claimBridesmaidId.value)
    ElMessage.success('认领成功')
    showClaimDialog.value = false
    loadTasks()
  } catch (e) {
    ElMessage.error('认领失败')
  }
}

const openTaskDetail = (task) => {
  selectedTask.value = { ...task }
  progressValue.value = task.progress
  newAssignee.value = task.assigned_to
  adjustReason.value = ''
  showDetailDialog.value = true
}

const handleProgressChange = () => {}

const updateTaskProgress = async () => {
  try {
    await updateProgress(selectedTask.value.id, progressValue.value)
    ElMessage.success('进度已更新')
    loadTasks()
    selectedTask.value.progress = progressValue.value
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

const beforePhotoUpload = async (file) => {
  try {
    const res = await uploadPhoto(selectedTask.value.id, file)
    if (res && res.photo_url) {
      selectedTask.value.photo_proof = res.photo_url
      ElMessage.success('照片上传成功')
      loadTasks()
    }
  } catch (e) {
    ElMessage.error('上传失败')
  }
  return false
}

const adjustTask = async () => {
  if (!newAssignee.value) {
    ElMessage.warning('请选择新的负责人')
    return
  }
  try {
    await assignTask(selectedTask.value.id, newAssignee.value, adjustReason.value || '突发情况调整')
    ElMessage.success('任务已重新分配')
    loadTasks()
    showDetailDialog.value = false
  } catch (e) {
    ElMessage.error('调整失败')
  }
}

onMounted(() => {
  loadCategories()
  loadBridesmaids()
  loadTasks()
})
</script>

<style scoped>
.task-board-page {
  min-height: 100%;
}

.header-actions {
  display: flex;
  align-items: center;
}

.board-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.board-column {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  display: flex;
  flex-direction: column;
  min-height: 500px;
}

.column-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.column-header.pending {
  background: #f4f4f5;
  color: #909399;
}

.column-header.in-progress {
  background: #ecf5ff;
  color: #409eff;
}

.column-header.completed {
  background: #f0f9eb;
  color: #67c23a;
}

.column-count {
  background: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.task-list {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
  position: relative;
}

.task-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #dcdfe6;
  transform: translateY(-2px);
}

.task-card.completed-card {
  opacity: 0.8;
}

.task-category {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: white;
  margin-bottom: 10px;
}

.task-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.task-desc {
  font-size: 12px;
  color: #909399;
  margin-bottom: 10px;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.task-assignee {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  font-size: 12px;
}

.priority {
  font-weight: 500;
}

.due-date {
  color: #909399;
}

.claim-btn {
  width: 100%;
  margin-top: 10px;
}

.photo-proof {
  margin-top: 10px;
}

.task-detail {
  padding: 10px 0;
}

.detail-header {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.detail-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
}

.detail-desc {
  color: #606266;
  margin-bottom: 20px;
  line-height: 1.6;
}

.detail-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.info-item {
  font-size: 14px;
}

.info-label {
  color: #909399;
}

.progress-section {
  margin-bottom: 20px;
}

.section-title {
  font-weight: 600;
  margin-bottom: 10px;
  color: #303133;
}

.notes-section,
.photo-section,
.adjustment-section {
  margin-bottom: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.photo-preview {
  margin-bottom: 10px;
}
</style>
