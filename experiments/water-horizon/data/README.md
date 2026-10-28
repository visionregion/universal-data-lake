# Data

One folder per run, named `YYYY-MM-DD_<flow>Lps_<freq>Hz`, for example `2026-11-01_0.60Lps_2.0Hz/`, containing:

- `run.json` — metadata (template in `docs/PROCEDURE.md`)
- `prediction.png` — output of `horizon.py`
- `result_eta.npz`, `result_*.png` — output of `surface_from_video.py`
- a link to the raw video in `run.json` (videos are too large for git; upload them to Zenodo, Google Drive or YouTube)

No runs yet.
