# Architecture

AeroMapper separates sensor generation (`vision.py`), hidden environment and mission execution (`simulation.py`), experiment orchestration (`experiment.py`), HTTP boundary (`api.py`), and presentation (`frontend/src`). JSON model weights are data, not executable serialized objects.

1. `world(seed, family)` creates terrain, known static no-fly cells, and hidden targets.
2. `choose(policy, position, seen, belief, blocked, step)` sees only observations/beliefs and known constraints. It cannot read targets or future imagery.
3. Four-connected BFS builds an obstacle-free route. Every edge has a bounded rest-to-rest speed profile. The executor reserves an exact feasible return before accepting an excursion.
4. `observe()` renders deterministic cell imagery at each reached waypoint. Pose-to-grid mapping is explicit: grid index × 8 m. The trained detector supplies cell probabilities.
5. The executed return is part of the same trace, so sensing during return counts equally for both policies.
6. FastAPI validates requests and returns paired, bounded mission runs. The frontend starts with a saved run, then can request new runs.

At 12 m altitude and 60° FOV, footprint width is `2 h tan(FOV/2) = 13.856 m`. Sampling uses included cell centers. Coverage is the fraction of grid cells sampled; it is separate from finding targets and from continuous swept-area coverage. Terrain visualization uses actual elevation data but compresses the displayed drone altitude.

Static no-fly maps are known in advance. This version does not implement revealed-obstacle SLAM, unknown obstacle discovery, vertical dynamics, aerodynamic flight, turning-rate constraints, finite vehicle size, or real energy units. The policy uncertainty term is included but inactive at the default one-cell footprint; the effective adaptive heuristic selects nearby unobserved cells.

`POST /api/compare` accepts integer seed 0–100000, time budget 40–600 s, and family `test`/`ood`. Services bind only to loopback. Full experiments run via CLI and can be interrupted; UI cancellation stops waiting, not server computation. Runtime is bounded by a 12 × 12 grid and at most 200 planner iterations.
