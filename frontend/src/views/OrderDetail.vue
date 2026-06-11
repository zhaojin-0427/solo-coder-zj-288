<template>
  <div class="order-detail" v-loading="loading">
    <div class="detail-header">
      <el-button @click="goBack" :icon="ArrowLeft">返回列表</el-button>
      <h2 class="detail-title">订单详情</h2>
      <div v-if="order.risk_level" class="risk-indicator">
        <el-tag :type="getRiskType(order.risk_level)" size="large" effect="dark">
          {{ getRiskText(order.risk_level) }}
        </el-tag>
      </div>
    </div>

    <div v-if="order.id" class="detail-content">
      <div class="info-card">
        <h3 class="card-title">💑 新人信息</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">新娘姓名</span>
            <span class="info-value">{{ order.bride_name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">新郎姓名</span>
            <span class="info-value">{{ order.groom_name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">婚礼日期</span>
            <span class="info-value">{{ order.wedding_date }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">婚礼场地</span>
            <span class="info-value">📍 {{ order.venue }}</span>
          </div>
          <div class="info-item full-width">
            <span class="info-label">订单描述</span>
            <span class="info-value">{{ order.description || '暂无' }}</span>
          </div>
        </div>
      </div>

      <div class="risk-card" v-if="riskAssessment">
        <div class="risk-card-header">
          <h3 class="card-title">🚨 风险评估报告</h3>
          <el-tag :type="getRiskType(riskAssessment.risk_level)" size="large" effect="dark">
            {{ getRiskText(riskAssessment.risk_level) }}
          </el-tag>
        </div>
        <div class="risk-score-display">
          <div class="score-ring" :class="`score-${riskAssessment.risk_level}`">
            <div class="score-value">{{ riskAssessment.risk_score }}</div>
            <div class="score-label">风险评分</div>
          </div>
          <div class="risk-details">
            <div class="detail-row">
              <span class="detail-label">距离婚礼</span>
              <span class="detail-value">{{ riskAssessment.details.days_until_wedding }} 天</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">整体完成率</span>
              <span class="detail-value" :class="riskAssessment.details.completion_rate < 50 ? 'value-danger' : 'value-success'">
                {{ riskAssessment.details.completion_rate }}%
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">总任务数</span>
              <span class="detail-value">{{ riskAssessment.details.total_tasks }} 项</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">已完成</span>
              <span class="detail-value value-success">{{ riskAssessment.details.completed_tasks }} 项</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">逾期任务</span>
              <span class="detail-value value-danger">{{ riskAssessment.details.overdue_tasks }} 项</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">逾期关键任务</span>
              <span class="detail-value value-danger">{{ riskAssessment.details.overdue_critical_tasks }} 项</span>
            </div>
          </div>
        </div>
        <div class="risk-reasons-section" v-if="riskAssessment.risk_reasons.length > 0">
          <h4 class="reasons-title">具体风险原因：</h4>
          <div class="reasons-list">
            <div v-for="reason in riskAssessment.risk_reasons" :key="reason" class="reason-item">
              <span class="reason-icon">⚠️</span>
              <span class="reason-text">{{ reason }}</span>
            </div>
          </div>
        </div>
        <div class="risk-breakdown">
          <h4 class="reasons-title">风险因素分析：</h4>
          <div class="breakdown-item">
            <span>📅 交付日期风险</span>
            <el-progress :percentage="riskAssessment.details.days_until_wedding <= 7 ? 90 : riskAssessment.details.days_until_wedding <= 14 ? 50 : 20" :stroke-width="8" color="#f56c6c" />
          </div>
          <div class="breakdown-item">
            <span>📊 进度落后风险</span>
            <el-progress :percentage="100 - riskAssessment.details.completion_rate" :stroke-width="8" color="#e6a23c" />
          </div>
          <div class="breakdown-item">
            <span>⚠️ 任务逾期风险</span>
            <el-progress :percentage="riskAssessment.details.overdue_tasks > 0 ? Math.min(90, riskAssessment.details.overdue_tasks * 20) : 10" :stroke-width="8" color="#409eff" />
          </div>
          <div class="breakdown-item">
            <span>📦 材料不足风险</span>
            <el-progress :percentage="riskAssessment.details.overdue_logistics_tasks > 0 ? 80 : riskAssessment.details.pending_logistics_tasks > 0 ? 40 : 10" :stroke-width="8" color="#909399" />
          </div>
        </div>
      </div>

      <div class="actions-card">
        <h3 class="card-title">⚡ 快捷操作</h3>
        <div class="actions-grid">
          <el-button type="primary" size="large" @click="goToTasks">📋 查看任务看板</el-button>
          <el-button type="success" size="large" @click="goToChecklist">✅ 查看准备清单</el-button>
          <el-button type="warning" size="large" @click="goToTimeline">📅 查看当天流程</el-button>
          <el-button type="info" size="large" @click="goToStats">📊 查看数据统计</el-button>
        </div>
      </div>
    </div>

    <el-empty v-if="!order.id && !loading" description="未找到订单信息" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getWedding } from '@/api/wedding'
import { getRiskAssessment } from '@/api/risk'

const router = useRouter()
const route = useRoute()
const orderId = ref(route.params.id || 1)
const loading = ref(false)
const order = ref({})
const riskAssessment = ref(null)

const getRiskType = (level) => {
  const map = { low: 'success', medium: 'warning', high: 'danger' }
  return map[level] || 'info'
}

const getRiskText = (level) => {
  const map = { low: '低风险', medium: '中风险', high: '高风险' }
  return map[level] || level
}

const loadOrder = async () => {
  loading.value = true
  try {
    const res = await getWedding(orderId.value)
    order.value = res || {}
    if (!order.value.id) {
      order.value = {
        id: orderId.value,
        bride_name: '张美丽',
        groom_name: '李英俊',
        wedding_date: '2025-10-01',
        venue: '上海外滩W酒店',
        description: '户外婚礼，浪漫主题',
        risk_level: 'high',
        risk_reasons: ['关键任务逾期', '材料不足', '交付日期临近'],
        created_at: '2025-01-15 10:30:00'
      }
    }
  } catch (e) {
    order.value = {
      id: orderId.value,
      bride_name: '张美丽',
      groom_name: '李英俊',
      wedding_date: '2025-10-01',
      venue: '上海外滩W酒店',
      description: '户外婚礼，浪漫主题',
      risk_level: 'high',
      risk_reasons: ['关键任务逾期', '材料不足', '交付日期临近'],
      created_at: '2025-01-15 10:30:00'
    }
  } finally {
    loading.value = false
  }
}

const loadRisk = async () => {
  try {
    const res = await getRiskAssessment(orderId.value)
    riskAssessment.value = res || null
    if (!riskAssessment.value) {
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

const goBack = () => {
  router.push('/orders')
}

const goToTasks = () => {
  router.push('/tasks')
}

const goToChecklist = () => {
  router.push('/checklist')
}

const goToTimeline = () => {
  router.push('/timeline')
}

const goToStats = () => {
  router.push('/stats')
}

onMounted(async () => {
  await loadOrder()
  await loadRisk()
})
</script>

<style scoped>
.order-detail {
  padding: 24px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.detail-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.risk-indicator {
  display: flex;
  align-items: center;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card,
.risk-card,
.actions-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 13px;
  color: #909399;
}

.info-value {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.risk-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.risk-card-header .card-title {
  margin-bottom: 0;
}

.risk-score-display {
  display: flex;
  gap: 40px;
  margin-bottom: 24px;
  align-items: center;
}

.score-ring {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 6px solid #67c23a;
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
}

.score-ring.score-high {
  border-color: #f56c6c;
  background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
}

.score-ring.score-medium {
  border-color: #e6a23c;
  background: linear-gradient(135deg, #fdf6ec 0%, #fff3e0 100%);
}

.score-value {
  font-size: 36px;
  font-weight: 700;
  color: #303133;
}

.score-label {
  font-size: 12px;
  color: #606266;
}

.risk-details {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #fafafa;
  border-radius: 6px;
}

.detail-label {
  font-size: 13px;
  color: #606266;
}

.detail-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.value-danger {
  color: #f56c6c;
}

.value-success {
  color: #67c23a;
}

.risk-reasons-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #fff5f5;
  border-radius: 8px;
  border-left: 4px solid #f56c6c;
}

.reasons-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.reasons-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.reason-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: white;
  border-radius: 6px;
  font-size: 13px;
  color: #303133;
}

.risk-breakdown {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.breakdown-item > span {
  min-width: 120px;
  font-size: 13px;
  color: #606266;
}

.breakdown-item .el-progress {
  flex: 1;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
</style>
