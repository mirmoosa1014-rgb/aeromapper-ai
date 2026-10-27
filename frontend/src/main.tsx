import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

type Frame = { time_s: number; energy_proxy: number; position: number[]; coverage: number; belief: number[][]; observations: { x: number; y: number; confidence: number }[]; rationale: string; camera: number[][] };
type Mission = { metrics: Record<string, number | string | boolean>; trace: Frame[]; terrain: number[][]; obstacles: number[][]; targets: number[][] };
type Data = Record<string, Mission>;
const P = { paper: '#E6E1D8', raised: '#F7F4EF', surface: '#F4EFE6', ink: '#2B2A28', dim: '#6E675F', clay: '#E07A5F', sage: '#81B29A', indigo: '#3D405B', sand: '#F2CC8F' };
const mix = (hex: string, toward: string, ratio: number) => '#' + [1, 3, 5].map(i => Math.round(parseInt(hex.slice(i, i + 2), 16) * (1 - ratio) + parseInt(toward.slice(i, i + 2), 16) * ratio).toString(16).padStart(2, '0')).join('');

function AssemblyMark() {
  return <div className="assembly-mark" aria-hidden="true">{[P.clay, P.sage, P.indigo].map((color, i) => <span className="decor-object" style={{ '--block-index': i } as React.CSSProperties} key={color}><svg className="ground-shadow" viewBox="0 0 44 50"><ellipse cx="22" cy="43" rx="17" ry="5" fill={P.ink} opacity=".10" /></svg><span className="block-y"><svg className="block-scale" viewBox="0 0 44 50"><path d="M4 13 22 3 40 13 22 23Z" fill={mix(color, P.raised, .3)} /><path d="M4 13 22 23 22 43 4 33Z" fill={color} /><path d="M22 23 40 13 40 33 22 43Z" fill={mix(color, P.ink, .18)} /></svg></span></span>)}</div>;
}

function Terrain({ mission, frame, reveal }: { mission: Mission; frame: number; reveal: boolean }) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const [angle, setAngle] = useState(.66);
  const dragging = useRef<number | null>(null);
  useEffect(() => {
    const c = canvas.current;
    if (!c) return;
    const ctx = c.getContext('2d')!;
    const w = c.width = 1100, h = c.height = 720;
    ctx.clearRect(0, 0, w, h);
    const project = (x: number, y: number, z: number): [number, number] => {
      const a = (x - 5.5) * Math.cos(angle) - (y - 5.5) * Math.sin(angle);
      const b = (x - 5.5) * Math.sin(angle) + (y - 5.5) * Math.cos(angle);
      return [w / 2 + a * 47, h * .58 + b * 24 - z * 15];
    };
    const poly = (pts: [number, number][], fill: string, stroke?: string) => {
      ctx.beginPath(); pts.forEach((p, i) => i ? ctx.lineTo(...p) : ctx.moveTo(...p)); ctx.closePath();
      ctx.fillStyle = fill; ctx.fill();
      if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = .8; ctx.stroke(); }
    };
    const block = (x: number, y: number, top: number, bottom: number, half: number, color: string) => {
      const corners = [[x - half, y - half], [x + half, y - half], [x + half, y + half], [x - half, y + half]];
      const faces = corners.map((a, i) => { const b = corners[(i + 1) % 4]; return { a, b, depth: (a[0] + b[0]) * Math.sin(angle) + (a[1] + b[1]) * Math.cos(angle) }; }).sort((a, b) => a.depth - b.depth);
      faces.forEach((f, i) => poly([project(f.a[0], f.a[1], bottom), project(f.b[0], f.b[1], bottom), project(f.b[0], f.b[1], top), project(f.a[0], f.a[1], top)], mix(color, P.ink, i % 2 ? .19 : .08)));
      poly(corners.map(p => project(p[0], p[1], top)), mix(color, P.raised, .16), mix(color, P.ink, .12));
    };
    // A stationary contact ellipse is decoration; all measured geometry below stays fixed.
    ctx.beginPath(); ctx.ellipse(w / 2, h * .68, 396, 154, 0, 0, Math.PI * 2); ctx.fillStyle = '#2B2A280B'; ctx.fill();
    const f = mission.trace[Math.min(frame, mission.trace.length - 1)];
    const belief = new Map(f?.belief.map(([x, y, p]) => [`${x},${y}`, p]));
    const bottom = Math.min(...mission.terrain.flat()) - .75;
    const cells = mission.terrain.flatMap((row, y) => row.map((z, x) => ({ x, y, z }))).sort((a, b) => (a.x * Math.sin(angle) + a.y * Math.cos(angle)) - (b.x * Math.sin(angle) + b.y * Math.cos(angle)));
    cells.forEach(({ x, y, z }) => {
      const p = belief.get(`${x},${y}`);
      block(x, y, z, bottom, .49, p === undefined ? P.surface : p >= .5 ? P.clay : P.sage);
      if (mission.obstacles.some(v => v[0] === x && v[1] === y)) block(x, y, z + 2.8, z, .30, P.indigo);
      if (reveal && mission.targets.some(v => v[0] === x && v[1] === y)) {
        const q = project(x, y, z + .15); ctx.strokeStyle = P.ink; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(q[0] - 6, q[1]); ctx.lineTo(q[0] + 6, q[1]); ctx.moveTo(q[0], q[1] - 6); ctx.lineTo(q[0], q[1] + 6); ctx.stroke();
      }
    });
    ctx.strokeStyle = P.indigo; ctx.lineWidth = 3; ctx.lineJoin = 'round'; ctx.beginPath();
    mission.trace.slice(0, frame + 1).forEach((v, i) => { const p = project(v.position[0], v.position[1], mission.terrain[v.position[1]][v.position[0]] + .16); i ? ctx.lineTo(...p) : ctx.moveTo(...p); }); ctx.stroke();
    if (f) {
      const [x, y] = f.position, z = mission.terrain[y][x];
      const radius = 13.856406460551018 / 8 / 2;
      poly([project(x - radius, y - radius, z + .18), project(x + radius, y - radius, z + .18), project(x + radius, y + radius, z + .18), project(x - radius, y + radius, z + .18)], '#E07A5F22', P.clay);
      const surface = project(x, y, z), p = project(x, y, z + 12);
      ctx.strokeStyle = '#6E675F'; ctx.setLineDash([3, 5]); ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(...surface); ctx.lineTo(...p); ctx.stroke(); ctx.setLineDash([]);
      block(x, y, z + 12.22, z + 11.82, .2, P.clay);
      ctx.strokeStyle = P.indigo; ctx.lineWidth = 3;
      for (const [dx, dy] of [[-.45, -.45], [.45, -.45], [.45, .45], [-.45, .45]]) {
        const end = project(x + dx, y + dy, z + 12); ctx.beginPath(); ctx.moveTo(...p); ctx.lineTo(...end); ctx.stroke(); ctx.beginPath(); ctx.ellipse(end[0], end[1], 12, 5, 0, 0, Math.PI * 2); ctx.stroke();
      }
      const labelX = Math.min(w - 180, Math.max(25, p[0] + 43)), labelY = Math.max(20, p[1] - 18);
      ctx.fillStyle = P.raised; ctx.beginPath(); ctx.roundRect(labelX, labelY, 159, 37, 14); ctx.fill(); ctx.fillStyle = P.ink; ctx.font = '500 14px Helvetica Neue, Helvetica, Arial'; ctx.fillText('Camera · 12 m AGL', labelX + 15, labelY + 23);
    }
    ctx.fillStyle = P.dim; ctx.font = '600 12px SF Mono, Menlo, monospace';
    const east = project(11.9, 0, bottom), north = project(0, 11.9, bottom);
    ctx.fillText('E / 8 m CELL', Math.min(w - 140, east[0]), east[1] + 30);
    ctx.fillText('N', Math.max(20, north[0] - 20), north[1] + 28);
  }, [mission, frame, reveal, angle]);
  return <canvas ref={canvas} tabIndex={0} aria-label="Rotatable three-dimensional survey terrain with measured elevation, flight trace, camera footprint and known no-fly blocks. Use arrow keys or drag to rotate." onKeyDown={e => { if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') { e.preventDefault(); setAngle(a => a + (e.key === 'ArrowLeft' ? -.08 : .08)); } }} onPointerDown={e => { dragging.current = e.clientX; e.currentTarget.setPointerCapture(e.pointerId); }} onPointerMove={e => { if (dragging.current !== null) { setAngle(a => a + (e.clientX - dragging.current!) * .008); dragging.current = e.clientX; } }} onPointerUp={() => dragging.current = null} onPointerCancel={() => dragging.current = null} />;
}

function App() {
  const [data, setData] = useState<Data | null>(null), [policy, setPolicy] = useState('adaptive'), [frame, setFrame] = useState(0), [playing, setPlaying] = useState(false), [reveal, setReveal] = useState(false), [seed, setSeed] = useState(2000), [budget, setBudget] = useState(220), [busy, setBusy] = useState(false), [notice, setNotice] = useState('Saved experiment · synthetic data'), [family, setFamily] = useState('test');
  const abort = useRef<AbortController | null>(null);
  useEffect(() => { fetch('/demo.json').then(r => r.json()).then(d => { setData(d); setSeed(Number(d.adaptive.metrics.seed)); }).catch(() => setNotice('Saved demo could not load. Regenerate with python -m aeromapper.experiment.')); }, []);
  useEffect(() => { if (!playing || !data) return; const id = setInterval(() => setFrame(f => { if (f >= data[policy].trace.length - 1) { setPlaying(false); return f; } return f + 1; }), 240); return () => clearInterval(id); }, [playing, data, policy]);
  if (!data) return <main><p>Opening the survey desk…</p><p>{notice}</p></main>;
  const m = data[policy], f = m.trace[Math.min(frame, m.trace.length - 1)];
  const n = (key: string) => Number(m.metrics[key]);
  const run = async () => { setBusy(true); abort.current = new AbortController(); try { const r = await fetch('http://127.0.0.1:8105/api/compare', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ seed, budget, family }), signal: abort.current.signal }); if (!r.ok) throw Error('Invalid request'); setData(await r.json()); setFrame(0); setNotice('New paired experiment · same world and imagery'); } catch (e) { setNotice((e as Error).name === 'AbortError' ? 'Request cancelled' : 'Backend unavailable. Run ./run.sh; saved replay remains usable.'); } finally { setBusy(false); } };
  const exportCurrent = () => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })); a.download = 'aeromapper-mission.json'; a.click(); URL.revokeObjectURL(a.href); };
  return <main className="survey-desk">
    <header className="desk-header"><div className="wordmark"><AssemblyMark /><div><h1>AeroMapper</h1><p>Spatial survey desk</p></div></div><div className="folio"><span>FIELD STUDY / 05</span><p>Software-only · synthetic observations</p></div></header>
    <section className="mission-strip" aria-label="Mission controls"><div className="strip-title"><span className="mono">Mission</span><strong>{String(m.metrics.seed).padStart(4, '0')}</strong></div><label>World seed<input type="number" min="0" max="100000" value={seed} onChange={e => setSeed(+e.target.value)} /></label><label className="budget">Time budget <span>{budget} s</span><input aria-label="Time budget" type="range" min="40" max="600" value={budget} onChange={e => setBudget(+e.target.value)} /></label><label>Scene family<select value={family} onChange={e => setFamily(e.target.value)}><option value="test">Held-out scenes</option><option value="ood">Out-of-distribution noise</option></select></label><button className="run-button" onClick={busy ? () => abort.current?.abort() : run}>{busy ? 'Cancel request' : 'Run paired mission ↗'}</button></section>
    <section className="spatial-workspace" aria-label="Survey workspace"><div className="world-sheet"><div className="world-heading"><div><span className="mono">01 / World model</span><h2>Survey reconstruction</h2></div><div className="policy-tabs" aria-label="Planning policy">{['adaptive', 'lawnmower'].map(p => <button aria-pressed={p === policy} className={p === policy ? 'active' : ''} key={p} onClick={() => { setPolicy(p); setFrame(0); }}>{p}</button>)}</div></div><div className="world-stage"><div className="coordinate-label"><span className="mono">96 × 96 m</span><span>Terrain + observed beliefs</span></div><Terrain mission={m} frame={frame} reveal={reveal} /><span className="drag-label">Drag or use ← → to rotate the desk</span></div><div className="world-key"><span><i className="unseen" />Unobserved</span><span><i className="sage" />Low target belief</span><span><i className="clay" />High target belief</span><span><i className="indigo" />Known no-fly cells</span></div><div className="replay-strip"><button className="play-button" aria-label={playing ? 'Pause replay' : 'Play replay'} onClick={() => setPlaying(!playing)}>{playing ? 'Ⅱ' : '▶'}</button><div><label htmlFor="mission-replay">Observation timeline <span>{f?.time_s.toFixed(1)} s / {String(m.metrics.time_s)} s</span></label><input id="mission-replay" aria-label="Mission replay" type="range" min="0" max={m.trace.length - 1} value={Math.min(frame, m.trace.length - 1)} onChange={e => { setPlaying(false); setFrame(+e.target.value); }} /></div><label className="truth-control"><input type="checkbox" checked={reveal} onChange={e => setReveal(e.target.checked)} />Reveal truth for review</label></div></div>
      <aside className="camera-sheet"><span className="mono">02 / Camera sample</span><h2>Synthetic perception</h2><div className="camera-frame"><svg viewBox="0 0 120 120" role="img" aria-label="Actual synthetic camera patch used by detector">{f?.camera.flatMap((row, y) => row.map((v, x) => <rect key={`${x}-${y}`} x={x * 10} y={y * 10} width="10" height="10" fill={`rgb(${v * 255},${v * 255},${v * 255})`} />))}</svg><div className="frame-corners" aria-hidden="true" /></div><div className="sample-caption"><span>12 × 12 px</span><span>Cell {f?.position.join(', ')}</span></div><div className="confidence"><span>Target probability</span><strong>{((f?.observations.at(-1)?.confidence ?? 0) * 100).toFixed(0)}<small>%</small></strong></div><p className="rationale">{f?.rationale}</p><dl><dt>East / North</dt><dd>{f?.position.map(v => v * 8).join(' / ')} m</dd><dt>Altitude AGL</dt><dd>12 m</dd><dt>Footprint width</dt><dd>13.86 m</dd><dt>Detector</dt><dd>Trained logistic</dd><dt>Blocked proposals</dt><dd>{String(m.metrics.blocked_proposals)}</dd></dl><p className="sheet-note">This is the image the detector received. Reveal truth only for reviewing the scene; the planner cannot read it.</p></aside>
    </section>
    <details className="inspection-drawer" open><summary><span><span className="mono">03 / Inspection drawer</span><strong>Coverage & target findings</strong></span><span className="drawer-hint">Final mission totals <span aria-hidden="true">⌄</span></span></summary><div className="inspection-content"><section className="coverage-sheet"><h3>Coverage through time</h3><p>Observation coverage and detection are different measurements.</p><svg className="coverage-chart" viewBox="0 0 500 230" role="img" aria-label="Coverage as function of mission time"><path d="M35 15V190H490" fill="none" stroke={P.dim} strokeWidth="1" />{[0, 25, 50, 75, 100].map(v => <g key={v}><path d={`M35 ${190 - v * 1.7}H490`} stroke="#6E675F22" /><text x="4" y={194 - v * 1.7} fill={P.dim} fontSize="10">{v}%</text></g>)}{['adaptive', 'lawnmower'].map((p, i) => <polyline key={p} points={data[p].trace.map(t => `${35 + t.time_s / Number(data[p].metrics.budget_s) * 450},${190 - t.coverage * 170}`).join(' ')} fill="none" stroke={i === 0 ? P.clay : P.indigo} strokeWidth="3" />)}<text x="35" y="216" fill={P.dim} fontSize="11">0</text><text x="405" y="216" fill={P.dim} fontSize="11">{String(m.metrics.budget_s)} seconds</text></svg><div className="chart-key"><span><i className="clay" />Adaptive</span><span><i className="indigo" />Lawnmower</span></div></section><section className="paired-sheet"><h3>Matched-world comparison</h3><table><thead><tr><th scope="col">Final result</th><th scope="col">Adaptive</th><th scope="col">Lawnmower</th></tr></thead><tbody>{[['coverage', 'Coverage'], ['recall', 'Target recall'], ['precision', 'Precision']].map(([k, title]) => <tr key={k}><th scope="row">{title}</th>{['adaptive', 'lawnmower'].map(p => <td key={p}>{(Number(data[p].metrics[k]) * 100).toFixed(1)}%</td>)}</tr>)}</tbody></table><dl className="distance-note"><dt>Selected-policy path</dt><dd>{n('path_m').toFixed(0)} m</dd><dt>Illustrative energy</dt><dd>{n('energy_proxy').toFixed(1)} units</dd></dl><p>Same hidden world, detector and budget. Unobserved targets count as missed.</p></section><section className="target-sheet"><h3>Observed target beliefs</h3><p>Current replay frame · cells ranked by probability</p><ol>{[...(f?.belief ?? [])].sort((a, b) => b[2] - a[2]).slice(0, 5).map(([x, y, probability]) => <li key={`${x},${y}`}><span className={`sample-swatch ${probability >= .5 ? 'clay' : 'sage'}`} /><span>Cell {x}, {y}</span><strong>{(probability * 100).toFixed(0)}%</strong></li>)}</ol><button className="export-button" onClick={exportCurrent}>Export current comparison ↓</button><a href="/demo.json" download="mission-trace.json">Saved trace + imagery</a></section></div></details>
    <footer><p role="status">{notice}</p><p>No hardware connection. Synthetic imagery does not validate real aerial detection or flight safety.</p></footer>
  </main>;
}
createRoot(document.getElementById('root')!).render(<App />);
