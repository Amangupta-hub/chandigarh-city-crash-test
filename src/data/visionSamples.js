/**
 * Preset photo samples of Chandigarh urban infrastructure hazards for instant Vision & Multimodal demo testing.
 * Each item has a title, sector, category, realistic SVG visual data URI, and simulated/test metadata.
 */

// Helper to convert SVG string to base64 Data URI
function svgToDataUri(svgString) {
  const clean = svgString.replace(/\n\s*/g, ' ').trim();
  // Safe btoa for browser
  if (typeof window !== 'undefined' && window.btoa) {
    return `data:image/svg+xml;base64,${window.btoa(unescape(encodeURIComponent(clean)))}`;
  }
  return `data:image/svg+xml;utf8,${encodeURIComponent(clean)}`;
}

// 1. Waterlogged Underpass (Sector 17)
const svgFlood = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <defs>
    <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#475569" />
      <stop offset="100%" stop-color="#64748b" />
    </linearGradient>
    <linearGradient id="waterGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.8" />
      <stop offset="60%" stop-color="#0284c7" stop-opacity="0.95" />
      <stop offset="100%" stop-color="#0369a1" />
    </linearGradient>
    <linearGradient id="roadGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#334155" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>
  </defs>
  <!-- Background overcast stormy sky -->
  <rect width="600" height="400" fill="url(#skyGrad)" />
  
  <!-- Underpass Bridge Structure -->
  <rect x="0" y="80" width="600" height="40" fill="#94a3b8" />
  <rect x="80" y="80" width="30" height="150" fill="#64748b" />
  <rect x="490" y="80" width="30" height="150" fill="#64748b" />
  
  <!-- Chandigarh Signboard -->
  <rect x="180" y="88" width="240" height="25" rx="4" fill="#1e3a8a" />
  <text x="300" y="105" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">SECTOR 17 SUBWAY UNDERPASS</text>

  <!-- Roadway Base -->
  <polygon points="0,200 600,200 600,400 0,400" fill="url(#roadGrad)" />
  <!-- Road Divider Markings (partially submerged) -->
  <rect x="290" y="210" width="20" height="30" fill="#facc15" />
  
  <!-- Deep Stormwater Layer (Waterlogging) -->
  <polygon points="0,230 600,220 600,400 0,400" fill="url(#waterGrad)" />
  <!-- Water ripples and surface reflections -->
  <ellipse cx="200" cy="270" rx="90" ry="10" fill="#e0f2fe" opacity="0.4" />
  <ellipse cx="420" cy="310" rx="140" ry="12" fill="#bae6fd" opacity="0.5" />
  <ellipse cx="280" cy="350" rx="180" ry="16" fill="#7dd3fc" opacity="0.4" />

  <!-- Submerged Car Silhouette -->
  <path d="M 320 280 Q 340 250 380 250 L 440 250 Q 470 255 490 280 L 510 295 L 300 295 Z" fill="#b91c1c" />
  <rect x="350" y="255" width="40" height="20" fill="#cbd5e1" opacity="0.8" />
  <rect x="400" y="255" width="40" height="20" fill="#cbd5e1" opacity="0.8" />
  <!-- Water covering wheels -->
  <ellipse cx="400" cy="295" rx="110" ry="15" fill="#0369a1" opacity="0.85" />
  
  <!-- Water Depth Gauge Graphic -->
  <rect x="75" y="220" width="10" height="130" fill="#ef4444" />
  <rect x="75" y="220" width="10" height="20" fill="#ffffff" />
  <rect x="75" y="260" width="10" height="20" fill="#ffffff" />
  <rect x="75" y="300" width="10" height="20" fill="#ffffff" />
  <text x="95" y="280" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#f87171">DEPTH: 14" (Knee-Deep)</text>

  <!-- Hazard Badge Overlay -->
  <rect x="15" y="15" width="220" height="32" rx="6" fill="#dc2626" opacity="0.9" />
  <text x="125" y="36" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">⚠ SEVERE WATERLOGGING</text>
</svg>
`;

// 2. Severe Road Pothole & Cave-in (Sector 22)
const svgPothole = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <defs>
    <linearGradient id="asphalt" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1e293b" />
      <stop offset="50%" stop-color="#334155" />
      <stop offset="100%" stop-color="#0f172a" />
    </linearGradient>
    <radialGradient id="crater" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#020617" />
      <stop offset="60%" stop-color="#1e293b" />
      <stop offset="90%" stop-color="#475569" />
      <stop offset="100%" stop-color="#0f172a" />
    </radialGradient>
  </defs>
  <!-- Road Surface -->
  <rect width="600" height="400" fill="url(#asphalt)" />
  <!-- White lane marking with severe fracture -->
  <line x1="280" y1="0" x2="280" y2="140" stroke="#f8fafc" stroke-width="14" stroke-dasharray="30 20" />
  <line x1="280" y1="280" x2="280" y2="400" stroke="#f8fafc" stroke-width="14" stroke-dasharray="30 20" />

  <!-- Street Sign Header -->
  <rect x="15" y="15" width="250" height="32" rx="6" fill="#ca8a04" opacity="0.9" />
  <text x="140" y="36" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">⚠ ROAD DAMAGE / CAVE-IN</text>
  <rect x="420" y="15" width="165" height="26" rx="4" fill="#0f172a" stroke="#475569" />
  <text x="502" y="32" font-family="Arial, sans-serif" font-size="11" fill="#cbd5e1" text-anchor="middle">Sector 22-B Main Market</text>

  <!-- Spider Cracks & Alligator Cracking -->
  <path d="M 120 180 L 220 220 L 150 270 M 220 220 L 250 160 M 380 170 L 460 210 L 510 180 M 460 210 L 480 290" stroke="#64748b" stroke-width="3" fill="none" />
  <path d="M 230 140 L 280 180 L 330 150" stroke="#94a3b8" stroke-width="2" fill="none" />

  <!-- Deep Road Crater / Pothole -->
  <ellipse cx="300" cy="220" rx="140" ry="75" fill="url(#crater)" stroke="#090d16" stroke-width="6" />
  
  <!-- Dislodged Aggregate Stones & Silt -->
  <ellipse cx="260" cy="235" rx="12" ry="7" fill="#64748b" />
  <ellipse cx="320" cy="245" rx="15" ry="9" fill="#475569" />
  <ellipse cx="290" cy="210" rx="10" ry="6" fill="#94a3b8" />
  <ellipse cx="350" cy="215" rx="14" ry="8" fill="#334155" />
  <ellipse cx="340" cy="255" rx="70" ry="20" fill="#0f172a" opacity="0.8" />
  <!-- Stagnant Dirty Water in Pothole bottom -->
  <ellipse cx="295" cy="235" rx="60" ry="22" fill="#0284c7" opacity="0.6" />

  <!-- Measurement Overlay -->
  <line x1="160" y1="220" x2="440" y2="220" stroke="#facc15" stroke-width="2" stroke-dasharray="4 4" />
  <rect x="245" y="280" width="110" height="24" rx="4" fill="#000000" opacity="0.8" />
  <text x="300" y="296" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#facc15" text-anchor="middle">WIDTH: 1.2 METERS</text>
</svg>
`;

// 3. Blocked Stormwater Gully (Sector 35)
const svgDrain = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <defs>
    <linearGradient id="curbGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#94a3b8" />
      <stop offset="100%" stop-color="#64748b" />
    </linearGradient>
  </defs>
  <!-- Road Surface & Concrete Curb -->
  <rect width="600" height="400" fill="#334155" />
  <rect x="0" y="0" width="600" height="120" fill="url(#curbGrad)" />
  <line x1="0" y1="120" x2="600" y2="120" stroke="#1e293b" stroke-width="5" />

  <!-- Road Gully Chamber Cutout -->
  <rect x="180" y="100" width="240" height="180" rx="8" fill="#0f172a" stroke="#020617" stroke-width="4" />
  
  <!-- Cast Iron Grating Bars -->
  <line x1="220" y1="100" x2="220" y2="280" stroke="#475569" stroke-width="10" />
  <line x1="260" y1="100" x2="260" y2="280" stroke="#475569" stroke-width="10" />
  <line x1="300" y1="100" x2="300" y2="280" stroke="#475569" stroke-width="10" />
  <line x1="340" y1="100" x2="340" y2="280" stroke="#475569" stroke-width="10" />
  <line x1="380" y1="100" x2="380" y2="280" stroke="#475569" stroke-width="10" />

  <!-- Thick Plastic Debris & Silt Accumulation Blocking Grate -->
  <!-- Mud/Silt patch -->
  <path d="M 170 170 Q 240 140 320 180 Q 410 150 430 220 Q 380 290 280 280 Q 180 290 170 170 Z" fill="#78350f" opacity="0.85" />
  
  <!-- Discarded Plastic Waste / Bottles / Bags -->
  <!-- Plastic bottles -->
  <rect x="230" y="180" width="45" height="18" rx="5" fill="#38bdf8" opacity="0.85" transform="rotate(-15 230 180)" />
  <rect x="310" y="210" width="40" height="16" rx="5" fill="#f43f5e" opacity="0.8" transform="rotate(25 310 210)" />
  <!-- Poly bags -->
  <path d="M 270 200 Q 300 170 330 220 Q 300 240 270 200 Z" fill="#f8fafc" opacity="0.8" />
  <path d="M 340 170 Q 380 150 390 190 Q 360 210 340 170 Z" fill="#facc15" opacity="0.8" />

  <!-- Backed Up Water Pooling around Grate -->
  <ellipse cx="300" cy="300" rx="200" ry="50" fill="#0284c7" opacity="0.5" />
  <ellipse cx="300" cy="310" rx="140" ry="30" fill="#38bdf8" opacity="0.4" />

  <!-- Status Tag -->
  <rect x="15" y="15" width="240" height="32" rx="6" fill="#b45309" opacity="0.9" />
  <text x="135" y="36" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">⚠ DRAINAGE CHOKE (85% BLOCKED)</text>
  <rect x="420" y="15" width="165" height="26" rx="4" fill="#0f172a" stroke="#475569" />
  <text x="502" y="32" font-family="Arial, sans-serif" font-size="11" fill="#cbd5e1" text-anchor="middle">Sector 35-C Inner Road</text>
</svg>
`;

// 4. Waste Overflow near Roundabout (Sector 9)
const svgWaste = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <defs>
    <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#475569" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>
  </defs>
  <!-- Background Road and Verge -->
  <rect width="600" height="400" fill="url(#ground)" />
  <rect x="0" y="0" width="600" height="150" fill="#15803d" opacity="0.6" />
  <!-- Roundabout Curb Arch -->
  <path d="M 0 150 Q 300 200 600 150" stroke="#f8fafc" stroke-width="8" fill="none" />

  <!-- Green Municipal Dumper Bin (Overflowing) -->
  <rect x="220" y="120" width="160" height="120" rx="6" fill="#166534" stroke="#14532d" stroke-width="4" />
  <text x="300" y="180" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#86efac" text-anchor="middle">MCC CHANDIGARH</text>
  <rect x="210" y="110" width="180" height="15" rx="3" fill="#14532d" />

  <!-- Garbage Mound spilling over onto carriageway -->
  <path d="M 180 240 Q 220 100 300 90 Q 380 100 420 240 Q 480 320 380 340 Q 260 360 160 320 Q 140 270 180 240 Z" fill="#854d0e" opacity="0.9" />
  
  <!-- Colored Waste items -->
  <circle cx="260" cy="270" r="18" fill="#38bdf8" />
  <rect x="310" y="260" width="30" height="25" fill="#f8fafc" rx="4" />
  <rect x="220" y="290" width="35" height="15" fill="#facc15" rx="3" />
  <circle cx="360" cy="285" r="15" fill="#ef4444" />
  <rect x="280" y="310" width="40" height="20" fill="#a855f7" rx="4" />
  <ellipse cx="320" cy="335" rx="65" ry="15" fill="#451a03" />

  <!-- Header Badge -->
  <rect x="15" y="15" width="220" height="32" rx="6" fill="#b45309" opacity="0.9" />
  <text x="125" y="36" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">⚠ SOLID WASTE HOTSPOT</text>
  <rect x="420" y="15" width="165" height="26" rx="4" fill="#0f172a" stroke="#475569" />
  <text x="502" y="32" font-family="Arial, sans-serif" font-size="11" fill="#cbd5e1" text-anchor="middle">Sector 9 Matka Chowk</text>
</svg>
`;

export const PRESET_DAMAGE_PHOTOS = [
  {
    id: 'flood-sec17',
    title: 'Waterlogged Subway Underpass',
    sector: 'Sector 17',
    category: 'Waterlogging',
    severity: 'High',
    notes: 'Subway underpass flooded with 14-inch standing stormwater, both lanes blocked, cars halted',
    badge: '14" Flash Flood',
    badgeColor: 'bg-blue-600 text-white',
    svgDataUri: svgToDataUri(svgFlood),
  },
  {
    id: 'pothole-sec22',
    title: 'Road Cave-in & Pothole Crater',
    sector: 'Sector 22',
    category: 'Road disruption',
    severity: 'High',
    notes: 'Massive 1.2m pothole crater with structural alligator cracking on dividing road 22-B',
    badge: '1.2m Road Crater',
    badgeColor: 'bg-amber-600 text-white',
    svgDataUri: svgToDataUri(svgPothole),
  },
  {
    id: 'drain-sec35',
    title: 'Blocked Stormwater Gully Chamber',
    sector: 'Sector 35',
    category: 'Drain blockage',
    severity: 'High',
    notes: 'Cast iron road gully grate completely clogged with plastic packaging and thick silt',
    badge: '85% Drain Choked',
    badgeColor: 'bg-red-600 text-white',
    svgDataUri: svgToDataUri(svgDrain),
  },
  {
    id: 'waste-sec9',
    title: 'Roundabout Waste Spillage',
    sector: 'Sector 09',
    category: 'Waste hotspot',
    severity: 'Moderate',
    notes: 'Solid waste dumpster overflowing onto road shoulder and pedestrian verge near Matka Chowk',
    badge: 'Solid Waste Hotspot',
    badgeColor: 'bg-orange-600 text-white',
    svgDataUri: svgToDataUri(svgWaste),
  },
];
