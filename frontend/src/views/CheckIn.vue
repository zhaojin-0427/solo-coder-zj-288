<template>
  <div class="checkin-page">
    <div class="page-header">
      <h1 class="page-title">✅ 现场签到</h1>
      <div class="header-stats">
        <div class="mini-stat">
          <span class="mini-stat-value" style="color: #67c23a;">{{ checkinStats.checked_in_count || 0 }}</span>
          <span class="mini-stat-label">已签到</span>
        </div>
        <div class="mini-stat">
          <span class="mini-stat-value" style="color: #e6a23c;">{{ checkinStats.late_count || 0 }}</span>
          <span class="mini-stat-label">迟到</span>
        </div>
        <div class="mini-stat">
          <span class="mini-stat-value" style="color: #f56c6c;">{{ checkinStats.absent_count || 0 }}</span>
          <span class="mini-stat-label">未到</span>
        </div>
        <div class="mini-stat">
          <span class="mini-stat-value" style="color: #909399;">{{ checkinStats.pending_count || 0 }}</span>
          <span class="mini-stat-label">待签到</span>
        </div>
      </div>
    </div>

    <div class="search-section">
      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="输入宾客姓名或手机号快速搜索"
          size="large"
          clearable
          @input="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon :size="20"><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" size="large" @click="handleSearch">
          搜索
        </el-button>
      </div>
      <div class="quick-filters">
        <el-tag
          v-for="filter in quickFilters"
          :key="filter.value"
          :type="activeFilter === filter.value ? 'primary' : 'info'"
          :effect="activeFilter === filter.value ? 'dark' : 'plain'"
          class="filter-tag"
          @click="toggleFilter(filter.value)"
        >
          {{ filter.label }}
        </el-tag>
      </div>
    </div>

    <div class="high-priority-section" v-if="highPriorityGuests.length > 0">
      <div class="section-title">
        <span class="title-icon">⭐</span>
        <span>高关注宾客提醒</span>
        <el-tag type="danger" size="small">{{ highPriorityPending }} 位待签到</el-tag>
      </div>
      <div class="high-priority-list">
        <div
          v-for="guest in highPriorityGuests"
          :key="guest.id"
          class="priority-guest-card"
          :class="getPriorityCardClass(guest.checkin_status)"
        >
          <div class="priority-guest-info">
            <div class="guest-name">
              <el-tag type="danger" size="small" effect="dark">高优</el-tag>
              {{ guest.name }}
            </div>
            <div class="guest-meta">
              <span>{{ guest.relation_tag }}</span>
              <span>·</span>
              <span>{{ guest.group_name }}</span>
            </div>
            <div class="guest-notes" v-if="guest.special_notes">
              📝 {{ guest.special_notes }}
            </div>
          </div>
          <div class="priority-guest-status">
            <el-tag :type="getStatusType(guest.checkin_status)" effect="dark">
              {{ getStatusText(guest.checkin_status) }}
            </el-tag>
          </div>
          <div class="priority-guest-actions">
            <el-button
              v-if="guest.checkin_status === 'pending'"
              type="primary"
              size="small"
              @click="quickCheckin(guest)"
            >
              签到
            </el-button>
            <el-button
              v-else
              size="small"
              @click="openCheckinDialog(guest)"
            >
              详情
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <div class="results-section">
      <div class="section-header">
        <h3 class="section-title">搜索结果 ({{ searchResults.length }})</h3>
      </div>

      <div v-if="searchResults.length === 0 && searchKeyword" class="empty-state">
        <div class="empty-icon">🔍</div>
        <div class="empty-text">未找到匹配的宾客</div>
        <div class="empty-tip">请尝试输入其他姓名或手机号</div>
      </div>

      <div v-else class="guest-cards">
        <div
          v-for="guest in searchResults"
          :key="guest.id"
          class="guest-card"
          :class="{ 'checked': guest.checkin_status !== 'pending' }"
        >
          <div class="guest-card-header">
            <div class="guest-name-row">
              <span class="guest-name">{{ guest.name }}</span>
              <el-tag v-if="guest.is_high_priority" type="danger" size="small">高优</el-tag>
              <el-tag :type="getStatusType(guest.checkin_status)" size="small" effect="light">
                {{ getStatusText(guest.checkin_status) }}
              </el-tag>
            </div>
            <div class="guest-phone">{{ guest.phone }}</div>
          </div>

          <div class="guest-card-body">
            <div class="info-row">
              <span class="info-label">分组:</span>
              <el-tag size="small">{{ guest.group_name || '未分组' }}</el-tag>
            </div>
            <div class="info-row">
              <span class="info-label">关系:</span>
              <span class="info-value">{{ guest.relation_tag || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">预计人数:</span>
              <span class="info-value">{{ guest.total_count }} 人</span>
            </div>
            <div class="info-row">
              <span class="info-label">桌位:</span>
              <el-tag v-if="guest.table_name" type="success" size="small">{{ guest.table_name }}</el-tag>
              <span v-else style="color: #f56c6c;">未分配</span>
            </div>
            <div class="info-row" v-if="guest.checkin_status !== 'pending'">
              <span class="info-label">实到人数:</span>
              <span class="info-value" :class="{ 'text-danger': guest.actual_arrival_count !== guest.total_count }">
                {{ guest.actual_arrival_count }} 人
              </span>
            </div>
            <div class="info-row" v-if="guest.special_notes">
              <span class="info-label">备注:</span>
              <span class="info-value special">{{ guest.special_notes }}</span>
            </div>
          </div>

          <div class="guest-card-footer">
            <template v-if="guest.checkin_status === 'pending'">
              <el-button type="primary" size="small" @click="openCheckinDialog(guest)">
                签到
              </el-button>
              <el-button size="small" @click="markAsAbsent(guest)">
                标记未到
              </el-button>
            </template>
            <template v-else>
              <el-button size="small" @click="openCheckinDialog(guest)">
                查看/修改
              </el-button>
              <el-button size="small" type="warning" @click="resetStatus(guest)">
                重置状态
              </el-button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="checkinDialogVisible"
      title="宾客签到"
      width="500px"
    >
      <div class="checkin-guest-info" v-if="currentGuest">
        <div class="info-header">
          <span class="guest-name">{{ currentGuest.name }}</span>
          <el-tag v-if="currentGuest.is_high_priority" type="danger">高关注宾客</el-tag>
        </div>
        <div class="info-details">
          <div class="detail-item">
            <span class="detail-label">手机号:</span>
            <span class="detail-value">{{ currentGuest.phone }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">分组:</span>
            <span class="detail-value">{{ currentGuest.group_name || '未分组' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">关系:</span>
            <span class="detail-value">{{ currentGuest.relation_tag || '-' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">预计人数:</span>
            <span class="detail-value">{{ currentGuest.total_count }} 人</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">桌位:</span>
            <span class="detail-value">{{ currentGuest.table_name || '未分配' }}</span>
          </div>
          <div class="detail-item full-width" v-if="currentGuest.special_notes">
            <div class="special-notes-box">
              <div class="notes-title">⚠️ 特殊备注</div>
              <div class="notes-content">{{ currentGuest.special_notes }}</div>
            </div>
          </div>
        </div>
      </div>

      <el-divider />

      <el-form :model="checkinForm" label-width="100px">
        <el-form-item label="签到状态">
          <el-radio-group v-model="checkinForm.status">
            <el-radio label="checked_in">已签到</el-radio>
            <el-radio label="late">迟到</el-radio>
            <el-radio label="absent">未到</el-radio>
            <el-radio label="changed">临时变更</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="实到人数">
          <el-input-number v-model="checkinForm.actual_count" :min="0" :max="50" />
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">
            预计 {{ currentGuest?.total_count || 0 }} 人
          </span>
        </el-form-item>
        <el-form-item label="人数变化">
          <el-tag v-if="countChange > 0" type="success">+{{ countChange }} 人（临时增加）</el-tag>
          <el-tag v-else-if="countChange < 0" type="warning">{{ countChange }} 人（临时减少）</el-tag>
          <el-tag v-else type="info">与预计一致</el-tag>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="checkinForm.remark"
            type="textarea"
            :rows="2"
            placeholder="签到备注信息"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="checkinDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCheckin">确认签到</el-button>
      </template>
    </el-dialog>

    <div class="tables-quick-view">
      <div class="section-title">
        <span class="title-icon">🪑</span>
        <span>桌位签到概览</span>
      </div>
      <div class="tables-mini-grid">
        <div
          v-for="table in tables"
          :key="table.id"
          class="table-mini-card"
          :class="{ 'over': table.is_over_capacity, 'full': table.seating_rate >= 100 }"
        >
          <div class="table-mini-name">{{ table.name }}</div>
          <div class="table-mini-progress">
            <div
              class="progress-fill"
              :style="{ width: Math.min(table.seating_rate, 100) + '%' }"
            ></div>
          </div>
          <div class="table-mini-info">
            {{ table.checked_in_count }}/{{ table.capacity }}人
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { searchGuestsForCheckin, checkinGuest, updateCheckinStatus, getCheckinStats } from '@/api/checkin'
import { getTables } from '@/api/table'

const WEDDING_ID = 1
const OPERATOR_ID = 1

const searchKeyword = ref('')
const activeFilter = ref('all')
const searchResults = ref([])
const checkinStats = ref({})
const tables = ref([])

const checkinDialogVisible = ref(false)
const currentGuest = ref(null)
const checkinForm = ref({
  status: 'checked_in',
  actual_count: 0,
  remark: ''
})

const quickFilters = [
  { label: '全部', value: 'all' },
  { label: '待签到', value: 'pending' },
  { label: '已签到', value: 'checked_in' },
  { label: '迟到', value: 'late' },
  { label: '未到', value: 'absent' }
]

const highPriorityGuests = computed(() => {
  return searchResults.value.filter(g => g.is_high_priority)
})

const highPriorityPending = computed(() => {
  return highPriorityGuests.value.filter(g => g.checkin_status === 'pending').length
})

const countChange = computed(() => {
  const expected = currentGuest.value?.total_count || 0
  const actual = checkinForm.value.actual_count || 0
  return actual - expected
})

const getStatusType = (status) => {
  const map = {
    pending: 'info',
    checked_in: 'success',
    late: 'warning',
    absent: 'danger',
    changed: ''
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待签到',
    checked_in: '已签到',
    late: '迟到',
    absent: '未到',
    changed: '临时变更'
  }
  return map[status] || status
}

const getPriorityCardClass = (status) => {
  const map = {
    pending: 'pending',
    checked_in: 'checked',
    late: 'late',
    absent: 'absent'
  }
  return map[status] || ''
}

const toggleFilter = (value) => {
  if (activeFilter.value === value) {
    activeFilter.value = 'all'
  } else {
    activeFilter.value = value
  }
  handleSearch()
}

const handleSearch = async () => {
  try {
    let results = []
    if (searchKeyword.value) {
      const res = await searchGuestsForCheckin({
        wedding_id: WEDDING_ID,
        keyword: searchKeyword.value
      })
      results = res || []
    } else {
      const res = await searchGuestsForCheckin({
        wedding_id: WEDDING_ID,
        keyword: ''
      })
      results = res || []
    }

    if (activeFilter.value !== 'all') {
      results = results.filter(g => g.checkin_status === activeFilter.value)
    }

    searchResults.value = results
  } catch (e) {
    console.error('搜索失败', e)
  }
}

const loadStats = async () => {
  try {
    const res = await getCheckinStats({ wedding_id: WEDDING_ID })
    checkinStats.value = res || {}
  } catch (e) {
    console.error('加载统计失败', e)
  }
}

const loadTables = async () => {
  try {
    const res = await getTables({ wedding_id: WEDDING_ID })
    tables.value = res || []
  } catch (e) {
    console.error('加载桌位失败', e)
  }
}

const openCheckinDialog = (guest) => {
  currentGuest.value = guest
  checkinForm.value = {
    status: guest.checkin_status === 'pending' ? 'checked_in' : guest.checkin_status,
    actual_count: guest.actual_arrival_count || guest.total_count,
    remark: ''
  }
  checkinDialogVisible.value = true
}

const quickCheckin = async (guest) => {
  try {
    await checkinGuest(guest.id, {
      status: 'checked_in',
      actual_count: guest.total_count,
      operator_id: OPERATOR_ID,
      remark: '快速签到'
    })
    ElMessage.success(`${guest.name} 签到成功`)
    handleSearch()
    loadStats()
    loadTables()
  } catch (e) {
    ElMessage.error('签到失败')
    console.error(e)
  }
}

const markAsAbsent = (guest) => {
  ElMessageBox.confirm(`确定将 ${guest.name} 标记为未到吗？`, '确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await updateCheckinStatus(guest.id, {
        status: 'absent',
        actual_count: 0,
        operator_id: OPERATOR_ID,
        remark: '未到场'
      })
      ElMessage.success('已标记为未到')
      handleSearch()
      loadStats()
      loadTables()
    } catch (e) {
      ElMessage.error('操作失败')
      console.error(e)
    }
  }).catch(() => {})
}

const resetStatus = (guest) => {
  ElMessageBox.confirm(`确定将 ${guest.name} 的签到状态重置为待签到吗？`, '确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await updateCheckinStatus(guest.id, {
        status: 'pending',
        actual_count: 0,
        operator_id: OPERATOR_ID,
        remark: '重置状态'
      })
      ElMessage.success('状态已重置')
      handleSearch()
      loadStats()
      loadTables()
    } catch (e) {
      ElMessage.error('操作失败')
      console.error(e)
    }
  }).catch(() => {})
}

const confirmCheckin = async () => {
  try {
    if (currentGuest.value.checkin_status === 'pending') {
      await checkinGuest(currentGuest.value.id, {
        status: checkinForm.value.status,
        actual_count: checkinForm.value.actual_count,
        operator_id: OPERATOR_ID,
        remark: checkinForm.value.remark
      })
    } else {
      await updateCheckinStatus(currentGuest.value.id, {
        status: checkinForm.value.status,
        actual_count: checkinForm.value.actual_count,
        operator_id: OPERATOR_ID,
        remark: checkinForm.value.remark
      })
    }
    ElMessage.success('签到信息已更新')
    checkinDialogVisible.value = false
    handleSearch()
    loadStats()
    loadTables()
  } catch (e) {
    ElMessage.error('操作失败')
    console.error(e)
  }
}

let refreshTimer = null

onMounted(() => {
  handleSearch()
  loadStats()
  loadTables()
  
  refreshTimer = setInterval(() => {
    loadStats()
    loadTables()
  }, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.checkin-page {
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-stats {
  display: flex;
  gap: 20px;
}

.mini-stat {
  text-align: center;
  padding: 8px 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.mini-stat-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
}

.mini-stat-label {
  font-size: 12px;
  color: #909399;
}

.search-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.search-box {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.search-box .el-input {
  flex: 1;
}

.quick-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-tag {
  cursor: pointer;
  user-select: none;
}

.high-priority-section {
  background: linear-gradient(135deg, #fff0f0 0%, #ffe8e8 100%);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
  border: 1px solid #ffcccc;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.title-icon {
  font-size: 20px;
}

.high-priority-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.priority-guest-card {
  background: white;
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-left: 4px solid #f56c6c;
}

.priority-guest-card.checked {
  border-left-color: #67c23a;
  opacity: 0.7;
}

.priority-guest-card.late {
  border-left-color: #e6a23c;
}

.priority-guest-card.absent {
  border-left-color: #909399;
  opacity: 0.6;
}

.priority-guest-info {
  flex: 1;
  min-width: 0;
}

.guest-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.guest-meta {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.guest-notes {
  font-size: 12px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
}

.priority-guest-status {
  flex-shrink: 0;
}

.priority-guest-actions {
  flex-shrink: 0;
}

.results-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.section-header {
  margin-bottom: 16px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}

.empty-tip {
  font-size: 13px;
  color: #909399;
}

.guest-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.guest-card {
  border: 1px solid #ebeef5;
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.3s;
}

.guest-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.guest-card.checked {
  background: #f0f9eb;
  border-color: #c2e7b0;
}

.guest-card-header {
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

.guest-card.checked .guest-card-header {
  background: #e1f3d8;
}

.guest-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.guest-card-header .guest-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.guest-phone {
  font-size: 13px;
  color: #909399;
}

.guest-card-body {
  padding: 12px 16px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 13px;
}

.info-label {
  color: #909399;
  flex-shrink: 0;
}

.info-value {
  color: #606266;
}

.info-value.special {
  color: #e6a23c;
}

.text-danger {
  color: #f56c6c !important;
  font-weight: 500;
}

.guest-card-footer {
  padding: 12px 16px;
  border-top: 1px solid #ebeef5;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.checkin-guest-info {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.info-header .guest-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.info-details {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.detail-item {
  flex: 1;
  min-width: 45%;
  font-size: 13px;
}

.detail-item.full-width {
  flex: 100%;
}

.detail-label {
  color: #909399;
}

.detail-value {
  color: #303133;
  font-weight: 500;
}

.special-notes-box {
  background: #fdf6ec;
  border-radius: 6px;
  padding: 10px 12px;
  border: 1px solid #faecd8;
}

.notes-title {
  font-size: 13px;
  font-weight: 600;
  color: #e6a23c;
  margin-bottom: 4px;
}

.notes-content {
  font-size: 13px;
  color: #606266;
}

.tables-quick-view {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.tables-mini-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.table-mini-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 10px;
  text-align: center;
  border: 1px solid #ebeef5;
}

.table-mini-card.full {
  background: #f0f9eb;
  border-color: #c2e7b0;
}

.table-mini-card.over {
  background: #fef0f0;
  border-color: #fbc4c4;
}

.table-mini-name {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.table-mini-progress {
  height: 6px;
  background: #ebeef5;
  border-radius: 3px;
  margin-bottom: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #67c23a;
  border-radius: 3px;
  transition: width 0.3s;
}

.table-mini-card.over .progress-fill {
  background: #f56c6c;
}

.table-mini-info {
  font-size: 11px;
  color: #909399;
}
</style>
