#!/usr/bin/env python3
"""
surface_from_video.py - measure the water surface from a side-view video.

Film the channel through its transparent wall, with dyed water in front of a
plain light background. For every frame and every pixel column the script
finds the air/water boundary, which gives the surface elevation eta(x, t).

From eta(x, t) it produces:
  * eta.npz               - the raw surface data (x in m, t in s, eta in m)
  * spacetime.png         - eta(x, t) as an image: incoming waves are diagonal
                            stripes, a horizon is where the stripes stop
  * amplitude.png         - amplitude of the driving frequency along x, and
                            the local wavelength: at the horizon the long wave
                            dies away and short waves appear
  * spectrum.png          - 2D Fourier spectrum |eta(k, f)|, optionally with
                            the theoretical dispersion curve on top

Usage
-----
  python surface_from_video.py run.mp4 --px-per-cm 12.5 --roi 100 200 1800 420 \
         --drive-freq 2.0 --x0-cm -40 --out results/run1 \
         --overlay-speed 0.12 --overlay-depth 0.06

The ROI is "left top right bottom" in pixels and should contain only the
stretch of water surface you want to analyse (no obstacle, no reflections).
Open one frame in any image viewer to read those numbers off.
"""

from __future__ import annotations

import argparse
import math
import os

import cv2
import numpy as np


# --------------------------------------------------------------------------
# Surface extraction
# --------------------------------------------------------------------------

def frame_to_signal(frame, channel):
    """Return a float image where water is BRIGHT and air is DARK."""
    if channel == "gray":
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
        return 255.0 - img                     # dyed water is darker than background
    idx = {"b": 0, "g": 1, "r": 2}[channel]
    img = frame[:, :, idx].astype(np.float32)
    return 255.0 - img                         # dye absorbs this channel


def surface_rows(signal, threshold):
    """
    For every column, the sub-pixel row where the signal first rises above
    `threshold` scanning from the top (air) down into the water.
    Returns an array of rows (float) with nan where no surface was found.
    """
    above = signal > threshold
    first = np.argmax(above, axis=0)
    found = above[first, np.arange(signal.shape[1])]
    rows = first.astype(np.float64)
    # sub-pixel: linear interpolation between the row above and the crossing row
    cols = np.arange(signal.shape[1])
    ok = found & (first > 0)
    a = signal[first[ok] - 1, cols[ok]]
    b = signal[first[ok], cols[ok]]
    frac = np.clip((threshold - a) / np.maximum(b - a, 1e-6), 0, 1)
    rows[ok] = first[ok] - 1 + frac
    rows[~found] = np.nan
    return rows


def extract(video, roi, channel, threshold, start, end, every):
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open video {video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    n_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    i0 = int(start * fps)
    i1 = n_total if end is None else min(n_total, int(end * fps))
    cap.set(cv2.CAP_PROP_POS_FRAMES, i0)

    x0, y0, x1, y1 = roi
    rows, times = [], []
    auto = threshold is None
    for i in range(i0, i1):
        ok, frame = cap.read()
        if not ok:
            break
        if (i - i0) % every:
            continue
        sig = frame_to_signal(frame[y0:y1, x0:x1], channel)
        if auto:
            # Otsu on the first frame, then keep it fixed for consistency
            u8 = np.clip(sig, 0, 255).astype(np.uint8)
            threshold, _ = cv2.threshold(u8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            auto = False
            print(f"Automatic threshold: {threshold:.0f}")
        rows.append(surface_rows(sig, threshold))
        times.append(i / fps)
    cap.release()
    if not rows:
        raise SystemExit("No frames read. Check --start/--end.")
    return np.array(rows), np.array(times), fps / every, threshold


def clean(rows, max_jump_px=6):
    """Fill gaps and remove single-pixel spikes (splashes, specks of dirt)."""
    out = rows.copy()
    for r in out:
        bad = np.isnan(r)
        if bad.all():
            continue
        idx = np.arange(r.size)
        r[bad] = np.interp(idx[bad], idx[~bad], r[~bad])
        med = cv2.medianBlur(r.astype(np.float32).reshape(1, -1), 5).ravel()
        spikes = np.abs(r - med) > max_jump_px
        r[spikes] = med[spikes]
    return out


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------

def lockin(eta, t, f):
    """Complex amplitude of frequency f at every x (least-squares sinusoid)."""
    ph = np.exp(-2j * math.pi * f * t)[:, None]
    return 2 * np.mean(eta * ph, axis=0)


def local_wavelength(amp, dx, smooth=15):
    """Wavelength from the spatial phase gradient of the complex amplitude."""
    phase = np.unwrap(np.angle(amp))
    k = np.gradient(phase, dx)
    if smooth > 1:
        k = np.convolve(k, np.ones(smooth) / smooth, mode="same")
    with np.errstate(divide="ignore"):
        return 2 * math.pi / np.abs(k)


def spectrum(eta, dx, dt):
    win_t = np.hanning(eta.shape[0])[:, None]
    win_x = np.hanning(eta.shape[1])[None, :]
    F = np.fft.fftshift(np.fft.fft2(eta * win_t * win_x))
    f = np.fft.fftshift(np.fft.fftfreq(eta.shape[0], dt))
    # numpy's FFT uses exp(-i(wt + kx)); a wave cos(kx - wt) therefore shows up
    # at (-k, +f). Flip k so that, for f > 0, k has its physical sign.
    k = -np.fft.fftshift(np.fft.fftfreq(eta.shape[1], dx)) * 2 * math.pi
    return k[::-1], f, np.abs(F)[:, ::-1]


# --------------------------------------------------------------------------
# Plots
# --------------------------------------------------------------------------

def plots(out, x, t, eta, args):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    xc = x * 100
    lim = np.nanpercentile(np.abs(eta), 99) * 1000 or 1

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(eta * 1000, aspect="auto", origin="lower", cmap="RdBu_r",
                   extent=[xc[0], xc[-1], t[0], t[-1]], vmin=-lim, vmax=lim)
    fig.colorbar(im, ax=ax, label="surface elevation (mm)")
    ax.set_xlabel("x (cm)")
    ax.set_ylabel("time (s)")
    ax.set_title("Space-time diagram: stripes are wave crests")
    fig.tight_layout()
    fig.savefig(out + "_spacetime.png", dpi=130)
    plt.close(fig)

    if args.drive_freq:
        amp = lockin(eta, t, args.drive_freq)
        lam = local_wavelength(amp, x[1] - x[0])
        fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        axes[0].plot(xc, np.abs(amp) * 1000, color="#1f4e79")
        axes[0].set_ylabel("amplitude at drive (mm)")
        axes[0].set_title(f"Response at the driving frequency {args.drive_freq:g} Hz")
        axes[1].plot(xc, lam * 100, color="#c0504d")
        axes[1].set_ylabel("local wavelength (cm)")
        axes[1].set_xlabel("x (cm)")
        axes[1].set_ylim(0, np.nanpercentile(lam * 100, 95) * 1.3)
        fig.tight_layout()
        fig.savefig(out + "_amplitude.png", dpi=130)
        plt.close(fig)

    k, f, S = spectrum(eta, x[1] - x[0], t[1] - t[0])
    fig, ax = plt.subplots(figsize=(8, 5))
    pos = f >= 0
    ax.imshow(np.log10(S[pos] + 1e-12), aspect="auto", origin="lower", cmap="magma",
              extent=[k[0], k[-1], f[pos][0], f[pos][-1]])
    if args.overlay_speed is not None and args.overlay_depth is not None:
        from horizon import omega_intrinsic
        kk = np.linspace(1e-3, np.max(np.abs(k)), 1000)
        U, h = args.overlay_speed, args.overlay_depth
        # x axis points downstream: upstream waves have k < 0 in the video frame
        up = omega_intrinsic(kk, h) - U * kk      # crests move upstream (k < 0)
        down = omega_intrinsic(kk, h) + U * kk    # crests move downstream (k > 0)
        ax.plot(-kk, up / (2 * math.pi), "-", color="#9fd3ff", lw=1, label="theory")
        neg = U * kk - omega_intrinsic(kk, h)     # negative-norm ("Hawking partner") branch
        ax.plot(kk, down / (2 * math.pi), "--", color="#9fd3ff", lw=1)
        ax.plot(kk, np.where(neg > 0, neg, np.nan) / (2 * math.pi), ":", color="#ffd27f",
                lw=1.2, label="negative-norm branch")
        ax.legend(loc="upper right", frameon=False, labelcolor="white")
    ax.set_xlim(-args.kmax, args.kmax)
    fmax = args.fmax or (3 * args.drive_freq if args.drive_freq else f[pos][-1])
    ax.set_ylim(0, min(fmax, f[pos][-1]))
    ax.set_xlabel("wavenumber k (1/m)   [k < 0: crests move upstream]")
    ax.set_ylabel("frequency (Hz)")
    ax.set_title("Fourier spectrum |eta(k, f)|")
    fig.tight_layout()
    fig.savefig(out + "_spectrum.png", dpi=130)
    plt.close(fig)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("video")
    p.add_argument("--px-per-cm", type=float, required=True,
                   help="scale: film a ruler in the same plane as the surface")
    p.add_argument("--roi", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
                   required=True, help="region of interest in pixels")
    p.add_argument("--channel", default="r", choices=["r", "g", "b", "gray"],
                   help="colour channel the dye absorbs most (blue dye -> r)")
    p.add_argument("--threshold", type=float, help="fixed threshold (default: Otsu)")
    p.add_argument("--start", type=float, default=0.0, help="start time in s")
    p.add_argument("--end", type=float, help="end time in s")
    p.add_argument("--every", type=int, default=1, help="use every N-th frame")
    p.add_argument("--x0-cm", type=float, default=0.0,
                   help="x position (cm) of the ROI's left edge, e.g. relative to the crest")
    p.add_argument("--flip", action="store_true",
                   help="set if the flow goes right-to-left in the video")
    p.add_argument("--drive-freq", type=float, help="wave maker frequency in Hz")
    p.add_argument("--overlay-speed", type=float, help="U (m/s) for the dispersion overlay")
    p.add_argument("--overlay-depth", type=float, help="h (m) for the dispersion overlay")
    p.add_argument("--kmax", type=float, default=600, help="spectrum plot range in 1/m")
    p.add_argument("--fmax", type=float, help="spectrum plot range in Hz")
    p.add_argument("--out", default="results/run", help="output prefix")
    args = p.parse_args(argv)

    rows, t, fps, thr = extract(args.video, args.roi, args.channel, args.threshold,
                                args.start, args.end, args.every)
    rows = clean(rows)
    if args.flip:
        rows = rows[:, ::-1]

    scale = 1.0 / (args.px_per_cm * 100)          # metres per pixel
    eta = -(rows - np.nanmean(rows, axis=0)) * scale  # rows grow downwards
    x = args.x0_cm / 100 + np.arange(eta.shape[1]) * scale
    t = t - t[0]

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    np.savez_compressed(args.out + "_eta.npz", x=x, t=t, eta=eta, fps=fps, threshold=thr)
    print(f"{eta.shape[0]} frames at {fps:.1f} fps, {eta.shape[1]} columns "
          f"({(x[-1]-x[0])*100:.1f} cm); RMS elevation {np.std(eta)*1000:.2f} mm")
    plots(args.out, x, t, eta, args)
    print(f"Saved {args.out}_eta.npz and plots.")


if __name__ == "__main__":
    main()
