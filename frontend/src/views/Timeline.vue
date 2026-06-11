<template>
  <div class="timeline-page">
    <div class="page-header">
      <h1 class="page-title">📅 婚礼当天流程</h1>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog" :icon="Plus">
          添加流程节点
        </el-button>
      </div>
    </div>

    <div class="timeline-container">
      <div class="timeline">
        <div
          v-for="(node, index) in timelineNodes"
          :key="node.id"
          class="timeline-node"
          :class="{ active: currentNodeIndex === index, completed: node.status === 'completed' }"
        >
          <div class="timeline-dot">
            <span v-if="node.status === 'completed'" class="dot-icon">✓</span>
            <span v-else class="dot-number">{{ index + 1 }}</span>
          </div>
          
          <div class="timeline-content">
            <div class="time-badge">
              <span class="start-time">{{ formatTime(node.start_time) }}</span>
              <span v-if="node.end_time" class="end-time"> - {{ formatTime(node.end_time) }}</span>
            </div>
            
            <div class="node-card" :class="node.status">
              <div class="node-header">
                <h3 class="node-title">{{ node.title }}</h3>
                <el-tag :type="getStatusType(node.status)" size="small">
                  {{ getStatusText(node.status) }}
                </el-tag>
              </div>
              
              <p v-if="node.description" class="node-desc">{{ node.description }}</p>
              
              <div v-if="node.location" class="node-location">
                📍 {{ node.location }}
              </div>
              
              <div v-if="node.assigned_bridesmaids && node.assigned_bridesmaids.length > 0" class="node-assignees">
                <span class="assignees-label">负责人：</span>
                <div class="assignee-avatars">
                  <span
                    v-for="bm in node.assigned_bridesmaids"
                    :key="bm.id"
                    class="assignee-tag"
                    :title="bm.name"
                  >
                    {{ bm.avatar || '👩' }} {{ bm.name }}
                  </span>
                </div>
              </div>
              
              <div class="node-actions">
                <el-button size="small" @click="editNode(node)">编辑</el-button>
                <el-button size="small" type="success" v-if="node.status !== 'completed'" @click="markComplete(node)">
                  标记完成
                </el-button>
                <el-button size="small" type="warning" @click="reassignNode(node)">
                  调整分工
                </el-button>
              </div>
            </div>
          </div>
          
          <div v-if="index < timelineNodes.length - 1" class="timeline-line"></div>
        </div>
      </div>
    </div>

    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑流程节点' : '添加流程节点'" width="500px">
      <el-form :model="nodeForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="nodeForm.title" placeholder="请输入流程节点标题" />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-time-picker
            v-model="nodeForm.start_time"
            format="HH:mm"
            value-format="HH:mm:ss"
            placeholder="选择开始时间"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-time-picker
            v-model="nodeForm.end_time"
            format="HH:mm"
            value-format="HH:mm:ss"
            placeholder="选择结束时间（可选）"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="地点">
          <el-input v-model="nodeForm.location" placeholder="流程地点" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="nodeForm.description" type="textarea" :rows="2" placeholder="流程描述（可选）" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="selectedAssignees" multiple placeholder="选择负责的伴娘" style="width: 100%;">
            <el-option v-for="bm in bridesmaids" :key="bm.id" :label="bm.name" :value="bm.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelAddDialog">取消</el-button>
        <el-button type="primary" @click="saveNode">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showReassignDialog" title="快速调整分工" width="400px">
      <div v-if="currentNode" style="margin-bottom: 20px;">
        <p><strong>节点：</strong>{{ currentNode.title }}</p>
        <p><strong>时间：</strong>{{ formatTime(currentNode.start_time) }}</p>
      </div>
      <el-form label-width="80px">
        <el-form-item label="新负责人">
          <el-select v-model="reassignAssignees" multiple placeholder="选择负责的伴娘" style="width: 100%;">
            <el-option v-for="bm in bridesmaids" :key="bm.id" :label="bm.name" :value="bm.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="调整原因">
          <el-input v-model="reassignReason" type="textarea" :rows="2" placeholder="请输入调整原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReassignDialog = false">取消</el-button>
        <el-button type="warning" @click="confirmReassign">确认调整</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getTimeline,
  createTimelineNode,
  updateTimelineNode,
  deleteTimelineNode,
  assignBridesmaidToNode,
  updateNodeStatus
} from '@/api/timeline'
import { getBridesmaids } from '@/api/bridesmaid'

const WEDDING_ID = 1

const timelineNodes = ref([])
const bridesmaids = ref([])
const currentNodeIndex = ref(-1)

const showAddDialog = ref(false)
const showReassignDialog = ref(false)
const isEdit = ref(false)
const currentNode = ref(null)
const editingNodeId = ref(null)

const nodeForm = ref({
  title: '',
  start_time: '',
  end_time: '',
  location: '',
  description: ''
})

const selectedAssignees = ref([])
const reassignAssignees = ref([])
const reassignReason = ref('')

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  if (typeof timeStr === 'string') {
    return timeStr.substring(0, 5)
  }
  return timeStr
}

const getStatusType = (status) => {
  const map = {
    upcoming: 'info',
    in_progress: 'warning',
    completed: 'success'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    upcoming: '未开始',
    in_progress: '进行中',
    completed: '已完成'
  }
  return map[status] || status
}

const loadTimeline = async () => {
  try {
    const res = await getTimeline({ wedding_id: WEDDING_ID })
    timelineNodes.value = res || []
  } catch (e) {
    useMockData()
  }
}

const loadBridesmaids = async () => {
  try {
    const res = await getBridesmaids({ wedding_id: WEDDING_ID })
    bridesmaids.value = res || []
  } catch (e) {
    bridesmaids.value = [
      { id: 1, name: '王小雨', avatar: '👩‍🦰', role: 'leader' },
      { id: 2, name: '刘思琪', avatar: '👩‍🦱', role: 'member' },
      { id: 3, name: '陈梦瑶', avatar: '👩', role: 'member' },
      { id: 4, name: '杨雪婷', avatar: '👩‍🦳', role: 'member' },
      { id: 5, name: '赵嘉怡', avatar: '👩‍🦲', role: 'member' }
    ]
  }
}

const useMockData = () => {
  timelineNodes.value = [
    { id: 1, title: '新娘化妆', description: '化妆师到达，开始新娘妆发造型', start_time: '05:30:00', end_time: '07:30:00', location: '新娘家', status: 'upcoming', order_index: 0, assigned_bridesmaids: [{ id: 1, name: '王小雨', avatar: '👩‍🦰' }] },
    { id: 2, title: '摄影师到达', description: '摄影师到达新娘家，开始拍摄准备过程', start_time: '07:00:00', end_time: '07:30:00', location: '新娘家', status: 'upcoming', order_index: 1, assigned_bridesmaids: [] },
    { id: 3, title: '迎亲车队出发', description: '新郎带领迎亲车队从新郎家出发', start_time: '07:30:00', end_time: '08:00:00', location: '新郎家', status: 'upcoming', order_index: 2, assigned_bridesmaids: [{ id: 2, name: '刘思琪', avatar: '👩‍🦱' }] },
    { id: 4, title: '堵门游戏', description: '伴娘团设置堵门关卡，新郎闯关接新娘', start_time: '08:00:00', end_time: '09:00:00', location: '新娘家', status: 'upcoming', order_index: 3, assigned_bridesmaids: [{ id: 1, name: '王小雨', avatar: '👩‍🦰' }, { id: 3, name: '陈梦瑶', avatar: '👩' }] },
    { id: 5, title: '敬茶改口', description: '新人向双方父母敬茶，改口叫爸妈', start_time: '09:00:00', end_time: '09:30:00', location: '新娘家', status: 'upcoming', order_index: 4, assigned_bridesmaids: [{ id: 1, name: '王小雨', avatar: '👩‍🦰' }] },
    { id: 6, title: '婚礼仪式', description: '正式婚礼仪式，包括入场、交换戒指、宣誓等', start_time: '11:08:00', end_time: '12:00:00', location: '宴会厅', status: 'upcoming', order_index: 7, assigned_bridesmaids: [{ id: 1, name: '王小雨', avatar: '👩‍🦰' }, { id: 2, name: '刘思琪', avatar: '👩‍🦱' }, { id: 3, name: '陈梦瑶', avatar: '👩' }] },
    { id: 7, title: '婚宴开始', description: '宾客用餐，新人逐桌敬酒', start_time: '12:00:00', end_time: '14:00:00', location: '宴会厅', status: 'upcoming', order_index: 8, assigned_bridesmaids: [{ id: 1, name: '王小雨', avatar: '👩‍🦰' }, { id: 3, name: '陈梦瑶', avatar: '👩' }] }
  ]
}

const editNode = (node) => {
  isEdit.value = true
  editingNodeId.value = node.id
  nodeForm.value = {
    title: node.title,
    start_time: node.start_time,
    end_time: node.end_time || '',
    location: node.location || '',
    description: node.description || ''
  }
  selectedAssignees.value = node.assigned_bridesmaids ? node.assigned_bridesmaids.map(b => b.id) : []
  showAddDialog.value = true
}

const saveNode = async () => {
  if (!nodeForm.value.title || !nodeForm.value.start_time) {
    ElMessage.warning('请填写标题和开始时间')
    return
  }
  
  try {
    const data = {
      wedding_id: WEDDING_ID,
      ...nodeForm.value
    }
    
    if (isEdit.value) {
      await updateTimelineNode(editingNodeId.value, data)
      if (selectedAssignees.value.length > 0) {
        await assignBridesmaidToNode(editingNodeId.value, selectedAssignees.value)
      }
      ElMessage.success('更新成功')
    } else {
      const res = await createTimelineNode(data)
      if (selectedAssignees.value.length > 0) {
        await assignBridesmaidToNode(res.id, selectedAssignees.value)
      }
      ElMessage.success('添加成功')
    }
    
    showAddDialog.value = false
    loadTimeline()
    resetForm()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const openAddDialog = () => {
  resetForm()
  showAddDialog.value = true
}

const cancelAddDialog = () => {
  resetForm()
  showAddDialog.value = false
}

const resetForm = () => {
  nodeForm.value = {
    title: '',
    start_time: '',
    end_time: '',
    location: '',
    description: ''
  }
  selectedAssignees.value = []
  isEdit.value = false
  editingNodeId.value = null
}

const markComplete = async (node) => {
  try {
    await updateNodeStatus(node.id, 'completed')
    node.status = 'completed'
    ElMessage.success('已标记完成')
    loadTimeline()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const reassignNode = (node) => {
  currentNode.value = node
  reassignAssignees.value = node.assigned_bridesmaids ? node.assigned_bridesmaids.map(b => b.id) : []
  reassignReason.value = '突发情况调整'
  showReassignDialog.value = true
}

const confirmReassign = async () => {
  if (reassignAssignees.value.length === 0) {
    ElMessage.warning('请至少选择一位负责人')
    return
  }
  
  try {
    await assignBridesmaidToNode(currentNode.value.id, reassignAssignees.value)
    ElMessage.success('分工已调整')
    showReassignDialog.value = false
    loadTimeline()
  } catch (e) {
    ElMessage.error('调整失败')
  }
}

onMounted(() => {
  loadBridesmaids()
  loadTimeline()
})
</script>

<style scoped>
.timeline-page {
  min-height: 100%;
}

.timeline-container {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.timeline {
  position: relative;
  padding-left: 60px;
}

.timeline-node {
  position: relative;
  padding-bottom: 30px;
}

.timeline-node:last-child {
  padding-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: -60px;
  top: 0;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b9d 0%, #c44569 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  z-index: 2;
  box-shadow: 0 2px 8px rgba(196, 69, 105, 0.3);
}

.timeline-node.completed .timeline-dot {
  background: linear-gradient(135deg, #67c23a 0%, #4a9e2d 100%);
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
}

.dot-icon {
  font-size: 18px;
}

.dot-number {
  font-size: 16px;
}

.timeline-line {
  position: absolute;
  left: -39px;
  top: 44px;
  width: 2px;
  height: calc(100% - 14px);
  background: #e4e7ed;
  z-index: 1;
}

.timeline-node.completed .timeline-line {
  background: #67c23a;
}

.timeline-content {
  margin-left: 10px;
}

.time-badge {
  display: inline-block;
  background: #ecf5ff;
  color: #409eff;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 10px;
}

.timeline-node.completed .time-badge {
  background: #f0f9eb;
  color: #67c23a;
}

.start-time {
  font-weight: 600;
}

.end-time {
  color: #909399;
}

.node-card {
  background: #fafafa;
  border-radius: 10px;
  padding: 16px 20px;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.node-card:hover {
  border-color: #dcdfe6;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.node-card.completed {
  background: #f0f9eb;
  border-color: #c2e7b0;
}

.node-card.in_progress {
  background: #fdf6ec;
  border-color: #f5dab1;
}

.node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.node-title {
  font-size: 17px;
  font-weight: 600;
  color: #303133;
}

.node-desc {
  color: #606266;
  font-size: 14px;
  margin-bottom: 10px;
  line-height: 1.5;
}

.node-location {
  color: #909399;
  font-size: 13px;
  margin-bottom: 12px;
}

.node-assignees {
  margin-bottom: 12px;
}

.assignees-label {
  font-size: 13px;
  color: #909399;
  margin-right: 8px;
}

.assignee-avatars {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
}

.assignee-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: white;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
  color: #606266;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.node-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}
</style>
