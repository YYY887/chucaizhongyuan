<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  routes: {
    type: Array,
    default: () => []
  },
  selectedRoute: {
    type: Object,
    default: null
  },
  selectedRegion: {
    type: String,
    default: ''
  },
  hoveredRoute: {
    type: Object,
    default: null
  },
  selectedAttraction: {
    type: Object,
    default: null
  }
})

// 验证坐标是否有效
function parseCoord(lng, lat) {
  const parsedLng = Number(lng)
  const parsedLat = Number(lat)

  if (
    !Number.isFinite(parsedLng) ||
    !Number.isFinite(parsedLat) ||
    parsedLng === 0 ||
    parsedLat === 0 ||
    parsedLng < -180 ||
    parsedLng > 180 ||
    parsedLat < -90 ||
    parsedLat > 90
  ) {
    return null
  }

  return [parsedLng, parsedLat]
}

function isValidCoord(lng, lat) {
  return parseCoord(lng, lat) !== null
}

function getRoutePoints(routes) {
  return routes.flatMap(route => {
    if (!Array.isArray(route.attractions)) return []

    return route.attractions
      .map(attr => parseCoord(attr.longitude, attr.latitude))
      .filter(Boolean)
  })
}

function fitMapToPoints(points) {
  if (!map || !AMap || !points.length) return

  if (points.length === 1) {
    map.setCenter(points[0])
    map.setZoom(13)
    return
  }

  const lngs = points.map(point => point[0])
  const lats = points.map(point => point[1])
  const southWest = new AMap.LngLat(Math.min(...lngs), Math.min(...lats))
  const northEast = new AMap.LngLat(Math.max(...lngs), Math.max(...lats))
  const bounds = new AMap.Bounds(southWest, northEast)

  map.setBounds(bounds, false, [100, 100, 100, 100])
}

const mapContainer = ref(null)
let map = null
let AMap = null
let polylines = {}
let markers = {}
let userLocationMarker = null

// 初始化地图
const initMap = async () => {
  console.log('开始初始化地图...')
  AMap = window.AMap
  if (!AMap) {
    console.error('高德地图 API 未加载')
    return
  }

  if (!mapContainer.value) {
    console.error('地图容器不存在')
    return
  }

  console.log('创建地图实例...')
  map = new AMap.Map(mapContainer.value, {
    zoom: 7,
    center: [113.625, 34.746],
    viewMode: '2D',
    showLabel: true
  })

  console.log('地图创建成功:', map)

  showUserLocation()

  if (props.routes.length > 0) {
    drawRoutes()
  }
}

// 监听路线数据变化 - 使用浅层监听
watch(() => props.routes.map(r => r.id).join(','), () => {
  console.log('路线列表变化，重新绘制')
  if (!map) return

  const newRoutes = props.routes

  if (!newRoutes.length) {
    // 清空所有路线
    Object.values(polylines).forEach(line => {
      if (line) {
        try { map.remove(line) } catch (e) {}
      }
    })
    Object.values(markers).forEach(marker => {
      if (marker) {
        try { map.remove(marker) } catch (e) {}
      }
    })
    polylines = {}
    markers = {}
    return
  }

  // 清除旧元素
  Object.values(polylines).forEach(line => {
    if (line) {
      try { map.remove(line) } catch (e) {}
    }
  })
  Object.values(markers).forEach(marker => {
    if (marker) {
      try { map.remove(marker) } catch (e) {}
    }
  })

  polylines = {}
  markers = {}

  // 重新绘制
  drawRoutes()

  // 自动调整视野
  fitMapToPoints(getRoutePoints(newRoutes))
})

// 监听选中路线变化
watch(() => props.selectedRoute, (newRoute, oldRoute) => {
  if (!map) return

  Object.keys(polylines).forEach(routeId => {
    if (polylines[routeId]) {
      polylines[routeId].setOptions({
        strokeWeight: 6,
        strokeOpacity: 0.85,
        zIndex: 50
      })
    }
  })

  if (newRoute && polylines[newRoute.id]) {
    polylines[newRoute.id].setOptions({
      strokeWeight: 10,
      strokeOpacity: 1,
      zIndex: 100
    })

    if (newRoute.attractions && newRoute.attractions.length > 0) {
      fitMapToPoints(getRoutePoints([newRoute]))
    }
  }
})

// 监听悬停路线变化
watch(() => props.hoveredRoute, (newRoute, oldRoute) => {
  if (!map) return

  if (oldRoute && polylines[oldRoute.id]) {
    polylines[oldRoute.id].setOptions({
      strokeWeight: 6,
      strokeOpacity: 0.85,
      zIndex: 50
    })
  }

  if (newRoute && polylines[newRoute.id]) {
    polylines[newRoute.id].setOptions({
      strokeWeight: 10,
      strokeOpacity: 1,
      zIndex: 100
    })
  }
})

// 监听选中景点变化
watch(() => props.selectedAttraction, (newAttr, oldAttr) => {
  if (!map || !newAttr) return

  if (!isValidCoord(newAttr.longitude, newAttr.latitude)) {
    console.warn(`景点 ${newAttr.name} 坐标无效，无法定位:`, newAttr.longitude, newAttr.latitude)
    return
  }

  const position = parseCoord(newAttr.longitude, newAttr.latitude)

  map.setCenter(position)
  map.setZoom(15)

  if (oldAttr) {
    const oldMarkerKey = `${oldAttr.id}`
    if (markers[oldMarkerKey]) {
      const oldContent = markers[oldMarkerKey].getContent()
      if (oldContent) {
        oldContent.style.transform = 'scale(1)'
        oldContent.style.zIndex = '100'
      }
    }
  }

  const markerKey = `${newAttr.id}`
  if (markers[markerKey]) {
    const marker = markers[markerKey]
    const originalContent = marker.getContent()

    if (originalContent) {
      originalContent.style.transform = 'scale(1.5)'
      originalContent.style.transition = 'transform 0.3s'
      originalContent.style.zIndex = '200'
    }

    const infoWindow = new AMap.InfoWindow({
      content: `<div style="padding: 12px; min-width: 200px;">
        <h4 style="margin: 0 0 8px 0; font-size: 15px; font-weight: 600; color: #333;">${newAttr.name}</h4>
        <p style="margin: 0; font-size: 13px; color: #666; line-height: 1.5;">${newAttr.description || ''}</p>
        ${newAttr.address ? `<p style="margin: 8px 0 0 0; font-size: 12px; color: #999;"><i class="amap-icon amap-icon-marker"></i> ${newAttr.address}</p>` : ''}
      </div>`,
      offset: new AMap.Pixel(0, -30)
    })
    infoWindow.open(map, marker.getPosition())
  }
})

// 获取并显示用户位置
const showUserLocation = () => {
  if (!map || !AMap) return

  AMap.plugin('AMap.Geolocation', () => {
    const geolocation = new AMap.Geolocation({
      enableHighAccuracy: true,
      timeout: 5000,
      position: 'RB',
      offset: new AMap.Pixel(10, 20),
      zoomToAccuracy: false,
      showButton: true,
      buttonPosition: 'RB'
    })

    geolocation.getCurrentPosition((status, result) => {
      if (status === 'complete') {
        const lng = result.position?.lng
        const lat = result.position?.lat

        if (!isValidCoord(lng, lat)) {
          console.warn('定位坐标无效:', lng, lat)
          return
        }

        const position = parseCoord(lng, lat)

        if (userLocationMarker) {
          map.remove(userLocationMarker)
        }

        const markerContent = document.createElement('div')
        markerContent.style.cssText = `
          width: 20px;
          height: 20px;
          background: #1890ff;
          border: 4px solid white;
          border-radius: 50%;
          box-shadow: 0 2px 8px rgba(24,144,255,0.5);
          position: relative;
        `

        const pulse = document.createElement('div')
        pulse.style.cssText = `
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 40px;
          height: 40px;
          background: rgba(24,144,255,0.3);
          border-radius: 50%;
          animation: pulse 2s infinite;
        `
        markerContent.appendChild(pulse)

        if (!document.getElementById('pulse-animation')) {
          const style = document.createElement('style')
          style.id = 'pulse-animation'
          style.textContent = `
            @keyframes pulse {
              0% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
              100% { transform: translate(-50%, -50%) scale(2); opacity: 0; }
            }
          `
          document.head.appendChild(style)
        }

        userLocationMarker = new AMap.Marker({
          position: position,
          content: markerContent,
          offset: new AMap.Pixel(-10, -10),
          zIndex: 200
        })

        map.add(userLocationMarker)

        userLocationMarker.on('click', () => {
          const infoWindow = new AMap.InfoWindow({
            content: `<div style="padding: 12px; min-width: 180px;">
              <h4 style="margin: 0 0 8px 0; font-size: 15px; font-weight: 600; color: #333;">我的位置</h4>
              <p style="margin: 0; font-size: 13px; color: #666;">${result.formattedAddress || '当前位置'}</p>
            </div>`,
            offset: new AMap.Pixel(0, -30)
          })
          infoWindow.open(map, position)
        })

        console.log('用户位置获取成功:', result)
      } else {
        console.warn('定位失败:', result)
      }
    })

    map.addControl(geolocation)
  })
}

// 绘制路线
const drawRoutes = () => {
  console.log('开始绘制路线...')
  if (!map) {
    console.error('地图未初始化')
    return
  }

  if (!props.routes.length) {
    console.log('没有路线数据')
    return
  }

  console.log('路线数量:', props.routes.length)

  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
    '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2'
  ]

  props.routes.forEach((route, index) => {
    console.log(`处理路线 ${index + 1}:`, route.name, '景点数:', route.attractions?.length)

    if (!route.attractions || route.attractions.length === 0) {
      console.log(`路线 ${route.name} 没有景点数据`)
      return
    }

    // 限制景点数量，防止卡死
    const maxAttractions = 50
    const limitedAttractions = route.attractions.slice(0, maxAttractions)
    if (route.attractions.length > maxAttractions) {
      console.warn(`路线 ${route.name} 景点过多(${route.attractions.length})，只显示前${maxAttractions}个`)
    }

    // 过滤有效坐标
    const path = limitedAttractions
      .map(attr => {
        const coord = parseCoord(attr.longitude, attr.latitude)
        if (!coord) {
          console.warn(`景点 ${attr.name} 坐标无效:`, attr.longitude, attr.latitude)
        }
        return coord
      })
      .filter(Boolean)

    console.log('路线坐标:', path)

    if (path.length === 0) {
      console.log(`路线 ${route.name} 没有有效坐标`)
      return
    }

    // 绘制路线
    const polyline = new AMap.Polyline({
      path: path,
      strokeColor: colors[index % colors.length],
      strokeWeight: 6,
      strokeOpacity: 0.85,
      strokeStyle: 'solid',
      lineJoin: 'round',
      lineCap: 'round',
      zIndex: 50
    })

    polylines[route.id] = polyline
    map.add(polyline)
    console.log('路线绘制完成:', route.name)

    // 添加景点标记 - 提前过滤出有效景点
    const validAttractions = limitedAttractions
      .map((attr, idx) => ({ attr, idx, coord: parseCoord(attr.longitude, attr.latitude) }))
      .filter(item => {
        if (!item.coord) {
          console.warn(`跳过景点 ${item.attr.name}，坐标无效:`, item.attr.longitude, item.attr.latitude)
          return false
        }
        return true
      })

    validAttractions.forEach(({ attr, idx, coord }) => {
      const [lng, lat] = coord

      const markerContent = document.createElement('div')
      markerContent.style.cssText = `
        width: 28px;
        height: 28px;
        background: ${colors[index % colors.length]};
        border: 3px solid white;
        border-radius: 50%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 700;
        color: white;
        cursor: pointer;
      `
      markerContent.textContent = idx + 1

      const marker = new AMap.Marker({
        position: new AMap.LngLat(lng, lat),
        content: markerContent,
        offset: new AMap.Pixel(-14, -14),
        zIndex: 100
      })

      markers[`${attr.id}`] = marker

      marker.on('click', () => {
        const infoWindow = new AMap.InfoWindow({
          content: `<div style="padding: 12px; min-width: 200px;">
            <h4 style="margin: 0 0 8px 0; font-size: 15px; font-weight: 600; color: #333;">${attr.name}</h4>
            <p style="margin: 0; font-size: 13px; color: #666; line-height: 1.5;">${attr.description || ''}</p>
            ${attr.address ? `<p style="margin: 8px 0 0 0; font-size: 12px; color: #999;">${attr.address}</p>` : ''}
          </div>`,
          offset: new AMap.Pixel(0, -30)
        })
        infoWindow.open(map, new AMap.LngLat(lng, lat))
      })

      map.add(marker)
    })
  })

  if (props.routes.length > 0) {
    fitMapToPoints(getRoutePoints(props.routes))
  }
}

onMounted(() => {
  console.log('AMap组件已挂载')
  console.log('地图容器:', mapContainer.value)
  console.log('路线数据:', props.routes)

  if (!window.AMap) {
    console.log('开始加载高德地图API...')
    const script = document.createElement('script')
    const key = import.meta.env.VITE_AMAP_WEB_KEY || '854bd7331e8ddaf7bc537278ad2676ff'
    console.log('使用的Key:', key)
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${key}`
    script.async = true
    script.onload = () => {
      console.log('高德地图API加载完成')
      initMap()
    }
    script.onerror = (error) => {
      console.error('高德地图API加载失败:', error)
    }
    document.head.appendChild(script)
  } else {
    console.log('高德地图API已存在，直接初始化')
    initMap()
  }
})

onBeforeUnmount(() => {
  if (map) {
    map.destroy()
  }
})
</script>

<template>
  <div ref="mapContainer" class="amap-container"></div>
</template>

<style scoped>
.amap-container {
  width: 100%;
  height: 100%;
}
</style>
