# Model card

**Intended use:** a transparent synthetic cell-image detector in an educational survey simulator. No real-image or flight use is supported.

Input is a 12 × 12 grayscale patch. Features are bias, central brightness contrast, variance, bright-pixel fraction, and maximum 3 × 3 box-template contrast against the background. Labels enter only the synthetic rendering/training target, never decision-time features. The same renderer is used for training and mission observations.

The detector uses five logistic weights trained by batch logistic-loss gradient descent with a small weight penalty, 350 epochs, learning rate 0.6, and 1600 balanced training patches. Train family has background level 0.30. A distinct validation family (background 0.36, seeds 3000–3199) selects a scalar temperature from a fixed five-value grid using log loss. The selected temperature is 0.5. Held-out test background is 0.42; OOD is 0.53 and noisier. Whole patches and scene seeds are split; adjacent pixels/frames are never randomly split across train and test.

The saved `models/detector.json` records weights, format version, feature schema, threshold 0.5, train and validation identities. It is never loaded from a user upload. Missing/malformed weights fall back to the bounded box-template baseline. This fallback is tested, but a UI badge distinguishing fallback mode is a future improvement.

The baseline is a simple bright box-template/contrast score. Detector sweeps report precision, recall, and Brier error across target widths 3/5/7 pixels and noise standard deviations 0.05/0.15/0.25. Reliability bins on 500 untouched test patches are in `results/calibration.json`; the plot does not claim perfect calibration. In OOD missions, precision falls to about 10%, demonstrating a major synthetic domain-shift failure.

Synthetic target shapes are bright squares; distractors are broken lines, with texture and shadows. Visibility attenuates contrast rather than simulating realistic cloud/occlusion geometry. Performance on these patches does not establish recognition of real objects, roads, people, or vehicles.
