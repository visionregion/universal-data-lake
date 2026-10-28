import math

import pytest

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import udl_bell as ub


def test_replica_respects_bell_bound():
    r = ub.run_all(n=100_000, seed=3)
    assert abs(r.S_replica) <= 2 + 3 * ub.standard_error_S(r.n)
    assert r.best_table == 2


def test_inode_matches_quantum_prediction():
    r = ub.run_all(n=100_000, seed=4)
    assert abs(r.S_inode_alice_first) == pytest.approx(2 * math.sqrt(2), abs=0.03)


def test_order_does_not_matter():
    r = ub.run_all(n=100_000, seed=5)
    assert abs(r.S_inode_alice_first - r.S_inode_bob_first) < 0.04


def test_no_signalling():
    r = ub.run_all(n=100_000, seed=6)
    for vals in r.marginals.values():
        for v in vals.values():
            assert abs(v - 0.5) < 0.01


def test_writable_inode_would_signal():
    r = ub.run_all(n=10_000, seed=7)
    assert r.message_bits_ok == 1.0


def test_same_angle_perfect_anticorrelation():
    rng = np.random.default_rng(8)
    for m in (ub.ReplicaModel(rng), ub.InodeModel(rng)):
        A, B = m.run(0.3, 0.3, 10_000)
        assert np.all(A == -B)
