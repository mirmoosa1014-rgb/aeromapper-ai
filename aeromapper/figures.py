"""Restyle frozen experiment outputs only; never run a model or rewrite data."""
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/images'
PALETTE = {'paper': '#E6E1D8', 'raised': '#F7F4EF', 'surface': '#F4EFE6', 'ink': '#2B2A28', 'dim': '#6E675F', 'clay': '#E07A5F', 'sage': '#81B29A', 'indigo': '#3D405B', 'sand': '#F2CC8F'}
plt.rcParams.update({'figure.facecolor': PALETTE['paper'], 'axes.facecolor': PALETTE['paper'], 'axes.edgecolor': PALETTE['dim'], 'text.color': PALETTE['ink'], 'axes.labelcolor': PALETTE['dim'], 'xtick.color': PALETTE['dim'], 'ytick.color': PALETTE['dim'], 'grid.color': PALETTE['dim'], 'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica Neue', 'Helvetica', 'Arial', 'DejaVu Sans'], 'font.size': 9, 'savefig.facecolor': PALETTE['paper'], 'axes.titleweight': 'bold', 'axes.spines.top': False, 'axes.spines.right': False})
CMAP = LinearSegmentedColormap.from_list('isometric-target-belief', [PALETTE['surface'], PALETTE['sage'], PALETTE['clay']])
CMAP.set_bad(PALETTE['surface'])

def _tone(color, amount):
    a = np.array(matplotlib.colors.to_rgb(color)); b = np.array(matplotlib.colors.to_rgb(PALETTE['ink'] if amount < 0 else PALETTE['raised']))
    return tuple(a * (1 - abs(amount)) + b * abs(amount))

def generate():
    OUT.mkdir(exist_ok=True)
    demo = json.loads((ROOT / 'results/demo.json').read_text())
    with (ROOT / 'results/missions.csv').open() as handle: rows = list(csv.DictReader(handle))
    with (ROOT / 'results/detector.csv').open() as handle: detector = list(csv.DictReader(handle))
    calibration = json.loads((ROOT / 'results/calibration.json').read_text())
    fig = plt.figure(figsize=(16, 9))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.35, 1, 1], left=.035, right=.975, top=.85, bottom=.11, wspace=.34, hspace=.56)
    mission = demo['adaptive']; terrain = np.array(mission['terrain']); trace = mission['trace']
    ax = fig.add_subplot(gs[:, 0], projection='3d', computed_zorder=False)
    bottom = float(terrain.min()) - .7
    observed = {(int(x), int(y)): p for x, y, p in trace[-1]['belief']}
    for y in range(12):
        for x in range(12):
            z = float(terrain[y, x]); xx, yy = x * 8, y * 8
            corners = [(xx - 3.9, yy - 3.9), (xx + 3.9, yy - 3.9), (xx + 3.9, yy + 3.9), (xx - 3.9, yy + 3.9)]
            faces = [[(a, b, z) for a, b in corners], [(corners[0][0], corners[0][1], bottom), (corners[1][0], corners[1][1], bottom), (corners[1][0], corners[1][1], z), (corners[0][0], corners[0][1], z)], [(corners[1][0], corners[1][1], bottom), (corners[2][0], corners[2][1], bottom), (corners[2][0], corners[2][1], z), (corners[1][0], corners[1][1], z)]]
            probability = observed.get((x, y))
            color = PALETTE['surface'] if probability is None else PALETTE['clay'] if probability >= .5 else PALETTE['sage']
            ax.add_collection3d(Poly3DCollection(faces, facecolors=[_tone(color, .1), _tone(color, -.08), _tone(color, -.18)], edgecolors=_tone(color, -.1), linewidths=.25, zorder=1))
    ax.plot([f['position'][0] * 8 for f in trace], [f['position'][1] * 8 for f in trace], [terrain[f['position'][1], f['position'][0]] + .15 for f in trace], color=PALETTE['indigo'], lw=2, label='Executed ground-track overlay', zorder=10)
    ax.scatter([p[0] * 8 for p in mission['targets']], [p[1] * 8 for p in mission['targets']], [terrain[p[1], p[0]] + .25 for p in mission['targets']], color=PALETTE['clay'], marker='x', s=27, linewidths=1.5, label='Target truth (review only)', depthshade=False, zorder=11)
    ax.set(xlabel='East (m)', ylabel='North (m)', zlabel='Elevation (m)', title=f"01 / Terrain study\nSaved counterexample · seed {mission['metrics']['seed']}", xlim=(-5, 94), ylim=(-5, 94), zlim=(bottom, 7))
    ax.view_init(32, -55); ax.set_box_aspect((1, 1, .5)); ax.grid(False)
    for axis in [ax.xaxis, ax.yaxis, ax.zaxis]: axis.pane.fill = False; axis.pane.set_edgecolor('#00000000')
    ax.legend(loc='upper left', bbox_to_anchor=(.02, .94), frameon=False, fontsize=8)
    colors = {'adaptive': PALETTE['clay'], 'lawnmower': PALETTE['indigo']}
    ax = fig.add_subplot(gs[0, 1])
    for policy, color in colors.items():
        t = demo[policy]['trace']; ax.plot([f['time_s'] for f in t], [f['coverage'] * 100 for f in t], color=color, lw=2, label=policy.capitalize())
    ax.set(xlabel='Mission time (s)', ylabel='Observed cells (%)', title='02 / Coverage through time', ylim=(0, 40)); ax.grid(axis='y', alpha=.15); ax.legend(frameon=False, fontsize=8)
    ax = fig.add_subplot(gs[0, 2])
    groups = [[float(r['recall']) * 100 for r in rows if r['policy'] == p and r['family'] == f] for f in ['test', 'ood'] for p in ['lawnmower', 'adaptive']]
    bp = ax.boxplot(groups, patch_artist=True, tick_labels=['Fixed\nTest', 'Adaptive\nTest', 'Fixed\nOOD', 'Adaptive\nOOD'], medianprops={'color': PALETTE['ink']}, whiskerprops={'color': PALETTE['dim']}, capprops={'color': PALETTE['dim']}, flierprops={'markeredgecolor': PALETTE['dim']})
    for box, color in zip(bp['boxes'], [PALETTE['indigo'], PALETTE['clay']] * 2): box.set_facecolor(color); box.set_edgecolor(PALETTE['ink']); box.set_alpha(.75)
    ax.set(ylabel='Target recall (%)', title='03 / Recall across 24 paired scenes'); ax.grid(axis='y', alpha=.15)
    ax = fig.add_subplot(gs[1, 1]); ax.plot([0, 1], [0, 1], color=PALETTE['dim'], ls='--', lw=1)
    ax.plot([b['confidence'] for b in calibration], [b['frequency'] for b in calibration], marker='o', color=PALETTE['clay'], lw=2)
    ax.set(xlabel='Predicted probability', ylabel='Observed target fraction', title='04 / Saved calibration diagnostic', xlim=(0, 1), ylim=(0, 1.05)); ax.grid(alpha=.15)
    ax = fig.add_subplot(gs[1, 2])
    for name, color in [('logistic', PALETTE['clay']), ('template', PALETTE['indigo'])]:
        for metric, style in [('recall', '-'), ('precision', '--')]:
            points = [(noise, np.mean([float(r[metric]) for r in detector if r['detector'] == name and r['family'] == 'test' and float(r['noise_sigma']) == noise])) for noise in [.05, .15, .25]]
            ax.plot([p[0] for p in points], [p[1] for p in points], color=color, ls=style, marker='o' if metric == 'recall' else 's', ms=3, label=f'{name} · {metric}')
    ax.set(xlabel='Pixel-noise standard deviation', ylabel='Mean over target sizes', title='05 / Detection under image noise', ylim=(0, 1.05)); ax.grid(alpha=.15); ax.legend(frameon=False, fontsize=7, loc='lower left')
    fig.text(.035, .947, 'AeroMapper', fontsize=25, weight='bold')
    fig.text(.035, .911, 'SPATIAL SURVEY DESK / SAVED EXPERIMENTS', color=PALETTE['dim'], fontsize=9, fontfamily='monospace')
    fig.text(.975, .941, 'ISOMETRIC STUDIO\nSYNTHETIC DATA ONLY', ha='right', va='center', fontsize=9, color=PALETTE['indigo'], fontfamily='monospace')
    fig.text(.035, .081, 'Paper: unobserved   /   Sage: low target belief   /   Clay: high target belief', color=PALETTE['dim'], fontsize=9)
    fig.text(.035, .043, '96 measured missions · paired seeds · 220 s budget · energy is an illustrative proxy. This restyle reads frozen data only.', color=PALETTE['dim'], fontsize=10)
    fig.savefig(OUT / 'research-overview.png', dpi=150); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5)); writer = PillowWriter(fps=6)
    with writer.saving(fig, str(OUT / 'mission-replay.gif'), 90):
        maximum = max(len(demo[p]['trace']) for p in colors)
        for i in range(0, maximum, max(1, maximum // 36)):
            for ax, policy in zip(axes, colors):
                ax.clear(); m = demo[policy]; t = m['trace']; f = t[min(i, len(t) - 1)]; field = np.full((12, 12), np.nan)
                for x, y, probability in f['belief']: field[int(y), int(x)] = probability
                ax.imshow(field, cmap=CMAP, vmin=0, vmax=1, origin='lower')
                ax.plot([v['position'][0] for v in t[:i + 1]], [v['position'][1] for v in t[:i + 1]], color=colors[policy], lw=1.8)
                ax.set_title(f"{policy.capitalize()} · {f['time_s']:.0f} s · {f['coverage'] * 100:.0f}% coverage", fontsize=11)
                ax.set(xlabel='East cell (8 m)', ylabel='North cell (8 m)')
            fig.suptitle('Observed beliefs / saved mission replay', fontsize=14, weight='bold')
            fig.tight_layout(rect=(0, 0, 1, .94)); writer.grab_frame()
    plt.close(fig)

if __name__ == '__main__': generate()
