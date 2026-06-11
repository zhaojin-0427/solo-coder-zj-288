import request from './request'

export function getTasks(params = {}) {
  return request.get('/tasks/', { params })
}

export function getTask(id) {
  return request.get(`/tasks/${id}`)
}

export function createTask(data) {
  return request.post('/tasks/', data)
}

export function updateTask(id, data) {
  return request.put(`/tasks/${id}`, data)
}

export function deleteTask(id) {
  return request.delete(`/tasks/${id}`)
}

export function assignTask(id, bridesmaidId, reason = '') {
  return request.post(`/tasks/${id}/assign`, { bridesmaid_id: bridesmaidId, reason })
}

export function claimTask(id, bridesmaidId) {
  return request.post(`/tasks/${id}/claim`, { bridesmaid_id: bridesmaidId })
}

export function updateProgress(id, progress) {
  return request.post(`/tasks/${id}/progress`, { progress })
}

export function getCategories() {
  return request.get('/tasks/categories')
}

export function uploadPhoto(taskId, file) {
  const formData = new FormData()
  formData.append('photo', file)
  return request.post(`/tasks/${taskId}/upload-photo`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
