<template>
  <div class="checklist-page">
    <div class="page-header">
      <h1 class="page-title">✅ 准备清单</h1>
      <div class="header-actions">
        <el-select v-model="activeCategory" placeholder="选择分类" style="width: 180px;">
          <el-option label="全部分类" value="all" />
          <el-option v-for="cat in categories" :key="cat.id" :label="`${cat.icon} ${cat.name}`" :value="cat.id" />
        </el-select>
      </div>
    </div>

    <div class="overview-cards">
      <div class="stat-card total">
        <div class="stat-icon">📋</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总任务数</div>
        </div>
      </div>
      <div class="stat-card completed">
        <div class="stat-icon">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.completed }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>
      <div class="stat-card progress">
        <div class="stat-icon">⏳</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.inProgress }}</div>
          <div class="stat-label">进行中</div>
        </div>
      </div>
      <div class="stat-card rate">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ completionRate }}%</div>
          <div class="stat-label">完成率</div>
        </div>
      </div>
    </div>

    <div class="checklist-content">
      <div v-for="cat in filteredCategories" :key="cat.id" class="category-section">
        <div class="category-header" :style="{ background: cat.color + '20' }">
          <span class="category-icon">{{ cat.icon }}</span>
          <span class="category-name">{{ cat.name }}</span>
          <span class="category-count">
            {{ getCategoryCompleted(cat.id) }} / {{ getCategoryTotal(cat.id) }}
          </span>
        </div>
        <div class="task-items">
          <div
            v-for="task in getTasksByCategory(cat.id)"
            :key="task.id"
            class="task-item"
            :class="{ completed: task.status === 'completed' }"
          >
            <el-checkbox
              :model-value="task.status === 'completed'"
              @change="toggleTaskStatus(task)"
            />
            <div class="task-main" @click="showTaskDetail(task)">
              <span class="task-name" :class="{ 'task-completed': task.status === 'completed' }">
                {{ task.title }}
              </span>
              <span v-if="task.assigned_name" class="task-assignee">
                👤 {{ task.assigned_name }}
              </span>
            </div>
            <div class="task-progress">
              <el-progress :percentage="task.progress" :stroke-width="6" :show-text="false" style="width: 100px;" />
              <span class="progress-text">{{ task.progress }}%</span>
            </div>
            <div class="task-actions">
              <el-button size="small" type="primary" link @click="showUpdateProgress(task)">
                更新进度
              </el-button>
              <el-button size="small" type="danger" link @click="deleteTask(task)">
                删除
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="showProgressDialog" title="更新任务进度" width="400px">
      <div v-if="selectedTask">
        <p style="margin-bottom: 16px; color: #606266;">任务：{{ selectedTask.title }}</p>
        <el-slider v-model="progressValue" :show-tooltip="true" />
        <div style="text-align: center; margin-top: 20px;">
          <span style="font-size: 24px; font-weight: 600; color: #409eff;">{{ progressValue }}%</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="showProgressDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProgress">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTasks, getCategories, updateTask, updateProgress, deleteTask as apiDeleteTask } from '@/api/task'

const WEDDING_ID = 1

const tasks = ref([])
const categories = ref([])
const activeCategory = ref('all')

const showProgressDialog = ref(false)
const selectedTask = ref(null)
const progressValue = ref(0)

const filteredCategories = computed(() => {
  if (activeCategory.value === 'all') {
    return categories.value
  }
  return categories.value.filter(c => c.id === activeCategory.value)
})

const stats = computed(() => {
  const total = tasks.value.length
  const completed = tasks.value.filter(t => t.status === 'completed').length
  const inProgress = tasks.value.filter(t => t.status === 'in_progress').length
  return { total, completed, inProgress }
})

const completionRate = computed(() => {
  if (stats.value.total === 0) return 0
  return Math.round((stats.value.completed / stats.value.total) * 100)
})

const getTasksByCategory = (catId) => {
  return tasks.value.filter(t => t.category === catId)
}

const getCategoryTotal = (catId) => {
  return tasks.value.filter(t => t.category === catId).length
}

const getCategoryCompleted = (catId) => {
  return tasks.value.filter(t => t.category === catId && t.status === 'completed').length
}

const loadTasks = async () => {
  try {
    const res = await getTasks({ wedding_id: WEDDING_ID })
    tasks.value = res || []
  } catch (e) {
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
      { id: 'logistics', name: '物资采购', icon: '🛍️', color: '#aa96da' }
    ]
  }
}

const useMockData = () => {
  tasks.value = [
    { id: 1, title: '设计堵门游戏方案', category: 'door_game', status: 'in_progress', progress: 60, assigned_name: '王小雨' },
    { id: 2, title: '准备堵门红包', category: 'door_game', status: 'pending', progress: 0 },
    { id: 3, title: '采购拍照道具', category: 'photo_props', status: 'completed', progress: 100, assigned_name: '刘思琪' },
    { id: 4, title: '整理拍照pose清单', category: 'photo_props', status: 'in_progress', progress: 40, assigned_name: '陈梦瑶' },
    { id: 5, title: '准备应急医药包', category: 'emergency_kit', status: 'completed', progress: 100, assigned_name: '杨雪婷' },
    { id: 6, title: '准备补妆用品', category: 'emergency_kit', status: 'in_progress', progress: 70, assigned_name: '赵嘉怡' },
    { id: 7, title: '接亲路线踩点', category: 'route_check', status: 'completed', progress: 100, assigned_name: '王小雨' },
    { id: 8, title: '确认酒店停车位', category: 'route_check', status: 'pending', progress: 0 },
    { id: 9, title: '新房气球布置', category: 'decoration', status: 'pending', progress: 0 },
    { id: 10, title: '婚房喜字贴放', category: 'decoration', status: 'pending', progress: 0 },
    { id: 11, title: '采购喜糖', category: 'logistics', status: 'completed', progress: 100, assigned_name: '刘思琪' },
    { id: 12, title: '整理伴手礼', category: 'logistics', status: 'in_progress', progress: 50, assigned_name: '陈梦瑶' }
  ]
}

const toggleTaskStatus = async (task) => {
  const newStatus = task.status === 'completed' ? 'in_progress' : 'completed'
  const newProgress = newStatus === 'completed' ? 100 : (task.progress > 0 ? task.progress : 10)
  try {
    await updateTask(task.id, { status: newStatus, progress: newProgress })
    task.status = newStatus
    task.progress = newProgress
    ElMessage.success(newStatus === 'completed' ? '已标记完成' : '已取消完成')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const showUpdateProgress = (task) => {
  selectedTask.value = task
  progressValue.value = task.progress
  showProgressDialog.value = true
}

const saveProgress = async () => {
  if (!selectedTask.value) return
  try {
    await updateProgress(selectedTask.value.id, progressValue.value)
    selectedTask.value.progress = progressValue.value
    if (progressValue.value >= 100) {
      selectedTask.value.status = 'completed'
    } else if (progressValue.value > 0) {
      selectedTask.value.status = 'in_progress'
    }
    ElMessage.success('进度已更新')
    showProgressDialog.value = false
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

const showTaskDetail = (task) => {
  showUpdateProgress(task)
}

const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(`确定要删除任务"${task.title}"吗？`, '提示', {
      type: 'warning'
    })
    await apiDeleteTask(task.id)
    tasks.value = tasks.value.filter(t => t.id !== task.id)
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadCategories()
  loadTasks()
})
</script>

<style scoped>
.checklist-page {
  min-height: 100%;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.stat-icon {
  font-size: 36px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 12px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.stat-card.total .stat-icon { background: #ecf5ff; }
.stat-card.total .stat-value { color: #409eff; }
.stat-card.completed .stat-icon { background: #f0f9eb; }
.stat-card.completed .stat-value { color: #67c23a; }
.stat-card.progress .stat-icon { background: #fdf6ec; }
.stat-card.progress .stat-value { color: #e6a23c; }
.stat-card.rate .stat-icon { background: #fef0f0; }
.stat-card.rate .stat-value { color: #f56c6c; }

.checklist-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.category-section {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.category-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}

.category-icon {
  font-size: 20px;
}

.category-name {
  flex: 1;
  font-size: 15px;
}

.category-count {
  font-size: 13px;
  color: #606266;
  background: white;
  padding: 4px 12px;
  border-radius: 12px;
}

.task-items {
  padding: 8px 0;
}

.task-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  gap: 12px;
  transition: background 0.3s;
}

.task-item:hover {
  background: #f5f7fa;
}

.task-item.completed {
  opacity: 0.7;
}

.task-main {
  flex: 1;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-name {
  font-size: 14px;
  color: #303133;
}

.task-completed {
  text-decoration: line-through;
  color: #909399;
}

.task-assignee {
  font-size: 12px;
  color: #909399;
}

.task-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 160px;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  min-width: 35px;
}

.task-actions {
  display: flex;
  gap: 4px;
}
</style>
