# Isometric Studio / spatial survey desk

## Source and license

This presentation adapts **Isometric Studio** (`motionstyle_isometric`, style id `isometric`) from the Motion Graphic Style Library at revision **ab7faf2be3e17350f5c6c7e78dfb53d1792ae9cc**. The source catalog is `catalog/isometric.md`. The upstream export `isometric.css` is copied verbatim to `frontend/src/motion-theme.css` and imported by the application stylesheet. The source is MIT licensed; the complete notice is reproduced in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Token and primitive mapping

| Upstream token or primitive | Application mapping |
| --- | --- |
| `bg #E6E1D8`, `bgRaised #F7F4EF`, `surface #F4EFE6` | Warm paper desk, raised camera sample sheet, label/control surfaces |
| `ink #2B2A28`, `textDim #6E675F` | Measurement labels and quiet supporting text |
| `clay #E07A5F` | High target belief, active survey path comparison and camera/drone body |
| `sage #81B29A` | Low target-belief terrain cells |
| `secondary #3D405B` | Known no-fly blocks, executed ground trace and fixed-policy comparison |
| Three-face IsoBlock | Actual terrain columns, known obstacles and the virtual drone body; header assembly is separately decorative |
| Floor and contact ellipse | A stationary paper plane with one faint group-contact ellipse; no horizon or glass |
| LabelChip, radius 14 px | Policy label and camera-altitude label; geometry itself retains hard faces |
| Display / body / mono typography | Helvetica Neue/Helvetica/Arial, display 700/-0.02em/1.0, body 500/1.4, SF Mono stack 600/+0.04em/uppercase |
| Soft shadow | Used only on the selected policy label; contact-depth shading is confined to geometry |

The canvas palette is an explicit matching token table because Canvas 2D does not inherit CSS fill properties. Each object's top/left/right tones are mixed only with the upstream raised paper and ink colors. Gray camera pixels remain the **actual frozen sensor values**; they are data, not recolored decoration. Chart labels, axes, legends and plots use the same light-paper palette. Research figures now read only saved CSV/JSON outputs, including saved calibration bins, and never call inference or rewrite data.

## Layout

The interface is a working survey desk, not a marketing landing page. A compact mission strip contains the existing seed, budget, family and request controls. The primary workspace is the 3D terrain and its adjacent camera sample. A lower, collapsible inspection drawer contains actual coverage curves, final paired measurements and current-frame target beliefs. There are no oversized promotional headlines, AI badge, dark-mint KPI grid or duplicated generic SaaS card layout.

The terrain renderer uses the exact saved `(x, y, elevation)` data; each 8 m cell has hard column faces. The drone's camera is shown 12 m above the current cell terrain, with a 13.856 m footprint and a stationary altitude guide. The path is the executed ground trace. Replay steps, measurement values and target probabilities are not interpolated or counted up. Colors correspond to current observed beliefs; unobserved terrain stays paper-colored. Truth markers appear only after the review toggle is selected.

## Motion clips and deliberate adaptations

- Decorative header blocks use upstream **`block_y`**: `-48 px → 0`, exactly **0.5 s**, `cubic-bezier(0.16, 1, 0.3, 1)`.
- Nested header SVGs use upstream **`block_scale`**: `0.94 → 1`, exactly **0.5 s**, the same prescribed easing. The two clips compose without changing either keyframe span.
- Repeated blocks are staggered by the exact upstream **0.08 s**, using the exported CSS variables. There is no overshoot.
- **`idle_bob` is intentionally not applied.** A scientific measurement surface, camera position, path, or value must not move to keep a video visually busy. The interface has no decorative hero requiring an idle bob.
- Upstream's locked-camera rule is a video composition guideline. This interactive application deliberately retains **user-driven drag and keyboard rotation**, with no autonomous spin or orbit. It changes only the view projection, never world positions, observation order, camera image or metrics.
- Upstream's “nothing stays still” narration guidance is intentionally not applied to a replay paused for inspection. A paused scientific scene remains completely still.
- `prefers-reduced-motion: reduce` disables the two decorative assembly clips. User-requested replay, seeking, drawer controls and rotation remain functional.
- Video safe margins and one-column 9:16 guidance are adapted to a fluid desk with a single-column **390 px** layout. Camera pixels and all meaningful controls remain accessible.

## Verification and current screenshot status

The TypeScript check and Vite production build passed locally after redesign. Frozen model, result and demo-file hashes are checked separately; no backend, model, CSV or JSON experiment data was edited. The saved-output research PNG and replay GIF were regenerated in the new palette and inspected.

Local Mac Chrome/headless-shell launch is blocked by the execution environment's Mach-rendezvous sandbox permission. This is an environment blocker, not a successful browser check. The redesign has **not** been represented by fabricated screenshots. Existing `app-screenshot.png` and `mobile-screenshot.png` are historical screenshots of the previous dark interface and are not evidence for this redesign.

A deterministic Linux verification script is supplied at `scripts/design-check.mjs`, with the workflow `.github/workflows/design-review.yml`. It serves only the built static frontend and the frozen replay. It does **not** run the simulation. One request-wiring assertion intercepts the existing API request and returns the unchanged saved fixture; the assertion is explicitly distinct from a new experiment. It verifies:

- exact clip duration, easing and stagger, palette variables and reduced-motion disabling;
- a stationary paused measurement canvas, deliberate drag and keyboard rotation without replay-state changes;
- actual saved camera pixels, replay play/pause/seek, policy selection, truth review and the inspection drawer;
- export equality with the frozen fixture and mission request payloads;
- desktop **1440 × 1080**, mobile **390 × 844**, no horizontal overflow and accessible camera/control content;
- zero page errors and genuine desktop/mobile/reduced-motion screenshots.

Run on Linux with Node 24 and the matching Playwright browser/system dependencies:

```bash
(cd frontend && npm ci && npx playwright install --with-deps chromium && npm run build)
node scripts/design-check.mjs
```

Outputs: `artifacts/design/desktop-1440.png`, `mobile-390.png`, `reduced-motion.png`, `verification.txt`, and a fixture-verified export. These are uploaded as the workflow artifact `aeromapper-isometric-desktop-mobile-reduced-motion`. The workflow is prepared but has not been pushed or run; screenshot and interaction assertions remain pending that Linux run.
