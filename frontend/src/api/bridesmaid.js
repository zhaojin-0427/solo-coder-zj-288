import request from './request'

export function getBridesmaids(params = {}) {
  return request.get('/bridesmaids/', { params })
}

export function getBridesmaid(id) {
  return request.get(`/bridesmaids/${id}`)
}

export function createBridesmaid(data) {
  return request.post('/bridesmaids/', data)
}

export function updateBridesmaid(id, data) {
  return request.put(`/bridesmaids/${id}`, data)
}

export function deleteBridesmaid(id) {
  return request.delete(`/bridesmaids/${id}`)
}

export function getBridesmaidTasks(id) {
  return request.get(`/bridesmaids/${id}/tasks`)
}
