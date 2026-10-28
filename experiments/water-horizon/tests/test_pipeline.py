"""End-to-end checks: physics sanity and the video pipeline on synthetic data."""

import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ANALYSIS = Path(__file__).resolve().parents[1] / "analysis"
sys.path.insert(0, str(ANALYSIS))

import horizon  # noqa: E402
from surface_from_video import lockin, local_wavelength  # noqa: E402


def test_deep_water_limit():
    # long gravity waves in deep water: Omega^2 = g k
    k, h = 5.0, 10.0
    assert horizon.omega_intrinsic(k, h, sigma=0) == pytest.approx(math.sqrt(9.81 * k), rel=1e-6)


def test_slow_current_blocks_nothing():
    # slower than the minimum group velocity of water waves (~0.18 m/s): no horizon
    f, _ = horizon.blocking_frequency(0.10, 0.06)
    assert math.isinf(f)


def test_faster_current_blocks_lower_frequencies():
    f1, _ = horizon.blocking_frequency(0.25, 0.03)
    f2, _ = horizon.blocking_frequency(0.35, 0.03)
    assert 0 < f2 < f1 < 10


def test_reference_setup_has_a_horizon():
    x = np.linspace(-0.3, 0.3, 301)
    zb = horizon.bump_profile(x, 0.03, 0.20)
    h = horizon.solve_depth(0.6e-3, 0.08, 0.06, zb)
    assert not np.isnan(h).any()
    U = 0.6e-3 / (0.08 * h)
    crest = int(np.argmin(h))
    f_crest, _ = horizon.blocking_frequency(U[crest], h[crest])
    f_far, _ = horizon.blocking_frequency(U[-1], h[-1])
    assert math.isinf(f_far) and 0.8 < f_crest < 1.5


def test_choked_flow_is_detected():
    zb = horizon.bump_profile(np.array([0.0]), 0.05, 0.20)
    h = horizon.solve_depth(1.5e-3, 0.08, 0.06, zb)
    assert np.isnan(h).all()


def test_video_pipeline_recovers_known_wave(tmp_path):
    video = tmp_path / "syn.mp4"
    out = tmp_path / "res" / "syn"
    run = lambda *a: subprocess.run([sys.executable, *a], cwd=ANALYSIS, check=True,
                                    capture_output=True)
    run("make_synthetic_video.py", "--out", str(video), "--seconds", "6")
    run("surface_from_video.py", str(video), "--px-per-cm", "10",
        "--roi", "0", "100", "600", "300", "--drive-freq", "2", "--out", str(out))

    d = np.load(str(out) + "_eta.npz")
    amp = lockin(d["eta"], d["t"], 2.0)
    lam = local_wavelength(amp, d["x"][1] - d["x"][0])
    i = np.searchsorted(d["x"], 0.45)

    from scipy.optimize import brentq
    w = 2 * math.pi * 2.0
    k_true = brentq(lambda k: horizon.omega_lab_upstream(k, 0.12, 0.06) - w, 0.1, 60)

    assert abs(amp[i]) * 1000 == pytest.approx(2.0, rel=0.05)       # 2 mm amplitude
    assert lam[i] == pytest.approx(2 * math.pi / k_true, rel=0.03)  # wavelength
    assert abs(amp[30]) * 1000 < 0.1                                # dead zone past the horizon
