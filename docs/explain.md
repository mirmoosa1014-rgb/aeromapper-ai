# A plain-language explanation

Imagine searching a field with a camera and a timer. You cannot inspect everything before the battery budget runs out. One strategy moves through the field in fixed rows. Another selects a nearby place it has not seen yet. AeroMapper tests these ideas on the same pretend world.

The pretend camera produces a small grayscale image. A trained mathematical model turns five brightness/texture measurements into a probability that a target is present. The model learned from generated examples, not real photographs. The drone's policy sees only observed probabilities. The simulator knows the hidden targets so it can grade the completed search.

Coverage answers “how much did I look at?” Recall answers “how many actual targets did I find?” Precision answers “how many reported targets were real?” A system can look at more cells and still miss more targets, or report many false alarms. This prototype deliberately preserves those failures in its results.

Each movement has a time and energy cost. Before going outward, the simulator checks that the outward route and a complete return route fit. Obstacles are static no-fly cells supplied in advance. That makes the path check transparent, but it does not reproduce a real flying vehicle.

## Ten reviewer questions

1. **What is learned?** Five logistic image-detector weights and a validation-selected temperature; not the flight planner.
2. **What is the baseline?** Fixed lawnmower coverage plus the same detector, and a simple box-template image detector in perception sweeps.
3. **Can the planner read hidden targets?** No. Its function receives position, seen cells, beliefs and known blocked cells.
4. **Why use matched seeds?** To avoid giving one policy easier target placement or different image noise.
5. **Why separate families?** To test different rendering conditions rather than memorizing repeated images.
6. **What happens if the model is missing?** Inference falls back to the transparent box-template score.
7. **Does it return home?** Yes, on an explicitly reserved and executed obstacle-free grid route within the proxy budgets.
8. **Where does it fail?** Seed 2015 misses two targets that lawnmower finds; OOD precision falls near 10%.
9. **Is this a real camera or flight test?** No. All imagery, terrain, targets and motion are generated in software.
10. **What would improve it next?** Realistic image/occlusion modeling, an uncertainty-aware multi-cell sensing policy, and independently validated dynamics before any hardware work.
