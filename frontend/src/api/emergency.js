import request from './request'

export function getContacts(params = {}) {
  return request.get('/emergency/contacts', { params })
}

export function createContact(data) {
  return request.post('/emergency/contacts', data)
}

export function updateContact(id, data) {
  return request.put(`/emergency/contacts/${id}`, data)
}

export function deleteContact(id) {
  return request.delete(`/emergency/contacts/${id}`)
}
