#!/usr/bin/env python3
"""
make_synthetic_video.py - generate a fake channel video with known waves.

Use it to check that surface_from_video.py works before you film anything,
or to practise the analysis. The video shows dyed water (blue) under white
air, flow left-to-right, with:
  * a long wave at --freq Hz travelling upstream (right-to-left) against a
    current --speed, with the wavelength given by the real dispersion relation;
  * the long wave fading out over a "horizon" zone on the left;
  * short capillary waves appearing in that zone, as mode conversion would.

  python make_synthetic_video.py --out synthetic.mp4
  python surface_from_video.py synthetic.mp4 --px-per-cm 10 --roi 0 100 600 300 \
      --drive-freq 2 --overlay-speed 0.12 --overlay-depth 0.06 --out results/synthetic
"""

import argparse
import math

import cv2
import numpy as np
from scipy.optimize import brentq

from horizon import omega_lab_upstream


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="synthetic.mp4")
    p.add_argument("--freq", type=float, default=2.0)
    p.add_argument("--speed", type=float, default=0.12)
    p.add_argument("--depth", type=float, default=0.06)
    p.add_argument("--amp-mm", type=float, default=2.0)
    p.add_argument("--seconds", type=float, default=10.0)
    p.add_argument("--fps", type=float, default=30.0)
    p.add_argument("--px-per-cm", type=float, default=10.0)
    p.add_argument("--noise", type=float, default=4.0, help="pixel noise (0-255)")
    args = p.parse_args()

    w = 2 * math.pi * args.freq
    # long upstream wave: first root of Omega(k) - U k = w
    k_long = brentq(lambda k: omega_lab_upstream(k, args.speed, args.depth) - w, 0.1, 60)
    k_short = 6 * k_long
    print(f"long wave: wavelength {2*math.pi/k_long*100:.2f} cm (k = {k_long:.1f} 1/m)")

    W, Hpx = 600, 400
    base = 200                                    # surface row at rest
    xs = np.arange(W) / (args.px_per_cm * 100)    # metres
    L = xs[-1]
    env_long = 0.5 * (1 + np.tanh((xs - 0.3 * L) / (0.04 * L)))
    env_short = 0.25 * np.exp(-((xs - 0.25 * L) / (0.08 * L)) ** 2)

    rng = np.random.default_rng(1)
    vw = cv2.VideoWriter(args.out, cv2.VideoWriter_fourcc(*"mp4v"), args.fps, (W, Hpx))
    rows = np.arange(Hpx)[:, None]
    for n in range(int(args.seconds * args.fps)):
        t = n / args.fps
        # x points downstream; an upstream wave is cos(-k x - w t) = cos(k x + w t)
        eta = args.amp_mm / 1000 * (env_long * np.cos(k_long * xs + w * t)
                                    + env_short * np.cos(k_short * xs + w * t))
        surf = base - eta * args.px_per_cm * 100
        # smooth (anti-aliased) edge
        water = np.clip(rows - surf[None, :] + 0.5, 0, 1)
        img = np.empty((Hpx, W, 3), np.float32)
        img[..., 0] = 245 - 25 * water            # B
        img[..., 1] = 245 - 145 * water           # G
        img[..., 2] = 245 - 205 * water           # R  (blue dye absorbs red)
        img += rng.normal(0, args.noise, img.shape)
        vw.write(np.clip(img, 0, 255).astype(np.uint8))
    vw.release()
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
