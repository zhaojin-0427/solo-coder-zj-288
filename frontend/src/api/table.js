import request from './request'

export function getTables(params = {}) {
  return request.get('/tables/', { params })
}

export function getTable(id) {
  return request.get(`/tables/${id}`)
}

export function createTable(data) {
  return request.post('/tables/', data)
}

export function updateTable(id, data) {
  return request.put(`/tables/${id}`, data)
}

export function deleteTable(id) {
  return request.delete(`/tables/${id}`)
}

export function batchCreateTables(data) {
  return request.post('/tables/batch', data)
}

export function getTablesOverview(params = {}) {
  return request.get('/tables/overview', { params })
}
