import request from './request'

export function getMaterials(weddingId) {
  return request.get('/material/items', { params: { wedding_id: weddingId } })
}

export function getMaterial(materialId) {
  return request.get(`/material/items/${materialId}`)
}

export function createMaterial(data) {
  return request.post('/material/items', data)
}

export function updateMaterial(materialId, data) {
  return request.put(`/material/items/${materialId}`, data)
}

export function deleteMaterial(materialId) {
  return request.delete(`/material/items/${materialId}`)
}

export function getBorrowings(params = {}) {
  return request.get('/material/borrowings', { params })
}

export function createBorrowing(data) {
  return request.post('/material/borrowings', data)
}

export function returnBorrowing(borrowingId, data) {
  return request.post(`/material/borrowings/${borrowingId}/return`, data)
}

export function getMaterialSummary(weddingId) {
  return request.get('/material/summary', { params: { wedding_id: weddingId } })
}

export function getMaterialStats(weddingId) {
  return request.get('/stats/material-stats', { params: { wedding_id: weddingId } })
}

export function getOverdueAlerts(weddingId) {
  return request.get('/material/overdue-alerts', { params: { wedding_id: weddingId } })
}

export function getAbnormalReturns(weddingId) {
  return request.get('/material/abnormal-returns', { params: { wedding_id: weddingId } })
}

export function getTaskMaterials(params = {}) {
  return request.get('/material/task-materials', { params })
}

export function linkTaskMaterial(data) {
  return request.post('/material/task-materials', data)
}

export function unlinkTaskMaterial(linkId) {
  return request.delete(`/material/task-materials/${linkId}`)
}

export function getTimelineMaterials(params = {}) {
  return request.get('/material/timeline-materials', { params })
}

export function linkTimelineMaterial(data) {
  return request.post('/material/timeline-materials', data)
}

export function unlinkTimelineMaterial(linkId) {
  return request.delete(`/material/timeline-materials/${linkId}`)
}
