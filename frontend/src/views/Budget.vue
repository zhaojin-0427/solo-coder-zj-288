<template>
  <div class="budget-page">
    <div class="page-header">
      <h1 class="page-title">💰 预算与费用报销</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showAddCategoryDialog = true" :icon="Plus">
          新建预算分类
        </el-button>
        <el-button type="success" @click="showAddExpenseDialog = true" :icon="Plus">
          申请报销
        </el-button>
      </div>
    </div>

    <div class="budget-overview">
      <div class="stat-card total-budget">
        <div class="stat-icon">💵</div>
        <div class="stat-content">
          <div class="stat-value">¥{{ summary.total_budget?.toLocaleString() || 0 }}</div>
          <div class="stat-label">总预算</div>
        </div>
      </div>
      <div class="stat-card approved">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-value">¥{{ summary.total_approved?.toLocaleString() || 0 }}</div>
          <div class="stat-label">已报销</div>
        </div>
      </div>
      <div class="stat-card pending">
        <div class="stat-icon">⏳</div>
        <div class="stat-content">
          <div class="stat-value">¥{{ summary.total_pending?.toLocaleString() || 0 }}</div>
          <div class="stat-label">待审核</div>
        </div>
      </div>
      <div class="stat-card remaining">
        <div class="stat-icon">💳</div>
        <div class="stat-content">
          <div class="stat-value" :class="{ 'text-danger': summary.total_remaining < 0 }">
            ¥{{ summary.total_remaining?.toLocaleString() || 0 }}
          </div>
          <div class="stat-label">剩余额度</div>
        </div>
      </div>
      <div class="stat-card usage">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.overall_usage_rate || 0 }}%</div>
          <div class="stat-label">预算使用率</div>
        </div>
      </div>
      <div class="stat-card over-budget" v-if="summary.over_budget_count > 0">
        <div class="stat-icon">⚠️</div>
        <div class="stat-content">
          <div class="stat-value text-danger">{{ summary.over_budget_count || 0 }}</div>
          <div class="stat-label">超支分类</div>
        </div>
      </div>
    </div>

    <div class="content-row">
      <div class="categories-section">
        <h3 class="section-title">📁 预算分类</h3>
        <div class="category-list">
          <div
            v-for="category in categories"
            :key="category.id"
            class="category-card"
            :class="{ 'over-budget': category.is_over_budget }"
          >
            <div class="category-header">
              <div class="category-info">
                <span class="category-icon" :style="{ background: category.color + '20' }">{{ category.icon }}</span>
                <span class="category-name">{{ category.name }}</span>
                <el-tag
                  v-if="category.is_over_budget"
                  type="danger"
                  size="small"
                  effect="dark"
                >
                  超支
                </el-tag>
              </div>
              <div class="category-actions">
                <el-button
                  size="small"
                  type="primary"
                  text
                  @click="editCategory(category)"
                >
                  编辑
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  text
                  @click="handleDeleteCategory(category)"
                >
                  删除
                </el-button>
              </div>
            </div>
            <div class="budget-amounts">
              <div class="amount-item">
                <span class="amount-label">预算</span>
                <span class="amount-value">¥{{ category.budget_limit.toLocaleString() }}</span>
              </div>
              <div class="amount-item">
                <span class="amount-label">已用</span>
                <span class="amount-value">¥{{ category.approved_amount.toLocaleString() }}</span>
              </div>
              <div class="amount-item">
                <span class="amount-label">待审</span>
                <span class="amount-value">¥{{ category.pending_amount.toLocaleString() }}</span>
              </div>
              <div class="amount-item">
                <span class="amount-label">剩余</span>
                <span
                  class="amount-value"
                  :class="{ 'text-danger': category.remaining < 0 }"
                >
                  ¥{{ category.remaining.toLocaleString() }}
                </span>
              </div>
            </div>
            <div class="progress-section">
              <div class="progress-header">
                <span>使用率</span>
                <span :class="{ 'text-danger': category.usage_rate > 100 }">
                  {{ category.usage_rate }}%
                </span>
              </div>
              <el-progress
                :percentage="Math.min(category.usage_rate, 100)"
                :stroke-width="8"
                :color="category.usage_rate > 100 ? '#f56c6c' : category.color"
              />
            </div>
            <div class="category-footer">
              <span class="expense-count">{{ category.expense_count }} 笔费用</span>
              <el-button
                size="small"
                type="primary"
                text
                @click="filterByCategory(category.id)"
              >
                查看费用 →
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="expenses-section">
      <div class="section-header">
        <h3 class="section-title">📋 费用记录</h3>
        <div class="filter-tabs">
          <el-radio-group v-model="activeTab" @change="loadExpenses">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="pending">待审核 ({{ pendingCount }})</el-radio-button>
            <el-radio-button value="approved">已通过</el-radio-button>
            <el-radio-button value="rejected">已驳回</el-radio-button>
          </el-radio-group>
        </div>
      </div>

      <el-table :data="filteredExpenses" stripe style="width: 100%;" v-loading="loadingExpenses">
        <el-table-column label="分类" width="130">
          <template #default="{ row }">
            <span
              class="category-tag"
              :style="{ background: row.category_color + '20', color: row.category_color }"
            >
              {{ row.category_name }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="purpose" label="用途" min-width="180" show-overflow-tooltip />
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            <span class="amount">¥{{ row.amount.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100" />
        <el-table-column label="关联任务" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.task_title">{{ row.task_title }}</span>
            <span v-else style="color: #909399;">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="submitted_by_name" label="申请人" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small" effect="dark">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="票据" width="80">
          <template #default="{ row }">
            <el-button
              v-if="row.receipt_url"
              size="small"
              type="primary"
              text
              @click="viewReceipt(row.receipt_url)"
            >
              查看
            </el-button>
            <span v-else style="color: #909399;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="申请时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              size="small"
              type="success"
              @click="openReviewDialog(row, 'approved')"
            >
              通过
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              size="small"
              type="danger"
              @click="openReviewDialog(row, 'rejected')"
            >
              驳回
            </el-button>
            <el-button
              size="small"
              type="primary"
              text
              @click="viewExpenseDetail(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="showAddCategoryDialog" title="新建预算分类" width="500px">
      <el-form :model="newCategory" label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="newCategory.name" placeholder="如：堵门红包、拍照道具" />
        </el-form-item>
        <el-form-item label="图标">
          <el-select v-model="newCategory.icon" placeholder="选择图标" style="width: 100%;">
            <el-option label="🧧 红包" value="🧧" />
            <el-option label="📸 拍照" value="📸" />
            <el-option label="🩹 应急" value="🩹" />
            <el-option label="🚗 交通" value="🚗" />
            <el-option label="💐 布置" value="💐" />
            <el-option label="🛍️ 采购" value="🛍️" />
            <el-option label="🍽️ 餐饮" value="🍽️" />
            <el-option label="💰 其他" value="💰" />
          </el-select>
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="newCategory.color" show-alpha />
        </el-form-item>
        <el-form-item label="预算上限">
          <el-input-number
            v-model="newCategory.budget_limit"
            :min="0"
            :step="100"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="说明">
          <el-input
            v-model="newCategory.description"
            type="textarea"
            :rows="2"
            placeholder="预算分类说明（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddCategoryDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateCategory">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEditCategoryDialog" title="编辑预算分类" width="500px">
      <el-form :model="editingCategory" label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="editingCategory.name" />
        </el-form-item>
        <el-form-item label="图标">
          <el-select v-model="editingCategory.icon" style="width: 100%;">
            <el-option label="🧧 红包" value="🧧" />
            <el-option label="📸 拍照" value="📸" />
            <el-option label="🩹 应急" value="🩹" />
            <el-option label="🚗 交通" value="🚗" />
            <el-option label="💐 布置" value="💐" />
            <el-option label="🛍️ 采购" value="🛍️" />
            <el-option label="🍽️ 餐饮" value="🍽️" />
            <el-option label="💰 其他" value="💰" />
          </el-select>
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="editingCategory.color" show-alpha />
        </el-form-item>
        <el-form-item label="预算上限">
          <el-input-number
            v-model="editingCategory.budget_limit"
            :min="0"
            :step="100"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="说明">
          <el-input
            v-model="editingCategory.description"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditCategoryDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateCategory">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAddExpenseDialog" title="申请费用报销" width="560px">
      <el-form :model="newExpense" label-width="100px">
        <el-form-item label="费用分类" required>
          <el-select v-model="newExpense.category_id" placeholder="选择预算分类" style="width: 100%;">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            >
              <span>{{ cat.icon }} {{ cat.name }}</span>
              <span style="color: #909399; margin-left: 8px;">
                预算: ¥{{ cat.budget_limit.toLocaleString() }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="关联任务">
          <el-select v-model="newExpense.task_id" placeholder="选择关联任务（可选）" clearable style="width: 100%;">
            <el-option
              v-for="task in tasks"
              :key="task.id"
              :label="task.title"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="金额" required>
          <el-input-number
            v-model="newExpense.amount"
            :min="0"
            :step="10"
            :precision="2"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="用途" required>
          <el-input
            v-model="newExpense.purpose"
            type="textarea"
            :rows="2"
            placeholder="请详细说明费用用途"
          />
        </el-form-item>
        <el-form-item label="支付方式">
          <el-select v-model="newExpense.payment_method" placeholder="选择支付方式" clearable style="width: 100%;">
            <el-option label="微信支付" value="微信支付" />
            <el-option label="支付宝" value="支付宝" />
            <el-option label="现金" value="现金" />
            <el-option label="银行卡" value="银行卡" />
            <el-option label="淘宝" value="淘宝" />
            <el-option label="京东" value="京东" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="申请人" required>
          <el-select v-model="newExpense.submitted_by" placeholder="选择申请人" style="width: 100%;">
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
        <el-form-item label="上传票据">
          <el-upload
            action=""
            :show-file-list="false"
            :before-upload="beforeReceiptUpload"
            accept="image/*"
          >
            <el-button size="small" type="primary">📷 上传票据</el-button>
            <div v-if="newExpense.receipt_url" style="margin-top: 10px;">
              <el-image
                :src="newExpense.receipt_url"
                fit="cover"
                style="width: 120px; height: 90px; border-radius: 4px;"
                :preview-src-list="[newExpense.receipt_url]"
              />
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetExpenseForm">取消</el-button>
        <el-button type="primary" @click="handleCreateExpense">提交申请</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showReviewDialog" :title="reviewTitle" width="500px">
      <div v-if="reviewingExpense" class="review-content">
        <div class="review-info">
          <p><strong>分类：</strong>{{ reviewingExpense.category_name }}</p>
          <p><strong>金额：</strong><span class="amount">¥{{ reviewingExpense.amount.toLocaleString() }}</span></p>
          <p><strong>用途：</strong>{{ reviewingExpense.purpose }}</p>
          <p><strong>申请人：</strong>{{ reviewingExpense.submitted_by_name }}</p>
          <p v-if="reviewingExpense.receipt_url">
            <strong>票据：</strong>
            <el-button size="small" type="primary" text @click="viewReceipt(reviewingExpense.receipt_url)">
              查看票据
            </el-button>
          </p>
        </div>
        <el-form label-width="80px">
          <el-form-item label="审核备注">
            <el-input
              v-model="reviewComment"
              type="textarea"
              :rows="3"
              placeholder="请填写审核备注（可选）"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button :type="reviewAction === 'approved' ? 'success' : 'danger'" @click="handleReview">
          {{ reviewAction === 'approved' ? '确认通过' : '确认驳回' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="费用详情" width="500px">
      <div v-if="selectedExpense" class="expense-detail">
        <div class="detail-row">
          <span class="detail-label">分类：</span>
          <span
            class="category-tag"
            :style="{ background: selectedExpense.category_color + '20', color: selectedExpense.category_color }"
          >
            {{ selectedExpense.category_name }}
          </span>
        </div>
        <div class="detail-row">
          <span class="detail-label">金额：</span>
          <span class="amount">¥{{ selectedExpense.amount.toLocaleString() }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">用途：</span>
          <span>{{ selectedExpense.purpose }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">支付方式：</span>
          <span>{{ selectedExpense.payment_method || '-' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">关联任务：</span>
          <span>{{ selectedExpense.task_title || '-' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">申请人：</span>
          <span>{{ selectedExpense.submitted_by_name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">状态：</span>
          <el-tag :type="getStatusType(selectedExpense.status)" size="small" effect="dark">
            {{ getStatusText(selectedExpense.status) }}
          </el-tag>
        </div>
        <div class="detail-row" v-if="selectedExpense.status !== 'pending'">
          <span class="detail-label">审核人：</span>
          <span>{{ selectedExpense.reviewed_by_name || '-' }}</span>
        </div>
        <div class="detail-row" v-if="selectedExpense.review_comment">
          <span class="detail-label">审核备注：</span>
          <span>{{ selectedExpense.review_comment }}</span>
        </div>
        <div class="detail-row" v-if="selectedExpense.receipt_url">
          <span class="detail-label">票据：</span>
          <el-image
            :src="selectedExpense.receipt_url"
            fit="cover"
            style="width: 200px; height: 150px; border-radius: 4px;"
            :preview-src-list="[selectedExpense.receipt_url]"
          />
        </div>
        <div class="detail-row">
          <span class="detail-label">申请时间：</span>
          <span>{{ formatDateTime(selectedExpense.created_at) }}</span>
        </div>
        <div class="detail-row" v-if="selectedExpense.reviewed_at">
          <span class="detail-label">审核时间：</span>
          <span>{{ formatDateTime(selectedExpense.reviewed_at) }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getBudgetCategories,
  getBudgetSummary,
  createBudgetCategory,
  updateBudgetCategory,
  deleteBudgetCategory,
  getExpenses,
  createExpense,
  reviewExpense,
  uploadReceiptIndependent
} from '@/api/budget'
import { getTasks } from '@/api/task'
import { getBridesmaids } from '@/api/bridesmaid'

const WEDDING_ID = 1

const loadingExpenses = ref(false)
const categories = ref([])
const expenses = ref([])
const tasks = ref([])
const bridesmaids = ref([])
const summary = ref({})
const activeTab = ref('all')
const filterCategoryId = ref(null)

const showAddCategoryDialog = ref(false)
const showEditCategoryDialog = ref(false)
const showAddExpenseDialog = ref(false)
const showReviewDialog = ref(false)
const showDetailDialog = ref(false)

const newCategory = ref({
  name: '',
  icon: '💰',
  color: '#409eff',
  budget_limit: 0,
  description: ''
})

const editingCategory = ref(null)

const newExpense = ref({
  category_id: null,
  task_id: null,
  amount: 0,
  purpose: '',
  payment_method: '',
  submitted_by: null,
  receipt_url: ''
})

const reviewingExpense = ref(null)
const reviewAction = ref('approved')
const reviewComment = ref('')
const selectedExpense = ref(null)

const pendingCount = computed(() => {
  return expenses.value.filter(e => e.status === 'pending').length
})

const filteredExpenses = computed(() => {
  let result = expenses.value
  if (activeTab.value !== 'all') {
    result = result.filter(e => e.status === activeTab.value)
  }
  if (filterCategoryId.value) {
    result = result.filter(e => e.category_id === filterCategoryId.value)
  }
  return result
})

const reviewTitle = computed(() => {
  return reviewAction.value === 'approved' ? '审核通过' : '审核驳回'
})

const getStatusText = (status) => {
  const map = { pending: '待审核', approved: '已通过', rejected: '已驳回' }
  return map[status] || status
}

const getStatusType = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return dateStr.replace('T', ' ').substring(0, 16)
}

const loadCategories = async () => {
  try {
    const res = await getBudgetCategories(WEDDING_ID)
    categories.value = res || []
  } catch (e) {
    console.error('加载预算分类失败', e)
  }
}

const loadSummary = async () => {
  try {
    const res = await getBudgetSummary(WEDDING_ID)
    summary.value = res || {}
  } catch (e) {
    console.error('加载预算汇总失败', e)
  }
}

const loadExpenses = async () => {
  loadingExpenses.value = true
  try {
    const params = { wedding_id: WEDDING_ID }
    if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }
    const res = await getExpenses(params)
    expenses.value = res || []
  } catch (e) {
    console.error('加载费用记录失败', e)
  } finally {
    loadingExpenses.value = false
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

const loadBridesmaids = async () => {
  try {
    const res = await getBridesmaids({ wedding_id: WEDDING_ID })
    bridesmaids.value = res || []
  } catch (e) {
    console.error('加载伴娘列表失败', e)
  }
}

const handleCreateCategory = async () => {
  if (!newCategory.value.name) {
    ElMessage.warning('请输入分类名称')
    return
  }
  try {
    const data = {
      wedding_id: WEDDING_ID,
      ...newCategory.value
    }
    await createBudgetCategory(data)
    ElMessage.success('预算分类创建成功')
    showAddCategoryDialog.value = false
    newCategory.value = { name: '', icon: '💰', color: '#409eff', budget_limit: 0, description: '' }
    await Promise.all([loadCategories(), loadSummary()])
  } catch (e) {
    ElMessage.error('创建失败')
  }
}

const editCategory = (category) => {
  editingCategory.value = { ...category }
  showEditCategoryDialog.value = true
}

const handleUpdateCategory = async () => {
  if (!editingCategory.value.name) {
    ElMessage.warning('请输入分类名称')
    return
  }
  try {
    await updateBudgetCategory(editingCategory.value.id, editingCategory.value)
    ElMessage.success('更新成功')
    showEditCategoryDialog.value = false
    await Promise.all([loadCategories(), loadSummary()])
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

const handleDeleteCategory = async (category) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类"${category.name}"吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await deleteBudgetCategory(category.id)
    ElMessage.success('删除成功')
    await Promise.all([loadCategories(), loadSummary()])
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e?.response?.data?.error || '删除失败')
    }
  }
}

const filterByCategory = (categoryId) => {
  filterCategoryId.value = filterCategoryId.value === categoryId ? null : categoryId
}

const resetExpenseForm = () => {
  newExpense.value = {
    category_id: null,
    task_id: null,
    amount: 0,
    purpose: '',
    payment_method: '',
    submitted_by: null,
    receipt_url: ''
  }
  showAddExpenseDialog.value = false
}

const beforeReceiptUpload = async (file) => {
  try {
    if (newExpense.value.receipt_url) {
      ElMessage.warning('请先提交当前报销再上传新票据')
      return false
    }
    const res = await uploadReceiptIndependent(file)
    if (res && res.receipt_url) {
      newExpense.value.receipt_url = res.receipt_url
      ElMessage.success('票据上传成功')
    }
  } catch (e) {
    ElMessage.error('上传失败')
  }
  return false
}

const handleCreateExpense = async () => {
  if (!newExpense.value.category_id || !newExpense.value.amount || !newExpense.value.purpose || !newExpense.value.submitted_by) {
    ElMessage.warning('请填写必填项')
    return
  }
  try {
    const data = {
      wedding_id: WEDDING_ID,
      category_id: newExpense.value.category_id,
      task_id: newExpense.value.task_id,
      amount: newExpense.value.amount,
      purpose: newExpense.value.purpose,
      payment_method: newExpense.value.payment_method,
      submitted_by: newExpense.value.submitted_by,
      receipt_url: newExpense.value.receipt_url
    }
    await createExpense(data)
    ElMessage.success('报销申请提交成功')
    resetExpenseForm()
    await Promise.all([loadExpenses(), loadCategories(), loadSummary()])
  } catch (e) {
    ElMessage.error('提交失败')
  }
}

const openReviewDialog = (expense, action) => {
  reviewingExpense.value = expense
  reviewAction.value = action
  reviewComment.value = ''
  showReviewDialog.value = true
}

const handleReview = async () => {
  try {
    await reviewExpense(reviewingExpense.value.id, {
      status: reviewAction.value,
      reviewed_by: 1,
      review_comment: reviewComment.value
    })
    ElMessage.success(reviewAction.value === 'approved' ? '已通过' : '已驳回')
    showReviewDialog.value = false
    await Promise.all([loadExpenses(), loadCategories(), loadSummary()])
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const viewExpenseDetail = (expense) => {
  selectedExpense.value = expense
  showDetailDialog.value = true
}

const viewReceipt = (url) => {
  window.open(url, '_blank')
}

onMounted(() => {
  loadCategories()
  loadSummary()
  loadExpenses()
  loadTasks()
  loadBridesmaids()
})
</script>

<style scoped>
.budget-page {
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

.budget-overview {
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

.stat-card.total-budget .stat-icon { background: #ecf5ff; }
.stat-card.total-budget .stat-value { color: #409eff; }
.stat-card.approved .stat-icon { background: #f0f9eb; }
.stat-card.approved .stat-value { color: #67c23a; }
.stat-card.pending .stat-icon { background: #fdf6ec; }
.stat-card.pending .stat-value { color: #e6a23c; }
.stat-card.remaining .stat-icon { background: #f0f0ff; }
.stat-card.remaining .stat-value { color: #9093ff; }
.stat-card.usage .stat-icon { background: #fef0f0; }
.stat-card.usage .stat-value { color: #f56c6c; }
.stat-card.over-budget .stat-icon { background: #fef0f0; }
.stat-card.over-budget .stat-value { color: #f56c6c; }

.content-row {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.category-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.category-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: all 0.3s;
  border: 2px solid transparent;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

.category-card.over-budget {
  border-color: #f56c6c;
  background: #fff5f5;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.category-icon {
  font-size: 20px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.category-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.category-actions {
  display: flex;
  gap: 4px;
}

.budget-amounts {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.amount-item {
  text-align: center;
}

.amount-label {
  display: block;
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.amount-value {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.progress-section {
  margin-bottom: 12px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
}

.category-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.expense-count {
  font-size: 12px;
  color: #909399;
}

.expenses-section {
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

.category-tag {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.amount {
  font-weight: 600;
  color: #f56c6c;
}

.review-content {
  padding: 10px 0;
}

.review-info {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.review-info p {
  margin-bottom: 8px;
}

.review-info p:last-child {
  margin-bottom: 0;
}

.expense-detail {
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
