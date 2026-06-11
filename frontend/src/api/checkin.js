import request from './request'

export function checkinGuest(guestId, data) {
  return request.post(`/checkin/${guestId}`, data)
}

export function updateCheckinStatus(guestId, data) {
  return request.put(`/checkin/${guestId}/status`, data)
}

export function getCheckinRecords(params = {}) {
  return request.get('/checkin/records', { params })
}

export function getCheckinStats(params = {}) {
  return request.get('/checkin/stats', { params })
}

export function searchGuestsForCheckin(params = {}) {
  return request.get('/checkin/search', { params })
}

export function batchCheckin(data) {
  return request.post('/checkin/batch', data)
}
