import request from './request'

export function getRiskAssessment(weddingId) {
  return request.get('/risk/assessment', { params: { wedding_id: weddingId } })
}

export function getRiskOverview() {
  return request.get('/risk/overview')
}

export function getHighRiskTasks(weddingId) {
  return request.get('/risk/high-risk-tasks', { params: { wedding_id: weddingId } })
}

export function getRiskDistribution(weddingId) {
  return request.get('/stats/risk-distribution', { params: { wedding_id: weddingId } })
}
