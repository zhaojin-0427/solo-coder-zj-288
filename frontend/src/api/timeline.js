import request from './request'

export function getTimeline(params = {}) {
  return request.get('/timeline/', { params })
}

export function getTimelineNode(id) {
  return request.get(`/timeline/${id}`)
}

export function createTimelineNode(data) {
  return request.post('/timeline/', data)
}

export function updateTimelineNode(id, data) {
  return request.put(`/timeline/${id}`, data)
}

export function deleteTimelineNode(id) {
  return request.delete(`/timeline/${id}`)
}

export function assignBridesmaidToNode(id, bridesmaidIds, role = '负责人') {
  return request.post(`/timeline/${id}/assign`, { bridesmaid_ids: bridesmaidIds, role })
}

export function updateNodeStatus(id, status) {
  return request.post(`/timeline/${id}/status`, { status })
}

export function reorderTimeline(nodeOrder) {
  return request.post('/timeline/reorder', { node_order: nodeOrder })
}
