import request from '../utils/request'

export function getPublicBanners() {
  return request({
    url: '/config/banners',
    method: 'get'
  })
}

export function getPublicSiteConfig() {
  return request({
    url: '/config/site',
    method: 'get'
  })
}

export function getPublicAbout() {
  return request({
    url: '/config/about',
    method: 'get'
  })
}

export function getPublicVisitSummary() {
  return request({
    url: '/visits/summary',
    method: 'get'
  })
}
