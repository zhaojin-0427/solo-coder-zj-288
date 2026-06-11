<template>
  <div class="production-schedule">
    <div class="page-header">
      <h2 class="page-title">📅 生产排期</h2>
      <div class="header-filters">
        <el-select v-model="filterRisk" placeholder="按风险筛选" clearable style="width: 160px; margin-right: 12px;">
          <el-option label="高风险" value="high" />
          <el-option label="中风险" value="medium" />
          <el-option label="低风险" value="low" />
        </el-select>
        <el-select v-model="filterCategory" placeholder="按类别筛选" clearable style="width: 160px; margin-right: 12px;">
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
        <el-date-picker v-model="filterDate" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width: 280px;" />
      </div>
    </div>

    <div v-if="riskAssessment" class="risk-summary-bar">
      <div class="risk-summary-item">
        <span class="risk-label">整体风险等级：</span>
        <el-tag :type="getRiskLevelType(riskAssessment.risk_level)" size="large" effect="dark">
          {{ getRiskLevelText(riskAssessment.risk_level) }}
        </el-tag>
      </div>
      <div class="risk-summary-item" v-if="riskAssessment.risk_reasons.length > 0">
        <span class="risk-label">风险原因：</span>
        <el-tag v-for="reason in riskAssessment.risk_reasons" :key="reason" type="danger" size="small" style="margin-right: 6px;">
          {{ reason }}
        </el-tag>
      </div>
      <div class="risk-summary-item">
        <span class="risk-label">距婚礼：</span>
        <span style="font-weight: 600; color: #303133;">{{ riskAssessment.details.days_until_wedding }} 天</span>
      </div>
      <div class="risk-summary-item">
        <span class="risk-label">完成率：</span>
        <span style="font-weight: 600;" :style="{ color: riskAssessment.details.completion_rate < 50 ? '#f56c6c' : '#67c23a' }">{{ riskAssessment.details.completion_rate }}%</span>
      </div>
    </div>

    <div class="timeline-wrapper">
      <div class="timeline-header">
        <div class="timeline-legend">
          <div class="legend-item">
            <span class="legend-dot high"></span>
            <span>高风险</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot medium"></span>
            <span>中风险</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot low"></span>
            <span>低风险</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot completed"></span>
            <span>已完成</span>
          </div>
        </div>
      </div>

      <div class="timeline-container" v-loading="loading">
        <div class="timeline-days">
          <div v-for="day in timelineDays" :key="day.date" class="timeline-day" :class="{ 'day-today': day.isToday, 'day-weekend': day.isWeekend }">
            <div class="day-header">
              <div class="day-week">{{ day.weekday }}</div>
              <div class="day-date">{{ day.displayDate }}</div>
            </div>
            <div class="day-tasks">
              <div v-for="task in getTasksForDate(day.date)" :key="task.id" 
                   class="timeline-task" 
                   :class="`task-${task.risk_level} task-${task.status}`"
                   @click="openTaskDetail(task)">
                <div class="task-risk-bar" :class="`bar-${task.risk_level}`"></div>
                <div class="task-content">
                  <div class="task-title">{{ task.title }}</div>
                  <div class="task-meta">
                    <span class="task-category" :style="{ background: getCategoryColor(task.category) }">
                      {{ getCategoryName(task.category) }}
                    </span>
                    <span v-if="task.risk_reasons && task.risk_reasons.length > 0" class="task-risk-tag">
                      <el-tag :type="getRiskLevelType(task.risk_level)" size="small" effect="dark">
                        {{ task.risk_reasons[0] }}
                      </el-tag>
                    </span>
                  </div>
                  <el-progress :percentage="task.progress" :stroke-width="4" :color="task.status === 'completed' ? '#67c23a' : getRiskColor(task.risk_level)" />
                </div>
              </div>
              <div v-if="getTasksForDate(day.date).length === 0" class="day-empty">
                无任务
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="priority-section" v-if="highPriorityTasks.length > 0">
      <h3 class="section-heading">🚨 高风险任务 - 优先处理</h3>
      <div class="priority-task-list">
        <div v-for="task in highPriorityTasks" :key="task.id" class="priority-task-card" @click="openTaskDetail(task)">
          <div class="priority-risk-reason">
            <el-tag type="danger" size="small" effect="dark">{{ task.risk_reasons?.[0] || '高风险' }}</el-tag>
          </div>
          <div class="priority-task-title">{{ task.title }}</div>
          <div class="priority-task-meta">
            <span class="task-category" :style="{ background: getCategoryColor(task.category) }">
              {{ getCategoryName(task.category) }}
            </span>
            <span>📅 {{ task.due_date }}</span>
            <span>进度 {{ task.progress }}%</span>
            <span class="risk-level" :class="`risk-${task.risk_level}`">
              {{ getRiskLevelText(task.risk_level) }}
            </span>
          </div>
          <el-progress :percentage="task.progress" :stroke-width="6" :color="getRiskColor(task.risk_level)" />
        </div>
      </div>
    </div>

    <el-dialog v-model="showDetail" title="任务详情" width="600px">
      <div v-if="selectedTask" class="detail-content">
        <div class="detail-row">
          <span class="detail-label">任务名称</span>
          <span class="detail-value">{{ selectedTask.title }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">任务描述</span>
          <span class="detail-value">{{ selectedTask.description || '暂无' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">所属类别</span>
          <el-tag :type="getCategoryType(selectedTask.category)" size="small">{{ getCategoryName(selectedTask.category) }}</el-tag>
        </div>
        <div class="detail-row">
          <span class="detail-label">当前状态</span>
          <el-tag :type="selectedTask.status === 'completed' ? 'success' : selectedTask.status === 'in_progress' ? 'primary' : 'info'" size="small">
            {{ getStatusName(selectedTask.status) }}
          </el-tag>
        </div>
        <div class="detail-row">
          <span class="detail-label">优先级</span>
          <el-tag :type="selectedTask.priority === 'high' ? 'danger' : selectedTask.priority === 'medium' ? 'warning' : 'success'" size="small">
            {{ selectedTask.priority === 'high' ? '高' : selectedTask.priority === 'medium' ? '中' : '低' }}
          </el-tag>
        </div>
        <div class="detail-row">
          <span class="detail-label">截止日期</span>
          <span class="detail-value">{{ selectedTask.due_date }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">完成进度</span>
          <el-progress :percentage="selectedTask.progress" :stroke-width="8" :color="getRiskColor(selectedTask.risk_level)" />
        </div>
        <div class="detail-row" v-if="selectedTask.risk_level">
          <span class="detail-label">风险等级</span>
          <el-tag :type="getRiskLevelType(selectedTask.risk_level)" size="small" effect="dark">
            {{ getRiskLevelText(selectedTask.risk_level) }}
          </el-tag>
        </div>
        <div class="detail-row" v-if="selectedTask.risk_reasons && selectedTask.risk_reasons.length > 0">
          <span class="detail-label">风险原因</span>
          <div class="risk-reasons">
            <el-tag v-for="reason in selectedTask.risk_reasons" :key="reason" type="danger" size="small" style="margin-right: 6px;">
              {{ reason }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getTasks } from '@/api/task'
import { getRiskAssessment } from '@/api/risk'

const WEDDING_ID = 1

const tasks = ref([])
const loading = ref(false)
const filterRisk = ref('')
const filterCategory = ref('')
const filterDate = ref(null)
const riskAssessment = ref(null)
const showDetail = ref(false)
const selectedTask = ref(null)

const categories = [
  { id: 'wedding_ceremony', name: '婚礼仪式' },
  { id: 'dress_accessories', name: '礼服配饰' },
  { id: 'photography', name: '摄影摄像' },
  { id: 'logistics', name: '物资采购' },
  { id: 'venue_decor', name: '场地布置' }
]

const categoryColors = {
  wedding_ceremony: '#409eff',
  dress_accessories: '#e6a23c',
  photography: '#909399',
  logistics: '#67c23a',
  venue_decor: '#f56c6c'
}

const getRiskLevelType = (level) => {
  const map = { low: 'success', medium: 'warning', high: 'danger' }
  return map[level] || 'info'
}

const getRiskLevelText = (level) => {
  const map = { low: '低风险', medium: '中风险', high: '高风险' }
  return map[level] || level
}

const getRiskColor = (level) => {
  const map = { low: '#67c23a', medium: '#e6a23c', high: '#f56c6c' }
  return map[level] || '#909399'
}

const getCategoryName = (id) => {
  const cat = categories.find(c => c.id === id)
  return cat ? cat.name : id
}

const getCategoryColor = (id) => {
  return categoryColors[id] || '#909399'
}

const getCategoryType = (id) => {
  const map = { wedding_ceremony: 'primary', dress_accessories: 'warning', photography: 'info', logistics: 'success', venue_decor: 'danger' }
  return map[id] || 'info'
}

const getStatusName = (status) => {
  const map = { pending: '待认领', in_progress: '进行中', completed: '已完成' }
  return map[status] || status
}

const timelineDays = computed(() => {
  const days = []
  const today = new Date()
  for (let i = 0; i < 14; i++) {
    const date = new Date(today)
    date.setDate(today.getDate() + i)
    const weekdayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    days.push({
      date: date.toISOString().split('T')[0],
      displayDate: `${date.getMonth() + 1}/${date.getDate()}`,
      weekday: weekdayNames[date.getDay()],
      isToday: i === 0,
      isWeekend: date.getDay() === 0 || date.getDay() === 6
    })
  }
  return days
})

const filteredTasks = computed(() => {
  let result = [...tasks.value]
  if (filterRisk.value) {
    result = result.filter(t => t.risk_level === filterRisk.value)
  }
  if (filterCategory.value) {
    result = result.filter(t => t.category === filterCategory.value)
  }
  return result
})

const highPriorityTasks = computed(() => {
  return tasks.value.filter(t => t.risk_level === 'high' && t.status !== 'completed')
})

const getTasksForDate = (dateStr) => {
  return filteredTasks.value.filter(t => t.due_date === dateStr)
}

const openTaskDetail = (task) => {
  selectedTask.value = task
  showDetail.value = true
}

const getDateStr = (daysOffset) => {
  const d = new Date()
  d.setDate(d.getDate() + daysOffset)
  return d.toISOString().split('T')[0]
}

const loadTasks = async () => {
  loading.value = true
  try {
    const res = await getTasks({ wedding_id: WEDDING_ID })
    tasks.value = res || []
    if (tasks.value.length === 0) {
      useMockData()
    }
  } catch (e) {
    useMockData()
  } finally {
    loading.value = false
  }
}

const useMockData = () => {
  tasks.value = [
    { id: 1, title: '设计堵门游戏方案', category: 'wedding_ceremony', status: 'in_progress', priority: 'high', progress: 60, due_date: getDateStr(2), description: '设计3个有趣的堵门游戏', risk_level: 'high', risk_score: 75, risk_reasons: ['关键任务逾期', '交付日期临近'] },
    { id: 2, title: '准备堵门红包', category: 'logistics', status: 'pending', priority: 'medium', progress: 0, due_date: getDateStr(3), description: '准备不同面额的红包', risk_level: 'medium', risk_score: 45, risk_reasons: ['尚未开始', '需协调物资'] },
    { id: 3, title: '采购拍照道具', category: 'logistics', status: 'completed', priority: 'low', progress: 100, due_date: getDateStr(1), description: '采购气球、花瓣等道具', risk_level: 'low', risk_score: 10, risk_reasons: [] },
    { id: 4, title: '试穿婚纱', category: 'dress_accessories', status: 'in_progress', priority: 'high', progress: 30, due_date: getDateStr(1), description: '预约试穿婚纱礼服', risk_level: 'high', risk_score: 65, risk_reasons: ['关键任务逾期'] },
    { id: 5, title: '预约摄影师', category: 'photography', status: 'completed', priority: 'high', progress: 100, due_date: getDateStr(0), description: '确认摄影师档期', risk_level: 'low', risk_score: 5, risk_reasons: [] },
    { id: 6, title: '场地布置方案确认', category: 'venue_decor', status: 'in_progress', priority: 'high', progress: 25, due_date: getDateStr(5), description: '确认场地布置方案', risk_level: 'high', risk_score: 70, risk_reasons: ['作品完成数量落后', '交付日期临近'] },
    { id: 7, title: '准备应急医药包', category: 'logistics', status: 'pending', priority: 'low', progress: 0, due_date: getDateStr(7), description: '准备常用药品', risk_level: 'low', risk_score: 15, risk_reasons: [] }
  ]
}

const loadRisk = async () => {
  try {
    const res = await getRiskAssessment(WEDDING_ID)
    riskAssessment.value = res || null
  } catch (e) {
    riskAssessment.value = {
      risk_level: 'high',
      risk_score: 85,
      risk_reasons: ['关键任务逾期', '材料不足', '交付日期临近'],
      details: {
        days_until_wedding: 5,
        completion_rate: 41.7,
        overdue_critical_tasks: 2,
        pending_logistics_tasks: 3,
        overdue_logistics_tasks: 1,
        total_tasks: 12,
        completed_tasks: 5,
        overdue_tasks: 3
      }
    }
  }
}

onMounted(() => {
  loadTasks()
  loadRisk()
})
</script>

<style scoped>
.production-schedule {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-filters {
  display: flex;
  gap: 12px;
}

.risk-summary-bar {
  background: white;
  border-radius: 12px;
  padding: 16px 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.risk-summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.risk-label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.timeline-wrapper {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  margin-bottom: 24px;
}

.timeline-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.timeline-legend {
  display: flex;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.high { background: #f56c6c; }
.legend-dot.medium { background: #e6a23c; }
.legend-dot.low { background: #67c23a; }
.legend-dot.completed { background: #909399; }

.timeline-container {
  overflow-x: auto;
}

.timeline-days {
  display: flex;
  gap: 8px;
  min-width: 1400px;
}

.timeline-day {
  flex: 1;
  min-width: 100px;
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
}

.timeline-day.day-today {
  background: #ecf5ff;
}

.timeline-day.day-weekend {
  background: #fdf6ec;
}

.day-header {
  padding: 12px 8px;
  text-align: center;
  background: rgba(0,0,0,0.02);
  border-bottom: 1px solid #ebeef5;
}

.day-week {
  font-size: 12px;
  color: #909399;
  margin-bottom: 2px;
}

.day-today .day-week {
  color: #409eff;
  font-weight: 600;
}

.day-date {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.day-today .day-date {
  color: #409eff;
}

.day-tasks {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 200px;
}

.timeline-task {
  background: white;
  border-radius: 6px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  overflow: hidden;
  border: 1px solid #ebeef5;
}

.timeline-task:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transform: translateY(-1px);
}

.timeline-task.task-completed {
  opacity: 0.7;
}

.task-risk-bar {
  width: 4px;
  flex-shrink: 0;
  margin: -8px 8px -8px -8px;
}

.bar-high { background: #f56c6c; }
.bar-medium { background: #e6a23c; }
.bar-low { background: #67c23a; }

.task-content {
  flex: 1;
  min-width: 0;
}

.task-title {
  font-size: 12px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-meta {
  display: flex;
  gap: 6px;
  margin-bottom: 6px;
  align-items: center;
  flex-wrap: wrap;
}

.task-category {
  padding: 1px 6px;
  border-radius: 3px;
  color: white;
  font-size: 10px;
  flex-shrink: 0;
}

.task-risk-tag {
  flex-shrink: 0;
}

.day-empty {
  text-align: center;
  color: #c0c4cc;
  font-size: 12px;
  padding: 20px 0;
}

.priority-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.section-heading {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.priority-task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.priority-task-card {
  background: #fff5f5;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  border-left: 4px solid #f56c6c;
}

.priority-task-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.priority-risk-reason {
  margin-bottom: 8px;
}

.priority-task-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.priority-task-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 10px;
  align-items: center;
}

.priority-task-meta .task-category {
  padding: 2px 8px;
  border-radius: 4px;
  color: white;
  font-size: 12px;
}

.risk-level {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.risk-high { background: #fef0f0; color: #f56c6c; }
.risk-medium { background: #fdf6ec; color: #e6a23c; }
.risk-low { background: #f0f9eb; color: #67c23a; }

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.detail-label {
  min-width: 100px;
  font-size: 14px;
  color: #909399;
  padding-top: 2px;
}

.detail-value {
  flex: 1;
  font-size: 14px;
  color: #303133;
}

.risk-reasons {
  flex: 1;
}
</style>
