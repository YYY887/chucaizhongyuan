<template>
  <div class="amap-picker">
    <div v-if="mode === 'picker'" class="picker-toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索地点、道路、景点"
        clearable
        @keyup.enter="searchPlace"
      >
        <template #append>
          <el-button @click="searchPlace">搜索</el-button>
        </template>
      </el-input>
      <div class="picker-tip">点击地图或搜索结果可回填经纬度与地址。</div>
    </div>
    <div ref="mapRef" class="map-box"></div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getMapConfig } from '../api/admin'

const props = defineProps({
  mode: {
    type: String,
    default: 'picker'
  },
  modelValue: {
    type: Object,
    default: () => ({ longitude: null, latitude: null, address: '' })
  },
  routePoints: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const mapRef = ref()
const keyword = ref('')

let map
let AMapLib
let pickerMarker
let polyline
let routeMarkers = []
let autoComplete
let placeSearch
let infoWindow

function isValidCoord(lng, lat) {
  return Number.isFinite(Number(lng)) && Number.isFinite(Number(lat))
}

async function loadAmapScript() {
  if (window.AMap) {
    return window.AMap
  }

  const res = await getMapConfig()
  const key = res.data.amap_web_key
  if (!key || key === 'your_amap_web_key_here') {
    throw new Error('未配置高德地图 Web Key')
  }

  await new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${key}&plugin=AMap.AutoComplete,AMap.PlaceSearch`
    script.async = true
    script.onload = resolve
    script.onerror = reject
    document.head.appendChild(script)
  })

  return window.AMap
}

function updatePickerPosition(payload) {
  emit('update:modelValue', {
    longitude: payload.longitude,
    latitude: payload.latitude,
    address: payload.address || props.modelValue.address || ''
  })
}

function setPickerMarker(lng, lat, address = '') {
  if (!map || !AMapLib || !isValidCoord(lng, lat)) {
    return
  }

  const position = [Number(lng), Number(lat)]
  if (!pickerMarker) {
    pickerMarker = new AMapLib.Marker({
      position,
      draggable: true
    })
    pickerMarker.on('dragend', (event) => {
      const nextLng = event.lnglat.getLng()
      const nextLat = event.lnglat.getLat()
      updatePickerPosition({
        longitude: nextLng,
        latitude: nextLat,
        address
      })
    })
    map.add(pickerMarker)
  } else {
    pickerMarker.setPosition(position)
  }

  map.setCenter(position)
  map.setZoom(15)
  updatePickerPosition({ longitude: position[0], latitude: position[1], address })
}

function drawRoutePreview() {
  if (!map || !AMapLib || props.mode !== 'preview') {
    return
  }

  if (polyline) {
    map.remove(polyline)
    polyline = null
  }
  routeMarkers.forEach((marker) => map.remove(marker))
  routeMarkers = []

  const points = props.routePoints
    .filter((item) => isValidCoord(item.longitude, item.latitude))
    .map((item) => [Number(item.longitude), Number(item.latitude)])

  if (!points.length) {
    return
  }

  polyline = new AMapLib.Polyline({
    path: points,
    strokeColor: '#ff6b7a',
    strokeWeight: 8,
    strokeOpacity: 0.75,
    lineJoin: 'round',
    lineCap: 'round',
    showDir: true
  })
  map.add(polyline)

  routeMarkers = props.routePoints
    .filter((item) => isValidCoord(item.longitude, item.latitude))
    .map((item, index) => {
      const markerContent = document.createElement('div')
      markerContent.className = 'route-marker-badge'
      markerContent.textContent = String(index + 1)

      const marker = new AMapLib.Marker({
        position: [Number(item.longitude), Number(item.latitude)],
        content: markerContent,
        offset: new AMapLib.Pixel(-16, -16),
        zIndex: 120
      })
      marker.on('click', () => {
        if (!infoWindow) {
          infoWindow = new AMapLib.InfoWindow({ offset: new AMapLib.Pixel(0, -26) })
        }
        infoWindow.setContent(`
          <div style="padding:10px 12px; min-width: 180px;">
            <div style="font-size:14px; font-weight:700; color:#1f2937;">${item.name}</div>
            <div style="margin-top:6px; font-size:12px; line-height:1.6; color:#606266;">${item.address || '暂无地址'}</div>
          </div>
        `)
        infoWindow.open(map, marker.getPosition())
      })
      marker.on('mouseover', () => {
        if (!infoWindow) {
          infoWindow = new AMapLib.InfoWindow({ offset: new AMapLib.Pixel(0, -26) })
        }
        infoWindow.setContent(`
          <div style="padding:10px 12px; min-width: 180px;">
            <div style="font-size:14px; font-weight:700; color:#1f2937;">${item.name}</div>
            <div style="margin-top:6px; font-size:12px; line-height:1.6; color:#606266;">${item.address || '暂无地址'}</div>
          </div>
        `)
        infoWindow.open(map, marker.getPosition())
      })
      marker.on('mouseout', () => {
        infoWindow?.close()
      })
      map.add(marker)
      return marker
    })

  if (points.length === 1) {
    map.setCenter(points[0])
    map.setZoom(14)
    return
  }

  map.setFitView([...routeMarkers, polyline], false, [60, 60, 60, 60])
}

function initSearchPlugin() {
  if (props.mode !== 'picker' || !AMapLib) {
    return
  }
  autoComplete = new AMapLib.AutoComplete()
  placeSearch = new AMapLib.PlaceSearch({ map })
}

function searchPlace() {
  if (!keyword.value || !placeSearch) {
    return
  }

  placeSearch.search(keyword.value, (status, result) => {
    if (status !== 'complete' || !result.poiList?.pois?.length) {
      ElMessage.warning('未找到相关地点')
      return
    }

    const first = result.poiList.pois[0]
    if (!first.location) {
      ElMessage.warning('该地点没有可用坐标')
      return
    }

    const lng = first.location.lng
    const lat = first.location.lat
    const address = [first.cityname, first.adname, first.address].filter(Boolean).join('')
    setPickerMarker(lng, lat, address)
  })
}

async function initMap() {
  try {
    AMapLib = await loadAmapScript()
  } catch (error) {
    ElMessage.error(error.message || '高德地图加载失败')
    return
  }

  await nextTick()
  map = new AMapLib.Map(mapRef.value, {
    zoom: 12,
    center: [113.625, 34.7466],
    viewMode: '2D'
  })

  if (props.mode === 'picker') {
    initSearchPlugin()
    map.on('click', (event) => {
      setPickerMarker(event.lnglat.getLng(), event.lnglat.getLat(), props.modelValue.address)
    })
    if (isValidCoord(props.modelValue.longitude, props.modelValue.latitude)) {
      setPickerMarker(props.modelValue.longitude, props.modelValue.latitude, props.modelValue.address)
    }
  } else {
    drawRoutePreview()
  }
}

watch(
  () => [props.modelValue.longitude, props.modelValue.latitude],
  ([lng, lat]) => {
    if (props.mode === 'picker' && isValidCoord(lng, lat)) {
      setPickerMarker(lng, lat, props.modelValue.address)
    }
  }
)

watch(
  () => props.routePoints,
  () => {
    if (props.mode === 'preview') {
      drawRoutePreview()
    }
  },
  { deep: true }
)

onMounted(initMap)

onBeforeUnmount(() => {
  if (map) {
    map.destroy()
    map = null
  }
})
</script>

<style scoped>
.amap-picker {
  display: grid;
  gap: 12px;
}

.picker-toolbar {
  display: grid;
  gap: 8px;
}

.picker-tip {
  color: var(--admin-muted);
  font-size: 12px;
}

.map-box {
  width: 100%;
  height: 420px;
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  overflow: hidden;
}

:global(.route-marker-badge) {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #ff6b7a;
  color: #ffffff;
  border: 3px solid #ffffff;
  box-shadow: 0 8px 16px rgba(255, 107, 122, 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}
</style>
