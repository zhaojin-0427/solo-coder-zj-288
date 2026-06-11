import request from './request'

export function getBudgetCategories(weddingId) {
  return request.get('/budget/categories', { params: { wedding_id: weddingId } })
}

export function getBudgetCategory(categoryId) {
  return request.get(`/budget/categories/${categoryId}`)
}

export function createBudgetCategory(data) {
  return request.post('/budget/categories', data)
}

export function updateBudgetCategory(categoryId, data) {
  return request.put(`/budget/categories/${categoryId}`, data)
}

export function deleteBudgetCategory(categoryId) {
  return request.delete(`/budget/categories/${categoryId}`)
}

export function getExpenses(params = {}) {
  return request.get('/budget/expenses', { params })
}

export function getExpense(expenseId) {
  return request.get(`/budget/expenses/${expenseId}`)
}

export function createExpense(data) {
  return request.post('/budget/expenses', data)
}

export function reviewExpense(expenseId, data) {
  return request.post(`/budget/expenses/${expenseId}/review`, data)
}

export function uploadReceipt(expenseId, file) {
  const formData = new FormData()
  formData.append('receipt', file)
  return request.post(`/budget/expenses/${expenseId}/upload-receipt`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function uploadReceiptIndependent(file) {
  const formData = new FormData()
  formData.append('receipt', file)
  return request.post('/budget/upload-receipt', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function getBudgetSummary(weddingId) {
  return request.get('/budget/summary', { params: { wedding_id: weddingId } })
}

export function getBudgetStats(weddingId) {
  return request.get('/stats/budget-stats', { params: { wedding_id: weddingId } })
}
