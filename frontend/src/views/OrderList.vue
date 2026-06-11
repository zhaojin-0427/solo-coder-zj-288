<template>
  <div class="order-list">
    <div class="page-header">
      <h2 class="page-title">📋 订单列表</h2>
      <div class="header-filters">
        <el-select v-model="filterRisk" placeholder="按风险筛选" clearable style="width: 160px; margin-right: 12px;">
          <el-option label="高风险" value="high" />
          <el-option label="中风险" value="medium" />
          <el-option label="低风险" value="low" />
        </el-select>
        <el-input v-model="searchKeyword" placeholder="搜索新人姓名" clearable style="width: 200px;" />
      </div>
    </div>

    <div class="risk-summary-cards">
      <div class="risk-card high">
        <div class="risk-icon">🔴</div>
        <div class="risk-info">
          <div class="risk-count">{{ riskCounts.high }}</div>
          <div class="risk-label">高风险订单</div>
        </div>
      </div>
      <div class="risk-card medium">
        <div class="risk-icon">🟡</div>
        <div class="risk-info">
          <div class="risk-count">{{ riskCounts.medium }}</div>
          <div class="risk-label">中风险订单</div>
        </div>
      </div>
      <div class="risk-card low">
        <div class="risk-icon">🟢</div>
        <div class="risk-info">
          <div class="risk-count">{{ riskCounts.low }}</div>
          <div class="risk-label">低风险订单</div>
        </div>
      </div>
    </div>

    <div class="orders-table-wrapper">
      <el-table :data="filteredOrders" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="订单ID" width="100" />
        <el-table-column label="新人信息" min-width="200">
          <template #default="{ row }">
            <div class="couple-info">
              <div class="couple-names">{{ row.bride_name }} & {{ row.groom_name }}</div>
              <div class="couple-venue">📍 {{ row.venue }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="wedding_date" label="婚礼日期" width="140">
          <template #default="{ row }">
            <div class="date-info">
              <div>{{ row.wedding_date }}</div>
              <div class="days-remaining" :class="getDaysClass(row)">
                剩余 {{ getDaysRemaining(row.wedding_date) }} 天
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="风险等级" width="160">
          <template #default="{ row }">
            <el-tag :type="getRiskType(row.risk_level)" size="default" effect="dark">
              {{ getRiskText(row.risk_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="风险原因" min-width="250">
          <template #default="{ row }">
            <div v-if="row.risk_reasons && row.risk_reasons.length > 0">
              <el-tag v-for="reason in row.risk_reasons" :key="reason" :type="getRiskType(row.risk_level)" size="small" style="margin-right: 6px; margin-bottom: 4px;">
                {{ reason }}
              </el-tag>
            </div>
            <span v-else style="color: #909399;">无</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row.id)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-empty v-if="filteredOrders.length === 0 && !loading" description="暂无订单数据" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getWeddings } from '@/api/wedding'

const router = useRouter()
const orders = ref([])
const loading = ref(false)
const filterRisk = ref('')
const searchKeyword = ref('')

const getRiskType = (level) => {
  const map = { low: 'success', medium: 'warning', high: 'danger' }
  return map[level] || 'info'
}

const getRiskText = (level) => {
  const map = { low: '低风险', medium: '中风险', high: '高风险' }
  return map[level] || level
}

const getDaysRemaining = (dateStr) => {
  const today = new Date()
  const weddingDate = new Date(dateStr)
  const diff = Math.ceil((weddingDate - today) / (1000 * 60 * 60 * 24))
  return diff >= 0 ? diff : 0
}

const getDaysClass = (row) => {
  const days = getDaysRemaining(row.wedding_date)
  if (days <= 7) return 'days-urgent'
  if (days <= 14) return 'days-warning'
  return 'days-normal'
}

const riskCounts = computed(() => {
  return {
    high: orders.value.filter(o => o.risk_level === 'high').length,
    medium: orders.value.filter(o => o.risk_level === 'medium').length,
    low: orders.value.filter(o => o.risk_level === 'low').length
  }
})

const filteredOrders = computed(() => {
  let result = [...orders.value]
  
  if (filterRisk.value) {
    result = result.filter(o => o.risk_level === filterRisk.value)
  }
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(o => 
      o.bride_name.toLowerCase().includes(keyword) || 
      o.groom_name.toLowerCase().includes(keyword)
    )
  }
  
  return result
})

const loadOrders = async () => {
  loading.value = true
  try {
    const res = await getWeddings()
    orders.value = res || []
    if (orders.value.length === 0) {
      orders.value = [
        {
          id: 1,
          bride_name: '张美丽',
          groom_name: '李英俊',
          wedding_date: '2025-10-01',
          venue: '上海外滩W酒店',
          risk_level: 'high',
          risk_reasons: ['关键任务逾期', '材料不足', '交付日期临近'],
          created_at: '2025-01-15 10:30:00'
        },
        {
          id: 2,
          bride_name: '王小花',
          groom_name: '陈大明',
          wedding_date: '2025-11-15',
          venue: '北京钓鱼台国宾馆',
          risk_level: 'medium',
          risk_reasons: ['作品完成数量落后'],
          created_at: '2025-02-20 14:00:00'
        },
        {
          id: 3,
          bride_name: '刘诗涵',
          groom_name: '赵天成',
          wedding_date: '2026-01-08',
          venue: '杭州西湖国宾馆',
          risk_level: 'low',
          risk_reasons: [],
          created_at: '2025-03-01 09:00:00'
        }
      ]
    }
  } catch (e) {
    orders.value = [
      {
        id: 1,
        bride_name: '张美丽',
        groom_name: '李英俊',
        wedding_date: '2025-10-01',
        venue: '上海外滩W酒店',
        risk_level: 'high',
        risk_reasons: ['关键任务逾期', '材料不足', '交付日期临近'],
        created_at: '2025-01-15 10:30:00'
      },
      {
        id: 2,
        bride_name: '王小花',
        groom_name: '陈大明',
        wedding_date: '2025-11-15',
        venue: '北京钓鱼台国宾馆',
        risk_level: 'medium',
        risk_reasons: ['作品完成数量落后'],
        created_at: '2025-02-20 14:00:00'
      },
      {
        id: 3,
        bride_name: '刘诗涵',
        groom_name: '赵天成',
        wedding_date: '2026-01-08',
        venue: '杭州西湖国宾馆',
        risk_level: 'low',
        risk_reasons: [],
        created_at: '2025-03-01 09:00:00'
      }
    ]
  } finally {
    loading.value = false
  }
}

const viewDetail = (id) => {
  router.push(`/orders/${id}`)
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.order-list {
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

.risk-summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.risk-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  border-left: 4px solid #67c23a;
}

.risk-card.high {
  border-left-color: #f56c6c;
  background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
}

.risk-card.medium {
  border-left-color: #e6a23c;
  background: linear-gradient(135deg, #fdf6ec 0%, #fff3e0 100%);
}

.risk-card.low {
  border-left-color: #67c23a;
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
}

.risk-icon {
  font-size: 36px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.8);
  border-radius: 50%;
}

.risk-info {
  flex: 1;
}

.risk-count {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.risk-label {
  font-size: 13px;
  color: #606266;
}

.orders-table-wrapper {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.couple-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.couple-names {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.couple-venue {
  font-size: 12px;
  color: #909399;
}

.date-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.days-remaining {
  font-size: 12px;
}

.days-urgent {
  color: #f56c6c;
  font-weight: 600;
}

.days-warning {
  color: #e6a23c;
  font-weight: 600;
}

.days-normal {
  color: #67c23a;
}
</style>
