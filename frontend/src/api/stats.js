import request from './request'

export function getOverviewStats(weddingId) {
  return request.get('/stats/overview', { params: { wedding_id: weddingId } })
}

export function getWorkloadDistribution(weddingId) {
  return request.get('/stats/workload', { params: { wedding_id: weddingId } })
}

export function getStatsByCategory(weddingId) {
  return request.get('/stats/by-category', { params: { wedding_id: weddingId } })
}

export function getOverdueTasks(weddingId) {
  return request.get('/stats/overdue-tasks', { params: { wedding_id: weddingId } })
}

export function getAdjustmentHistory(weddingId) {
  return request.get('/stats/adjustments', { params: { wedding_id: weddingId } })
}
