<template>
  <div class="stats-page">
    <div class="page-header">
      <h1 class="page-title">📊 数据统计</h1>
    </div>

    <div class="stats-overview">
      <div class="stat-card total">
        <div class="stat-icon">📋</div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.total_tasks || 0 }}</div>
          <div class="stat-label">总任务数</div>
        </div>
      </div>
      <div class="stat-card completed">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.completed_tasks || 0 }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>
      <div class="stat-card rate">
        <div class="stat-icon">📈</div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.completion_rate || 0 }}%</div>
          <div class="stat-label">总完成率</div>
        </div>
      </div>
      <div class="stat-card adjust">
        <div class="stat-icon">🔄</div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.total_adjustments || 0 }}</div>
          <div class="stat-label">调整次数</div>
        </div>
      </div>
      <div class="stat-card overdue">
        <div class="stat-icon">⏰</div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.overdue_tasks || 0 }}</div>
          <div class="stat-label">逾期任务</div>
        </div>
      </div>
      <div class="stat-card bridesmaid">
        <div class="stat-icon">👭</div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.bridesmaids_count || 0 }}</div>
          <div class="stat-label">伴娘人数</div>
        </div>
      </div>
      <div class="stat-card high-risk">
        <div class="stat-icon">🚨</div>
        <div class="stat-content">
          <div class="stat-value">{{ riskData.high_risk_count }}</div>
          <div class="stat-label">高风险订单</div>
        </div>
      </div>
      <div class="stat-card risk-level">
        <div class="stat-icon">⚡</div>
        <div class="stat-content">
          <div class="stat-value" style="display: flex; gap: 6px; font-size: 16px;">
            <el-tag type="danger" size="small">{{ riskData.risk_distribution.high }}</el-tag>
            <el-tag type="warning" size="small">{{ riskData.risk_distribution.medium }}</el-tag>
            <el-tag type="success" size="small">{{ riskData.risk_distribution.low }}</el-tag>
          </div>
          <div class="stat-label">风险分布(高/中/低)</div>
        </div>
      </div>
      <div class="stat-card budget-total">
        <div class="stat-icon">💵</div>
        <div class="stat-content">
          <div class="stat-value">¥{{ budgetStats.total_budget?.toLocaleString() || 0 }}</div>
          <div class="stat-label">总预算</div>
        </div>
      </div>
      <div class="stat-card budget-used">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-value">¥{{ budgetStats.total_approved?.toLocaleString() || 0 }}</div>
          <div class="stat-label">已报销</div>
        </div>
      </div>
      <div class="stat-card budget-usage">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ budgetStats.overall_usage_rate || 0 }}%</div>
          <div class="stat-label">预算使用率</div>
        </div>
      </div>
      <div class="stat-card budget-over">
        <div class="stat-icon">⚠️</div>
        <div class="stat-content">
          <div class="stat-value" :class="{ 'text-danger': budgetStats.over_budget_count > 0 }">
            {{ budgetStats.over_budget_count || 0 }}
          </div>
          <div class="stat-label">超支分类</div>
        </div>
      </div>
      <div class="stat-card budget-pending">
        <div class="stat-icon">⏳</div>
        <div class="stat-content">
          <div class="stat-value" style="color: #e6a23c;">{{ budgetStats.pending_expense_count || 0 }}</div>
          <div class="stat-label">待审核报销</div>
        </div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3 class="chart-title">📊 各伴娘工作量分布</h3>
        <div ref="workloadChartRef" class="chart-container"></div>
      </div>
      <div class="chart-card">
        <h3 class="chart-title">📈 任务类别分布</h3>
        <div ref="categoryChartRef" class="chart-container"></div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3 class="chart-title">👭 伴娘完成率排行</h3>
        <div class="ranking-list">
          <div
            v-for="(item, index) in workloadData"
            :key="item.bridesmaid_id"
            class="ranking-item"
          >
            <div class="rank-num" :class="`rank-${index + 1}`">
              {{ index + 1 }}
            </div>
            <div class="rank-avatar">👩</div>
            <div class="rank-info">
              <div class="rank-name">
                {{ item.name }}
                <span v-if="item.role === 'leader'" class="leader-badge">团长</span>
              </div>
              <div class="rank-progress">
                <el-progress :percentage="item.completion_rate" :stroke-width="8" />
              </div>
            </div>
            <div class="rank-stats">
              <div class="stat-num">{{ item.completed_tasks }}/{{ item.total_tasks }}</div>
              <div class="stat-label">完成/总数</div>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <h3 class="chart-title">⏰ 逾期任务提醒</h3>
        <div class="overdue-list">
          <div
            v-for="task in overdueTasks"
            :key="task.id"
            class="overdue-item"
          >
            <div class="overdue-icon">⚠️</div>
            <div class="overdue-info">
              <div class="overdue-title">{{ task.title }}</div>
              <div class="overdue-meta">
                <span class="category-tag">{{ getCategoryName(task.category) }}</span>
                <span class="assignee">👤 {{ task.assigned_name || '未分配' }}</span>
              </div>
              <div class="overdue-date">
                截止日期：{{ task.due_date }}
              </div>
            </div>
            <el-button size="small" type="primary" @click="handleTask(task)">
              处理
            </el-button>
          </div>
          <div v-if="overdueTasks.length === 0" class="empty-state">
            <div class="empty-icon">🎉</div>
            <div class="empty-text">太棒了！暂无逾期任务</div>
          </div>
        </div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3 class="chart-title">🚨 风险分布统计</h3>
        <div ref="riskChartRef" class="chart-container"></div>
      </div>
      <div class="chart-card">
        <h3 class="chart-title">⚡ 风险因素分析</h3>
        <div class="risk-breakdown-list">
          <div class="risk-breakdown-item">
            <div class="breakdown-icon">📅</div>
            <div class="breakdown-info">
              <div class="breakdown-name">交付日期临近</div>
              <el-progress :percentage="getBreakdownPercent('delivery_date_risk')" :stroke-width="10" color="#f56c6c" />
            </div>
            <div class="breakdown-count">{{ riskData.risk_breakdown.delivery_date_risk }}</div>
          </div>
          <div class="risk-breakdown-item">
            <div class="breakdown-icon">⚠️</div>
            <div class="breakdown-info">
              <div class="breakdown-name">关键任务逾期</div>
              <el-progress :percentage="getBreakdownPercent('task_overdue_risk')" :stroke-width="10" color="#e6a23c" />
            </div>
            <div class="breakdown-count">{{ riskData.risk_breakdown.task_overdue_risk }}</div>
          </div>
          <div class="risk-breakdown-item">
            <div class="breakdown-icon">📊</div>
            <div class="breakdown-info">
              <div class="breakdown-name">完成进度落后</div>
              <el-progress :percentage="getBreakdownPercent('progress_behind_risk')" :stroke-width="10" color="#409eff" />
            </div>
            <div class="breakdown-count">{{ riskData.risk_breakdown.progress_behind_risk }}</div>
          </div>
          <div class="risk-breakdown-item">
            <div class="breakdown-icon">📦</div>
            <div class="breakdown-info">
              <div class="breakdown-name">材料库存不足</div>
              <el-progress :percentage="getBreakdownPercent('material_shortage_risk')" :stroke-width="10" color="#909399" />
            </div>
            <div class="breakdown-count">{{ riskData.risk_breakdown.material_shortage_risk }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="adjustment-history">
      <h3 class="chart-title">📝 任务调整记录</h3>
      <el-table :data="adjustmentHistory" stripe style="width: 100%;">
        <el-table-column prop="task_title" label="任务名称" min-width="180" />
        <el-table-column label="调整前" width="150">
          <template #default="{ row }">
            <span v-if="row.previous_assignee_name">{{ row.previous_assignee_name }}</span>
            <span v-else style="color: #909399;">未分配</span>
          </template>
        </el-table-column>
        <el-table-column label="调整后" width="150">
          <template #default="{ row }">
            <span v-if="row.new_assignee_name">{{ row.new_assignee_name }}</span>
            <span v-else style="color: #909399;">未分配</span>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="调整原因" min-width="200" />
        <el-table-column label="调整时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.adjusted_at) }}
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3 class="chart-title">💰 费用占比分布</h3>
        <div ref="expenseChartRef" class="chart-container"></div>
      </div>
      <div class="chart-card">
        <h3 class="chart-title">📊 预算使用率排行</h3>
        <div ref="budgetUsageChartRef" class="chart-container"></div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3 class="chart-title">📦 物资统计概览</h3>
        <div class="material-stats-grid">
          <div class="material-stat-item">
            <div class="material-stat-icon">📦</div>
            <div class="material-stat-info">
              <div class="material-stat-value">{{ materialStats.total_items }}</div>
              <div class="material-stat-label">物资种类</div>
            </div>
          </div>
          <div class="material-stat-item">
            <div class="material-stat-icon">🔢</div>
            <div class="material-stat-info">
              <div class="material-stat-value">{{ materialStats.total_quantity }}</div>
              <div class="material-stat-label">库存总量</div>
            </div>
          </div>
          <div class="material-stat-item">
            <div class="material-stat-icon">📤</div>
            <div class="material-stat-info">
              <div class="material-stat-value" style="color: #e6a23c;">{{ materialStats.total_borrowed }}</div>
              <div class="material-stat-label">已借出</div>
            </div>
          </div>
          <div class="material-stat-item">
            <div class="material-stat-icon">📥</div>
            <div class="material-stat-info">
              <div class="material-stat-value" style="color: #67c23a;">{{ materialStats.total_available }}</div>
              <div class="material-stat-label">可用数量</div>
            </div>
          </div>
          <div class="material-stat-item">
            <div class="material-stat-icon">📊</div>
            <div class="material-stat-info">
              <div class="material-stat-value" style="color: #409eff;">{{ materialStats.usage_rate }}%</div>
              <div class="material-stat-label">使用率</div>
            </div>
          </div>
          <div class="material-stat-item">
            <div class="material-stat-icon">⚠️</div>
            <div class="material-stat-info">
              <div class="material-stat-value" :class="{ 'text-danger': materialStats.overdue_count > 0 }">{{ materialStats.overdue_count }}</div>
              <div class="material-stat-label">逾期未还</div>
            </div>
          </div>
          <div class="material-stat-item">
            <div class="material-stat-icon">🔴</div>
            <div class="material-stat-info">
              <div class="material-stat-value" :class="{ 'text-danger': materialStats.abnormal_count > 0 }">{{ materialStats.abnormal_count }}</div>
              <div class="material-stat-label">异常归还</div>
            </div>
          </div>
        </div>
      </div>
      <div class="chart-card">
        <h3 class="chart-title">🏆 高频借用物资排行</h3>
        <div class="top-borrowed-list">
          <div
            v-for="(item, index) in materialStats.top_borrowed"
            :key="item.name"
            class="top-borrowed-item"
          >
            <div class="borrowed-rank" :class="`rank-${index + 1}`">
              {{ index + 1 }}
            </div>
            <div class="borrowed-info">
              <div class="borrowed-name">{{ item.name }}</div>
              <el-progress :percentage="getTopBorrowedPercent(index)" :stroke-width="8" color="#409eff" />
            </div>
            <div class="borrowed-count">{{ item.count }}次</div>
          </div>
          <div v-if="materialStats.top_borrowed.length === 0" class="empty-state">
            <div class="empty-icon">📦</div>
            <div class="empty-text">暂无借用记录</div>
          </div>
        </div>
      </div>
    </div>

    <div class="guest-stats-section">
      <h3 class="section-title-big">👥 宾客签到统计</h3>
      
      <div class="stats-overview">
        <div class="stat-card guest-total">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <div class="stat-value">{{ guestStats.total_guests || 0 }}</div>
            <div class="stat-label">宾客总数</div>
          </div>
        </div>
        <div class="stat-card guest-expected">
          <div class="stat-icon">👨‍👩‍👧</div>
          <div class="stat-content">
            <div class="stat-value">{{ guestStats.total_expected || 0 }}</div>
            <div class="stat-label">预计人数</div>
          </div>
        </div>
        <div class="stat-card guest-arrived">
          <div class="stat-icon">✅</div>
          <div class="stat-content">
            <div class="stat-value">{{ guestStats.total_arrived || 0 }}</div>
            <div class="stat-label">已到人数</div>
          </div>
        </div>
        <div class="stat-card guest-rate">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <div class="stat-value">{{ guestStats.arrival_rate || 0 }}%</div>
            <div class="stat-label">到场率</div>
          </div>
        </div>
        <div class="stat-card guest-checkin">
          <div class="stat-icon">✍️</div>
          <div class="stat-content">
            <div class="stat-value">{{ guestStats.checkin_rate || 0 }}%</div>
            <div class="stat-label">签到率</div>
          </div>
        </div>
        <div class="stat-card guest-pending">
          <div class="stat-icon">⏳</div>
          <div class="stat-content">
            <div class="stat-value">{{ guestStats.pending_count || 0 }}</div>
            <div class="stat-label">待签到</div>
          </div>
        </div>
        <div class="stat-card guest-late">
          <div class="stat-icon">⏰</div>
          <div class="stat-content">
            <div class="stat-value" style="color: #e6a23c;">{{ guestStats.late_count || 0 }}</div>
            <div class="stat-label">迟到</div>
          </div>
        </div>
        <div class="stat-card guest-absent">
          <div class="stat-icon">❌</div>
          <div class="stat-content">
            <div class="stat-value" style="color: #f56c6c;">{{ guestStats.absent_count || 0 }}</div>
            <div class="stat-label">未到</div>
          </div>
        </div>
        <div class="stat-card guest-temp-add">
          <div class="stat-icon">➕</div>
          <div class="stat-content">
            <div class="stat-value" style="color: #67c23a;">+{{ guestStats.temp_added || 0 }}</div>
            <div class="stat-label">临时增加</div>
          </div>
        </div>
        <div class="stat-card guest-temp-reduce">
          <div class="stat-icon">➖</div>
          <div class="stat-content">
            <div class="stat-value" style="color: #e6a23c;">-{{ guestStats.temp_reduced || 0 }}</div>
            <div class="stat-label">临时减少</div>
          </div>
        </div>
        <div class="stat-card guest-high">
          <div class="stat-icon">⭐</div>
          <div class="stat-content">
            <div class="stat-value" style="color: #f56c6c;">{{ guestStats.high_priority_total || 0 }}</div>
            <div class="stat-label">高关注宾客</div>
          </div>
        </div>
        <div class="stat-card guest-unassigned">
          <div class="stat-icon">🪑</div>
          <div class="stat-content">
            <div class="stat-value">{{ guestStats.unassigned_guest_count || 0 }}</div>
            <div class="stat-label">未分桌</div>
          </div>
        </div>
      </div>

      <div class="charts-row">
        <div class="chart-card">
          <h3 class="chart-title">📊 签到状态分布</h3>
          <div ref="checkinChartRef" class="chart-container"></div>
        </div>
        <div class="chart-card">
          <h3 class="chart-title">🪑 各桌入座情况</h3>
          <div ref="seatingChartRef" class="chart-container"></div>
        </div>
      </div>

      <div class="charts-row">
        <div class="chart-card">
          <h3 class="chart-title">👨‍👩‍👧‍👦 各分组人数统计</h3>
          <div class="group-stats-list">
            <div
              v-for="group in guestStats.group_stats"
              :key="group.group_name"
              class="group-stat-item"
            >
              <div class="group-name">{{ group.group_name }}</div>
              <div class="group-info">
                <span class="group-count">{{ group.guest_count }} 户 / {{ group.total_people }} 人</span>
              </div>
              <el-progress 
                :percentage="Math.round(group.total_people / (guestStats.total_expected || 1) * 100)" 
                :stroke-width="8" 
              />
            </div>
            <div v-if="guestStats.group_stats?.length === 0" class="empty-state">
              <div class="empty-icon">📊</div>
              <div class="empty-text">暂无分组数据</div>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <h3 class="chart-title">⭐ 高关注宾客提醒</h3>
          <div class="high-priority-list">
            <div
              v-for="guest in guestStats.high_priority_guests"
              :key="guest.id"
              class="high-priority-item"
              :class="{ 'arrived': guest.checkin_status === 'checked_in' || guest.checkin_status === 'late' }"
            >
              <div class="hp-icon">⭐</div>
              <div class="hp-info">
                <div class="hp-name">
                  {{ guest.name }}
                  <el-tag size="small" :type="guest.checkin_status === 'checked_in' || guest.checkin_status === 'late' ? 'success' : 'warning'">
                    {{ getCheckinStatusText(guest.checkin_status) }}
                  </el-tag>
                </div>
                <div class="hp-meta">
                  <span>{{ guest.relation_tag || '-' }}</span>
                  <span>·</span>
                  <span>{{ guest.group_name || '未分组' }}</span>
                </div>
                <div class="hp-notes" v-if="guest.special_notes">
                  📝 {{ guest.special_notes }}
                </div>
              </div>
            </div>
            <div v-if="guestStats.high_priority_guests?.length === 0" class="empty-state">
              <div class="empty-icon">⭐</div>
              <div class="empty-text">暂无高关注宾客</div>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <h3 class="chart-title">📋 桌位入座详情</h3>
        <el-table :data="guestStats.table_stats" stripe style="width: 100%;">
          <el-table-column prop="table_name" label="桌位名称" width="120" />
          <el-table-column prop="capacity" label="容量" width="80" align="center" />
          <el-table-column prop="guest_count" label="户数" width="80" align="center" />
          <el-table-column label="已分配人数" width="100" align="center">
            <template #default="{ row }">
              <span :class="{ 'text-danger': row.is_over_capacity }">{{ row.assigned_count }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="checked_in_count" label="已签到人数" width="100" align="center" />
          <el-table-column prop="available_seats" label="空位" width="80" align="center">
            <template #default="{ row }">
              <span :class="{ 'text-success': row.available_seats > 0 }">{{ row.available_seats }}</span>
            </template>
          </el-table-column>
          <el-table-column label="入座率" width="160">
            <template #default="{ row }">
              <el-progress :percentage="row.seating_rate" :stroke-width="6" :color="row.is_over_capacity ? '#f56c6c' : '#67c23a'" />
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.is_over_capacity" type="danger" size="small">超员</el-tag>
              <el-tag v-else-if="row.seating_rate >= 100" type="success" size="small">满座</el-tag>
              <el-tag v-else type="info" size="small">正常</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  getOverviewStats,
  getWorkloadDistribution,
  getStatsByCategory,
  getOverdueTasks,
  getAdjustmentHistory,
  getRiskDistribution,
  getBudgetStats,
  getGuestStats
} from '@/api/stats'
import { getMaterialStats } from '@/api/material'
import { getCategories } from '@/api/task'

const WEDDING_ID = 1
const router = useRouter()

const overview = ref({})
const workloadData = ref([])
const categoryStats = ref([])
const overdueTasks = ref([])
const adjustmentHistory = ref([])
const categories = ref([])
const riskData = ref({
  risk_distribution: { low: 0, medium: 0, high: 0 },
  high_risk_count: 0,
  high_risk_tasks: [],
  risk_breakdown: {
    delivery_date_risk: 0,
    task_overdue_risk: 0,
    progress_behind_risk: 0,
    material_shortage_risk: 0
  }
})

const budgetStats = ref({
  total_budget: 0,
  total_approved: 0,
  total_pending: 0,
  total_rejected: 0,
  total_remaining: 0,
  overall_usage_rate: 0,
  over_budget_count: 0,
  pending_expense_count: 0,
  category_count: 0,
  expense_by_category: []
})

const materialStats = ref({
  total_items: 0,
  total_quantity: 0,
  total_borrowed: 0,
  total_available: 0,
  usage_rate: 0,
  overdue_count: 0,
  abnormal_count: 0,
  top_borrowed: []
})

const guestStats = ref({
  total_guests: 0,
  total_expected: 0,
  total_arrived: 0,
  arrival_rate: 0,
  checkin_rate: 0,
  checked_in_count: 0,
  late_count: 0,
  absent_count: 0,
  pending_count: 0,
  changed_count: 0,
  temp_added: 0,
  temp_reduced: 0,
  high_priority_total: 0,
  high_priority_arrived: 0,
  high_priority_pending: 0,
  high_priority_guests: [],
  group_stats: [],
  table_stats: [],
  total_tables: 0,
  total_capacity: 0,
  total_assigned: 0,
  over_capacity_count: 0,
  overall_seating_rate: 0,
  unassigned_guest_count: 0,
  unassigned_guests: []
})

const workloadChartRef = ref(null)
const categoryChartRef = ref(null)
const riskChartRef = ref(null)
const expenseChartRef = ref(null)
const budgetUsageChartRef = ref(null)

let workloadChart = null
let categoryChart = null
let riskChart = null
let expenseChart = null
let budgetUsageChart = null
let checkinChart = null
let seatingChart = null

const getCategoryName = (catId) => {
  const cat = categories.value.find(c => c.id === catId)
  return cat ? cat.name : catId
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return dateStr.replace('T', ' ').substring(0, 16)
}

const loadOverview = async () => {
  try {
    const res = await getOverviewStats(WEDDING_ID)
    overview.value = res || {}
  } catch (e) {
    overview.value = {
      total_tasks: 12,
      completed_tasks: 5,
      in_progress_tasks: 4,
      pending_tasks: 3,
      completion_rate: 41.7,
      total_adjustments: 3,
      overdue_tasks: 1,
      timeline_nodes: 11,
      bridesmaids_count: 5
    }
  }
}

const loadWorkload = async () => {
  try {
    const res = await getWorkloadDistribution(WEDDING_ID)
    workloadData.value = res || []
  } catch (e) {
    workloadData.value = [
      { bridesmaid_id: 1, name: '王小雨', role: 'leader', total_tasks: 4, completed_tasks: 2, in_progress_tasks: 2, pending_tasks: 0, avg_progress: 65, completion_rate: 50 },
      { bridesmaid_id: 2, name: '刘思琪', role: 'member', total_tasks: 3, completed_tasks: 2, in_progress_tasks: 1, pending_tasks: 0, avg_progress: 75, completion_rate: 66.7 },
      { bridesmaid_id: 3, name: '陈梦瑶', role: 'member', total_tasks: 2, completed_tasks: 0, in_progress_tasks: 2, pending_tasks: 0, avg_progress: 45, completion_rate: 0 },
      { bridesmaid_id: 4, name: '杨雪婷', role: 'member', total_tasks: 1, completed_tasks: 1, in_progress_tasks: 0, pending_tasks: 0, avg_progress: 100, completion_rate: 100 },
      { bridesmaid_id: 5, name: '赵嘉怡', role: 'member', total_tasks: 1, completed_tasks: 0, in_progress_tasks: 1, pending_tasks: 0, avg_progress: 70, completion_rate: 0 }
    ]
  }
}

const loadCategoryStats = async () => {
  try {
    const res = await getStatsByCategory(WEDDING_ID)
    categoryStats.value = res || []
  } catch (e) {
    categoryStats.value = [
      { category: 'door_game', total: 2, completed: 0, in_progress: 1, pending: 1 },
      { category: 'photo_props', total: 2, completed: 1, in_progress: 1, pending: 0 },
      { category: 'emergency_kit', total: 2, completed: 1, in_progress: 1, pending: 0 },
      { category: 'route_check', total: 2, completed: 1, in_progress: 0, pending: 1 },
      { category: 'decoration', total: 2, completed: 0, in_progress: 0, pending: 2 },
      { category: 'logistics', total: 2, completed: 1, in_progress: 1, pending: 0 }
    ]
  }
}

const loadOverdueTasks = async () => {
  try {
    const res = await getOverdueTasks(WEDDING_ID)
    overdueTasks.value = res || []
  } catch (e) {
    overdueTasks.value = [
      { id: 1, title: '设计堵门游戏方案', category: 'door_game', due_date: '2025-09-20', assigned_name: '王小雨', progress: 60 }
    ]
  }
}

const loadAdjustments = async () => {
  try {
    const res = await getAdjustmentHistory(WEDDING_ID)
    adjustmentHistory.value = res || []
  } catch (e) {
    adjustmentHistory.value = [
      { id: 1, task_title: '采购拍照道具', previous_assignee_name: '王小雨', new_assignee_name: '刘思琪', reason: '王小雨有事，临时调整', adjusted_at: '2025-09-12 14:30' },
      { id: 2, task_title: '整理伴手礼', previous_assignee_name: null, new_assignee_name: '陈梦瑶', reason: '伴娘主动认领', adjusted_at: '2025-09-15 10:00' },
      { id: 3, task_title: '准备补妆用品', previous_assignee_name: '杨雪婷', new_assignee_name: '赵嘉怡', reason: '突发情况调整', adjusted_at: '2025-09-20 16:45' }
    ]
  }
}

const loadCategories = async () => {
  try {
    const res = await getCategories()
    categories.value = res || []
  } catch (e) {
    categories.value = [
      { id: 'door_game', name: '堵门游戏', color: '#ff6b6b' },
      { id: 'photo_props', name: '拍照道具', color: '#4ecdc4' },
      { id: 'emergency_kit', name: '应急包', color: '#ffe66d' },
      { id: 'route_check', name: '接亲路线踩点', color: '#95e1d3' },
      { id: 'decoration', name: '场地布置', color: '#f38181' },
      { id: 'logistics', name: '物资采购', color: '#aa96da' }
    ]
  }
}

const loadRiskDistribution = async () => {
  try {
    const res = await getRiskDistribution(WEDDING_ID)
    riskData.value = res || riskData.value
  } catch (e) {
    riskData.value = {
      risk_distribution: { low: 3, medium: 2, high: 1 },
      high_risk_count: 1,
      high_risk_tasks: [],
      risk_breakdown: {
        delivery_date_risk: 1,
        task_overdue_risk: 2,
        progress_behind_risk: 1,
        material_shortage_risk: 1
      }
    }
  }
}

const loadBudgetStats = async () => {
  try {
    const res = await getBudgetStats(WEDDING_ID)
    budgetStats.value = res || budgetStats.value
  } catch (e) {
    budgetStats.value = {
      total_budget: 19300,
      total_approved: 3650,
      total_pending: 1480,
      total_rejected: 800,
      total_remaining: 15650,
      overall_usage_rate: 18.9,
      over_budget_count: 0,
      pending_expense_count: 2,
      category_count: 6,
      expense_by_category: [
        { name: '堵门红包', color: '#ff6b6b', approved_amount: 0, pending_amount: 1200, budget_limit: 2000, usage_rate: 0 },
        { name: '拍照道具', color: '#4ecdc4', approved_amount: 680, pending_amount: 0, budget_limit: 800, usage_rate: 85 },
        { name: '应急物资', color: '#ffe66d', approved_amount: 320, pending_amount: 280, budget_limit: 500, usage_rate: 64 },
        { name: '交通餐饮', color: '#95e1d3', approved_amount: 150, pending_amount: 0, budget_limit: 3000, usage_rate: 5 },
        { name: '场地布置', color: '#f38181', approved_amount: 0, pending_amount: 0, budget_limit: 5000, usage_rate: 0 },
        { name: '物资采购', color: '#aa96da', approved_amount: 2500, pending_amount: 0, budget_limit: 8000, usage_rate: 31.3 }
      ]
    }
  }
}

const loadMaterialStats = async () => {
  try {
    const res = await getMaterialStats(WEDDING_ID)
    materialStats.value = res || materialStats.value
  } catch (e) {
    materialStats.value = {
      total_items: 6,
      total_quantity: 29,
      total_borrowed: 11,
      total_available: 18,
      usage_rate: 37.9,
      overdue_count: 1,
      abnormal_count: 1,
      top_borrowed: [
        { name: '对讲机', count: 2 },
        { name: '充电宝', count: 1 },
        { name: '补光灯', count: 1 },
        { name: '拍照道具套装', count: 1 }
      ]
    }
  }
}

const loadGuestStats = async () => {
  try {
    const res = await getGuestStats(WEDDING_ID)
    guestStats.value = res || guestStats.value
  } catch (e) {
    guestStats.value = {
      total_guests: 32,
      total_expected: 60,
      total_arrived: 0,
      arrival_rate: 0,
      checkin_rate: 0,
      checked_in_count: 0,
      late_count: 0,
      absent_count: 0,
      pending_count: 32,
      changed_count: 0,
      temp_added: 0,
      temp_reduced: 0,
      high_priority_total: 8,
      high_priority_arrived: 0,
      high_priority_pending: 8,
      high_priority_guests: [],
      group_stats: [],
      table_stats: [],
      total_tables: 11,
      total_capacity: 112,
      total_assigned: 52,
      over_capacity_count: 0,
      overall_seating_rate: 46.4,
      unassigned_guest_count: 2,
      unassigned_guests: []
    }
  }
}

const getRiskLevelText = (level) => {
  const map = { low: '低风险', medium: '中风险', high: '高风险' }
  return map[level] || level
}

const getRiskLevelType = (level) => {
  const map = { low: 'success', medium: 'warning', high: 'danger' }
  return map[level] || 'info'
}

const getBreakdownPercent = (key) => {
  const total = Object.values(riskData.value.risk_breakdown).reduce((a, b) => a + b, 0)
  if (total === 0) return 0
  return Math.round((riskData.value.risk_breakdown[key] / total) * 100)
}

const getTopBorrowedPercent = (index) => {
  const list = materialStats.value.top_borrowed
  if (!list.length) return 0
  const max = list[0].count
  return Math.round((list[index].count / max) * 100)
}

const getCheckinStatusText = (status) => {
  const map = {
    pending: '待签到',
    checked_in: '已签到',
    late: '迟到',
    absent: '未到',
    changed: '临时变更'
  }
  return map[status] || status
}

const initRiskChart = () => {
  if (!riskChartRef.value) return

  riskChart = echarts.init(riskChartRef.value)

  const dist = riskData.value.risk_distribution

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}个 ({d}%)'
    },
    legend: {
      bottom: 0,
      data: ['高风险', '中风险', '低风险']
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c}个',
          fontSize: 13
        },
        data: [
          { name: '高风险', value: dist.high, itemStyle: { color: '#f56c6c' } },
          { name: '中风险', value: dist.medium, itemStyle: { color: '#e6a23c' } },
          { name: '低风险', value: dist.low, itemStyle: { color: '#67c23a' } }
        ]
      }
    ]
  }

  riskChart.setOption(option)
}

const initWorkloadChart = () => {
  if (!workloadChartRef.value) return
  
  workloadChart = echarts.init(workloadChartRef.value)
  
  const names = workloadData.value.map(item => item.name)
  const completedData = workloadData.value.map(item => item.completed_tasks)
  const inProgressData = workloadData.value.map(item => item.in_progress_tasks)
  const pendingData = workloadData.value.map(item => item.pending_tasks)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['已完成', '进行中', '待认领'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: {
        rotate: 0,
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [
      {
        name: '已完成',
        type: 'bar',
        stack: 'total',
        data: completedData,
        itemStyle: { color: '#67c23a', borderRadius: [0, 0, 0, 0] }
      },
      {
        name: '进行中',
        type: 'bar',
        stack: 'total',
        data: inProgressData,
        itemStyle: { color: '#409eff' }
      },
      {
        name: '待认领',
        type: 'bar',
        stack: 'total',
        data: pendingData,
        itemStyle: { color: '#909399', borderRadius: [4, 4, 0, 0] }
      }
    ]
  }
  
  workloadChart.setOption(option)
}

const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  
  categoryChart = echarts.init(categoryChartRef.value)
  
  const catNames = categoryStats.value.map(item => {
    const cat = categories.value.find(c => c.id === item.category)
    return cat ? cat.name : item.category
  })
  
  const data = categoryStats.value.map(item => item.total)
  const colors = categoryStats.value.map(item => {
    const cat = categories.value.find(c => c.id === item.category)
    return cat ? cat.color : '#ccc'
  })
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}个 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { fontSize: 12 }
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        data: catNames.map((name, index) => ({
          name,
          value: data[index],
          itemStyle: { color: colors[index] }
        }))
      }
    ]
  }
  
  categoryChart.setOption(option)
}

const handleTask = (task) => {
  router.push('/tasks')
}

const initExpenseChart = () => {
  if (!expenseChartRef.value) return

  expenseChart = echarts.init(expenseChartRef.value)

  const expenseData = budgetStats.value.expense_by_category
    .filter(c => c.approved_amount > 0 || c.pending_amount > 0)
    .map(c => ({
      name: c.name,
      value: c.approved_amount + c.pending_amount,
      itemStyle: { color: c.color }
    }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      bottom: 0,
      data: expenseData.map(d => d.name)
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n¥{c}',
          fontSize: 12
        },
        data: expenseData
      }
    ]
  }

  expenseChart.setOption(option)
}

const initBudgetUsageChart = () => {
  if (!budgetUsageChartRef.value) return

  budgetUsageChart = echarts.init(budgetUsageChartRef.value)

  const usageData = [...budgetStats.value.expense_by_category]
    .sort((a, b) => b.usage_rate - a.usage_rate)

  const names = usageData.map(d => d.name)
  const usageRates = usageData.map(d => d.usage_rate)
  const colors = usageData.map(d => d.usage_rate > 100 ? '#f56c6c' : d.color)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: '{b}<br/>使用率: {c}%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: {
        fontSize: 12
      }
    },
    series: [
      {
        type: 'bar',
        data: usageRates.map((value, index) => ({
          value: Math.min(value, 100),
          itemStyle: {
            color: colors[index],
            borderRadius: [0, 4, 4, 0]
          }
        })),
        label: {
          show: true,
          position: 'right',
          formatter: '{c}%',
          fontSize: 12,
          fontWeight: 600
        },
        markLine: {
          silent: true,
          lineStyle: {
            color: '#f56c6c',
            type: 'dashed'
          },
          data: [
            { xAxis: 100, label: { formatter: '预算线', fontSize: 11 } }
          ]
        }
      }
    ]
  }

  budgetUsageChart.setOption(option)
}

const initCheckinChart = () => {
  if (!checkinChartRef.value) return

  checkinChart = echarts.init(checkinChartRef.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}人 ({d}%)'
    },
    legend: {
      bottom: 0,
      data: ['已签到', '迟到', '未到', '待签到', '临时变更']
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c}人',
          fontSize: 13
        },
        data: [
          { name: '已签到', value: guestStats.value.checked_in_count, itemStyle: { color: '#67c23a' } },
          { name: '迟到', value: guestStats.value.late_count, itemStyle: { color: '#e6a23c' } },
          { name: '未到', value: guestStats.value.absent_count, itemStyle: { color: '#f56c6c' } },
          { name: '待签到', value: guestStats.value.pending_count, itemStyle: { color: '#909399' } },
          { name: '临时变更', value: guestStats.value.changed_count, itemStyle: { color: '#9093ff' } }
        ]
      }
    ]
  }

  checkinChart.setOption(option)
}

const initSeatingChart = () => {
  if (!seatingChartRef.value) return

  seatingChart = echarts.init(seatingChartRef.value)

  const tableData = guestStats.value.table_stats
  const names = tableData.map(t => t.table_name)
  const capacities = tableData.map(t => t.capacity)
  const assigned = tableData.map(t => t.assigned_count)
  const checkedIn = tableData.map(t => t.checked_in_count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['已分配', '已签到', '容量'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: {
        rotate: 45,
        fontSize: 11,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [
      {
        name: '容量',
        type: 'bar',
        data: capacities,
        itemStyle: { color: '#dcdfe6', borderRadius: [4, 4, 0, 0] }
      },
      {
        name: '已分配',
        type: 'bar',
        data: assigned,
        itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] }
      },
      {
        name: '已签到',
        type: 'bar',
        data: checkedIn,
        itemStyle: { color: '#67c23a', borderRadius: [4, 4, 0, 0] }
      }
    ]
  }

  seatingChart.setOption(option)
}

onMounted(async () => {
  await loadCategories()
  await Promise.all([
    loadOverview(),
    loadWorkload(),
    loadCategoryStats(),
    loadOverdueTasks(),
    loadAdjustments(),
    loadRiskDistribution(),
    loadBudgetStats(),
    loadMaterialStats(),
    loadGuestStats()
  ])
  
  await nextTick()
  initWorkloadChart()
  initCategoryChart()
  initRiskChart()
  initExpenseChart()
  initBudgetUsageChart()
  initCheckinChart()
  initSeatingChart()
  
  window.addEventListener('resize', () => {
    workloadChart?.resize()
    categoryChart?.resize()
    riskChart?.resize()
    expenseChart?.resize()
    budgetUsageChart?.resize()
    checkinChart?.resize()
    seatingChart?.resize()
  })
})
</script>

<style scoped>
.stats-page {
  min-height: 100%;
}

.stats-overview {
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
  gap: 14px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

.stat-icon {
  font-size: 32px;
  width: 56px;
  height: 56px;
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
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.stat-card.total .stat-icon { background: #ecf5ff; }
.stat-card.total .stat-value { color: #409eff; }
.stat-card.completed .stat-icon { background: #f0f9eb; }
.stat-card.completed .stat-value { color: #67c23a; }
.stat-card.rate .stat-icon { background: #fef0f0; }
.stat-card.rate .stat-value { color: #f56c6c; }
.stat-card.adjust .stat-icon { background: #fdf6ec; }
.stat-card.adjust .stat-value { color: #e6a23c; }
.stat-card.overdue .stat-icon { background: #fef0f0; }
.stat-card.overdue .stat-value { color: #f56c6c; }
.stat-card.bridesmaid .stat-icon { background: #f0f0ff; }
.stat-card.bridesmaid .stat-value { color: #9093ff; }
.stat-card.high-risk .stat-icon { background: #fef0f0; }
.stat-card.high-risk .stat-value { color: #f56c6c; }
.stat-card.risk-level .stat-icon { background: #fdf6ec; }
.stat-card.risk-level .stat-value { color: #e6a23c; }

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #303133;
}

.chart-container {
  height: 280px;
  width: 100%;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.rank-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  background: #f0f0f0;
  color: #909399;
  flex-shrink: 0;
}

.rank-1 { background: linear-gradient(135deg, #ffd700, #ffb800); color: white; }
.rank-2 { background: linear-gradient(135deg, #c0c0c0, #a8a8a8); color: white; }
.rank-3 { background: linear-gradient(135deg, #cd7f32, #b87333); color: white; }

.rank-avatar {
  font-size: 24px;
  flex-shrink: 0;
}

.rank-info {
  flex: 1;
  min-width: 0;
}

.rank-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 6px;
}

.leader-badge {
  display: inline-block;
  background: linear-gradient(90deg, #ff6b9d, #c44569);
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 6px;
  font-weight: normal;
}

.rank-progress {
  width: 100%;
}

.rank-stats {
  text-align: center;
  flex-shrink: 0;
}

.stat-num {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 11px;
  color: #909399;
}

.overdue-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.overdue-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: #fff5f5;
  border-radius: 8px;
  border-left: 4px solid #f56c6c;
}

.overdue-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.overdue-info {
  flex: 1;
  min-width: 0;
}

.overdue-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.overdue-meta {
  display: flex;
  gap: 10px;
  margin-bottom: 4px;
}

.category-tag {
  background: #ffe5e5;
  color: #f56c6c;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.assignee {
  font-size: 12px;
  color: #606266;
}

.overdue-date {
  font-size: 12px;
  color: #909399;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-text {
  color: #909399;
  font-size: 14px;
}

.adjustment-history {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.risk-breakdown-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.risk-breakdown-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.breakdown-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 8px;
  flex-shrink: 0;
}

.breakdown-info {
  flex: 1;
  min-width: 0;
}

.breakdown-name {
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
}

.breakdown-count {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  min-width: 30px;
  text-align: center;
  flex-shrink: 0;
}

.material-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.material-stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px;
  background: #fafafa;
  border-radius: 8px;
}

.material-stat-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 8px;
  flex-shrink: 0;
}

.material-stat-info {
  flex: 1;
  min-width: 0;
}

.material-stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}

.material-stat-label {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
}

.top-borrowed-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.top-borrowed-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.borrowed-rank {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  background: #f0f0f0;
  color: #909399;
  flex-shrink: 0;
}

.borrowed-info {
  flex: 1;
  min-width: 0;
}

.borrowed-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 6px;
}

.borrowed-count {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
  flex-shrink: 0;
}

.guest-stats-section {
  margin-top: 24px;
}

.section-title-big {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.guest-total .stat-icon { background: #ecf5ff; }
.guest-total .stat-value { color: #409eff; }
.guest-expected .stat-icon { background: #f0f0ff; }
.guest-expected .stat-value { color: #9093ff; }
.guest-arrived .stat-icon { background: #f0f9eb; }
.guest-arrived .stat-value { color: #67c23a; }
.guest-rate .stat-icon { background: #e1f3d8; }
.guest-rate .stat-value { color: #67c23a; }
.guest-checkin .stat-icon { background: #d9ecff; }
.guest-checkin .stat-value { color: #409eff; }
.guest-pending .stat-icon { background: #f4f4f5; }
.guest-pending .stat-value { color: #909399; }
.guest-late .stat-icon { background: #fdf6ec; }
.guest-late .stat-value { color: #e6a23c; }
.guest-absent .stat-icon { background: #fef0f0; }
.guest-absent .stat-value { color: #f56c6c; }
.guest-temp-add .stat-icon { background: #f0f9eb; }
.guest-temp-add .stat-value { color: #67c23a; }
.guest-temp-reduce .stat-icon { background: #fdf6ec; }
.guest-temp-reduce .stat-value { color: #e6a23c; }
.guest-high .stat-icon { background: #fef0f0; }
.guest-high .stat-value { color: #f56c6c; }
.guest-unassigned .stat-icon { background: #f4f4f5; }
.guest-unassigned .stat-value { color: #909399; }

.group-stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 280px;
  overflow-y: auto;
}

.group-stat-item {
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.group-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 6px;
}

.group-info {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.group-count {
  font-weight: 500;
  color: #606266;
}

.high-priority-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 280px;
  overflow-y: auto;
}

.high-priority-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #fef0f0;
  border-radius: 8px;
  border-left: 3px solid #f56c6c;
}

.high-priority-item.arrived {
  background: #f0f9eb;
  border-left-color: #67c23a;
}

.hp-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.hp-info {
  flex: 1;
  min-width: 0;
}

.hp-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.hp-meta {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.hp-notes {
  font-size: 12px;
  color: #e6a23c;
  background: rgba(230, 162, 60, 0.1);
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
}

.text-danger {
  color: #f56c6c !important;
}

.text-success {
  color: #67c23a !important;
}
</style>
