#!/usr/bin/env python3
"""
horizon.py - predict where a "white hole" horizon forms in a water channel.

Surface waves are sent upstream, against a current that speeds up as it
passes over an obstacle on the channel floor. Where the current becomes as
fast as the waves' group velocity, they can no longer move upstream: that
point is the analogue of an event horizon.

The script:
  1. solves the 1D Bernoulli equation for the water depth h(x) and flow
     speed U(x) over a smooth bump (subcritical branch),
  2. uses the full gravity-capillary dispersion relation
         Omega(k)^2 = (g k + sigma k^3 / rho) tanh(k h)
     to find, at every x, the highest lab-frame frequency f_block(x) that can
     still travel upstream,
  3. reports where f_block(x) equals each requested wave frequency
     (the horizon) and plots the result.

Usage examples
--------------
  # whole channel, flow given as a discharge in litres per second
  python horizon.py --depth 0.06 --width 0.08 --flow 0.9 \
                    --bump-height 0.035 --bump-length 0.15 --freq 2 3 4

  # single point: what is blocked at U = 0.30 m/s, h = 0.03 m?
  python horizon.py --point --speed 0.30 --depth 0.03 --freq 2 3

All units are SI unless the option says otherwise.
"""

from __future__ import annotations

import argparse
import math
import sys

import numpy as np
from scipy.optimize import brentq, minimize_scalar

G = 9.81          # m/s^2
RHO = 1000.0      # kg/m^3
SIGMA = 0.072     # N/m, clean water; tap water is often closer to 0.06-0.07


# --------------------------------------------------------------------------
# Dispersion relation
# --------------------------------------------------------------------------

def omega_intrinsic(k, h, sigma=SIGMA):
    """Angular frequency in the frame moving with the water (rad/s)."""
    k = np.asarray(k, dtype=float)
    return np.sqrt((G * k + sigma * k**3 / RHO) * np.tanh(k * h))


def group_velocity(k, h, sigma=SIGMA, dk=1e-4):
    """d Omega / dk, numerically (m/s)."""
    return (omega_intrinsic(k + dk, h, sigma) - omega_intrinsic(k - dk, h, sigma)) / (2 * dk)


def omega_lab_upstream(k, U, h, sigma=SIGMA):
    """
    Lab-frame frequency of a wave whose crests move upstream relative to the
    water, in a current of speed U flowing downstream. k > 0 is the
    wavenumber magnitude.
    """
    return omega_intrinsic(k, h, sigma) - U * k


def blocking_frequency(U, h, sigma=SIGMA, k_max=3000.0):
    """
    Highest lab-frame frequency (Hz) that can still propagate upstream on the
    gravity branch, and the wavenumber where it is reached.

    Returns (f_block, k_block). If the current is slower than the minimum
    group velocity of water waves, nothing is blocked: returns (inf, nan).
    """
    if U <= 0:
        return math.inf, math.nan

    # Gravity-branch blocking point: first k where group velocity drops to U.
    ks = np.logspace(-1, math.log10(k_max), 4000)
    cg = group_velocity(ks, h, sigma)
    below = np.nonzero(cg < U)[0]
    if below.size == 0:
        return math.inf, math.nan
    i = below[0]
    if i == 0:
        # even the longest waves are slower than the flow
        return 0.0, ks[0]
    kb = brentq(lambda k: group_velocity(k, h, sigma) - U, ks[i - 1], ks[i])
    wb = omega_lab_upstream(kb, U, h, sigma)
    return max(wb, 0.0) / (2 * math.pi), kb


def wavenumbers_for_frequency(f, U, h, sigma=SIGMA, k_max=3000.0):
    """
    All wavenumbers k > 0 at which an upstream-type wave has lab frequency f
    in a current U. Below the blocking frequency there are typically two
    gravity solutions plus one short capillary ("blue-shifted") solution;
    above it only the capillary one survives.
    """
    w = 2 * math.pi * f
    ks = np.logspace(-1, math.log10(k_max), 20000)
    vals = omega_lab_upstream(ks, U, h, sigma) - w
    roots = []
    for a, b, va, vb in zip(ks[:-1], ks[1:], vals[:-1], vals[1:]):
        if va == 0:
            roots.append(a)
        elif va * vb < 0:
            roots.append(brentq(lambda k: omega_lab_upstream(k, U, h, sigma) - w, a, b))
    return roots


# --------------------------------------------------------------------------
# Flow over the obstacle (1D Bernoulli, subcritical branch)
# --------------------------------------------------------------------------

def bump_profile(x, height, length):
    """Smooth obstacle: a cos^2 hump of given height and total length."""
    out = np.zeros_like(x)
    inside = np.abs(x) <= length / 2
    out[inside] = height * np.cos(math.pi * x[inside] / length) ** 2
    return out


def solve_depth(Q, W, H_far, zb):
    """
    Water depth over a bed elevation zb, conserving specific energy
        E = h + q^2 / (2 g h^2) + zb,   q = Q / W,
    on the subcritical (deep, slow) branch. H_far is the depth far from the
    obstacle where zb = 0. Returns nan where the flow would have to go
    supercritical (no smooth subcritical solution: expect a hydraulic jump).
    """
    q = Q / W
    E = H_far + q**2 / (2 * G * H_far**2)
    h_crit = (q**2 / G) ** (1 / 3)

    def f(h, z):
        return h + q**2 / (2 * G * h**2) + z - E

    hs = np.empty_like(zb)
    for i, z in enumerate(zb):
        if f(h_crit, z) > 0:          # energy below the critical minimum
            hs[i] = np.nan
            continue
        hs[i] = brentq(f, h_crit, H_far + 1.0, args=(z,))
    return hs


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------

def run_point(args):
    U, h = args.speed, args.depth
    fb, kb = blocking_frequency(U, h, args.sigma)
    print(f"Current U = {U:.3f} m/s, depth h = {h*100:.1f} cm")
    if math.isinf(fb):
        print("  Current is slower than the slowest water waves: nothing is blocked.")
    else:
        print(f"  Blocking frequency f_block = {fb:.2f} Hz "
              f"(wavelength at blocking {2*math.pi/kb*100:.1f} cm)")
    for f in args.freq:
        ks = wavenumbers_for_frequency(f, U, h, args.sigma)
        lam = ", ".join(f"{2*math.pi/k*100:.2f} cm" for k in ks) or "none"
        state = "propagates upstream" if f < fb else "BLOCKED (horizon reached)"
        print(f"  f = {f:.2f} Hz: {state}; wavelengths of solutions: {lam}")


def run_channel(args):
    if args.flow is not None:
        Q = args.flow / 1000.0
    elif args.speed is not None:
        Q = args.speed * args.width * args.depth
    else:
        sys.exit("Give either --flow (L/s) or --speed (m/s, far from the obstacle).")

    L = args.bump_length
    x = np.linspace(-1.5 * L, 1.5 * L, 601)
    zb = bump_profile(x, args.bump_height, L)
    h = solve_depth(Q, args.width, args.depth, zb)
    U = Q / (args.width * h)

    U0 = Q / (args.width * args.depth)
    print(f"Discharge Q = {Q*1000:.2f} L/s ({Q*3.6e6:.0f} L/h), "
          f"far-field speed U0 = {U0:.3f} m/s, depth {args.depth*100:.1f} cm")

    if np.isnan(h).any():
        print("\nThe flow cannot stay smooth over this bump: it would go supercritical "
              "and form a hydraulic jump, which hides the effect.\n"
              "Lower the bump, lower the flow rate, or raise the water level.")
        sys.exit(1)
    crest = int(np.argmin(h))

    fblock = np.array([blocking_frequency(u, hh, args.sigma)[0] if np.isfinite(hh) else np.nan
                       for u, hh in zip(U, h)])
    Fr = U / np.sqrt(G * h)

    print(f"Over the crest: depth {h[crest]*100:.2f} cm, U = {U[crest]:.3f} m/s, "
          f"Froude number {Fr[crest]:.2f}, f_block = {fblock[crest]:.2f} Hz")

    # Waves arrive from downstream (x > 0) heading upstream (towards -x).
    print("\nHorizon positions (x measured from the bump crest, + is downstream):")
    downstream = x >= 0
    xs, fs, Us = x[downstream], fblock[downstream], U[downstream]
    for f in args.freq:
        if fs[-1] <= f:
            print(f"  f = {f:.2f} Hz: already blocked far downstream - the waves never "
                  f"reach the obstacle. Use a lower frequency or a slower flow.")
            continue
        # walk from far downstream towards the crest; first blocked point is the horizon
        hit = np.nonzero(fs <= f)[0]
        if hit.size == 0:
            print(f"  f = {f:.2f} Hz: never blocked - waves pass over the obstacle.")
        else:
            j = hit[-1]
            print(f"  f = {f:.2f} Hz: horizon at x = {xs[j]*100:+.1f} cm "
                  f"(local U = {Us[j]:.3f} m/s, depth {h[downstream][j]*100:.2f} cm)")

    if args.plot:
        plot_channel(x, zb, h, U, fblock, args, crest)


def plot_channel(x, zb, h, U, fblock, args, crest):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 1, figsize=(8, 9), sharex=False,
                             gridspec_kw={"height_ratios": [1.1, 1, 1.3]})
    xc = x * 100

    ax = axes[0]
    ax.fill_between(xc, 0, zb * 100, color="#8a7b6a", label="obstacle")
    ax.fill_between(xc, zb * 100, (zb + h) * 100, color="#6fa8dc", alpha=0.6, label="water")
    ax.set_ylabel("height (cm)")
    ax.set_title("Channel profile (flow from left to right)")
    ax.legend(loc="upper right", frameon=False)

    ax = axes[1]
    ax.plot(xc, U, color="#1f4e79")
    ax.set_ylabel("flow speed U (m/s)", color="#1f4e79")
    ax2 = ax.twinx()
    fplot = np.where(np.isfinite(fblock), fblock, np.nan)
    ax2.plot(xc, fplot, color="#c0504d")
    ax2.set_ylabel("blocking frequency (Hz)", color="#c0504d")
    top = max(max(args.freq) * 1.25, np.nanmax(fplot) if np.isfinite(fplot).any() else 1)
    ax2.set_ylim(0, top)
    for f in args.freq:
        ax2.axhline(f, ls="--", lw=0.8, color="#888")
        ax2.text(xc[0], f, f"{f:g} Hz ", va="bottom", ha="left", fontsize=8, color="#555")
        fs = fblock[x >= 0]
        hit = np.nonzero(fs <= f)[0]
        reaches_obstacle = not fs[-1] <= f
        if hit.size and reaches_obstacle:
            ax2.plot(xc[x >= 0][hit[-1]], f, "o", color="#c0504d", ms=5)
    ax.set_xlabel("x (cm), crest at 0; waves arrive from the right")
    ax.set_title("A wave is stopped where its frequency meets the red curve (dots)\n"
                 "outside the red curve the current blocks nothing")

    # Dispersion diagram at the crest
    ax = axes[2]
    hc, Uc = h[crest], U[crest]
    k = np.linspace(1, 2500, 4000)
    ax.plot(k, omega_intrinsic(k, hc, args.sigma) / (2 * math.pi), color="#999",
            label="still water")
    ax.plot(k, omega_lab_upstream(k, Uc, hc, args.sigma) / (2 * math.pi), color="#1f4e79",
            label=f"against U = {Uc:.2f} m/s")
    for f in args.freq:
        ax.axhline(f, ls="--", lw=0.8, color="#888")
    ax.set_ylim(-3, max(max(args.freq) * 2, 5))
    ax.axhline(0, color="#ccc", lw=0.6)
    ax.set_xlabel("wavenumber k (1/m)")
    ax.set_ylabel("lab frequency (Hz)")
    ax.set_title("Dispersion over the crest: each crossing of a dashed line is an allowed wave\n"
                 "(the right-hand rise is the short capillary 'blue-shifted' branch)")
    ax.legend(frameon=False)

    fig.tight_layout()
    fig.savefig(args.plot, dpi=140)
    print(f"\nPlot saved to {args.plot}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--point", action="store_true",
                   help="analyse a single location given --speed and --depth")
    p.add_argument("--depth", type=float, required=True,
                   help="water depth in m (far from the obstacle, or local with --point)")
    p.add_argument("--speed", type=float, help="flow speed in m/s")
    p.add_argument("--flow", type=float, help="discharge in litres per second")
    p.add_argument("--width", type=float, default=0.08, help="channel width in m (default 0.08)")
    p.add_argument("--bump-height", type=float, default=0.03, help="obstacle height in m")
    p.add_argument("--bump-length", type=float, default=0.20, help="obstacle length in m")
    p.add_argument("--freq", type=float, nargs="+", default=[2.0, 3.0, 4.0],
                   help="wave frequencies to check, in Hz")
    p.add_argument("--sigma", type=float, default=SIGMA,
                   help="surface tension in N/m (default 0.072)")
    p.add_argument("--plot", help="save a figure to this PNG file")
    args = p.parse_args(argv)

    if args.point:
        if args.speed is None:
            p.error("--point needs --speed")
        run_point(args)
    else:
        run_channel(args)


if __name__ == "__main__":
    main()
