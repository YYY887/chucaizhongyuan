import request from './request'

export const login = (data) => request.post('/admin/auth/login', data)
export const getProfile = () => request.get('/admin/profile')
export const uploadImage = (data) => request.post('/admin/uploads', data)

export const getVisitStats = () => request.get('/admin/visits')

export const getBanners = (params) => request.get('/admin/banners', { params })
export const createBanner = (data) => request.post('/admin/banners', data)
export const updateBanner = (id, data) => request.put(`/admin/banners/${id}`, data)
export const saveBannerOrder = (data) => request.put('/admin/banners/reorder', data)
export const deleteBanner = (id) => request.delete(`/admin/banners/${id}`)

export const getPoints = (params) => request.get('/admin/points', { params })
export const getPointDetail = (id) => request.get(`/admin/points/${id}`)
export const createPoint = (data) => request.post('/admin/points', data)
export const updatePoint = (id, data) => request.put(`/admin/points/${id}`, data)
export const deletePoint = (id) => request.delete(`/admin/points/${id}`)
export const importPoints = (data) => request.post('/admin/points/import', data)

export const getRoutes = (params) => request.get('/admin/routes', { params })
export const updateRoute = (id, data) => request.put(`/admin/routes/${id}`, data)
export const getRoutePoints = (id) => request.get(`/admin/routes/${id}/points`)
export const saveRoutePointOrder = (id, data) => request.put(`/admin/routes/${id}/points/order`, data)

export const getAbout = () => request.get('/admin/about')
export const updateAbout = (data) => request.put('/admin/about', data)
export const getSiteConfig = () => request.get('/admin/site-config')
export const updateSiteConfig = (data) => request.put('/admin/site-config', data)
export const getMapConfig = () => request.get('/config/map')
