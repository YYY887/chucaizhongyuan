import{A as e,E as t,F as n,L as r,M as i,j as a}from"./index-C6rAqp0S.js";import{t as o}from"./_plugin-vue_export-helper-BDNMzG2s.js";var s=o({__name:`AMap`,props:{routes:{type:Array,default:()=>[]},selectedRoute:{type:Object,default:null},selectedRegion:{type:String,default:``},hoveredRoute:{type:Object,default:null},selectedAttraction:{type:Object,default:null}},setup(o){let s=o;function c(e,t){let n=Number(e),r=Number(t);return!Number.isFinite(n)||!Number.isFinite(r)||n===0||r===0||n<-180||n>180||r<-90||r>90?null:[n,r]}function l(e,t){return c(e,t)!==null}function u(e){return e.flatMap(e=>Array.isArray(e.attractions)?e.attractions.map(e=>c(e.longitude,e.latitude)).filter(Boolean):[])}function d(e){if(!p||!m||!e.length)return;if(e.length===1){p.setCenter(e[0]),p.setZoom(13);return}let t=e.map(e=>e[0]),n=e.map(e=>e[1]),r=new m.LngLat(Math.min(...t),Math.min(...n)),i=new m.LngLat(Math.max(...t),Math.max(...n)),a=new m.Bounds(r,i);p.setBounds(a,!1,[100,100,100,100])}let f=r(null),p=null,m=null,h={},g={},_=null,v=async()=>{if(console.log(`开始初始化地图...`),m=window.AMap,!m){console.error(`高德地图 API 未加载`);return}if(!f.value){console.error(`地图容器不存在`);return}console.log(`创建地图实例...`),p=new m.Map(f.value,{zoom:7,center:[113.625,34.746],viewMode:`2D`,showLabel:!0}),console.log(`地图创建成功:`,p),y(),s.routes.length>0&&b()};n(()=>s.routes.map(e=>e.id).join(`,`),()=>{if(console.log(`路线列表变化，重新绘制`),!p)return;let e=s.routes;if(!e.length){Object.values(h).forEach(e=>{if(e)try{p.remove(e)}catch{}}),Object.values(g).forEach(e=>{if(e)try{p.remove(e)}catch{}}),h={},g={};return}Object.values(h).forEach(e=>{if(e)try{p.remove(e)}catch{}}),Object.values(g).forEach(e=>{if(e)try{p.remove(e)}catch{}}),h={},g={},b(),d(u(e))}),n(()=>s.selectedRoute,(e,t)=>{p&&(Object.keys(h).forEach(e=>{h[e]&&h[e].setOptions({strokeWeight:6,strokeOpacity:.85,zIndex:50})}),e&&h[e.id]&&(h[e.id].setOptions({strokeWeight:10,strokeOpacity:1,zIndex:100}),e.attractions&&e.attractions.length>0&&d(u([e]))))}),n(()=>s.hoveredRoute,(e,t)=>{p&&(t&&h[t.id]&&h[t.id].setOptions({strokeWeight:6,strokeOpacity:.85,zIndex:50}),e&&h[e.id]&&h[e.id].setOptions({strokeWeight:10,strokeOpacity:1,zIndex:100}))}),n(()=>s.selectedAttraction,(e,t)=>{if(!p||!e)return;if(!l(e.longitude,e.latitude)){console.warn(`景点 ${e.name} 坐标无效，无法定位:`,e.longitude,e.latitude);return}let n=c(e.longitude,e.latitude);if(p.setCenter(n),p.setZoom(15),t){let e=`${t.id}`;if(g[e]){let t=g[e].getContent();t&&(t.style.transform=`scale(1)`,t.style.zIndex=`100`)}}let r=`${e.id}`;if(g[r]){let t=g[r],n=t.getContent();n&&(n.style.transform=`scale(1.5)`,n.style.transition=`transform 0.3s`,n.style.zIndex=`200`),new m.InfoWindow({content:`<div style="padding: 12px; min-width: 200px;">
        <h4 style="margin: 0 0 8px 0; font-size: 15px; font-weight: 600; color: #333;">${e.name}</h4>
        <p style="margin: 0; font-size: 13px; color: #666; line-height: 1.5;">${e.description||``}</p>
        ${e.address?`<p style="margin: 8px 0 0 0; font-size: 12px; color: #999;"><i class="amap-icon amap-icon-marker"></i> ${e.address}</p>`:``}
      </div>`,offset:new m.Pixel(0,-30)}).open(p,t.getPosition())}});let y=()=>{!p||!m||m.plugin(`AMap.Geolocation`,()=>{let e=new m.Geolocation({enableHighAccuracy:!0,timeout:5e3,position:`RB`,offset:new m.Pixel(10,20),zoomToAccuracy:!1,showButton:!0,buttonPosition:`RB`});e.getCurrentPosition((e,t)=>{if(e===`complete`){let e=t.position?.lng,n=t.position?.lat;if(!l(e,n)){console.warn(`定位坐标无效:`,e,n);return}let r=c(e,n);_&&p.remove(_);let i=document.createElement(`div`);i.style.cssText=`
          width: 20px;
          height: 20px;
          background: #1890ff;
          border: 4px solid white;
          border-radius: 50%;
          box-shadow: 0 2px 8px rgba(24,144,255,0.5);
          position: relative;
        `;let a=document.createElement(`div`);if(a.style.cssText=`
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 40px;
          height: 40px;
          background: rgba(24,144,255,0.3);
          border-radius: 50%;
          animation: pulse 2s infinite;
        `,i.appendChild(a),!document.getElementById(`pulse-animation`)){let e=document.createElement(`style`);e.id=`pulse-animation`,e.textContent=`
            @keyframes pulse {
              0% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
              100% { transform: translate(-50%, -50%) scale(2); opacity: 0; }
            }
          `,document.head.appendChild(e)}_=new m.Marker({position:r,content:i,offset:new m.Pixel(-10,-10),zIndex:200}),p.add(_),_.on(`click`,()=>{new m.InfoWindow({content:`<div style="padding: 12px; min-width: 180px;">
              <h4 style="margin: 0 0 8px 0; font-size: 15px; font-weight: 600; color: #333;">我的位置</h4>
              <p style="margin: 0; font-size: 13px; color: #666;">${t.formattedAddress||`当前位置`}</p>
            </div>`,offset:new m.Pixel(0,-30)}).open(p,r)}),console.log(`用户位置获取成功:`,t)}else console.warn(`定位失败:`,t)}),p.addControl(e)})},b=()=>{if(console.log(`开始绘制路线...`),!p){console.error(`地图未初始化`);return}if(!s.routes.length){console.log(`没有路线数据`);return}console.log(`路线数量:`,s.routes.length);let e=[`#FF6B6B`,`#4ECDC4`,`#45B7D1`,`#FFA07A`,`#98D8C8`,`#F7DC6F`,`#BB8FCE`,`#85C1E2`];s.routes.forEach((t,n)=>{if(console.log(`处理路线 ${n+1}:`,t.name,`景点数:`,t.attractions?.length),!t.attractions||t.attractions.length===0){console.log(`路线 ${t.name} 没有景点数据`);return}let r=t.attractions.slice(0,50);t.attractions.length>50&&console.warn(`路线 ${t.name} 景点过多(${t.attractions.length})，只显示前50个`);let i=r.map(e=>{let t=c(e.longitude,e.latitude);return t||console.warn(`景点 ${e.name} 坐标无效:`,e.longitude,e.latitude),t}).filter(Boolean);if(console.log(`路线坐标:`,i),i.length===0){console.log(`路线 ${t.name} 没有有效坐标`);return}let a=new m.Polyline({path:i,strokeColor:e[n%e.length],strokeWeight:6,strokeOpacity:.85,strokeStyle:`solid`,lineJoin:`round`,lineCap:`round`,zIndex:50});h[t.id]=a,p.add(a),console.log(`路线绘制完成:`,t.name),r.map((e,t)=>({attr:e,idx:t,coord:c(e.longitude,e.latitude)})).filter(e=>e.coord?!0:(console.warn(`跳过景点 ${e.attr.name}，坐标无效:`,e.attr.longitude,e.attr.latitude),!1)).forEach(({attr:t,idx:r,coord:i})=>{let[a,o]=i,s=document.createElement(`div`);s.style.cssText=`
        width: 28px;
        height: 28px;
        background: ${e[n%e.length]};
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
      `,s.textContent=r+1;let c=new m.Marker({position:new m.LngLat(a,o),content:s,offset:new m.Pixel(-14,-14),zIndex:100});g[`${t.id}`]=c,c.on(`click`,()=>{new m.InfoWindow({content:`<div style="padding: 12px; min-width: 200px;">
            <h4 style="margin: 0 0 8px 0; font-size: 15px; font-weight: 600; color: #333;">${t.name}</h4>
            <p style="margin: 0; font-size: 13px; color: #666; line-height: 1.5;">${t.description||``}</p>
            ${t.address?`<p style="margin: 8px 0 0 0; font-size: 12px; color: #999;">${t.address}</p>`:``}
          </div>`,offset:new m.Pixel(0,-30)}).open(p,new m.LngLat(a,o))}),p.add(c)})}),s.routes.length>0&&d(u(s.routes))};return a(()=>{if(console.log(`AMap组件已挂载`),console.log(`地图容器:`,f.value),console.log(`路线数据:`,s.routes),window.AMap)console.log(`高德地图API已存在，直接初始化`),v();else{console.log(`开始加载高德地图API...`);let e=document.createElement(`script`),t=`854bd7331e8ddaf7bc537278ad2676ff`;console.log(`使用的Key:`,t),e.src=`https://webapi.amap.com/maps?v=2.0&key=${t}`,e.async=!0,e.onload=()=>{console.log(`高德地图API加载完成`),v()},e.onerror=e=>{console.error(`高德地图API加载失败:`,e)},document.head.appendChild(e)}}),e(()=>{p&&p.destroy()}),(e,n)=>(i(),t(`div`,{ref_key:`mapContainer`,ref:f,class:`amap-container`},null,512))}},[[`__scopeId`,`data-v-838b2298`]]);export{s as t};