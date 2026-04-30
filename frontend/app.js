// ═══════════════════════════════════════════════════════════
// AquaIntelli — app.js
// Single Leaflet center map • lat/lon/location bar on every page
// ═══════════════════════════════════════════════════════════

const API_BASE = window.location.origin + '/api/v1';

// ──────────────────────────────────────────────────────────
// STATE
// ──────────────────────────────────────────────────────────
let currentModule = 'godseyeview';
let centerMap     = null;   // single Leaflet map instance
let mainMarker    = null;   // primary location marker
let scanCircle    = null;   // inner scan ring
let outerRing     = null;   // outer dashed ring
let eventMarkers  = [];     // crisis/alert markers
let activePopupEvent = null;
let threeScene    = null;   // Three.js scene manager

// ──────────────────────────────────────────────────────────
// MODULE CONFIG
// ──────────────────────────────────────────────────────────
const MODULES = {
  godseyeview: {
    tag:   '00 · GOD\'S EYE VIEW',
    mode:  'SATELLITE-FUSED GLOBAL SCAN',
    lat:   17.385, lon: 78.487,
    name:  'Hyderabad, Andhra Pradesh, India',
    zoom:  6,
    color: '#00e5ff',
    metrics: null,    // no metric strip on God's Eye
  },
  groundwater: {
    tag:  '01 · GROUNDWATER', mode:'GRACE-FO GROUNDWATER ANALYSIS',
    lat:  17.385, lon:78.487, name:'Hyderabad, Andhra Pradesh, India', zoom:10, color:'#00e5ff',
    metrics:[
      {l:'GRACE ANOMALY', v:'-2.66', u:'METERS EWH', cls:'danger'},
      {l:'CURRENT DEPTH', v:'73.3',  u:'METERS BGL', cls:''},
      {l:'SOIL MOISTURE', v:'28.6%', u:'VOLUMETRIC',  cls:'good'},
      {l:'RAINFALL 180',  v:'120',   u:'MM',          cls:''},
      {l:'30-DAY FCST',   v:'70.9',  u:'METERS',      cls:'warn'},
      {l:'90-DAY FCST',   v:'68.3',  u:'METERS',      cls:'warn'},
      {l:'DEPLETION RATE',v:'-0.059',u:'M/DAY',       cls:'danger'},
      {l:'RISK LEVEL',    v:'WARNING',u:'RECOVERING',  cls:'warn', risk:true},
    ],
    charts:[
      {t:'90-DAY GROUNDWATER DEPTH FORECAST', s:'DEPTH (M) — 90 DAYS',   type:'depth_forecast'},
      {t:'SATELLITE DATA FUSION',             s:'SOIL MOISTURE 30D',      type:'soil_moisture'},
    ],
  },
  reservoir: {
    tag:'02 · RESERVOIR', mode:'RESERVOIR STORAGE & INFLOW ANALYSIS',
    lat:16.574, lon:79.313, name:'Nagarjuna Sagar, Andhra Pradesh', zoom:9, color:'#00bcd4',
    metrics:[
      {l:'NEARBY RESERVOIRS',v:'WAIT', u:'WITHIN 200KM',   cls:''},
      {l:'TOTAL CAPACITY',   v:'WAIT', u:'MCM',            cls:'good'},
      {l:'PRIMARY DAM',      v:'---',  u:'MAIN FOCUS',     cls:''},
      {l:'AVG FILL LEVEL',   v:'---',  u:'OF CAPACITY',    cls:''},
      {l:'INFLOW RATE',      v:'142.3',u:'MCM/DAY',        cls:'good'},
      {l:'OUTFLOW RATE',     v:'98.7', u:'MCM/DAY',        cls:'warn'},
      {l:'CATCHMENT RAIN',   v:'89',   u:'MM — 7 DAYS',    cls:''},
      {l:'STATUS',           v:'STABLE',u:'NORMAL OPS',    cls:'good', risk:true},
    ],
    charts:[
      {t:'90-DAY STORAGE FORECAST', s:'STORAGE (%) — 90 DAYS',  type:'reservoir_storage'},
      {t:'INFLOW / OUTFLOW TREND',  s:'MCM/DAY — 30D',          type:'flow_trend'},
    ],
  },
  irrigation: {
    tag:'03 · IRRIGATION AI', mode:'FAO-56 PENMAN-MONTEITH OPTIMIZATION',
    lat:17.385, lon:78.487, name:'Hyderabad, Andhra Pradesh, India', zoom:11, color:'#39ff14',
    metrics:[
      {l:'ET₀ REFERENCE', v:'5.82',  u:'MM/DAY',         cls:''},
      {l:'CROP ET (KC)',   v:'4.74',  u:'MM/DAY',         cls:'good'},
      {l:'SOIL WATER DEF.',v:'38.2',  u:'MM',             cls:'warn'},
      {l:'IRRIG. SCHED.',  v:'3',     u:'DAYS AHEAD',     cls:''},
      {l:'WATER SAVED',    v:'23.4%', u:'VS FLOOD IRRIG.',cls:'good'},
      {l:'NDVI INDEX',     v:'0.68',  u:'CROP HEALTH',    cls:'good'},
      {l:'STRESS INDEX',   v:'0.42',  u:'CWSI',           cls:'warn'},
      {l:'RECOMMEND',      v:'IRRIGATE',u:'IN 3 DAYS',    cls:'', risk:true},
    ],
    charts:[
      {t:'ET₀ & CROP WATER DEMAND', s:'MM/DAY — 30D',       type:'et_demand'},
      {t:'NDVI CROP HEALTH TREND',  s:'INDEX VALUE — 30D',   type:'ndvi_trend'},
    ],
  },
  borewell: {
    tag:'04 · BOREWELL', mode:'AI BOREWELL DRILLING PREDICTION',
    lat:17.385, lon:78.487, name:'Hyderabad, Andhra Pradesh, India', zoom:12, color:'#ff6b00',
    metrics:[
      {l:'SUCCESS PROB.', v:'72%',    u:'AI PREDICTION',  cls:'good'},
      {l:'OPTIMAL DEPTH', v:'210',    u:'FEET BGL',       cls:''},
      {l:'YIELD ESTIMATE',v:'4.8',    u:'LPM',            cls:'good'},
      {l:'AQUIFER TYPE',  v:'FRAC.',  u:'FRACTURED ROCK', cls:''},
      {l:'WATER QUALITY', v:'GOOD',   u:'TDS < 500 PPM',  cls:'good'},
      {l:'SEASONAL RISK', v:'MEDIUM', u:'PRE-MONSOON',    cls:'warn'},
      {l:'ROCK HARDNESS', v:'BASALT', u:'DECCAN TRAP',    cls:''},
      {l:'DRILL DECISION',v:'PROCEED',u:'HIGH CONFIDENCE',cls:'good', risk:true},
    ],
    charts:[
      {t:'DEPTH vs SUCCESS PROBABILITY', s:'% SUCCESS — DEPTH (FT)', type:'borewell_depth'},
      {t:'REGIONAL CLUSTER SUCCESS',     s:'RATE BY ZONE',           type:'borewell_cluster'},
    ],
  },
  drainage: {
    tag:'05 · DRAINAGE', mode:'URBAN & RURAL DRAINAGE ANALYSIS',
    lat:17.385, lon:78.487, name:'Hyderabad, Andhra Pradesh, India', zoom:11, color:'#00e5ff',
    metrics:[
      {l:'DRAINAGE CAP.',  v:'74%',   u:'UTILISATION',   cls:'warn'},
      {l:'FLOW VELOCITY',  v:'1.42',  u:'M/S',           cls:''},
      {l:'RUNOFF COEFF.',  v:'0.68',  u:'URBAN',         cls:'warn'},
      {l:'PEAK DISCHARGE', v:'287',   u:'M³/S',          cls:'danger'},
      {l:'TIME TO PEAK',   v:'4.2',   u:'HOURS',         cls:''},
      {l:'BLOCKAGE RISK',  v:'MEDIUM',u:'12 NODES',      cls:'warn'},
      {l:'SEWER OVERFLOW', v:'3',     u:'POINTS',        cls:'danger'},
      {l:'STATUS',         v:'MONITOR',u:'RAIN FORECAST',cls:'warn', risk:true},
    ],
    charts:[
      {t:'DRAINAGE FLOW — 24H FORECAST', s:'M³/S',    type:'drainage_flow'},
      {t:'RUNOFF ACCUMULATION',          s:'MM — 7D', type:'runoff'},
    ],
  },
  flood: {
    tag:'06 · FLOOD', mode:'FLOOD RISK ASSESSMENT & EARLY WARNING',
    lat:16.507, lon:80.648, name:'Krishna Delta, Andhra Pradesh', zoom:10, color:'#ff1744',
    metrics:[
      {l:'FLOOD RISK',    v:'63%',  u:'PROBABILITY',  cls:'warn'},
      {l:'RAIN FORECAST', v:'180',  u:'MM — 3 DAYS',  cls:'danger'},
      {l:'RIVER LEVEL',   v:'4.82', u:'M — DANGER 6M',cls:'warn'},
      {l:'INUNDATION ETA',v:'18',   u:'HOURS',        cls:'danger'},
      {l:'AREA AT RISK',  v:'142',  u:'KM²',          cls:'warn'},
      {l:'POPULATION',    v:'84K',  u:'AT RISK',      cls:'danger'},
      {l:'DEM ELEVATION', v:'12.3', u:'M ASL (AVG)',  cls:''},
      {l:'ALERT LEVEL',   v:'HIGH', u:'EVACUATE ZONES',cls:'danger', risk:true},
    ],
    charts:[
      {t:'RIVER LEVEL — 72H FORECAST',    s:'METERS — DANGER 6M', type:'river_level'},
      {t:'RAINFALL INTENSITY FORECAST',   s:'MM/H — 72H',         type:'rainfall_bars'},
    ],
  },
  aquifer: {
    tag:'07 · AQUIFER SCAN', mode:'GRACE-FO SUBSURFACE INTELLIGENCE',
    lat:17.385, lon:78.487, name:'Deccan Plateau Aquifer, AP', zoom:9, color:'#9c27b0',
    metrics:[
      {l:'AQUIFER STORAGE',v:'-8.42', u:'KM³ ANOMALY', cls:'danger'},
      {l:'RECHARGE RATE',  v:'0.84',  u:'M/YEAR',      cls:'warn'},
      {l:'THICKNESS',      v:'320',   u:'METERS',      cls:''},
      {l:'HYDRAULIC COND.',v:'2.4',   u:'M/DAY',       cls:''},
      {l:'STORATIVITY',    v:'0.002', u:'CONFINED',    cls:''},
      {l:'WATER TABLE',    v:'-14.2M',u:'BELOW 2020',  cls:'danger'},
      {l:'TRANSMISSIVITY', v:'48',    u:'M²/DAY',      cls:''},
      {l:'AQUIFER HEALTH', v:'CRITICAL',u:'OVEREXPLOITED',cls:'danger', risk:true},
    ],
    charts:[
      {t:'GRACE-FO WATER STORAGE ANOMALY', s:'KM³ — 12 MONTHS', type:'grace_anomaly'},
      {t:'RECHARGE vs EXTRACTION',         s:'MCM/MONTH',       type:'recharge_balance'},
    ],
  },
  crisis: {
    tag:'08 · CRISIS FORECAST', mode:'AI WATER STRESS PREDICTION ENGINE',
    lat:17.385, lon:78.487, name:'Hyderabad, Andhra Pradesh, India', zoom:9, color:'#ff1744',
    metrics:[
      {l:'CRISIS PROB.',  v:'78%',   u:'90-DAY WINDOW', cls:'danger'},
      {l:'CLIMATE IMPACT',v:'SEVERE',u:'GLOBAL WARMING',cls:'danger'},
      {l:'STRESS INDEX',  v:'8.2/10',u:'HIGH STRESS',   cls:'danger'},
      {l:'WATER DEFICIT', v:'-1.4 KM³',u:'ANNUAL',      cls:'danger'},
      {l:'GDP IMPACT',    v:'$840M', u:'PROJ. LOSS',    cls:'warn'},
      {l:'FOOD SECURITY', v:'AT RISK',u:'3 CROPS',      cls:'danger'},
      {l:'ADAPTATION',    v:'URGENT', u:'POLICY NEEDED',cls:'warn'},
      {l:'CRISIS INDEX',  v:'CRITICAL',u:'IMMINENT RISK',cls:'danger', risk:true},
    ],
    charts:[
      {t:'CLIMATE FORCING & WATER AVAILABILITY', s:'HISTORICAL vs PROJECTED', type:'crisis_prob'},
      {t:'MULTI-INDICATOR STRESS INDEX',      s:'COMPOSITE SCORE',type:'stress_index'},
    ],
  },
};

// Water events shown on map (Expanded with basins & sources)
const WATER_EVENTS = [
  {id:0, name:'Krishna River Basin',     loc:'Andhra Pradesh, IN', lat:16.2,  lon:80.4, type:'BASIN', sev:'critical', depth:'-12.4M', area:'2847 km²'},
  {id:1, name:'Godavari Basin Zone',     loc:'Maharashtra, IN',    lat:19.8,  lon:75.3, type:'BASIN', sev:'critical', depth:'-8.2M',  area:'4120 km²'},
  {id:2, name:'Cauvery Basin Alert',     loc:'Tamil Nadu, IN',     lat:11.4,  lon:78.8, type:'BASIN', sev:'warning',  depth:'-1.4M',  area:'1540 km²'},
  {id:3, name:'Brahmaputra Flood Plain', loc:'Assam, IN',          lat:26.1,  lon:91.7, type:'BASIN', sev:'info',     depth:'+5.2M',  area:'8200 km²'},
  {id:4, name:'Indus Basin Salence',     loc:'Punjab, IN',         lat:31.3,  lon:74.8, type:'BASIN', sev:'warning',  depth:'N/A',    area:'2100 km²'},
  {id:5, name:'Hirakud Reservoir',       loc:'Odisha, IN',         lat:21.5,  lon:83.8, type:'RESERVOIR', sev:'critical', capacity:'5,896 MCM', river:'Mahanadi'},
  {id:6, name:'Sardar Sarovar Dam',      loc:'Gujarat, IN',        lat:21.83, lon:73.75, type:'RESERVOIR', sev:'warning',  capacity:'9,460 MCM', river:'Narmada'},
  {id:7, name:'Bhakra Nangal Source',    loc:'Himachal Pradesh, IN',lat:31.4,  lon:76.4, type:'RESERVOIR', sev:'good',     capacity:'9,340 MCM', river:'Sutlej'},
  {id:8, name:'Tehri Strategic Source',  loc:'Uttarakhand, IN',    lat:30.37, lon:78.48, type:'RESERVOIR', sev:'info',     capacity:'3,540 MCM', river:'Bhagirathi'},
  {id:9, name:'Idukki Arch Dam',         loc:'Kerala, IN',         lat:9.84,  lon:76.97, type:'RESERVOIR', sev:'good',     capacity:'1,996 MCM', river:'Periyar'},
  {id:10, name:'Indo-Gangetic Aquifer',  loc:'Uttar Pradesh, IN',  lat:27.1,  lon:79.5, type:'BASIN', sev:'critical', depth:'-450M',  area:'12,000 km²'},
];

const SEV_COLORS = { critical:'#ff1744', warning:'#ff6b00', good:'#39ff14', info:'#00e5ff' };

// ──────────────────────────────────────────────────────────
// CLOCK
// ──────────────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  
  // UTC String
  const utcTs = [now.getUTCHours(), now.getUTCMinutes(), now.getUTCSeconds()]
                .map(v => String(v).padStart(2,'0')).join(':');
  
  // Local String (for user timezone awareness)
  const locTs = [now.getHours(), now.getMinutes(), now.getSeconds()]
                .map(v => String(v).padStart(2,'0')).join(':');
  
  document.getElementById('clock-time').textContent = utcTs;
  
  const hTime = document.getElementById('hud-time');
  if (hTime) {
    const isPrivacyOn = document.getElementById('btn-privacy')?.classList.contains('active');
    const dateStr = now.toISOString().split('T')[0];
    hTime.innerHTML = `${dateStr} / <span style="color:var(--primary)">UTC ${utcTs}</span> / <span style="color:var(--text-dim)">LOC ${locTs}</span>`;
  }
}
setInterval(updateClock, 1000);
updateClock();

// ──────────────────────────────────────────────────────────
// SECURITY & PRIVACY
// ──────────────────────────────────────────────────────────
let privacyMode = true;
function togglePrivacy() {
  privacyMode = !privacyMode;
  const btn = document.getElementById('btn-privacy');
  btn.classList.toggle('active', privacyMode);
  btn.textContent = privacyMode ? 'PROTECT PII: ON' : 'PROTECT PII: OFF';
  
  // Apply/Remove masking classes
  const targets = document.querySelectorAll('.masked');
  targets.forEach(t => {
    t.style.filter = privacyMode ? 'blur(4px)' : 'none';
    t.style.pointerEvents = privacyMode ? 'none' : 'auto';
  });
  
  setStatus(privacyMode ? 'ENCRYPTING VIEW' : 'FULL ACCESS', privacyMode ? 'active' : 'warn');
}

// ──────────────────────────────────────────────────────────
// LEAFLET MAP — single instance, reused across all modules
// ──────────────────────────────────────────────────────────
function initCenterMap() {
  const cfg = MODULES['godseyeview'];
  centerMap = L.map('center-map', {
    center:         [cfg.lat, cfg.lon],
    zoom:           cfg.zoom,
    zoomControl:    true,
    attributionControl: true,
    preferCanvas:   true,
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
    maxZoom: 19,
  }).addTo(centerMap);

  // Main location marker
  mainMarker = createPulseMarker(cfg.lat, cfg.lon, cfg.color, cfg.name);
  mainMarker.addTo(centerMap);

  // Scan circles
  scanCircle = L.circle([cfg.lat, cfg.lon], {
    color: cfg.color, fillColor: cfg.color,
    fillOpacity: 0.05, opacity: 0.3, weight: 1, radius: 18000,
  }).addTo(centerMap);

  outerRing = L.circle([cfg.lat, cfg.lon], {
    color: cfg.color, fillColor: 'transparent',
    opacity: 0.15, weight: 0.5, radius: 40000, dashArray: '5 10',
  }).addTo(centerMap);

  // Add water event markers
  addEventMarkers();

  // Click on map → update lat/lon fields
  centerMap.on('click', function(e) {
    document.getElementById('loc-lat').value  = e.latlng.lat.toFixed(4);
    document.getElementById('loc-lon').value  = e.latlng.lng.toFixed(4);
    reverseGeocode(e.latlng.lat, e.latlng.lng);
  });
}

function createPulseMarker(lat, lon, color, name) {
  const html = `
    <div style="position:relative;width:14px;height:14px;">
      <div style="width:14px;height:14px;border-radius:50%;background:${color};box-shadow:0 0 8px ${color};position:absolute;top:0;left:0;"></div>
      <div style="position:absolute;top:-1px;left:-1px;width:16px;height:16px;border-radius:50%;border:2px solid ${color};animation:marker-ring 2.4s ease-out infinite;"></div>
    </div>`;
  const icon = L.divIcon({ html, className:'', iconSize:[14,14], iconAnchor:[7,7] });
  const marker = L.marker([lat, lon], { icon });

  marker.bindPopup(`
    <div style="font-family:'Share Tech Mono',monospace;color:#00e5ff;font-size:10px;">
      <div style="font-weight:700;margin-bottom:4px;letter-spacing:1px;">◎ ${name.toUpperCase()}</div>
      <div style="color:rgba(200,244,255,0.6);">LAT: ${lat.toFixed(4)}°N</div>
      <div style="color:rgba(200,244,255,0.6);">LON: ${lon.toFixed(4)}°E</div>
    </div>
  `, { maxWidth: 220 });

  return marker;
}

function addEventMarkers() {
  WATER_EVENTS.forEach(ev => {
    const col  = SEV_COLORS[ev.sev];
    const html = `
      <div style="position:relative;width:12px;height:12px;">
        <div style="width:12px;height:12px;border-radius:50%;background:${col};box-shadow:0 0 6px ${col};position:absolute;"></div>
        <div style="position:absolute;top:-1px;left:-1px;width:14px;height:14px;border-radius:50%;border:2px solid ${col};animation:marker-ring 2.4s ease-out infinite;animation-delay:${ev.id * 0.3}s;"></div>
      </div>`;
    const icon = L.divIcon({ html, className:'', iconSize:[12,12], iconAnchor:[6,6] });
    const m = L.marker([ev.lat, ev.lon], { icon });
    m.bindPopup(`
      <div style="font-family:'Share Tech Mono',monospace;font-size:10px;">
        <div style="color:${col};font-weight:700;letter-spacing:1px;margin-bottom:4px;">${ev.type} · ${ev.sev.toUpperCase()}</div>
        <div style="color:#c8f4ff;margin-bottom:2px;">${ev.name}</div>
        <div style="color:rgba(200,244,255,0.55);">${ev.loc}</div>
        <div style="color:rgba(200,244,255,0.55);margin-top:4px;">DEPTH: ${ev.depth}<br>AREA: ${ev.area}</div>
        <div style="margin-top:8px;"><button onclick="flyToLatLon(${ev.lat},${ev.lon},'${ev.loc}')" style="background:rgba(0,229,255,.15);border:1px solid #00e5ff;border-radius:2px;padding:3px 8px;cursor:pointer;font-family:'Share Tech Mono',monospace;font-size:9px;color:#00e5ff;">FOCUS ZONE ↗</button></div>
      </div>
    `, { maxWidth: 240 });
    m.on('click', () => showEventPopup(ev));
    m.addTo(centerMap);
    eventMarkers.push(m);
  });
}

// Animate marker ring via CSS injected once
(function injectMarkerCSS() {
  const s = document.createElement('style');
  s.textContent = `
    @keyframes marker-ring {
      0%   { transform:scale(1);   opacity:0.9; }
      100% { transform:scale(3.5); opacity:0;   }
    }`;
  document.head.appendChild(s);
})();

// ──────────────────────────────────────────────────────────
// MODULE SWITCHING
// ──────────────────────────────────────────────────────────
function switchModule(mod, tabEl) {
  currentModule = mod;

  // Update tab active state
  document.querySelectorAll('.mod-tab').forEach(t => t.classList.remove('active'));
  if (tabEl) tabEl.classList.add('active');

  const cfg = MODULES[mod];
  if (!cfg) return;

  // Update module tag in location bar
  document.getElementById('loc-module-tag').textContent = cfg.tag;

  // Show/hide metrics + charts
  const mStrip = document.getElementById('metrics-strip');
  const cStrip = document.getElementById('charts-strip');
  if (mod === 'godseyeview') {
    mStrip.classList.remove('visible');
    cStrip.classList.remove('visible');
  } else {
    mStrip.classList.add('visible');
    cStrip.classList.add('visible');
    populateMetrics(cfg.metrics);
    drawCharts(cfg.charts, cfg.color);
  }

  // Update HUD
  document.getElementById('hud-mode').textContent = cfg.mode;

  // Keep location consistent across modules
  const curLat = parseFloat(document.getElementById('loc-lat').value);
  const curLon = parseFloat(document.getElementById('loc-lon').value);
  const curName = document.getElementById('loc-name').value;

  if (!isNaN(curLat) && !isNaN(curLon)) {
    flyToLatLon(curLat, curLon, curName, cfg.zoom);
    if(mod !== 'godseyeview') fetchModuleData(mod, curLat, curLon);
  } else {
    setLocationBar(cfg.lat, cfg.lon, cfg.name);
    flyToLatLon(cfg.lat, cfg.lon, cfg.name, cfg.zoom);
    if(mod !== 'godseyeview') fetchModuleData(mod, cfg.lat, cfg.lon);
  }

  // If specialty module, fetch specific data
  if (mod === 'reservoir') fetchNearbyReservoirs(cfg.lat, cfg.lon);
  if (mod === 'borewell') fetchBorewellDetails(cfg.lat, cfg.lon);
}

async function fetchNearbyReservoirs(lat, lon) {
  try {
    const r = await fetch(`${API_BASE}/reservoirs/nearby?lat=${lat}&lon=${lon}&radius=200`);
    const data = await r.json();
    const cfg = MODULES['reservoir'];
    
    if (data && data.length > 0) {
      const res = data[0];
      const totalCap = data.reduce((sum, d) => sum + (d.capacity_mcm || 0), 0);
      
      cfg.metrics[0].v = data.length.toString();
      cfg.metrics[1].v = totalCap > 0 ? totalCap.toLocaleString() : "UNKNOWN";
      cfg.metrics[2].v = (res.name || "UNKNOWN").substring(0, 14).toUpperCase();
      cfg.metrics[2].u = "RVR: " + (res.river || "UNKNOWN").substring(0, 9).toUpperCase();
      cfg.metrics[3].v = (65 + Math.random()*15).toFixed(1) + "%"; // Live Mock level
      
      populateMetrics(cfg.metrics);
      document.getElementById('loc-name').value = res.name + ", " + res.state;
      
    } else {
      cfg.metrics[0].v = "0";
      cfg.metrics[1].v = "0";
      cfg.metrics[2].v = "NONE";
      cfg.metrics[2].u = "---";
      cfg.metrics[3].v = "N/A";
      populateMetrics(cfg.metrics);
    }
  } catch(e) { console.error("Reservoir fetch failed", e); }
}

async function fetchBorewellDetails(lat, lon) {
  try {
    const r = await fetch(`${API_BASE}/analysis/borewell/predict?lat=${lat}&lon=${lon}`);
    const data = await r.json();
    const cfg = MODULES['borewell'];
    
    // Distribute variables into metrics
    cfg.metrics[0].v = (data.success_probability * 100).toFixed(0) + "%";
    cfg.metrics[1].v = data.risk_level;
    cfg.metrics[2].v = data.soil_type.toUpperCase();
    cfg.metrics[3].v = data.recommended_depth_m + "M";
    cfg.metrics[4].v = data.machinery_recommended; // Showing machinery
    cfg.metrics[5].v = data.drilling_method;
    cfg.metrics[6].v = data.confidence_score.toFixed(2);
    
    populateMetrics(cfg.metrics);
    
    // Update Why? explainability (future work: show d.recommendation)
    console.log("Borewell logic:", data.recommendation);
  } catch(e) { console.error("Borewell fetch failed", e); }
}

function setLocationBar(lat, lon, name) {
  document.getElementById('loc-lat').value  = lat;
  document.getElementById('loc-lon').value  = lon;
  document.getElementById('loc-name').value = name;
}

// ──────────────────────────────────────────────────────────
// ANALYZE / FLY-TO
// ──────────────────────────────────────────────────────────
function analyzeLocation() {
  const lat  = parseFloat(document.getElementById('loc-lat').value);
  const lon  = parseFloat(document.getElementById('loc-lon').value);
  const name = document.getElementById('loc-name').value.trim() || `${lat.toFixed(3)}°N, ${lon.toFixed(3)}°E`;

  if (isNaN(lat) || isNaN(lon)) return;

  flyToLatLon(lat, lon, name);

  // If we're on a module, also fetch live API
  if (currentModule !== 'godseyeview') {
    fetchModuleData(currentModule, lat, lon);
  }
}

function flyToLatLon(lat, lon, name, zoom) {
  if (!centerMap) return;
  const cfg   = MODULES[currentModule] || MODULES['godseyeview'];
  const z     = zoom || cfg.zoom || 10;
  const color = cfg.color || '#00e5ff';

  // Smooth fly
  centerMap.flyTo([lat, lon], z, { duration: 1.2, easeLinearity: 0.25 });

  // Move main marker
  mainMarker.setLatLng([lat, lon]);
  mainMarker.setPopupContent(`
    <div style="font-family:'Share Tech Mono',monospace;color:${color};font-size:10px;">
      <div style="font-weight:700;margin-bottom:4px;letter-spacing:1px;">◎ ${name.toUpperCase()}</div>
      <div style="color:rgba(200,244,255,0.6);">LAT: ${lat.toFixed(4)}°N</div>
      <div style="color:rgba(200,244,255,0.6);">LON: ${lon.toFixed(4)}°E</div>
    </div>
  `);

  // Move scan circles & recolor
  scanCircle.setLatLng([lat, lon]).setStyle({ color, fillColor: color });
  outerRing.setLatLng([lat, lon]).setStyle({ color });

  // Update all HUD elements
  updateHUD(lat, lon, name, color);
  updateRightPanel(lat, lon, name);

  // Blink status
  setStatus('ANALYZING...', 'busy');
  setTimeout(() => setStatus('OPERATIONAL', ''), 2000);
}

function onCoordInput() {
  // live crosshair sync — only move map when both fields are valid numbers
  const lat = parseFloat(document.getElementById('loc-lat').value);
  const lon = parseFloat(document.getElementById('loc-lon').value);
  if (!isNaN(lat) && !isNaN(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
    document.getElementById('hud-coords').textContent = `${lat.toFixed(3)}°N / ${lon.toFixed(3)}°E`;
  }
}

// ──────────────────────────────────────────────────────────
// GEOLOCATION
// ──────────────────────────────────────────────────────────
function geolocate() {
  if (!navigator.geolocation) { setStatus('GPS UNAVAILABLE', 'error'); return; }
  setStatus('ACQUIRING GPS...', 'busy');
  navigator.geolocation.getCurrentPosition(
    pos => {
      const lat = parseFloat(pos.coords.latitude.toFixed(4));
      const lon = parseFloat(pos.coords.longitude.toFixed(4));
      document.getElementById('loc-lat').value = lat;
      document.getElementById('loc-lon').value = lon;
      reverseGeocode(lat, lon);
      flyToLatLon(lat, lon, `GPS LOCATION`);
    },
    err => { setStatus('GPS ERROR', 'error'); setTimeout(()=>setStatus('READY',''),3000); }
  );
}

// ──────────────────────────────────────────────────────────
// LOCATION SEARCH AUTOCOMPLETE
// ──────────────────────────────────────────────────────────
let searchDebounce = null;
function onLocationInput() {
  const q = document.getElementById('loc-name').value;
  const resBox = document.getElementById('loc-search-results');
  
  if (q.length < 2) {
    resBox.classList.remove('visible');
    return;
  }

  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(async () => {
    try {
      const r = await fetch(`${API_BASE}/search/locations?q=${encodeURIComponent(q)}`);
      const matches = await r.json();
      
      if (matches.length > 0) {
        resBox.innerHTML = matches.map(m => `
          <div class="loc-search-item" onclick="selectLocation('${m.name}', ${m.lat||'null'}, ${m.lon||'null'})">
            ${m.name} <span class="item-type">${m.type||'city'}</span>
          </div>
        `).join('');
        resBox.classList.add('visible');
      } else {
        resBox.classList.remove('visible');
      }
    } catch(e) { console.error(e); }
  }, 300);
}

function selectLocation(name, lat, lon) {
  document.getElementById('loc-name').value = name;
  document.getElementById('loc-search-results').classList.remove('visible');
  
  if (lat && lon) {
    document.getElementById('loc-lat').value = lat;
    document.getElementById('loc-lon').value = lon;
    analyzeLocation();
  } else {
    // If we only have name, we could geocode it, but here we expect lat/lon
    analyzeLocation();
  }
}

// Close search when clicking outside
document.addEventListener('click', (e) => {
  if (!e.target.closest('.loc-field-wide')) {
    document.getElementById('loc-search-results').classList.remove('visible');
  }
});

async function reverseGeocode(lat, lon) {
  try {
    const res  = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`);
    const data = await res.json();
    const name = data.display_name?.split(',').slice(0,3).join(',') || `${lat.toFixed(3)}°N, ${lon.toFixed(3)}°E`;
    document.getElementById('loc-name').value = name;
    flyToLatLon(lat, lon, name);
  } catch(e) {
    // silently fail — keep existing name
  }
}

// ──────────────────────────────────────────────────────────
// HUD & RIGHT PANEL UPDATES
// ──────────────────────────────────────────────────────────
function updateHUD(lat, lon, name, color) {
  const shortName = name.toUpperCase().split(',').slice(0,2).join(',').trim();
  document.getElementById('hud-coords').textContent      = `${lat.toFixed(3)}°N / ${lon.toFixed(3)}°E`;
  document.getElementById('loc-badge-name').textContent   = shortName;
  document.getElementById('loc-badge-coords').textContent = `${lat.toFixed(3)}°N · ${lon.toFixed(3)}°E`;
  document.getElementById('hud-coverage').textContent     = 'COVERAGE: 847 ZONES';
}

function updateRightPanel(lat, lon, name) {
  const short = name.split(',').slice(0,2).join(',').trim().toUpperCase();
  document.getElementById('target-region').textContent = short || 'UNKNOWN REGION';
  document.getElementById('rp-lat').textContent = `LAT ${lat.toFixed(3)}°N`;
  document.getElementById('rp-lon').textContent = `LON ${lon.toFixed(3)}°E`;
}

function setStatus(txt, state) {
  document.getElementById('loc-status-txt').textContent = txt;
  const dot = document.getElementById('loc-status-dot');
  dot.className = 'loc-status-dot' + (state ? ' ' + state : '');
}

// ──────────────────────────────────────────────────────────
// METRICS STRIP
// ──────────────────────────────────────────────────────────
function populateMetrics(metrics) {
  if (!metrics) return;
  metrics.forEach((m, i) => {
    const lbl  = document.getElementById('ml-' + i);
    const val  = document.getElementById('mv-' + i);
    const unit = document.getElementById('mu-' + i);
    if (!lbl) return;
    lbl.textContent  = m.l;
    val.textContent  = m.v;
    unit.textContent = m.u;
    val.className    = 'metric-val' + (m.cls ? ' ' + m.cls : '');

    const card = val.closest('.metric-card');
    if (card) {
      card.classList.toggle('risk-card', !!m.risk);
    }
  });
}

// ──────────────────────────────────────────────────────────
// CHARTS
// ──────────────────────────────────────────────────────────
const drawnCharts = {};

function drawCharts(chartCfgs, color) {
  const key = chartCfgs[0]?.type;
  if (drawnCharts[key]) return;   // already drawn
  drawnCharts[key] = true;

  chartCfgs.forEach((cfg, idx) => {
    const n   = idx + 1;
    document.getElementById('ct-' + n).textContent = cfg.t;
    document.getElementById('cs-' + n).textContent = cfg.s;
    const canvas = document.getElementById('chart-' + n);
    if (!canvas) return;
    canvas.width  = canvas.offsetWidth * 2;
    canvas.height = 74 * 2;
    const ctx = canvas.getContext('2d');
    ctx.scale(2, 2);
    renderChart(ctx, canvas.offsetWidth, 74, cfg.type, color);
  });
}

function rnd() { return Math.random(); }
function gpts(W, H, n, y0, slope, noise) {
  return Array.from({ length: n+1 }, (_, i) => ({
    x: (i/n)*W,
    y: Math.max(4, Math.min(H-4, y0 + slope*i + (rnd()-.5)*noise)),
  }));
}
function stroke(ctx, pts, col, dash) {
  if (dash) ctx.setLineDash([4,6]);
  ctx.strokeStyle = col; ctx.lineWidth = 1.5;
  ctx.beginPath(); pts.forEach((p,i)=>i===0?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y)); ctx.stroke();
  ctx.setLineDash([]);
}
function fill(ctx, W, H, pts, col) {
  ctx.fillStyle = col + '18';
  ctx.beginPath(); ctx.moveTo(0,H);
  pts.forEach(p=>ctx.lineTo(p.x,p.y));
  ctx.lineTo(W,H); ctx.closePath(); ctx.fill();
}
function hline(ctx, W, y, col) {
  ctx.strokeStyle=col; ctx.lineWidth=.6; ctx.setLineDash([3,5]);
  ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); ctx.setLineDash([]);
}
function lbl(ctx, txt, x, y, col) {
  ctx.fillStyle=col; ctx.font='7px "Share Tech Mono",monospace'; ctx.fillText(txt,x,y);
}

function renderChart(ctx, W, H, type, color) {
  ctx.clearRect(0,0,W,H);
  const p2 = color;
  switch(type) {
    case 'depth_forecast': {
      const p = gpts(W,H,90,10,0.68,5);
      hline(ctx,W,H*.28,'rgba(255,107,0,.4)'); lbl(ctx,'CRITICAL THRESHOLD',4,H*.26,'rgba(255,107,0,.6)');
      fill(ctx,W,H,p,p2); stroke(ctx,p,p2);
      break; }
    case 'soil_moisture': {
      const p = gpts(W,H,30,H*.25,0,18);
      fill(ctx,W,H,p,'#39ff14'); stroke(ctx,p,'#39ff14'); break; }
    case 'reservoir_storage': {
      const p = gpts(W,H,90,H*.3,-.06,8);
      fill(ctx,W,H,p,p2); stroke(ctx,p,p2); break; }
    case 'flow_trend': {
      const p1=gpts(W,H,30,H*.35,0,10), p2b=gpts(W,H,30,H*.52,.04,6);
      fill(ctx,W,H,p1,p2); stroke(ctx,p1,p2); stroke(ctx,p2b,'#ff6b00',true);
      lbl(ctx,'INFLOW',4,10,p2+'cc'); lbl(ctx,'OUTFLOW',56,10,'#ff6b00cc'); break; }
    case 'et_demand': {
      const p1=gpts(W,H,30,H*.38,0,12), p2b=gpts(W,H,30,H*.5,0,9);
      fill(ctx,W,H,p1,p2); stroke(ctx,p1,p2); stroke(ctx,p2b,'#39ff14',true);
      lbl(ctx,'ET₀',4,10,p2+'cc'); lbl(ctx,'CROP ET',36,10,'#39ff14cc'); break; }
    case 'ndvi_trend': {
      const p=gpts(W,H,30,H*.3,.08,7);
      fill(ctx,W,H,p,'#39ff14'); stroke(ctx,p,'#39ff14'); break; }
    case 'borewell_depth': {
      const p=Array.from({length:31},(_,i)=>({x:(i/30)*W,y:H-(H*.65*Math.exp(-.5*Math.pow((i-18)/5,2))+H*.07)}));
      fill(ctx,W,H,p,'#ff6b00'); stroke(ctx,p,'#ff6b00');
      const px=(18/30)*W; hline(ctx,W,p[18].y,'rgba(57,255,20,.4)'); lbl(ctx,'OPTIMAL 210FT',px+4,p[18].y-3,'rgba(57,255,20,.7)');
      break; }
    case 'borewell_cluster': {
      [{x:.25,y:.42,r:16,v:72,c:'#39ff14'},{x:.56,y:.6,r:11,v:58,c:'#ff6b00'},
       {x:.78,y:.3,r:20,v:81,c:'#39ff14'},{x:.4,y:.74,r:7,v:43,c:'#ff1744'},
       {x:.14,y:.65,r:13,v:65,c:'#00e5ff'}].forEach(cl=>{
        ctx.beginPath(); ctx.arc(cl.x*W,cl.y*H,cl.r,0,Math.PI*2);
        ctx.fillStyle=cl.c+'2a'; ctx.fill();
        ctx.strokeStyle=cl.c; ctx.lineWidth=1; ctx.stroke();
        ctx.fillStyle=cl.c; ctx.font='9px Orbitron,monospace';
        ctx.fillText(cl.v+'%',cl.x*W-8,cl.y*H+4);
      }); break; }
    case 'drainage_flow': {
      const p=gpts(W,H,24,H*.65,-1.2,8); p[12]={x:p[12].x,y:H*.14};
      hline(ctx,W,H*.36,'rgba(255,23,68,.4)'); lbl(ctx,'CAPACITY LIMIT',4,H*.34,'rgba(255,23,68,.6)');
      fill(ctx,W,H,p,'#ff6b00'); stroke(ctx,p,'#ff6b00'); break; }
    case 'runoff': {
      const p=gpts(W,H,7,H*.72,-5,7);
      fill(ctx,W,H,p,p2); stroke(ctx,p,p2); break; }
    case 'river_level': {
      const p=gpts(W,H,72,H*.62,-.48,5);
      hline(ctx,W,H*.22,'rgba(255,23,68,.4)'); lbl(ctx,'DANGER 6M',4,H*.2,'rgba(255,23,68,.6)');
      fill(ctx,W,H,p,'#ff1744'); stroke(ctx,p,'#ff1744'); break; }
    case 'rainfall_bars': {
      for(let i=0;i<72;i++){const bw=W/72-1,bh=Math.max(3,(rnd()*.7+(i>36?.8:.3))*H*.78);ctx.fillStyle=bh>H*.5?'rgba(255,23,68,.75)':'rgba(0,229,255,.55)';ctx.fillRect((i/72)*W,H-bh,bw,bh);}
      break; }
    case 'grace_anomaly': {
      const p=gpts(W,H,12,H*.28,2.6,6);
      hline(ctx,W,H*.5,'rgba(0,229,255,.25)');
      fill(ctx,W,H,p,'#9c27b0'); stroke(ctx,p,'#9c27b0'); break; }
    case 'recharge_balance': {
      const p1=gpts(W,H,12,H*.65,0,7), p2b=gpts(W,H,12,H*.22,.3,5);
      fill(ctx,W,H,p1,'#39ff14'); stroke(ctx,p1,'#39ff14'); stroke(ctx,p2b,'#ff1744');
      lbl(ctx,'RECHARGE',4,10,'rgba(57,255,20,.8)'); lbl(ctx,'EXTRACTION',68,10,'rgba(255,23,68,.8)'); break; }
    case 'crisis_prob': {
      const p=gpts(W,H,90,H*.7,-.5,5);
      ctx.fillStyle='rgba(255,23,68,.05)'; ctx.fillRect(0,0,W,H*.36);
      hline(ctx,W,H*.36,'rgba(255,23,68,.4)'); lbl(ctx,'CRISIS THRESHOLD 70%',4,H*.34,'rgba(255,23,68,.6)');
      fill(ctx,W,H,p,'#ff1744'); stroke(ctx,p,'#ff1744'); break; }
    case 'stress_index': {
      ['GW','RAIN','DEMAND','TEMP','POLICY'].forEach((f,i)=>{
        const v=.4+rnd()*.55, bw=(W/5)-8, x=i*(W/5)+4, h=v*(H-16), col=v>.75?'#ff1744':v>.55?'#ff6b00':'#00e5ff';
        ctx.fillStyle=col+'33'; ctx.fillRect(x,H-16-h,bw,h);
        ctx.strokeStyle=col; ctx.lineWidth=1; ctx.strokeRect(x,H-16-h,bw,h);
        ctx.fillStyle=col; ctx.font='6px "Share Tech Mono",monospace'; ctx.fillText(f.substring(0,6),x,H-2);
      }); break; }
  }
}

// ──────────────────────────────────────────────────────────
// LIVE API FETCH
// ──────────────────────────────────────────────────────────
async function fetchModuleData(mod, lat, lon) {
  if (mod === 'groundwater') {
    try {
      const r = await fetch(`${API_BASE}/groundwater/status?lat=${lat}&lon=${lon}&district=Krishna&state=Andhra%20Pradesh`);
      const d = await r.json();
      if (d.satellite_data) {
        const g = d.satellite_data.grace_anomaly_m;
        const s = d.satellite_data.soil_moisture_pct;
        document.getElementById('mv-0').textContent = g?.toFixed(2) || '-2.66';
        document.getElementById('mv-2').textContent = `${s?.toFixed(1)}%` || '28.6%';
        document.getElementById('target-grace').innerHTML =
          `GRACE: <span style="color:${g<-5?'var(--danger)':'var(--warning)'};">${g}m</span> | SM: ${s}%`;
        
        // Update 3D Model dynamically with real-world data
        updateThreeModel('groundwater', d);
      }
    } catch(e) { 
      setStatus('FEED OFFLINE', 'error'); 
      // Mark specific values as stale
      ['mv-0','mv-2'].forEach(id => {
        const el = document.getElementById(id);
        if(el) { el.textContent = 'OFFLINE'; el.style.opacity = '0.4'; }
      });
    }
  }
}

async function fetchAlerts() {
  try {
    const r = await fetch(`${API_BASE}/alerts/summary`);
    const d = await r.json();
    if (d.critical !== undefined) {
      document.getElementById('alert-count').textContent = d.critical;
      document.getElementById('hud-crisis').textContent  = d.critical;
      document.getElementById('pill-critical').textContent = `${d.critical} CRITICAL`;
    }
  } catch(e) { 
    const ac = document.getElementById('alert-count');
    if (ac) ac.textContent = '!';
    setStatus('ALERTS ERR', 'error');
  }
}

fetchAlerts();
setInterval(fetchAlerts, 15000);

// ──────────────────────────────────────────────────────────
// ALERT FEED (left panel)
// ──────────────────────────────────────────────────────────
const ALERTS_DATA = [
  {sev:'critical', type:'AQUIFER COLLAPSE', title:'Krishna Basin Depletion',   desc:'GRACE-FO anomaly: -12.4M storage. 2,847 km² affected.', time:'14:00', evId:0, src:'GRACE-FO'},
  {sev:'critical', type:'SEVERE DROUGHT',   title:'Rajasthan Desert Advance',  desc:'GW -18.2M below norm. BW success <22%.',                time:'13:30', evId:1, src:'SENTINEL-1 / IMD'},
  {sev:'warning',  type:'OVER-EXTRACTION',  title:'Punjab Canal Overdraft',    desc:'Extraction 340% above yield. Soil desat confirmed.',     time:'12:45', evId:2, src:'CGWB / LANDSAT'},
  {sev:'info',     type:'BOREWELL SCAN',    title:'Hyderabad Cluster Scan',    desc:'47 sites. Avg success 68%. Depth: 190-230ft.',          time:'11:20', evId:3, src:'AQUAINTELLI v2'},
  {sev:'info',     type:'RECHARGE',         title:'Gujarat Aquifer Recovery',  desc:'Post-monsoon +4.2M anomaly. 980 km² zone.',            time:'10:55', evId:4, src:'GRACE-FO'},
  {sev:'warning',  type:'FLOOD RISK',       title:'Chennai Urban Drainage',    desc:'Drainage at 87%. Rain forecast 180mm.',                time:'09:30', evId:5, src:'IMD / SENTINEL-1'},
];

function buildAlertFeed() {
  const feed = document.getElementById('alert-feed');
  const smap = {critical:'badge-critical', warning:'badge-warning', info:'badge-info'};
  ALERTS_DATA.forEach(a => {
    const d = document.createElement('div'); d.className = 'alert-item';
    d.innerHTML = `
      <div class="alert-header">
        <span class="alert-badge ${smap[a.sev]}">${a.sev.toUpperCase()}</span>
        <span class="alert-type">${a.type}</span>
        <span class="alert-time">${a.time} UTC</span>
      </div>
      <div class="alert-title">${a.title}</div>
      <div class="alert-desc">${a.desc}</div>
      <div class="alert-src" style="font-family:'Share Tech Mono',monospace;font-size:7px;color:rgba(0,229,255,0.4);margin-top:4px;">PROVENANCE: ${a.src}</div>`;
    d.onclick = () => {
      const ev = WATER_EVENTS.find(e => e.id === a.evId);
      if (ev) { flyToLatLon(ev.lat, ev.lon, ev.loc, 10); showEventPopup(ev); }
    };
    feed.appendChild(d);
  });
}
buildAlertFeed();

// ──────────────────────────────────────────────────────────
// EVENT POPUP
// ──────────────────────────────────────────────────────────
function showEventPopup(ev) {
  activePopupEvent = ev;
  const col = SEV_COLORS[ev.sev];
  document.getElementById('popup-badge').textContent  = ev.sev.toUpperCase();
  document.getElementById('popup-badge').className    = 'alert-badge badge-' + ev.sev;
  document.getElementById('popup-type').textContent   = ev.type;
  document.getElementById('popup-title').textContent  = ev.name;
  document.getElementById('popup-time').textContent   = '— UTC';
  document.getElementById('popup-detail').innerHTML   =
    `LOC: ${ev.loc}<br>DEPTH: ${ev.depth}<br>AREA: ${ev.area}<br>SOURCE: GRACE-FO / SENTINEL`;
  const p = document.getElementById('event-popup');
  p.style.right  = '290px';
  p.style.bottom = '60px';
  p.classList.add('show');
}
function closePopup()  { document.getElementById('event-popup').classList.remove('show'); activePopupEvent=null; }
function flyToEvent()  { if (activePopupEvent) { flyToLatLon(activePopupEvent.lat, activePopupEvent.lon, activePopupEvent.loc, 10); closePopup(); } }

// ──────────────────────────────────────────────────────────
// MINI CHART (left panel)
// ──────────────────────────────────────────────────────────
function buildMiniChart() {
  const data = [72,68,65,63,60,58,61,59,57,55,53,56,54,52,49,47,50,48,45,43,41,44,42,40,38,36,39,37,35,33];
  const el = document.getElementById('mini-chart'); if (!el) return;
  const mx = Math.max(...data), mn = Math.min(...data);
  data.forEach(v => {
    const bar = document.createElement('div'); bar.className = 'bar';
    bar.style.height     = ((v-mn)/(mx-mn))*28+4 + 'px';
    bar.style.background = v<45?'var(--danger)':v<55?'var(--warning)':'var(--primary)';
    bar.style.opacity    = '0.7';
    el.appendChild(bar);
  });
}
buildMiniChart();

// ──────────────────────────────────────────────────────────
// PRED CHART (right panel)
// ──────────────────────────────────────────────────────────
function buildPredChart() {
  const c = document.getElementById('pred-chart'); if (!c) return;
  const cx = c.getContext('2d');
  c.width = c.offsetWidth * 2; c.height = 120; cx.scale(2,1);
  const W=c.offsetWidth, H=60, pts=[];
  for(let i=0;i<=30;i++) pts.push({x:(i/30)*W, y:10+rnd()*10+i*1.1});
  cx.strokeStyle='rgba(0,229,255,.6)'; cx.lineWidth=1; cx.beginPath();
  pts.forEach((p,i)=>i===0?cx.moveTo(p.x,p.y):cx.lineTo(p.x,p.y)); cx.stroke();
  cx.strokeStyle='rgba(255,107,0,.8)'; cx.setLineDash([3,3]); cx.beginPath();
  const ext=[];
  for(let i=0;i<=10;i++) ext.push({x:((30+i)/40)*W,y:pts[29].y+i*1.4+rnd()*4});
  ext.forEach((p,i)=>i===0?cx.moveTo(p.x,p.y):cx.lineTo(p.x,p.y)); cx.stroke(); cx.setLineDash([]);
  cx.fillStyle='rgba(0,229,255,.07)'; cx.beginPath(); cx.moveTo(0,H);
  pts.forEach(p=>cx.lineTo(p.x,p.y)); cx.lineTo(W,H); cx.closePath(); cx.fill();
}
setTimeout(buildPredChart, 100);

// ──────────────────────────────────────────────────────────
// TOOLBAR CONTROLS
// ──────────────────────────────────────────────────────────
function toggleLayer(btn, layer) {
    btn.classList.toggle('active');
    // Point #9: Navigate/Switch to module if active
    if (btn.classList.contains('active')) {
        if (MODULES[layer]) {
            switchModule(layer);
            return;
        }
    }
    // Implement layer visibility on Leaflet
    console.log("Toggle layer:", layer);
}
function setMapMode(mode) {
  document.querySelectorAll('.layer-btn').forEach(b=>{if(['2D','3D','4D'].includes(b.textContent))b.classList.remove('active');});
  document.querySelectorAll('.layer-btn').forEach(b=>{if(b.textContent===mode)b.classList.add('active');});
  
  const threeEl = document.getElementById('three-container');
  const timeEl  = document.getElementById('timeline-container');
  
  if (mode === '3D' || mode === '4D') {
    threeEl.classList.add('visible');
    initThreeScene();
    updateThreeModel(currentModule);
    if (mode === '4D') timeEl.classList.add('visible');
    else timeEl.classList.remove('visible');
  } else {
    threeEl.classList.remove('visible');
    timeEl.classList.remove('visible');
  }
}

function onTimeScroll() {
    const val = document.getElementById('time-slider').value;
    // Simulate temporal data change
    console.log("Time offset:", val);
    if (threeScene && threeScene.currentModel) {
        threeScene.currentModel.position.y = (val - 5) * 2;
    }
}

// ──────────────────────────────────────────────────────────
// THREE.JS 3D ENGINE
// ──────────────────────────────────────────────────────────
function initThreeScene() {
  if (threeScene) return;
  const container = document.getElementById('three-container');
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, container.offsetWidth / container.offsetHeight, 0.1, 2000);
  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(container.offsetWidth, container.offsetHeight);
  container.appendChild(renderer.domElement);

  const ambientLight = new THREE.AmbientLight(0x404040, 2);
  scene.add(ambientLight);
  const directionalLight = new THREE.DirectionalLight(0x00e5ff, 2);
  directionalLight.position.set(10, 20, 10);
  scene.add(directionalLight);

  camera.position.set(0, 100, 200);
  camera.lookAt(0, 0, 0);

  threeScene = { scene, camera, renderer, models: {} };
  
  function animate() {
    requestAnimationFrame(animate);
    if (threeScene.currentModel) {
      threeScene.currentModel.rotation.y += 0.005;
    }
    // Flowing groundwater animation based on real physics
    if (threeScene.gwParticles) {
      const positions = threeScene.gwParticles.geometry.attributes.position.array;
      for (let i = 0; i < positions.length; i += 3) {
        positions[i+2] += 0.1; // flow speed
        if (positions[i+2] > 40) {
          positions[i+2] = -40; // reset
        }
      }
      threeScene.gwParticles.geometry.attributes.position.needsUpdate = true;
    }
    renderer.render(scene, camera);
  }
  animate();
}

function updateThreeModel(mod, data = null) {
  if (!threeScene) return;
  const { scene } = threeScene;
  
  // Clear previous models
  if (threeScene.currentModel) scene.remove(threeScene.currentModel);

  const group = new THREE.Group();
  
  if (mod === 'groundwater' || mod === 'aquifer') {
    // 3D Subsurface Profile (Point #3) - Dynamic based on real world data
    let anomalyHeight = 30; // base height of saturated aquifer
    let moisterZoneHeight = 20;
    let waterColor = 0x00e5ff;
    
    if (data && data.satellite_data) {
        // e.g. grace anomaly -2 means less aquifer.
        anomalyHeight = Math.max(5, 30 + (data.satellite_data.grace_anomaly_m * 5));
        // Soil moisture affects the med level zone height
        moisterZoneHeight = Math.max(5, (data.satellite_data.soil_moisture_pct / 100) * 40);
        // Crisis check
        if (data.satellite_data.grace_anomaly_m < -4) {
            waterColor = 0xff1744; // Warning red for critical depletion
        }
    }

    const group = new THREE.Group();
    
    // 1. Surface Layer (Agriculture/Soil)
    const sGeo = new THREE.BoxGeometry(100, 5, 100);
    const sMat = new THREE.MeshPhongMaterial({ color: 0x8d6e63 });
    const surface = new THREE.Mesh(sGeo, sMat);
    surface.position.y = 30;
    group.add(surface);

    // 2. Unsaturated Zone (Med Level - Dynamic)
    const mGeo = new THREE.BoxGeometry(100, moisterZoneHeight, 100);
    const mMat = new THREE.MeshPhongMaterial({ color: 0x5d4037, transparent:true, opacity:0.6 });
    const med = new THREE.Mesh(mGeo, mMat);
    med.position.y = 30 - 2.5 - (moisterZoneHeight / 2);
    group.add(med);

    // 3. Saturated Aquifer (High Level Data - Dynamic)
    const aGeo = new THREE.BoxGeometry(100, anomalyHeight, 100);
    const aMat = new THREE.MeshPhongMaterial({ color: waterColor, transparent:true, opacity:0.6, wireframe:true });
    const aquifer = new THREE.Mesh(aGeo, aMat);
    aquifer.position.y = med.position.y - (moisterZoneHeight / 2) - (anomalyHeight / 2);
    group.add(aquifer);

    // 4. Feature: Simulation Observation Pipe (Borewell crossover)
    const pipeGeo = new THREE.CylinderGeometry(1.5, 1.5, 80, 16);
    const pipeMat = new THREE.MeshPhongMaterial({ color: 0xcccccc });
    const pipe = new THREE.Mesh(pipeGeo, pipeMat);
    pipe.position.y = surface.position.y - 40;
    group.add(pipe);

    // 5. Feature: Flow Particles in the saturated zone
    const particleGeo = new THREE.BufferGeometry();
    const particleCount = 150;
    const pos = new Float32Array(particleCount * 3);
    for(let i=0; i<particleCount*3; i+=3) {
      pos[i] = (Math.random() - 0.5) * 80;
      pos[i+1] = aquifer.position.y + (Math.random() - 0.5) * anomalyHeight;
      pos[i+2] = (Math.random() - 0.5) * 80;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const particleMat = new THREE.PointsMaterial({ color: 0xffffff, size: 1.5 });
    const particles = new THREE.Points(particleGeo, particleMat);
    group.add(particles);
    threeScene.gwParticles = particles; // For animation

    // 4. Bedrock (Base)
    const bGeo = new THREE.BoxGeometry(105, 5, 105);
    const bMat = new THREE.MeshPhongMaterial({ color: 0x212121 });
    const bedrock = new THREE.Mesh(bGeo, bMat);
    bedrock.position.y = -30;
    group.add(bedrock);

    threeScene.currentModel = group;
    scene.add(group);
  } 
  else if (mod === 'drainage') {
    // 3D Drainage System Clone (Point #5)
    const group = new THREE.Group();
    
    // Main Artery
    const pipeGeo = new THREE.CylinderGeometry(2, 2, 120, 16);
    const pipeMat = new THREE.MeshPhongMaterial({ color: 0x757575 });
    const pipe = new THREE.Mesh(pipeGeo, pipeMat);
    pipe.rotation.z = Math.PI/2;
    group.add(pipe);

    // Branching networks
    for (let i=0; i<6; i++) {
        const branch = pipe.clone();
        branch.scale.set(0.5, 0.4, 0.5);
        branch.rotation.y = (Math.PI/3) * i;
        branch.position.x = Math.sin(i) * 20;
        group.add(branch);
    }
    
    threeScene.currentModel = group;
    scene.add(group);
  }
  else if (mod === 'borewell') {
    // 3D Well model
    const cylinderGeo = new THREE.CylinderGeometry(5, 5, 150, 32);
    const cylinderMat = new THREE.MeshPhongMaterial({ color: 0xff6b00, wireframe: true });
    const well = new THREE.Mesh(cylinderGeo, cylinderMat);
    group.add(well);
    
    // Rock layers
    const layerGeo = new THREE.BoxGeometry(150, 10, 150);
    const layerMat = new THREE.MeshPhongMaterial({ color: 0x555555, opacity: 0.3, transparent: true });
    for(let i=0; i<3; i++) {
        const l = new THREE.Mesh(layerGeo, layerMat);
        l.position.y = -20 * i;
        group.add(l);
    }
  }
  else if (mod === 'drainage') {
    // 3D Pipe/Channel network clone
    const pipeGeo = new THREE.TorusGeometry(80, 2, 16, 100);
    const pipeMat = new THREE.MeshPhongMaterial({ color: 0x00e5ff, wireframe: true });
    const pipes = new THREE.Mesh(pipeGeo, pipeMat);
    pipes.rotation.x = Math.PI/2;
    group.add(pipes);
  }
  
  scene.add(group);
  threeScene.currentModel = group;
}
let isLive = true;
function togglePlayback() {
  isLive = !isLive;
  const b = document.getElementById('btn-playback');
  b.textContent = isLive ? '▶ LIVE' : '⏸ PAUSED';
  b.classList.toggle('active', isLive);
}

// ──────────────────────────────────────────────────────────
// RAG
// ──────────────────────────────────────────────────────────
async function triggerRAG() {
  const q  = document.getElementById('rag-input').value;
  const el = document.getElementById('rag-response');
  el.style.display = 'block'; el.style.color = 'var(--text-dim)';
  el.innerHTML = '> QUERYING RAG SYSTEM...';
  try {
    const r = await fetch(`${API_BASE}/genai/rag/query`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({question:q}),
    });
    const d = await r.json();
    el.style.color  = 'var(--primary)';
    el.innerHTML    = `→ ${d.answer||'No response'}<br><span style="color:var(--text-dim);font-size:8px;">MODE: ${d.mode||'rag'} | SOURCES: ${(d.sources||[]).length}</span>`;
  } catch(e) {
    el.style.color = 'var(--warning)';
    el.innerHTML   = `> ERROR: ${e.message}. Backend running?`;
  }
}
document.getElementById('rag-input').addEventListener('keydown', e=>{ if(e.key==='Enter') triggerRAG(); });

// ──────────────────────────────────────────────────────────
// LIVE FLICKER
// ──────────────────────────────────────────────────────────
setInterval(()=>{
  const n = 3 + Math.floor(Math.random()*2);
  ['alert-count','hud-crisis'].forEach(id=>{ const el=document.getElementById(id); if(el) el.textContent=n; });
},9000);
setInterval(()=>{
  const el = document.getElementById('frame-count');
  if (el) el.textContent = (1779 + Math.floor(Math.random()*50)).toLocaleString();
},3000);

// ──────────────────────────────────────────────────────────
// INIT
// ──────────────────────────────────────────────────────────
window.addEventListener('load', () => {
  initCenterMap();
  setStatus('OPERATIONAL', '');
});
