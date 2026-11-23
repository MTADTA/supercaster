// Supercaster II neck — parametric geometry. Units: inches.
// x runs from the nut (0) toward the body, y across the neck (bass side +), z up (top of board at centerline = 0).
(function (global) {
  const DEFAULTS = {
    scale: 25.5,
    frets: 21,
    nutWidth: 1.65,
    width21: 2.2,
    radiusNut: 7.25,
    radiusBridge: 9.5,
    radiusMode: "saddle", // 'saddle': 9.5" lands at the saddles (true cone) | 'lastFret': 9.5" at the last fret
    boardThickness: 0.2,
    edgeRoll: 0.07,
    depth1: 0.82, // total depth (board + neck) at the 1st fret
    depth12Linear: 0.92, // only used by the 'linear' taper
    taperMode: "radius", // 'radius' | 'width' | 'linear'
    apexOffset: 0.08, // fraction of half-width the deepest point shifts toward the bass side
    bassP: 2.3, // superellipse exponent, bass shoulder (>2 fuller, thumb shelf)
    trebleP: 1.7, // treble shoulder (<2 trimmed, fingers reach)
    crownWidth: 0.078, // Dunlop 6230
    crownHeight: 0.043,
    fretInset: 0.03,
    fretEnd: "semi", // 'hemi' dome radius = crown/2 | 'semi' elongated dome = crown width
    // 'wave': custom wire. A 6230-sized crest (.043 tall, .035 crest radius) on concave flanks of radius waveRho,
    //         which continue into the wood as the scallop. Every concave surface is larger than a fingertip.
    // 'stock': Dunlop 6230 + sin^2 micro scallop (buildable today, but the finger still catches the crown).
    fretProfile: "wave",
    waveRho: 0.4,
    waveDepth: 0.02,
    crestRadius: 0.0354, // = 6230 crown top radius (.039^2 / .043)
    featherEdge: 0.004, // minimum metal edge thickness, seated in a matching board rebate
    scallop1: 0.01,
    scallop12: 0.02,
    scallopShow: 1, // visual exaggeration only
    heelStartFret: 15,
    heelDepth: 1.3,
    heelLength: 2.4,
    headstockThickness: 0.55,
  };

  const fretX = (p, n) => p.scale * (1 - Math.pow(2, -n / 12));
  const lastX = (p) => fretX(p, p.frets);
  const boardEnd = (p) => lastX(p) + 0.25;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smooth = (t) => { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); };

  const width = (p, x) => p.nutWidth + ((p.width21 - p.nutWidth) * x) / lastX(p);
  function radius(p, x) {
    const L = p.radiusMode === "saddle" ? p.scale : lastX(p);
    return p.radiusNut + ((p.radiusBridge - p.radiusNut) * x) / L;
  }
  function depth(p, x) {
    const x1 = fretX(p, 1), x12 = fretX(p, 12);
    if (p.taperMode === "radius") return (p.depth1 * radius(p, x)) / radius(p, x1);
    if (p.taperMode === "width") return (p.depth1 * width(p, x)) / width(p, x1);
    return p.depth1 + ((p.depth12Linear - p.depth1) * (x - x1)) / (x12 - x1);
  }
  function scallopDepthAt(p, span) {
    const t = clamp((span - 1) / 11, 0, 1);
    return lerp(p.scallop1, p.scallop12, t);
  }
  // Wave fret cross-section. t = distance from the crest along x. Returns z relative to the board line (0).
  function waveGeom(p) {
    const rho = p.waveRho, rc = p.crestRadius, d = p.waveDepth, H = p.crownHeight + d;
    const al = Math.acos(1 - H / (rho + rc));
    const qi = rho * Math.sin(al), half = qi + rc * Math.sin(al);
    const qj = Math.sqrt(rho * rho - (rho - d) * (rho - d)); // floor tangent -> board line, along the flank
    return { rho, rc, d, H, al, qi, half, tj: half - qj };
  }
  function waveZ(g, t) {
    t = Math.abs(t);
    const q = g.half - t;
    if (q <= 0) return -g.d;
    if (q <= g.qi) return -g.d + g.rho - Math.sqrt(g.rho * g.rho - q * q);
    return -g.d + g.H - (g.rc - Math.sqrt(Math.max(0, g.rc * g.rc - t * t)));
  }
  function waveScallop(p, x) {
    if (x <= 0 || x >= lastX(p)) return 0;
    const g = waveGeom(p);
    let n = 0;
    while (n < p.frets && fretX(p, n + 1) <= x) n++;
    const left = n === 0 ? -g.tj : fretX(p, n), right = fretX(p, n + 1);
    const z = Math.min(0, Math.max(waveZ(g, x - left), waveZ(g, right - x)));
    return -z * p.scallopShow;
  }
  // Stock scallop: sin^2 between crown edges (v0.1). Zero slope at the crown foot, so the finger still meets a corner.
  function scallop(p, x) {
    if (p.fretProfile === "wave") return waveScallop(p, x);
    if (x <= 0 || x >= lastX(p)) return 0;
    let n = 0;
    while (n < p.frets && fretX(p, n + 1) <= x) n++;
    const a = fretX(p, n) + p.crownWidth / 2, b = fretX(p, n + 1) - p.crownWidth / 2;
    if (x <= a || x >= b) return 0;
    const s = Math.sin((Math.PI * (x - a)) / (b - a));
    return scallopDepthAt(p, n) * s * s * p.scallopShow;
  }
  const arcDrop = (R, y) => R - Math.sqrt(R * R - y * y);

  // Top of the board (no scallop) including the edge roll.
  function boardTop(p, x, y) {
    const hw = width(p, clamp(x, 0, boardEnd(p))) / 2, r = p.edgeRoll, R = radius(p, x);
    const ay = Math.abs(y);
    if (ay <= hw - r) return -arcDrop(R, ay);
    const zc = -arcDrop(R, hw - r) - r;
    const d = Math.min(ay - (hw - r), r);
    return zc + Math.sqrt(r * r - d * d);
  }

  // Closed polygon [y,z] for the rosewood board at x.
  function boardSection(p, x, N = 56, RN = 8) {
    const hw = width(p, x) / 2, r = p.edgeRoll, R = radius(p, x), sc = scallop(p, x), zg = -p.boardThickness;
    const top = (y) => -arcDrop(R, Math.abs(y)) - sc;
    const zt = top(hw - r);
    const pts = [[hw, zg], [hw, zg], [hw, zt - r]];
    for (let i = 1; i < RN; i++) { const a = (i / RN) * Math.PI / 2; pts.push([hw - r + r * Math.cos(a), zt - r + r * Math.sin(a)]); }
    for (let i = 0; i <= N; i++) { const y = (hw - r) * (1 - (2 * i) / N); pts.push([y, top(y)]); }
    for (let i = 1; i < RN; i++) { const a = Math.PI / 2 + (i / RN) * Math.PI / 2; pts.push([-hw + r + r * Math.cos(a), zt - r + r * Math.sin(a)]); }
    pts.push([-hw, zt - r], [-hw, zg], [-hw, zg]);
    return pts;
  }

  // Closed polygon [y,z] for the maple neck below the glue line, with the asymmetric back carve.
  function neckSection(p, x, N = 48) {
    const zg = -p.boardThickness, xl = lastX(p), xh = fretX(p, p.heelStartFret), xe = boardEnd(p) + p.heelLength;
    let W = width(p, clamp(x, 0, xe));
    let D = depth(p, clamp(x, 0, xl)) - p.boardThickness;
    let a = p.apexOffset, pb = p.bassP, pt = p.trebleP;
    if (x > xh) { // sculpted set-neck heel
      const t = smooth((x - xh) / (xe - xh));
      D = lerp(D, p.heelDepth, t);
      pb = lerp(pb, 4, t); pt = lerp(pt, 4, t); a = lerp(a, 0, t);
      W = lerp(W, W + 0.35, t);
    }
    if (x < 0) { // transition into the flat (non-angled) headstock
      const t = smooth(-x / 0.9);
      D = lerp(depth(p, 0) - p.boardThickness, p.headstockThickness, t);
      pb = lerp(pb, 8, t); pt = lerp(pt, 8, t); a = lerp(a, 0, t);
      W = p.nutWidth;
    }
    const hw = W / 2, side = 0.05, zs = zg - side, zmin = zg - D;
    const pts = [[-hw, zg], [-hw, zg], [hw, zg], [hw, zg], [hw, zs]];
    const half = N / 2;
    for (let i = 1; i <= half; i++) { // bass quadrant: edge -> apex
      const ph = (i / half) * Math.PI / 2;
      const u = a + (1 - a) * Math.pow(Math.cos(ph), 2 / pb);
      const g = Math.pow(Math.sin(ph), 2 / pb);
      pts.push([u * hw, zs - (zs - zmin) * g]);
    }
    for (let i = 1; i <= half; i++) { // treble quadrant: apex -> edge
      const ph = Math.PI / 2 + (i / half) * Math.PI / 2;
      const u = a - (1 + a) * Math.pow(Math.abs(Math.cos(ph)), 2 / pt);
      const g = Math.pow(Math.max(0, Math.sin(ph)), 2 / pt);
      pts.push([u * hw, zs - (zs - zmin) * g]);
    }
    pts.push([-hw, zs]);
    return pts;
  }

  // Loft rings of equal length into an indexed mesh with end caps.
  function loft(xs, rings) {
    const M = rings[0].length, pos = [], uv = [], idx = [];
    const L = xs[xs.length - 1] - xs[0] || 1;
    xs.forEach((x, k) => rings[k].forEach(([y, z], i) => { pos.push(x, y, z); uv.push((x - xs[0]) / L, i / (M - 1)); }));
    for (let k = 0; k < xs.length - 1; k++) for (let i = 0; i < M; i++) {
      const a = k * M + i, b = k * M + ((i + 1) % M), c = (k + 1) * M + i, d = (k + 1) * M + ((i + 1) % M);
      idx.push(a, b, c, b, d, c);
    }
    [0, xs.length - 1].forEach((k, e) => {
      let cy = 0, cz = 0; rings[k].forEach(([y, z]) => { cy += y; cz += z; });
      const ci = pos.length / 3; pos.push(xs[k], cy / M, cz / M); uv.push(0, 0);
      for (let i = 0; i < M; i++) { const a = k * M + i, b = k * M + ((i + 1) % M); e ? idx.push(ci, a, b) : idx.push(ci, b, a); }
    });
    return { position: pos, uv, index: idx };
  }

  function sampleXs(p, x0, x1, perSpan = 14) {
    const xs = new Set([x0, x1]);
    for (let n = 0; n <= p.frets; n++) {
      const a = fretX(p, n), b = n < p.frets ? fretX(p, n + 1) : boardEnd(p);
      for (let i = 0; i <= perSpan; i++) xs.add(a + ((b - a) * i) / perSpan);
    }
    for (let x = x0; x < x1; x += 0.15) xs.add(x);
    if (p.fretProfile === "wave") for (let n = 0; n <= p.frets; n++) {
      const c = fretX(p, n);
      for (let dx = -0.25; dx <= 0.25; dx += 0.0125) xs.add(c + dx);
    }
    return [...xs].filter((x) => x >= x0 && x <= x1).sort((a, b) => a - b);
  }

  function boardMesh(p) {
    const xs = sampleXs(p, 0, boardEnd(p));
    return loft(xs, xs.map((x) => boardSection(p, x)));
  }
  function neckMesh(p, opts = {}) {
    const xs = sampleXs(p, -0.9, boardEnd(p) + (opts.body ? 0.02 : p.heelLength));
    return loft(xs, xs.map((x) => neckSection(p, x)));
  }

  // One fret swept along the radiused board with domed ends. The cross-section is a closed ring [t, z]
  // (t along x from the fret line, z above the board line). Domed ends shrink the ring to a point.
  function fretRing(p) {
    if (p.fretProfile === "wave") {
      const g = waveGeom(p), te = p.featherEdge, ring = [], N = 28;
      for (let i = 0; i <= N; i++) { const u = -1 + (2 * i) / N, t = g.tj * Math.sign(u) * Math.pow(Math.abs(u), 1.6); ring.push([t, waveZ(g, t)]); }
      ring.push([g.tj, -te], [-g.tj, -te]);
      return { ring, half: g.tj };
    }
    const ring = [], T = 14;
    for (let i = 0; i <= T; i++) { const th = Math.PI - (Math.PI * i) / T; ring.push([(p.crownWidth / 2) * Math.cos(th), p.crownHeight * Math.sin(th)]); }
    ring.push([p.crownWidth / 2, -0.004], [-p.crownWidth / 2, -0.004]);
    return { ring, half: p.crownWidth / 2 };
  }
  function fretMesh(p, n, S = 64) {
    const x0 = fretX(p, n), hw = width(p, x0) / 2, Y = hw - p.fretInset;
    const { ring, half } = fretRing(p), M = ring.length;
    const rd = (p.fretEnd === "hemi" ? 1 : 2) * half;
    const pos = [], idx = [];
    for (let s = 0; s <= S; s++) {
      const v = -1 + (2 * s) / S, y = Y * Math.sin((Math.PI / 2) * v);
      const e = Y - Math.abs(y);
      const f = e < rd ? Math.sqrt(Math.max(0, 1 - Math.pow((rd - e) / rd, 2))) : 1;
      const zb = boardTop(p, x0, y), z0 = zb - 0.004;
      ring.forEach(([t, z]) => pos.push(x0 + t * f, y, z0 + (zb + z - z0) * f));
    }
    for (let s = 0; s < S; s++) for (let i = 0; i < M; i++) {
      const a = s * M + i, b = s * M + ((i + 1) % M), c = a + M, d = b + M;
      idx.push(a, c, b, b, c, d);
    }
    return { position: pos, index: idx };
  }

  // Rigid-fingertip proxy for "do you feel the fret?". A circle of radius R rolls from mid-span to a crest at x=0;
  // its centre path is the upper envelope. "Catch" is the largest slope jump in that path (0 = no corner anywhere).
  function spanProfile(p, L) {
    if (p.fretProfile === "wave") {
      const g = waveGeom(p);
      return (x) => Math.max(waveZ(g, x), waveZ(g, L - x));
    }
    const h = p.crownHeight, cw = p.crownWidth, d = p.scallop12;
    const ell = (x) => { const a = Math.abs(x) / (cw / 2); return a < 1 ? h * Math.sqrt(1 - a * a) : 0; };
    return (x) => {
      const e = Math.max(ell(x), ell(x - L)); if (e > 0) return e;
      const a = cw / 2, b = L - cw / 2; if (x <= a || x >= b) return 0;
      const sn = Math.sin((Math.PI * (x - a)) / (b - a)); return -d * sn * sn;
    };
  }
  function fingerFeel(f, R, L, dx = 0.0004) {
    const x0 = -0.3, n = Math.ceil((L + 0.6) / dx), zs = new Float64Array(n);
    for (let i = 0; i < n; i++) zs[i] = f(x0 + i * dx);
    const path = [];
    const w = Math.ceil(R / dx);
    for (let x = L / 2; x >= -0.0001; x -= dx) {
      const ci = Math.round((x - x0) / dx); let m = -1e9;
      for (let i = Math.max(0, ci - w); i <= Math.min(n - 1, ci + w); i++) {
        const q = x - (x0 + i * dx); if (Math.abs(q) < R) { const v = zs[i] + Math.sqrt(R * R - q * q); if (v > m) m = v; }
      }
      path.push([x, m]);
    }
    let worst = 0, at = 0;
    for (let k = 2; k < path.length; k++) {
      const j = Math.abs(Math.atan((path[k][1] - path[k - 1][1]) / dx) - Math.atan((path[k - 1][1] - path[k - 2][1]) / dx));
      if (j > worst) { worst = j; at = path[k - 1][0]; }
    }
    let lo = Infinity, hi = -Infinity; for (let x = 0; x <= L / 2; x += dx) { const z = f(x); lo = Math.min(lo, z); hi = Math.max(hi, z); }
    return { catchDeg: (worst * 180) / Math.PI, at, path, rise: hi - lo };
  }

  // PLACEHOLDER headstock: a plain uncut paddle blank, for display only (x behind the nut is negative, bass side +y).
  // The headstock shape is not designed yet (OPEN-CALCS.md, item 8). This is not it.
  const HEADSTOCK = [
    [0.05, 0.825], [-0.5, 0.95], [-1.1, 1.42], [-1.8, 1.6], [-3.0, 1.6], [-4.8, 1.6], [-6.6, 1.6],
    [-7.2, 1.32], [-7.42, 0.7], [-7.42, 0.1], [-7.42, -0.4], [-7.22, -0.76], [-6.8, -0.9],
    [-5.0, -0.9], [-3.0, -0.9], [-1.0, -0.9], [-0.4, -0.86], [0.05, -0.825],
  ];

  function fretMarkers(p) {
    const singles = [3, 5, 7, 9, 15, 17, 19, 21].filter((f) => f <= p.frets);
    const out = [];
    const mid = (f) => (fretX(p, f - 1) + fretX(p, f)) / 2;
    singles.forEach((f) => out.push({ x: mid(f), y: 0 }));
    if (p.frets >= 12) { out.push({ x: mid(12), y: 0.42 }, { x: mid(12), y: -0.42 }); }
    return out.map((m) => ({ ...m, z: boardTop(p, m.x, m.y) - scallop(p, m.x) }));
  }

  // Roasted flame maple: caramel base, flame bands running across the neck, faint long grain.
  function flameMaple(THREE) {
    const W = 2048, H = 256, c = document.createElement("canvas"); c.width = W; c.height = H;
    const g = c.getContext("2d");
    const base = g.createLinearGradient(0, 0, 0, H);
    base.addColorStop(0, "#b06d2e"); base.addColorStop(0.5, "#c3823d"); base.addColorStop(1, "#ab6a2c");
    g.fillStyle = base; g.fillRect(0, 0, W, H);
    const band = (x0, w, i, rgb, a) => {
      const wob = (y) => Math.sin(y * 0.028 + i * 1.7) * 7 + Math.sin(y * 0.07 + i) * 2 + (y / H) * 12;
      g.beginPath();
      for (let y = 0; y <= H; y += 8) { const x = x0 + wob(y); y ? g.lineTo(x, y) : g.moveTo(x, y); }
      for (let y = H; y >= 0; y -= 8) g.lineTo(x0 + w + wob(y), y);
      g.closePath();
      const grd = g.createLinearGradient(x0, 0, x0 + w, 0);
      grd.addColorStop(0, `rgba(${rgb},0)`); grd.addColorStop(0.5, `rgba(${rgb},${a})`); grd.addColorStop(1, `rgba(${rgb},0)`);
      g.fillStyle = grd; g.fill();
    };
    const n = 150, step = W / n;
    for (let i = 0; i < n; i++) {
      const x0 = (i + Math.random() * 0.5) * step, w = step * (0.4 + Math.random() * 0.3), a = 0.10 + Math.random() * 0.20;
      band(x0, w, i, "92,44,10", a);
      band(x0 + w * 0.8, w * 0.9, i + 0.5, "255,214,150", a * 0.75);
    }
    for (let i = 0; i < 70; i++) {
      const y = Math.random() * H; g.strokeStyle = `rgba(80,40,12,${0.04 + Math.random() * 0.08})`; g.lineWidth = 0.6 + Math.random() * 1.4;
      g.beginPath(); g.moveTo(0, y); for (let x = 0; x <= W; x += 64) g.lineTo(x, y + Math.sin(x * 0.002 + i) * 4); g.stroke();
    }
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
    return t;
  }

  // Build a THREE.Group (z-up model rotated to y-up). Pass the THREE namespace in.
  function buildNeck(THREE, params, mats, opts = {}) {
    const p = Object.assign({}, DEFAULTS, params);
    const g = new THREE.Group();
    const toGeo = (m) => {
      const geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.Float32BufferAttribute(m.position, 3));
      if (m.uv) geo.setAttribute("uv", new THREE.Float32BufferAttribute(m.uv, 2));
      geo.setIndex(m.index); geo.computeVertexNormals(); return geo;
    };
    const board = new THREE.Mesh(toGeo(boardMesh(p)), mats.board); board.name = "board";
    const neck = new THREE.Mesh(toGeo(neckMesh(p, opts)), mats.neck); neck.name = "neck";
    g.add(board, neck);
    for (let n = 1; n <= p.frets; n++) g.add(new THREE.Mesh(toGeo(fretMesh(p, n)), mats.fret));

    fretMarkers(p).forEach((m) => {
      const dot = new THREE.Mesh(new THREE.CircleGeometry(0.105, 32), mats.dot);
      dot.position.set(m.x, m.y, m.z + 0.002); g.add(dot);
    });
    // nut
    const nutH = 0.2 + 0.035;
    const nut = new THREE.Mesh(new THREE.BoxGeometry(0.19, p.nutWidth, nutH), mats.nut);
    nut.position.set(-0.095, 0, -p.boardThickness + nutH / 2); g.add(nut);
    // headstock
    const shape = new THREE.Shape();
    shape.moveTo(HEADSTOCK[0][0], HEADSTOCK[0][1]);
    shape.splineThru(HEADSTOCK.slice(1).map(([a, b]) => new THREE.Vector2(a, b)));
    const bev = 0.03;
    const hs = new THREE.Mesh(new THREE.ExtrudeGeometry(shape, { depth: p.headstockThickness - 2 * bev, bevelEnabled: true, bevelThickness: bev, bevelSize: bev, bevelSegments: 4, curveSegments: 64 }), mats.neck);
    const loftLen = boardEnd(p) + (opts.body ? 0.02 : p.heelLength) + 0.9;
    const hp = hs.geometry.attributes.position, hu = hs.geometry.attributes.uv;
    for (let i = 0; i < hp.count; i++) hu.setXY(i, (hp.getX(i) + 0.9) / loftLen, 0.5 + hp.getY(i) * 0.25);
    hs.position.z = -p.boardThickness - p.headstockThickness + bev; g.add(hs);
    // tuners and strings
    const posts = [];
    for (let i = 0; i < 6; i++) {
      const px = -1.75 - i * 0.98, py = 1.0 - i * 0.03;
      const post = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.45, 20), mats.metal);
      post.rotation.x = Math.PI / 2; post.position.set(px, py, -p.boardThickness + 0.22); g.add(post);
      const bush = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.05, 32), mats.metal);
      bush.rotation.x = Math.PI / 2; bush.position.set(px, py, -p.boardThickness + 0.025); g.add(bush);
      posts.push([px, py]);
    }
    if (opts.body && global.BodyGeo) g.add(global.BodyGeo.buildBody(THREE));
    const xb = opts.body ? 25.5 : boardEnd(p) + 2.2;
    const sz = (x) => 0.045 + 0.13 * (x / p.scale);
    for (let i = 0; i < 6; i++) {
      const s = 0.7 - i * 0.28; // low E (i=0) on the bass side
      const sb = s * (2.2 / 1.4) * (xb / p.scale) + s * (1 - xb / p.scale);
      const pts = [
        new THREE.Vector3(posts[i][0], posts[i][1], -p.boardThickness + 0.3),
        new THREE.Vector3(-0.1, s, sz(0)),
        new THREE.Vector3(xb, sb, sz(xb)),
      ];
      const geo = new THREE.BufferGeometry().setFromPoints(pts);
      g.add(new THREE.Line(geo, mats.string));
    }
    g.rotation.x = -Math.PI / 2; // z-up -> y-up
    const wrap = new THREE.Group(); wrap.add(g);
    wrap.userData.params = p;
    return wrap;
  }

  // Numbers for drawings/spec tables.
  function stations(p) {
    p = Object.assign({}, DEFAULTS, p);
    return [1, 5, 7, 12, 17, p.frets].map((n) => {
      const x = fretX(p, n);
      return { fret: n, x, width: width(p, x), radius: radius(p, x), depth: depth(p, x),
        depthRadius: depth({ ...p, taperMode: "radius" }, x), depthWidth: depth({ ...p, taperMode: "width" }, x), depthLinear: depth({ ...p, taperMode: "linear" }, x),
        scallop: scallopDepthAt(p, n), effective: p.crownHeight + scallopDepthAt(p, n) };
    });
  }

  global.NeckGeo = { DEFAULTS, fretX, lastX, boardEnd, width, radius, depth, scallop, scallopDepthAt, boardTop,
    boardSection, neckSection, fretMesh, buildNeck, stations, waveGeom, waveZ, spanProfile, fingerFeel, fretRing, flameMaple };
})(typeof window !== "undefined" ? window : globalThis);
