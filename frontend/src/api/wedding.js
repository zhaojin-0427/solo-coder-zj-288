import request from './request'

export function getWeddings() {
  return request.get('/wedding/')
}

export function getWedding(id) {
  return request.get(`/wedding/${id}`)
}

export function createWedding(data) {
  return request.post('/wedding/', data)
}

export function updateWedding(id, data) {
  return request.put(`/wedding/${id}`, data)
}

export function deleteWedding(id) {
  return request.delete(`/wedding/${id}`)
}
