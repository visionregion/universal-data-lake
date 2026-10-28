# Building the channel

The design below is the **reference setup** used throughout this repository. Everything can be scaled, but run `analysis/horizon.py` with your own numbers before cutting anything: the window in which a horizon forms without the flow choking is narrow.

```
   UPSTREAM TANK                    CHANNEL (clear walls)                   DOWNSTREAM TANK
  ┌────────────┐  ┌──────────────────────────────────────────────────┐  ┌────────────┐
  │            │  │ straws  absorber        ▁▂▄▆▄▂▁          wave    │  │            │
  │   inflow ──┼─▶│ ||||||  ╲╲╲      flow → ═bump═  ← waves  maker ▼ │weir│   pump ──┐ │
  │            │  │ ||||||   ╲╲╲                                      │  │          │ │
  └────────────┘  └──────────────────────────────────────────────────┘  └──────────┼─┘
        ▲                                                                           │
        └───────────────────────────── return hose ─────────────────────────────────┘
```

Water is pumped from the downstream tank back to the upstream tank, flows through a flow straightener, along the channel and over the bump, past the wave maker and over an adjustable weir back into the downstream tank. Waves made near the downstream end travel upstream, against the current, towards the bump.

## Parts

| Part | Reference spec | Notes |
|---|---|---|
| Channel | 1.5–2 m long, 8 cm wide (inside), 15 cm tall | 3–4 mm clear acrylic sheet, glued with acrylic cement and sealed with aquarium silicone. At least one side wall must be clear and free of scratches where you film. |
| Two tanks | 40–60 L plastic storage boxes | The upstream one feeds the channel through a hole near its bottom; the downstream one holds the pump. |
| Pump | Submersible pond/aquarium pump, 3000–4000 L/h nominal | Real flow at 0.5–1 m head is much lower than the label. Buy bigger and throttle it. A 12 V DC model is safer. |
| Flow control | Ball valve on the pump outlet, or a bypass back into the tank | A bypass is gentler on the pump. |
| Hose | 20–25 mm ID, with clamps | |
| Flow straightener | A bundle of drinking straws (about 10 cm long) filling the channel cross-section, plus a layer of open-cell foam in front | The most important part for clean results: turbulence from the inlet ruins the wave field. |
| Bump | 20 cm long, 3 cm tall, smooth cos² profile (shape below), full channel width | Sanded and varnished wood, a 3D print, or epoxy putty over a template. Seal its edges to the floor with silicone. |
| Weir | A plastic plate sliding in two guides at the outlet | Sets the water depth in the channel. |
| Wave maker | Hobby servo (e.g. MG996R class), Arduino Uno/Nano, separate 5–6 V 2 A supply, a wedge-shaped plunger of plastic or wood across the channel width | See `wavemaker/wavemaker.ino`. Mount the servo on a bridge above the channel, not on the wall. |
| Absorber ("beach") | Sloping pad of open-cell foam at the upstream end | Soaks up waves that get past the bump (at low frequency) so they don't reflect. |
| Camera | Any phone that records 60 fps, on a tripod | Lock focus and exposure. Lens at the height of the water surface, perpendicular to the wall. |
| Backlight | LED panel or a window, behind a sheet of white paper or tracing paper on the far wall | Even, flicker-free light. Avoid mains-frequency flicker with LED lamps that are rated flicker-free. |
| Dye | Blue food colouring | A few drops per 10 L. Blue dye absorbs red, so analyse the red channel. |
| Ruler | Waterproof ruler taped to the camera-side wall at surface level | Scale calibration. |
| Flow tracers | Ground pepper or dried herbs (they float) | For a rough surface-speed check. |
| Measuring | 10 L bucket, stopwatch | Flow rate by timing how long the outflow takes to fill the bucket. |
| Safety | 30 mA RCD/GFCI adapter for the pump | Not optional for a mains pump. |

## The bump profile

Use the same shape the calculator assumes: height `H`, length `L`,

```
z(x) = H · cos²(π x / L)   for |x| ≤ L/2,   0 elsewhere
```

For the reference bump (H = 3 cm, L = 20 cm), heights every 1 cm from the crest:

| x (cm) | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| z (mm) | 30.0 | 29.3 | 27.1 | 23.8 | 19.6 | 15.0 | 10.4 | 6.2 | 2.9 | 0.7 | 0 |

Print this profile 1:1, glue it to card, and use it as a template. Smooth slopes matter: a sharp edge sheds vortices.

## Assembly order

1. **Glue the channel** and let it cure for 24 h. Fill it with water on its own and check for leaks before adding anything else.
2. **Fit the bump** about 60% of the way along the channel from the inlet, so there is a long run of calm water downstream for the waves to travel through.
3. **Fit the flow straightener** at the inlet: foam first, then the straw bundle.
4. **Fit the weir** at the outlet and the **foam beach** at the upstream end, after the straightener.
5. **Mount the wave maker** 40–60 cm downstream of the bump. The plunger should dip 1–2 cm into the water at its centre position.
6. **Plumb the pump** with the valve or bypass, and put it behind the RCD.
7. **Set up the camera and backlight.** Frame a stretch of about 60 cm covering the downstream slope of the bump and the water in front of it. Tape the ruler on.

## Checking the flow before measuring anything

- Fill to the reference depth (6 cm far from the bump, adjusted with the weir) and start the pump at a low setting.
- Sprinkle a pinch of pepper. It should move smoothly and steadily, without swirling. If it swirls, improve the straightener.
- Increase the flow slowly. The surface over the bump should dip smoothly. If you see a sudden step or a foaming jump just downstream of the crest, the flow has gone supercritical: back off. `horizon.py` will tell you the same thing in advance.
- A small, stationary rippled pattern just downstream of the bump is normal: it is the "zero-frequency" mode of the horizon and was seen in the research flumes too.
