# 90-second demonstration

0–15 s: Open the locally running app. Identify the software-only badge and the four measured mission outcomes. Explain that coverage and target recall differ.

15–35 s: Drag the 3D scene, scrub replay, and identify the actual cell image and probability in the sensor panel. The bright squares are synthetic targets, not real drone images.

35–55 s: Toggle ground truth for review. Switch policies. The default seed 2015 shows adaptive coverage increasing while target recall drops from 8/14 to 6/14. Explain the local greedy failure.

55–75 s: Run a new paired seed with the same budget, then select OOD. Explain why increased noise produces false discoveries and poor precision. Export the current JSON trace.

75–90 s: Show the research figure and paired CSVs. Explain exact return-to-base budgeting, the known-map assumption, and why synthetic tests cannot establish flight safety.

If the backend is unavailable, saved replay still works under the frontend server; new missions require FastAPI. No flight hardware is connected.
