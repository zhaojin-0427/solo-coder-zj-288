<template>
  <div class="guest-management">
    <div class="page-header">
      <h1 class="page-title">👥 宾客管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="openGuestDialog()">
          <el-icon><Plus /></el-icon>
          添加宾客
        </el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="main-tabs">
      <el-tab-pane label="宾客名单" name="guests">
        <div class="filter-bar">
          <div class="filter-left">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索姓名或手机号"
              clearable
              style="width: 240px"
              @input="loadGuests"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="filterGroup"
              placeholder="分组筛选"
              clearable
              style="width: 160px"
              @change="loadGuests"
            >
              <el-option
                v-for="group in guestGroups"
                :key="group.group_name"
                :label="group.group_name"
                :value="group.group_name"
              />
            </el-select>
            <el-select
              v-model="filterTable"
              placeholder="桌位筛选"
              clearable
              style="width: 160px"
              @change="loadGuests"
            >
              <el-option label="未分桌" :value="0" />
              <el-option
                v-for="table in tables"
                :key="table.id"
                :label="table.name"
                :value="table.id"
              />
            </el-select>
          </div>
          <div class="filter-right">
            <span class="total-text">共 {{ guests.length }} 位宾客</span>
          </div>
        </div>

        <div class="guest-list">
          <el-table :data="guests" stripe style="width: 100%">
            <el-table-column prop="name" label="姓名" width="120">
              <template #default="{ row }">
                <span class="guest-name">
                  <el-tag v-if="row.is_high_priority" type="danger" size="small" effect="light">
                    高优
                  </el-tag>
                  {{ row.name }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="phone" label="手机号" width="140" />
            <el-table-column prop="group_name" label="分组" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ row.group_name || '未分组' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="relation_tag" label="关系标签" width="120" />
            <el-table-column label="随行人数" width="100">
              <template #default="{ row }">
                {{ row.companion_count }} 人（共 {{ row.total_count }} 人）
              </template>
            </el-table-column>
            <el-table-column prop="table_name" label="桌位" width="120">
              <template #default="{ row }">
                <el-tag v-if="row.table_name" type="success" size="small">
                  {{ row.table_name }}
                </el-tag>
                <span v-else style="color: #909399">未分配</span>
              </template>
            </el-table-column>
            <el-table-column prop="checkin_status" label="签到状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.checkin_status)" size="small">
                  {{ getStatusText(row.checkin_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="special_notes" label="特殊备注" min-width="180" show-overflow-tooltip />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="openGuestDialog(row)">编辑</el-button>
                <el-button link type="success" size="small" @click="openAssignDialog(row)">分配桌位</el-button>
                <el-popconfirm title="确定删除此宾客吗？" @confirm="handleDelete(row)">
                  <template #reference>
                    <el-button link type="danger" size="small">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="桌位安排" name="tables">
        <div class="table-overview">
          <div class="stat-card">
            <div class="stat-icon">🪑</div>
            <div class="stat-content">
              <div class="stat-value">{{ tableOverview.total_tables || 0 }}</div>
              <div class="stat-label">总桌数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <div class="stat-value">{{ tableOverview.total_capacity || 0 }}</div>
              <div class="stat-label">总座位</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-content">
              <div class="stat-value">{{ tableOverview.total_assigned || 0 }}</div>
              <div class="stat-label">已分配</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
              <div class="stat-value">{{ tableOverview.overall_seating_rate || 0 }}%</div>
              <div class="stat-label">入座率</div>
            </div>
          </div>
          <div class="stat-card warning">
            <div class="stat-icon">⚠️</div>
            <div class="stat-content">
              <div class="stat-value">{{ tableOverview.over_capacity_count || 0 }}</div>
              <div class="stat-label">超员桌</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">❓</div>
            <div class="stat-content">
              <div class="stat-value">{{ tableOverview.unassigned_guests || 0 }}</div>
              <div class="stat-label">未分桌宾客</div>
            </div>
          </div>
        </div>

        <div class="table-actions">
          <el-button type="primary" @click="openTableDialog()">
            <el-icon><Plus /></el-icon>
            添加桌位
          </el-button>
          <el-button @click="openBatchCreateDialog()">
            批量创建桌位
          </el-button>
        </div>

        <div class="tables-grid">
          <div
            v-for="table in tables"
            :key="table.id"
            class="table-card"
            :class="{ 'over-capacity': table.is_over_capacity }"
          >
            <div class="table-card-header">
              <span class="table-name">{{ table.name }}</span>
              <el-tag v-if="table.table_type === 'vip'" type="danger" size="small">VIP</el-tag>
            </div>
            <div class="table-card-body">
              <div class="table-info-row">
                <span class="label">座位容量:</span>
                <span class="value">{{ table.capacity }} 人</span>
              </div>
              <div class="table-info-row">
                <span class="label">已分配:</span>
                <span class="value" :class="{ 'text-danger': table.is_over_capacity }">
                  {{ table.assigned_count }} 人
                </span>
              </div>
              <div class="table-info-row">
                <span class="label">空位:</span>
                <span class="value" :class="{ 'text-success': table.available_seats > 0 }">
                  {{ table.available_seats }} 个
                </span>
              </div>
              <div class="table-info-row">
                <span class="label">入座率:</span>
                <span class="value">{{ table.seating_rate }}%</span>
              </div>
              <el-progress
                :percentage="table.seating_rate"
                :stroke-width="6"
                :color="table.is_over_capacity ? '#f56c6c' : '#67c23a'"
              />
              <div class="table-location" v-if="table.location">
                📍 {{ table.location }}
              </div>
            </div>
            <div class="table-card-footer">
              <el-button size="small" @click="viewTableGuests(table)">查看宾客</el-button>
              <el-button size="small" type="primary" @click="openTableDialog(table)">编辑</el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="未分桌宾客" name="unassigned">
        <div class="unassigned-section">
          <div class="unassigned-header">
            <h3>未分配桌位的宾客 ({{ unassignedGuests.length }} 位)</h3>
            <el-button type="primary" :disabled="selectedGuests.length === 0" @click="openBatchAssignDialog">
              批量分配桌位
            </el-button>
          </div>
          <el-table :data="unassignedGuests" stripe @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="phone" label="手机号" width="140" />
            <el-table-column prop="group_name" label="分组" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ row.group_name || '未分组' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="relation_tag" label="关系标签" width="120" />
            <el-table-column label="人数" width="100">
              <template #default="{ row }">
                {{ row.total_count }} 人
              </template>
            </el-table-column>
            <el-table-column prop="special_notes" label="特殊备注" min-width="180" show-overflow-tooltip />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="openAssignDialog(row)">
                  分配桌位
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog
      v-model="guestDialogVisible"
      :title="editingGuest ? '编辑宾客' : '添加宾客'"
      width="500px"
    >
      <el-form :model="guestForm" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="guestForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="guestForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="分组">
          <el-input v-model="guestForm.group_name" placeholder="如：新娘家人、新郎同事" />
        </el-form-item>
        <el-form-item label="关系标签">
          <el-input v-model="guestForm.relation_tag" placeholder="如：父亲、闺蜜、同事" />
        </el-form-item>
        <el-form-item label="随行人数">
          <el-input-number v-model="guestForm.companion_count" :min="0" :max="20" />
          <span style="margin-left: 10px; color: #909399;">
            共 {{ (guestForm.companion_count || 0) + 1 }} 人
          </span>
        </el-form-item>
        <el-form-item label="分配桌位">
          <el-select v-model="guestForm.table_id" placeholder="请选择桌位" clearable style="width: 100%">
            <el-option
              v-for="table in tables"
              :key="table.id"
              :label="`${table.name} (剩余${table.available_seats}座)`"
              :value="table.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="特殊备注">
          <el-input
            v-model="guestForm.special_notes"
            type="textarea"
            :rows="3"
            placeholder="如：素食、过敏、老人优先引导等"
          />
        </el-form-item>
        <el-form-item label="高关注宾客">
          <el-switch v-model="guestForm.is_high_priority" />
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">
            重要宾客，签到时优先提醒
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="guestDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveGuest">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="tableDialogVisible"
      :title="editingTable ? '编辑桌位' : '添加桌位'"
      width="500px"
    >
      <el-form :model="tableForm" label-width="100px">
        <el-form-item label="桌位名称">
          <el-input v-model="tableForm.name" placeholder="如：第1桌、主桌" />
        </el-form-item>
        <el-form-item label="座位容量">
          <el-input-number v-model="tableForm.capacity" :min="1" :max="30" />
        </el-form-item>
        <el-form-item label="桌位类型">
          <el-select v-model="tableForm.table_type" style="width: 100%">
            <el-option label="普通桌" value="normal" />
            <el-option label="VIP桌" value="vip" />
            <el-option label="儿童桌" value="kids" />
          </el-select>
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="tableForm.location" placeholder="如：宴会厅左侧前排" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="tableForm.notes"
            type="textarea"
            :rows="2"
            placeholder="桌位备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tableDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTable">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="assignDialogVisible" title="分配桌位" width="400px">
      <div class="assign-info">
        <p>宾客: <strong>{{ assigningGuest?.name }}</strong></p>
        <p>人数: <strong>{{ assigningGuest?.total_count }} 人</strong></p>
      </div>
      <el-select v-model="selectedTableId" placeholder="请选择桌位" style="width: 100%">
        <el-option
          v-for="table in tables"
          :key="table.id"
          :label="`${table.name} (已坐${table.assigned_count}/${table.capacity}人)`"
          :value="table.id"
        />
      </el-select>
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAssign">确认分配</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="batchCreateDialogVisible" title="批量创建桌位" width="400px">
      <el-form :model="batchForm" label-width="100px">
        <el-form-item label="起始桌号">
          <el-input-number v-model="batchForm.start_num" :min="1" />
        </el-form-item>
        <el-form-item label="创建数量">
          <el-input-number v-model="batchForm.count" :min="1" :max="50" />
        </el-form-item>
        <el-form-item label="每桌容量">
          <el-input-number v-model="batchForm.capacity" :min="1" :max="30" />
        </el-form-item>
        <el-form-item label="命名前缀">
          <el-input v-model="batchForm.prefix" />
        </el-form-item>
        <el-form-item label="命名后缀">
          <el-input v-model="batchForm.suffix" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchCreateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBatchCreate">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="tableGuestsDialogVisible" title="桌位宾客" width="600px">
      <div class="table-guests-header">
        <h3>{{ currentTable?.name }} - 宾客列表</h3>
        <span>共 {{ currentTable?.guest_count }} 户，{{ currentTable?.assigned_count }} 人</span>
      </div>
      <el-table :data="currentTableGuests" stripe size="small">
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="relation_tag" label="关系" width="100" />
        <el-table-column label="人数" width="80">
          <template #default="{ row }">{{ row.total_count }}</template>
        </el-table-column>
        <el-table-column prop="special_notes" label="备注" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getGuests,
  createGuest,
  updateGuest,
  deleteGuest,
  getGuestGroups,
  getUnassignedTableGuests,
  assignTable
} from '@/api/guest'
import {
  getTables,
  getTable,
  createTable,
  updateTable,
  deleteTable,
  batchCreateTables,
  getTablesOverview
} from '@/api/table'

const WEDDING_ID = 1

const activeTab = ref('guests')
const searchKeyword = ref('')
const filterGroup = ref('')
const filterTable = ref(null)

const guests = ref([])
const guestGroups = ref([])
const tables = ref([])
const tableOverview = ref({})
const unassignedGuests = ref([])
const selectedGuests = ref([])

const guestDialogVisible = ref(false)
const editingGuest = ref(null)
const guestForm = ref({
  name: '',
  phone: '',
  group_name: '',
  relation_tag: '',
  companion_count: 0,
  table_id: null,
  special_notes: '',
  is_high_priority: false
})

const tableDialogVisible = ref(false)
const editingTable = ref(null)
const tableForm = ref({
  name: '',
  capacity: 10,
  table_type: 'normal',
  location: '',
  notes: ''
})

const assignDialogVisible = ref(false)
const assigningGuest = ref(null)
const selectedTableId = ref(null)

const batchCreateDialogVisible = ref(false)
const batchForm = ref({
  start_num: 1,
  count: 10,
  capacity: 10,
  prefix: '第',
  suffix: '桌'
})

const tableGuestsDialogVisible = ref(false)
const currentTable = ref(null)
const currentTableGuests = ref([])

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

const loadGuests = async () => {
  try {
    const params = { wedding_id: WEDDING_ID }
    if (searchKeyword.value) params.keyword = searchKeyword.value
    if (filterGroup.value) params.group_name = filterGroup.value
    if (filterTable.value !== null && filterTable.value !== '') params.table_id = filterTable.value
    
    const res = await getGuests(params)
    guests.value = res || []
  } catch (e) {
    console.error('加载宾客列表失败', e)
  }
}

const loadGuestGroups = async () => {
  try {
    const res = await getGuestGroups({ wedding_id: WEDDING_ID })
    guestGroups.value = res || []
  } catch (e) {
    console.error('加载分组失败', e)
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

const loadTableOverview = async () => {
  try {
    const res = await getTablesOverview({ wedding_id: WEDDING_ID })
    tableOverview.value = res || {}
  } catch (e) {
    console.error('加载桌位概览失败', e)
  }
}

const loadUnassignedGuests = async () => {
  try {
    const res = await getUnassignedTableGuests({ wedding_id: WEDDING_ID })
    unassignedGuests.value = res || []
  } catch (e) {
    console.error('加载未分桌宾客失败', e)
  }
}

const openGuestDialog = (guest = null) => {
  editingGuest.value = guest
  if (guest) {
    guestForm.value = { ...guest }
  } else {
    guestForm.value = {
      name: '',
      phone: '',
      group_name: '',
      relation_tag: '',
      companion_count: 0,
      table_id: null,
      special_notes: '',
      is_high_priority: false
    }
  }
  guestDialogVisible.value = true
}

const saveGuest = async () => {
  try {
    if (editingGuest.value) {
      await updateGuest(editingGuest.value.id, guestForm.value)
      ElMessage.success('宾客信息已更新')
    } else {
      await createGuest({ ...guestForm.value, wedding_id: WEDDING_ID })
      ElMessage.success('宾客添加成功')
    }
    guestDialogVisible.value = false
    loadGuests()
    loadGuestGroups()
    loadUnassignedGuests()
    loadTables()
    loadTableOverview()
  } catch (e) {
    ElMessage.error('保存失败')
    console.error(e)
  }
}

const handleDelete = async (guest) => {
  try {
    await deleteGuest(guest.id)
    ElMessage.success('宾客已删除')
    loadGuests()
    loadGuestGroups()
    loadUnassignedGuests()
    loadTables()
    loadTableOverview()
  } catch (e) {
    ElMessage.error('删除失败')
    console.error(e)
  }
}

const openTableDialog = (table = null) => {
  editingTable.value = table
  if (table) {
    tableForm.value = { ...table }
  } else {
    tableForm.value = {
      name: '',
      capacity: 10,
      table_type: 'normal',
      location: '',
      notes: ''
    }
  }
  tableDialogVisible.value = true
}

const saveTable = async () => {
  try {
    if (editingTable.value) {
      await updateTable(editingTable.value.id, tableForm.value)
      ElMessage.success('桌位信息已更新')
    } else {
      await createTable({ ...tableForm.value, wedding_id: WEDDING_ID })
      ElMessage.success('桌位添加成功')
    }
    tableDialogVisible.value = false
    loadTables()
    loadTableOverview()
    loadGuests()
  } catch (e) {
    ElMessage.error('保存失败')
    console.error(e)
  }
}

const openAssignDialog = (guest) => {
  assigningGuest.value = guest
  selectedTableId.value = guest.table_id
  assignDialogVisible.value = true
}

const confirmAssign = async () => {
  try {
    await assignTable({
      guest_ids: [assigningGuest.value.id],
      table_id: selectedTableId.value || null
    })
    ElMessage.success('桌位已分配')
    assignDialogVisible.value = false
    loadGuests()
    loadTables()
    loadTableOverview()
    loadUnassignedGuests()
  } catch (e) {
    ElMessage.error('分配失败')
    console.error(e)
  }
}

const handleSelectionChange = (selection) => {
  selectedGuests.value = selection
}

const openBatchAssignDialog = () => {
  if (selectedGuests.value.length === 0) return
  assigningGuest.value = { name: `已选 ${selectedGuests.value.length} 位宾客`, total_count: '批量' }
  selectedTableId.value = null
  assignDialogVisible.value = true
}

const openBatchCreateDialog = () => {
  batchForm.value = {
    start_num: 1,
    count: 10,
    capacity: 10,
    prefix: '第',
    suffix: '桌'
  }
  batchCreateDialogVisible.value = true
}

const confirmBatchCreate = async () => {
  try {
    await batchCreateTables({
      wedding_id: WEDDING_ID,
      ...batchForm.value
    })
    ElMessage.success(`成功创建 ${batchForm.value.count} 个桌位`)
    batchCreateDialogVisible.value = false
    loadTables()
    loadTableOverview()
  } catch (e) {
    ElMessage.error('创建失败')
    console.error(e)
  }
}

const viewTableGuests = async (table) => {
  try {
    const res = await getTable(table.id)
    currentTable.value = res
    currentTableGuests.value = res.guests || []
    tableGuestsDialogVisible.value = true
  } catch (e) {
    console.error('加载桌位宾客失败', e)
  }
}

onMounted(() => {
  loadGuests()
  loadGuestGroups()
  loadTables()
  loadTableOverview()
  loadUnassignedGuests()
})
</script>

<style scoped>
.guest-management {
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

.main-tabs {
  background: white;
  border-radius: 12px;
  padding: 0 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 0;
}

.filter-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-right .total-text {
  color: #909399;
  font-size: 14px;
}

.guest-list {
  margin-bottom: 20px;
}

.guest-name {
  display: flex;
  align-items: center;
  gap: 6px;
}

.table-overview {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.stat-card.warning .stat-value {
  color: #e6a23c;
}

.stat-icon {
  font-size: 28px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 10px;
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
  margin-top: 2px;
}

.table-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.tables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.table-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s;
  border: 1px solid #ebeef5;
}

.table-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

.table-card.over-capacity {
  border-color: #f56c6c;
  background: #fef0f0;
}

.table-card-header {
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-card.over-capacity .table-card-header {
  background: linear-gradient(135deg, #f56c6c 0%, #e74c3c 100%);
}

.table-name {
  font-size: 16px;
  font-weight: 600;
}

.table-card-body {
  padding: 16px;
}

.table-info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.table-info-row .label {
  color: #909399;
}

.table-info-row .value {
  color: #303133;
  font-weight: 500;
}

.text-danger {
  color: #f56c6c !important;
}

.text-success {
  color: #67c23a !important;
}

.table-location {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

.table-card-footer {
  padding: 12px 16px;
  border-top: 1px solid #ebeef5;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.unassigned-section {
  padding: 10px 0;
}

.unassigned-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.unassigned-header h3 {
  font-size: 16px;
  color: #303133;
}

.assign-info {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.assign-info p {
  margin: 4px 0;
  color: #606266;
}

.table-guests-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-guests-header h3 {
  font-size: 16px;
  color: #303133;
}
</style>
