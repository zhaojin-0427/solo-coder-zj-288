import request from './request'

export function getGuests(params = {}) {
  return request.get('/guests/', { params })
}

export function getGuest(id) {
  return request.get(`/guests/${id}`)
}

export function createGuest(data) {
  return request.post('/guests/', data)
}

export function updateGuest(id, data) {
  return request.put(`/guests/${id}`, data)
}

export function deleteGuest(id) {
  return request.delete(`/guests/${id}`)
}

export function batchCreateGuests(data) {
  return request.post('/guests/batch', data)
}

export function getGuestGroups(params = {}) {
  return request.get('/guests/groups', { params })
}

export function getUnassignedTableGuests(params = {}) {
  return request.get('/guests/unassigned-table', { params })
}

export function assignTable(data) {
  return request.post('/guests/assign-table', data)
}
