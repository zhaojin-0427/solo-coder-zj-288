<template>
  <div class="material-page">
    <div class="page-header">
      <h1 class="page-title">📦 物资借用与归还追踪</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showAddMaterialDialog = true" :icon="Plus">
          新增物资
        </el-button>
        <el-button type="success" @click="showBorrowDialog = true" :icon="Position">
          登记借用
        </el-button>
        <el-button type="warning" @click="showLinkMaterialDialog = true" :icon="Connection">
          关联物资
        </el-button>
      </div>
    </div>

    <div class="material-overview">
      <div class="stat-card total">
        <div class="stat-icon">📦</div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.total_items || 0 }}</div>
          <div class="stat-label">物资种类</div>
        </div>
      </div>
      <div class="stat-card quantity">
        <div class="stat-icon">🔢</div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.total_quantity || 0 }}</div>
          <div class="stat-label">库存总量</div>
        </div>
      </div>
      <div class="stat-card borrowed">
        <div class="stat-icon">📤</div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.total_borrowed || 0 }}</div>
          <div class="stat-label">已借出</div>
        </div>
      </div>
      <div class="stat-card available">
        <div class="stat-icon">📥</div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.total_available || 0 }}</div>
          <div class="stat-label">可用数量</div>
        </div>
      </div>
      <div class="stat-card overdue">
        <div class="stat-icon">⚠️</div>
        <div class="stat-content">
          <div class="stat-value" :class="{ 'text-danger': summary.overdue_count > 0 }">{{ summary.overdue_count || 0 }}</div>
          <div class="stat-label">逾期未还</div>
        </div>
      </div>
      <div class="stat-card abnormal">
        <div class="stat-icon">🔴</div>
        <div class="stat-content">
          <div class="stat-value" :class="{ 'text-danger': summary.abnormal_count > 0 }">{{ summary.abnormal_count || 0 }}</div>
          <div class="stat-label">异常归还</div>
        </div>
      </div>
    </div>

    <div class="overdue-alert-section" v-if="overdueAlerts.length > 0">
      <h3 class="section-title">⚠️ 逾期未归还提醒</h3>
      <div class="overdue-alert-list">
        <div
          v-for="alert in overdueAlerts"
          :key="alert.borrowing_id"
          class="overdue-alert-card"
        >
          <div class="alert-icon">🚨</div>
          <div class="alert-content">
            <div class="alert-main">
              <span class="alert-material">{{ alert.material_name }}</span>
              <span class="alert-borrower">{{ alert.borrower_name }}</span>
              <span class="alert-quantity">借用 {{ alert.borrowed_quantity }} 件</span>
            </div>
            <div class="alert-detail">
              应还时间：{{ formatDateTime(alert.expected_return_time) }}
              <span class="overdue-duration">已逾期 {{ formatOverdueDuration(alert.overdue_minutes) }}</span>
            </div>
          </div>
          <el-button size="small" type="success" @click="openReturnFromAlert(alert)">
            催还/归还
          </el-button>
        </div>
      </div>
    </div>

    <div class="abnormal-section" v-if="abnormalReturns.length > 0">
      <h3 class="section-title">🔴 异常归还记录</h3>
      <el-table :data="abnormalReturns" stripe style="width: 100%;">
        <el-table-column label="物资" width="130">
          <template #default="{ row }">
            <span class="material-tag">{{ row.material_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="borrower_name" label="借用人" width="100" />
        <el-table-column label="借用/归还" width="110">
          <template #default="{ row }">
            <span class="text-danger">{{ row.returned_quantity }}/{{ row.borrowed_quantity }}</span>
          </template>
        </el-table-column>
        <el-table-column label="丢失/损坏" width="100">
          <template #default="{ row }">
            <el-tag type="danger" size="small">-{{ row.loss_quantity }}件</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="abnormal_note" label="异常说明" min-width="200" show-overflow-tooltip />
        <el-table-column label="归还时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.returned_at) }}
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="content-section">
      <h3 class="section-title">📋 物资清单</h3>
      <div class="material-list">
        <div
          v-for="item in materials"
          :key="item.id"
          class="material-card"
          :class="{ 'has-overdue': item.overdue_count > 0, 'low-stock': item.available_quantity === 0 }"
        >
          <div class="material-header">
            <div class="material-info">
              <span class="material-name">{{ item.name }}</span>
              <el-tag v-if="item.overdue_count > 0" type="danger" size="small" effect="dark">
                {{ item.overdue_count }}笔逾期
              </el-tag>
              <el-tag v-if="item.available_quantity === 0" type="warning" size="small" effect="dark">
                已借完
              </el-tag>
            </div>
            <div class="material-actions">
              <el-button size="small" type="primary" text @click="editMaterial(item)">编辑</el-button>
              <el-button size="small" type="danger" text @click="handleDeleteMaterial(item)">删除</el-button>
            </div>
          </div>
          <div class="quantity-row">
            <div class="quantity-item">
              <span class="quantity-label">总量</span>
              <span class="quantity-value">{{ item.total_quantity }}</span>
            </div>
            <div class="quantity-item">
              <span class="quantity-label">已借出</span>
              <span class="quantity-value borrowed">{{ item.borrowed_quantity }}</span>
            </div>
            <div class="quantity-item">
              <span class="quantity-label">可用</span>
              <span class="quantity-value available">{{ item.available_quantity }}</span>
            </div>
          </div>
          <div class="progress-section">
            <el-progress
              :percentage="item.total_quantity > 0 ? Math.round(item.borrowed_quantity / item.total_quantity * 100) : 0"
              :stroke-width="8"
              :color="item.available_quantity === 0 ? '#f56c6c' : item.borrowed_quantity > item.total_quantity / 2 ? '#e6a23c' : '#67c23a'"
            />
          </div>
          <div class="material-meta">
            <div class="meta-item" v-if="item.storage_location">
              <span class="meta-label">📍 存放位置：</span>
              <span>{{ item.storage_location }}</span>
            </div>
            <div class="meta-item" v-if="item.person_in_charge_name">
              <span class="meta-label">👤 负责人：</span>
              <span>{{ item.person_in_charge_name }}</span>
            </div>
            <div class="meta-item" v-if="item.notes">
              <span class="meta-label">📝 备注：</span>
              <span>{{ item.notes }}</span>
            </div>
          </div>
          <div class="material-footer">
            <span class="borrowing-count">{{ item.borrowing_count }} 笔借用记录</span>
            <el-button size="small" type="primary" text @click="filterBorrowings(item.id)">
              查看记录 →
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <div class="borrowings-section">
      <div class="section-header">
        <h3 class="section-title">📋 借还记录</h3>
        <div class="filter-tabs">
          <el-radio-group v-model="activeBorrowingTab" @change="loadBorrowings">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="borrowed">借用中</el-radio-button>
            <el-radio-button value="overdue">逾期未还</el-radio-button>
            <el-radio-button value="returned">已归还</el-radio-button>
          </el-radio-group>
        </div>
      </div>

      <el-table :data="filteredBorrowings" stripe style="width: 100%;" v-loading="loadingBorrowings">
        <el-table-column label="物资" width="130">
          <template #default="{ row }">
            <span class="material-tag">{{ row.material_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="borrower_name" label="借用人" width="100" />
        <el-table-column label="借用数量" width="90">
          <template #default="{ row }">
            <span>{{ row.borrowed_quantity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="purpose" label="用途" min-width="160" show-overflow-tooltip />
        <el-table-column label="预计归还" width="160">
          <template #default="{ row }">
            <span v-if="row.expected_return_time">{{ formatDateTime(row.expected_return_time) }}</span>
            <span v-else style="color: #909399;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getBorrowingStatusType(row.status)" size="small" effect="dark">
              {{ getBorrowingStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="归还数量" width="90">
          <template #default="{ row }">
            <span v-if="row.status === 'returned'">{{ row.returned_quantity }}/{{ row.borrowed_quantity }}</span>
            <span v-else style="color: #909399;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="异常" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_abnormal" type="danger" size="small">异常</el-tag>
            <span v-else style="color: #909399;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="借用时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status !== 'returned'"
              size="small"
              type="success"
              @click="openReturnDialog(row)"
            >
              归还
            </el-button>
            <el-button
              size="small"
              type="primary"
              text
              @click="viewBorrowingDetail(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="showAddMaterialDialog" title="新增物资" width="520px">
      <el-form :model="newMaterial" label-width="100px">
        <el-form-item label="物资名称" required>
          <el-input v-model="newMaterial.name" placeholder="如：对讲机、充电宝、补光灯" />
        </el-form-item>
        <el-form-item label="数量" required>
          <el-input-number v-model="newMaterial.total_quantity" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="存放位置">
          <el-input v-model="newMaterial.storage_location" placeholder="如：新娘房·储物柜A" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="newMaterial.person_in_charge" placeholder="选择负责人" clearable style="width: 100%;">
            <el-option
              v-for="bm in bridesmaids"
              :key="bm.id"
              :label="bm.name"
              :value="bm.id"
            >
              <span>{{ bm.avatar || '👩' }} {{ bm.name }}</span>
              <span v-if="bm.role === 'leader'" style="color: #e6a23c; margin-left: 8px; font-size: 12px;">团长</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="newMaterial.notes"
            type="textarea"
            :rows="2"
            placeholder="物资备注说明（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddMaterialDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateMaterial">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEditMaterialDialog" title="编辑物资" width="520px">
      <el-form :model="editingMaterial" label-width="100px">
        <el-form-item label="物资名称" required>
          <el-input v-model="editingMaterial.name" />
        </el-form-item>
        <el-form-item label="数量" required>
          <el-input-number v-model="editingMaterial.total_quantity" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="存放位置">
          <el-input v-model="editingMaterial.storage_location" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="editingMaterial.person_in_charge" placeholder="选择负责人" clearable style="width: 100%;">
            <el-option
              v-for="bm in bridesmaids"
              :key="bm.id"
              :label="bm.name"
              :value="bm.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="editingMaterial.notes"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditMaterialDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateMaterial">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBorrowDialog" title="登记借用" width="520px">
      <el-form :model="newBorrowing" label-width="100px">
        <el-form-item label="选择物资" required>
          <el-select v-model="newBorrowing.material_id" placeholder="选择物资" style="width: 100%;">
            <el-option
              v-for="item in materials"
              :key="item.id"
              :label="item.name"
              :value="item.id"
              :disabled="item.available_quantity === 0"
            >
              <span>{{ item.name }}</span>
              <span style="color: #909399; margin-left: 8px; font-size: 12px;">
                可用: {{ item.available_quantity }}/{{ item.total_quantity }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="借用人" required>
          <el-input v-model="newBorrowing.borrower_name" placeholder="借用人姓名" />
        </el-form-item>
        <el-form-item label="借用数量" required>
          <el-input-number v-model="newBorrowing.borrowed_quantity" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="用途">
          <el-input
            v-model="newBorrowing.purpose"
            type="textarea"
            :rows="2"
            placeholder="借用用途说明"
          />
        </el-form-item>
        <el-form-item label="预计归还">
          <el-date-picker
            v-model="newBorrowing.expected_return_time"
            type="datetime"
            placeholder="选择预计归还时间"
            style="width: 100%;"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBorrowDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateBorrowing">确认借用</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showReturnDialog" title="归还物资" width="520px">
      <div v-if="returningBorrowing" class="return-content">
        <div class="return-info">
          <p><strong>物资：</strong>{{ returningBorrowing.material_name }}</p>
          <p><strong>借用人：</strong>{{ returningBorrowing.borrower_name }}</p>
          <p><strong>借用数量：</strong>{{ returningBorrowing.borrowed_quantity }}</p>
          <p><strong>用途：</strong>{{ returningBorrowing.purpose || '-' }}</p>
        </div>
        <el-form label-width="100px">
          <el-form-item label="归还数量" required>
            <el-input-number
              v-model="returnData.returned_quantity"
              :min="1"
              :max="returningBorrowing.borrowed_quantity"
              style="width: 100%;"
            />
          </el-form-item>
          <el-form-item label="异常说明" v-if="returnData.returned_quantity < returningBorrowing.borrowed_quantity">
            <el-input
              v-model="returnData.abnormal_note"
              type="textarea"
              :rows="2"
              placeholder="请说明归还异常原因（如丢失、损坏等）"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showReturnDialog = false">取消</el-button>
        <el-button type="success" @click="handleReturn">确认归还</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBorrowingDetailDialog" title="借还详情" width="520px">
      <div v-if="selectedBorrowing" class="borrowing-detail">
        <div class="detail-row">
          <span class="detail-label">物资：</span>
          <span class="material-tag">{{ selectedBorrowing.material_name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">借用人：</span>
          <span>{{ selectedBorrowing.borrower_name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">借用数量：</span>
          <span>{{ selectedBorrowing.borrowed_quantity }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">用途：</span>
          <span>{{ selectedBorrowing.purpose || '-' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">预计归还：</span>
          <span>{{ formatDateTime(selectedBorrowing.expected_return_time) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">状态：</span>
          <el-tag :type="getBorrowingStatusType(selectedBorrowing.status)" size="small" effect="dark">
            {{ getBorrowingStatusText(selectedBorrowing.status) }}
          </el-tag>
        </div>
        <div class="detail-row" v-if="selectedBorrowing.status === 'returned'">
          <span class="detail-label">归还数量：</span>
          <span>{{ selectedBorrowing.returned_quantity }}/{{ selectedBorrowing.borrowed_quantity }}</span>
        </div>
        <div class="detail-row" v-if="selectedBorrowing.is_abnormal">
          <span class="detail-label">异常说明：</span>
          <span class="text-danger">{{ selectedBorrowing.abnormal_note || '-' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">借用时间：</span>
          <span>{{ formatDateTime(selectedBorrowing.created_at) }}</span>
        </div>
        <div class="detail-row" v-if="selectedBorrowing.returned_at">
          <span class="detail-label">归还时间：</span>
          <span>{{ formatDateTime(selectedBorrowing.returned_at) }}</span>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="showLinkMaterialDialog" title="关联物资到任务/流程" width="600px">
      <el-form label-width="100px">
        <el-form-item label="关联类型">
          <el-radio-group v-model="linkForm.type">
            <el-radio value="task">任务</el-radio>
            <el-radio value="timeline">流程节点</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="选择物资" required>
          <el-select v-model="linkForm.material_id" placeholder="选择物资" style="width: 100%;">
            <el-option
              v-for="item in materials"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="linkForm.type === 'task'" label="选择任务" required>
          <el-select v-model="linkForm.target_id" placeholder="选择任务" style="width: 100%;" filterable>
            <el-option
              v-for="task in tasks"
              :key="task.id"
              :label="task.title"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="linkForm.type === 'timeline'" label="选择流程" required>
          <el-select v-model="linkForm.target_id" placeholder="选择流程节点" style="width: 100%;" filterable>
            <el-option
              v-for="node in timelineNodes"
              :key="node.id"
              :label="`${node.title} (${node.start_time || ''})`"
              :value="node.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="需求数量">
          <el-input-number v-model="linkForm.quantity_needed" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="linkForm.notes" placeholder="关联备注（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLinkMaterialDialog = false">取消</el-button>
        <el-button type="primary" @click="handleLinkMaterial">确认关联</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Position, Connection } from '@element-plus/icons-vue'
import {
  getMaterials,
  createMaterial,
  updateMaterial,
  deleteMaterial,
  getBorrowings,
  createBorrowing,
  returnBorrowing,
  getMaterialSummary,
  getOverdueAlerts,
  getAbnormalReturns,
  linkTaskMaterial,
  linkTimelineMaterial
} from '@/api/material'
import { getBridesmaids } from '@/api/bridesmaid'
import { getTasks } from '@/api/task'
import { getTimeline } from '@/api/timeline'

const WEDDING_ID = 1

const materials = ref([])
const borrowings = ref([])
const bridesmaids = ref([])
const tasks = ref([])
const timelineNodes = ref([])
const summary = ref({})
const loadingBorrowings = ref(false)
const activeBorrowingTab = ref('all')
const filterMaterialId = ref(null)
const overdueAlerts = ref([])
const abnormalReturns = ref([])

const showAddMaterialDialog = ref(false)
const showEditMaterialDialog = ref(false)
const showBorrowDialog = ref(false)
const showReturnDialog = ref(false)
const showBorrowingDetailDialog = ref(false)
const showLinkMaterialDialog = ref(false)

const newMaterial = ref({
  name: '',
  total_quantity: 1,
  storage_location: '',
  person_in_charge: null,
  notes: ''
})

const editingMaterial = ref(null)

const newBorrowing = ref({
  material_id: null,
  borrower_name: '',
  borrowed_quantity: 1,
  purpose: '',
  expected_return_time: ''
})

const returningBorrowing = ref(null)
const returnData = ref({
  returned_quantity: 0,
  abnormal_note: ''
})

const selectedBorrowing = ref(null)

const linkForm = ref({
  type: 'task',
  material_id: null,
  target_id: null,
  quantity_needed: 1,
  notes: ''
})

const filteredBorrowings = computed(() => {
  let result = borrowings.value
  if (activeBorrowingTab.value !== 'all') {
    result = result.filter(b => b.status === activeBorrowingTab.value)
  }
  if (filterMaterialId.value) {
    result = result.filter(b => b.material_id === filterMaterialId.value)
  }
  return result
})

const getBorrowingStatusText = (status) => {
  const map = { borrowed: '借用中', overdue: '逾期未还', returned: '已归还' }
  return map[status] || status
}

const getBorrowingStatusType = (status) => {
  const map = { borrowed: 'primary', overdue: 'danger', returned: 'success' }
  return map[status] || 'info'
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return dateStr.replace('T', ' ').substring(0, 16)
}

const formatOverdueDuration = (minutes) => {
  if (minutes < 60) return `${minutes}分钟`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours < 24) return `${hours}小时${mins > 0 ? mins + '分钟' : ''}`
  const days = Math.floor(hours / 24)
  const remainHours = hours % 24
  return `${days}天${remainHours > 0 ? remainHours + '小时' : ''}`
}

const loadMaterials = async () => {
  try {
    const res = await getMaterials(WEDDING_ID)
    materials.value = res || []
  } catch (e) {
    console.error('加载物资列表失败', e)
  }
}

const loadSummary = async () => {
  try {
    const res = await getMaterialSummary(WEDDING_ID)
    summary.value = res || {}
  } catch (e) {
    console.error('加载物资汇总失败', e)
  }
}

const loadBorrowings = async () => {
  loadingBorrowings.value = true
  try {
    const params = { wedding_id: WEDDING_ID }
    if (activeBorrowingTab.value !== 'all') {
      params.status = activeBorrowingTab.value
    }
    const res = await getBorrowings(params)
    borrowings.value = res || []
  } catch (e) {
    console.error('加载借还记录失败', e)
  } finally {
    loadingBorrowings.value = false
  }
}

const loadBridesmaids = async () => {
  try {
    const res = await getBridesmaids({ wedding_id: WEDDING_ID })
    bridesmaids.value = res || []
  } catch (e) {
    console.error('加载伴娘列表失败', e)
  }
}

const loadTasks = async () => {
  try {
    const res = await getTasks({ wedding_id: WEDDING_ID })
    tasks.value = res || []
  } catch (e) {
    console.error('加载任务列表失败', e)
  }
}

const loadTimelineNodes = async () => {
  try {
    const res = await getTimeline({ wedding_id: WEDDING_ID })
    timelineNodes.value = res || []
  } catch (e) {
    console.error('加载流程节点失败', e)
  }
}

const loadOverdueAlerts = async () => {
  try {
    const res = await getOverdueAlerts(WEDDING_ID)
    overdueAlerts.value = res || []
  } catch (e) {
    console.error('加载逾期提醒失败', e)
  }
}

const loadAbnormalReturns = async () => {
  try {
    const res = await getAbnormalReturns(WEDDING_ID)
    abnormalReturns.value = res || []
  } catch (e) {
    console.error('加载异常归还记录失败', e)
  }
}

const handleCreateMaterial = async () => {
  if (!newMaterial.value.name) {
    ElMessage.warning('请输入物资名称')
    return
  }
  try {
    const data = {
      wedding_id: WEDDING_ID,
      ...newMaterial.value
    }
    await createMaterial(data)
    ElMessage.success('物资创建成功')
    showAddMaterialDialog.value = false
    newMaterial.value = { name: '', total_quantity: 1, storage_location: '', person_in_charge: null, notes: '' }
    await Promise.all([loadMaterials(), loadSummary()])
  } catch (e) {
    ElMessage.error('创建失败')
  }
}

const editMaterial = (item) => {
  editingMaterial.value = { ...item }
  showEditMaterialDialog.value = true
}

const handleUpdateMaterial = async () => {
  if (!editingMaterial.value.name) {
    ElMessage.warning('请输入物资名称')
    return
  }
  try {
    await updateMaterial(editingMaterial.value.id, editingMaterial.value)
    ElMessage.success('更新成功')
    showEditMaterialDialog.value = false
    await Promise.all([loadMaterials(), loadSummary()])
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

const handleDeleteMaterial = async (item) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除物资"${item.name}"吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await deleteMaterial(item.id)
    ElMessage.success('删除成功')
    await Promise.all([loadMaterials(), loadSummary()])
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e?.response?.data?.error || '删除失败')
    }
  }
}

const filterBorrowings = (materialId) => {
  filterMaterialId.value = filterMaterialId.value === materialId ? null : materialId
}

const handleCreateBorrowing = async () => {
  if (!newBorrowing.value.material_id || !newBorrowing.value.borrower_name || !newBorrowing.value.borrowed_quantity) {
    ElMessage.warning('请填写必填项')
    return
  }
  try {
    await createBorrowing(newBorrowing.value)
    ElMessage.success('借用登记成功')
    showBorrowDialog.value = false
    newBorrowing.value = { material_id: null, borrower_name: '', borrowed_quantity: 1, purpose: '', expected_return_time: '' }
    await Promise.all([loadMaterials(), loadBorrowings(), loadSummary(), loadOverdueAlerts()])
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || '借用登记失败')
  }
}

const openReturnDialog = (borrowing) => {
  returningBorrowing.value = borrowing
  returnData.value = {
    returned_quantity: borrowing.borrowed_quantity,
    abnormal_note: ''
  }
  showReturnDialog.value = true
}

const openReturnFromAlert = (alert) => {
  const borrowing = borrowings.value.find(b => b.id === alert.borrowing_id)
  if (borrowing) {
    openReturnDialog(borrowing)
  } else {
    ElMessage.info('请在借还记录中找到该记录进行归还操作')
  }
}

const handleReturn = async () => {
  try {
    await returnBorrowing(returningBorrowing.value.id, returnData.value)
    ElMessage.success('归还成功')
    showReturnDialog.value = false
    await Promise.all([loadMaterials(), loadBorrowings(), loadSummary(), loadOverdueAlerts(), loadAbnormalReturns()])
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || '归还失败')
  }
}

const viewBorrowingDetail = (borrowing) => {
  selectedBorrowing.value = borrowing
  showBorrowingDetailDialog.value = true
}

const handleLinkMaterial = async () => {
  if (!linkForm.value.material_id || !linkForm.value.target_id) {
    ElMessage.warning('请选择物资和关联对象')
    return
  }
  try {
    const payload = {
      material_id: linkForm.value.material_id,
      quantity_needed: linkForm.value.quantity_needed,
      notes: linkForm.value.notes
    }
    if (linkForm.value.type === 'task') {
      payload.task_id = linkForm.value.target_id
      await linkTaskMaterial(payload)
    } else {
      payload.timeline_node_id = linkForm.value.target_id
      await linkTimelineMaterial(payload)
    }
    ElMessage.success('关联成功')
    showLinkMaterialDialog.value = false
    linkForm.value = { type: 'task', material_id: null, target_id: null, quantity_needed: 1, notes: '' }
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || '关联失败')
  }
}

watch(() => newBorrowing.value.material_id, (newVal) => {
  if (newVal) {
    const mat = materials.value.find(m => m.id === newVal)
    if (mat && newBorrowing.value.borrowed_quantity > mat.available_quantity) {
      newBorrowing.value.borrowed_quantity = mat.available_quantity
    }
  }
})

onMounted(() => {
  loadMaterials()
  loadSummary()
  loadBorrowings()
  loadBridesmaids()
  loadTasks()
  loadTimelineNodes()
  loadOverdueAlerts()
  loadAbnormalReturns()
})
</script>

<style scoped>
.material-page {
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.material-overview {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

.stat-icon {
  font-size: 28px;
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 12px;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.text-danger {
  color: #f56c6c;
}

.stat-card.total .stat-icon { background: #ecf5ff; }
.stat-card.total .stat-value { color: #409eff; }
.stat-card.quantity .stat-icon { background: #f0f9eb; }
.stat-card.quantity .stat-value { color: #67c23a; }
.stat-card.borrowed .stat-icon { background: #fdf6ec; }
.stat-card.borrowed .stat-value { color: #e6a23c; }
.stat-card.available .stat-icon { background: #f0f0ff; }
.stat-card.available .stat-value { color: #9093ff; }
.stat-card.overdue .stat-icon { background: #fef0f0; }
.stat-card.overdue .stat-value { color: #f56c6c; }
.stat-card.abnormal .stat-icon { background: #fef0f0; }
.stat-card.abnormal .stat-value { color: #f56c6c; }

.overdue-alert-section {
  margin-bottom: 24px;
}

.overdue-alert-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.overdue-alert-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: #fff5f5;
  border-radius: 10px;
  border-left: 4px solid #f56c6c;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.1);
}

.alert-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-main {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.alert-material {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.alert-borrower {
  color: #606266;
  font-size: 13px;
}

.alert-quantity {
  color: #909399;
  font-size: 12px;
}

.alert-detail {
  font-size: 12px;
  color: #909399;
}

.overdue-duration {
  color: #f56c6c;
  font-weight: 600;
  margin-left: 8px;
}

.abnormal-section {
  margin-bottom: 24px;
}

.content-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.material-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.material-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: all 0.3s;
  border: 2px solid transparent;
}

.material-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

.material-card.has-overdue {
  border-color: #f56c6c;
  background: #fff5f5;
}

.material-card.low-stock {
  border-color: #e6a23c;
}

.material-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.material-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.material-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.material-actions {
  display: flex;
  gap: 4px;
}

.quantity-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 12px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.quantity-item {
  text-align: center;
}

.quantity-label {
  display: block;
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.quantity-value {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.quantity-value.borrowed {
  color: #e6a23c;
}

.quantity-value.available {
  color: #67c23a;
}

.progress-section {
  margin-bottom: 12px;
}

.material-meta {
  margin-bottom: 12px;
  font-size: 13px;
  color: #606266;
}

.meta-item {
  margin-bottom: 4px;
}

.meta-label {
  color: #909399;
}

.material-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.borrowing-count {
  font-size: 12px;
  color: #909399;
}

.borrowings-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-tabs {
  display: flex;
  align-items: center;
}

.material-tag {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: #ecf5ff;
  color: #409eff;
}

.return-content {
  padding: 10px 0;
}

.return-info {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.return-info p {
  margin-bottom: 8px;
}

.return-info p:last-child {
  margin-bottom: 0;
}

.borrowing-detail {
  padding: 10px 0;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 12px;
}

.detail-label {
  color: #909399;
  font-size: 14px;
  min-width: 80px;
  flex-shrink: 0;
}
</style>
