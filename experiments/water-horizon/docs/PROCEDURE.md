# Measurement protocol

One **run** = one flow rate, one depth, one wave frequency, one video. Store each run in its own folder under `data/` with the metadata file described at the end.

## 0. Before the first run

- Check the flow as described at the end of `BUILD.md`.
- Film the ruler and read off the scale: pixels per centimetre (`--px-per-cm`).
- Note the x position of the bump crest in the video (in pixels). You will use it to put x = 0 at the crest.

## 1. Measure the flow

1. Set the pump and the weir. Wait 2 minutes for the flow to settle.
2. **Discharge Q:** hold the bucket under the weir outflow and time how long it takes to collect 10 L. `Q [L/s] = 10 / seconds`. Repeat three times and average.
3. **Depth h₀:** read the water depth on the ruler at least 30 cm downstream of the bump.
4. **Sanity check of speed:** time a pepper flake over 50 cm of calm channel. The mean speed `Q / (width × h₀)` should be roughly 0.8–0.9 of that surface speed.

## 2. Predict

```bash
python analysis/horizon.py --depth <h0 in m> --width <w in m> --flow <Q in L/s> \
       --bump-height 0.03 --bump-length 0.20 --freq 1 1.5 2 2.5 3 --plot data/<run>/prediction.png
```

Note the crest blocking frequency `f_block`. Plan to drive at:
- one frequency **below** `f_block` (control: the wave should pass over the bump),
- two or three frequencies **above** it (the wave should be stopped).

## 3. Baseline without flow

With the pump off and the water still, drive the wave maker at each planned frequency and film 20 s. Waves should travel over the bump unhindered. This gives you the incoming amplitude and wavelength in still water, and checks the camera pipeline.

## 4. Runs with flow

For each frequency:

1. Start the pump, wait 2 minutes.
2. Start recording, then start the wave maker (`g` in the serial monitor). Use a small amplitude: the waves should be 1–3 mm high. Big waves break and behave nonlinearly.
3. Record 40–60 s after the waves reach the bump.
4. Stop the wave maker (`s`), wait until the surface is calm, stop recording.

## 5. Analyse

```bash
python analysis/surface_from_video.py data/<run>/video.mp4 \
       --px-per-cm <scale> --roi <left> <top> <right> <bottom> \
       --x0-cm <x of ROI left edge relative to the crest> \
       --drive-freq <f> --start <s> --end <s> \
       --overlay-speed <U far downstream> --overlay-depth <h0> \
       --out data/<run>/result
```

Choose the ROI so it contains the surface only: from just above the highest crest to just below the lowest trough, avoiding the wave maker and the ruler markings. If the flow goes right-to-left in your video, add `--flip`.

What to look for:

| Plot | Horizon present | No horizon (control) |
|---|---|---|
| `result_spacetime.png` | Diagonal stripes coming from the right stop at a fixed x | Stripes continue across the frame |
| `result_amplitude.png` | Amplitude at the drive frequency drops sharply; local wavelength shrinks just before the drop | Amplitude roughly constant |
| `result_spectrum.png` | Energy at the drive frequency on the upstream branch (k < 0) **and** at much larger \|k\|: the converted short waves | One peak on the upstream branch |

**Main result:** the measured horizon position vs. frequency, compared with the prediction from step 2. Plot one against the other for all runs.

## 6. Going further

- **Negative-frequency waves.** In the research experiments, a small part of the blocked wave converts into a "negative-norm" wave: a wave whose frequency is negative in the frame of the moving water. In `result_spectrum.png` it sits at the drive frequency on the dotted yellow curve (k > 0), drawn when you pass `--overlay-speed` and `--overlay-depth` for the region you analyse. Its amplitude relative to the positive one is the classical analogue of Hawking radiation (Weinfurtner et al. 2011). It is small and hard to see at home, but worth looking for with long, steady runs.
- **Surface tension.** Tap water is often less clean than the default `--sigma 0.072`. A drop of washing-up liquid changes it on purpose; see how the horizon moves.
- **Different bumps.** Steeper vs. gentler slopes change how sharp the horizon is.

## Run metadata

Save as `data/<run>/run.json`:

```json
{
  "date": "2026-11-01",
  "channel_width_m": 0.08,
  "depth_far_m": 0.06,
  "flow_L_per_s": 0.60,
  "flow_measurements_s_per_10L": [16.8, 16.5, 16.9],
  "bump_height_m": 0.03,
  "bump_length_m": 0.20,
  "drive_frequency_Hz": 2.0,
  "servo_amplitude_deg": 10,
  "camera_fps": 60,
  "px_per_cm": 12.4,
  "crest_x_px": 812,
  "water_temperature_C": 19,
  "notes": "slight swirl near inlet; fixed by adding second foam layer"
}
```
