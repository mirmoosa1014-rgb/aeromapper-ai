# Evaluation protocol and findings

The full bounded experiment runs 24 scenario seeds (2000–2023), two policies, and two families, producing 96 missions. Each matched pair uses the same terrain, target set, obstacles, sensor noise realizations, observation model, classifier, 220 s time limit, and 187-unit energy-proxy limit. Targets not observed are counted as missed. Final precision with no detections is defined as zero, rather than silently discarding the episode. Both policies execute and observe on the reserved return route.

Train patches use seeds 0–1599 and family `train`. Calibration uses only family `validation`, seeds 3000–3199. Detector testing uses family `test`/`ood`, seeds 10000–10099 in the size/noise sweeps and 10000–10499 for the separate calibration diagnostic. Mission camera seeds are `scene_seed * 10000 + cell_id`. No model parameters or planner constants were tuned on the final mission set.

Held-out scene averages: lawnmower recall 25.89% (sample SD 16.15 percentage points); adaptive recall 33.33% (SD 14.99 points). Coverage averages are 24.86% and 30.30%. These are small synthetic samples, without a claimed real-world effect or universal statistical superiority. The policies often finish below the budget because the next proposed excursion plus return will not fit.

**Counterexample:** seed 2015, test family. Lawnmower finds 8 of 14 targets, adaptive 6 of 14, both over 432 m and 216 s, returning to base. Adaptive coverage is 31.25%, higher than lawnmower's 27.78%, but local ordering spends time in a less target-rich area. The saved app example intentionally uses this unfavorable episode.

**OOD failure:** denser obstacles, different terrain and higher patch noise yield adaptive recall 32.14% but only 10.23% precision; lawnmower precision is 9.90%. More coverage is not a reliable detector. Inspect false discoveries, Brier error, and reliability bins rather than highlighting recall alone.

Runtime is measured with `perf_counter` per mission. It includes simulation, rendering, inference, planning and trace construction; warm caches, machine load and execution host affect it. Runtime values are not deterministic, while observations and traces are deterministic. Record means and sample SD from `results/summary.json`, not an assumed speedup.

Tests validate exact return/time/energy feasibility, collision-free four-connected routes, footprint and pose mapping, replay, missing-model fallback, matched-world identities, API errors, and family separation. TypeScript type-checking and production build passed. A clean pinned Python install passed. The normal Chromium binary failed on an environment socket permission; the headless-shell alternative launched successfully. Real browser checks passed replay seeking, truth toggling, policy switches, 3D drag rotation, a new API mission, JSON export, and desktop/mobile rendering without page errors. Actual screenshots are in docs/images. Generated plots/animation are separately identified as simulated evidence.

Major remaining gaps: no online discovery of unknown obstacles, no realistic camera occlusion, no continuous image mosaic, no uncertainty-aware revisiting (the default footprint is one grid cell), no terrain-following dynamics or vehicle footprint, and no real aerial dataset. These are explicit bounds on this prototype.
