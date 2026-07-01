import request from '../utils/request'

// 获取路线列表
export function getRouteList(params) {
  return request({
    url: '/routes',
    method: 'get',
    params
  })
}

// 获取路线详情
export function getRouteDetail(id) {
  return request({
    url: `/routes/${id}`,
    method: 'get'
  })
}

// 获取区域列表
export function getRegionList() {
  return request({
    url: '/regions',
    method: 'get'
  })
}

// 获取景点详情
export function getAttractionDetail(id) {
  return request({
    url: `/attractions/${id}`,
    method: 'get'
  })
}

export function trackVisit(path) {
  return request({
    url: '/visits/track',
    method: 'post',
    data: { path }
  })
}
