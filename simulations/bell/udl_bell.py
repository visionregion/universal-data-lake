#!/usr/bin/env python3
"""
udl_bell.py - two storage models of an entangled pair, put through a Bell test.

The Universal Data Lake (UDL) idea describes an entangled pair as ONE record
(an inode) reachable through TWO hard links in different places. This script
compares that model with the obvious alternative, a REPLICA, and shows that
only the first one reproduces what experiments see.

Two parties, Alice and Bob, each read their link along an angle of their
choice and get +1 or -1.

  ReplicaModel   At creation, the source writes the answer to every possible
                 query into both replicas (a "local hidden variable"). Each
                 side reads its own copy. Nothing is shared afterwards.

  InodeModel     There are no answers stored in advance, only one shared
                 record. The FIRST read, from either side, commits: it
                 returns a random value and fixes the record. The second read
                 resolves against the committed record. The probabilities are
                 those of the spin singlet: results disagree with probability
                 cos^2(dtheta / 2).

  WritableInode  A thought experiment: like InodeModel, but the first reader
                 may CHOOSE the committed value instead of getting a random
                 one. Used to show why that must be forbidden.

Checks performed:
  1. CHSH value S. Any replica model obeys |S| <= 2 (Bell's theorem);
     experiments and quantum theory give 2*sqrt(2) ~ 2.83.
  2. Exhaustive search over all deterministic replica tables: max |S| = 2.
  3. No-signalling: Bob's own results are 50/50 whatever Alice does.
  4. Order symmetry: InodeModel gives the same statistics whoever reads
     first, as relativity requires for spacelike-separated readers.
  5. WritableInode lets Alice send Bob a message instantly.

Usage:
  python udl_bell.py                 # print the report
  python udl_bell.py --plot fig.png  # also draw correlation vs angle
"""

from __future__ import annotations

import argparse
import itertools
import math
from dataclasses import dataclass

import numpy as np


# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------

class ReplicaModel:
    """Each replica stores its answers in advance (local hidden variable).

    The hidden value is a random direction lam. Alice answers sign(cos(a - lam)),
    Bob answers -sign(cos(b - lam)): perfectly anticorrelated when a == b, like
    the singlet, but with a straight-line (not cosine) correlation curve.
    """

    name = "replica (values written in advance)"

    def __init__(self, rng):
        self.rng = rng

    def run(self, a, b, n, first="alice"):
        lam = self.rng.uniform(0, 2 * math.pi, n)
        A = np.where(np.cos(a - lam) >= 0, 1, -1)
        B = -np.where(np.cos(b - lam) >= 0, 1, -1)
        return A, B


class InodeModel:
    """One shared record; the first read commits a random value.

    Singlet statistics: P(results equal) = sin^2((a - b) / 2).
    """

    name = "shared inode (commit on first read)"

    def __init__(self, rng):
        self.rng = rng

    def run(self, a, b, n, first="alice"):
        p_equal = math.sin((a - b) / 2) ** 2
        first_result = self.rng.choice([-1, 1], n)          # random commit
        equal = self.rng.random(n) < p_equal
        second_result = np.where(equal, first_result, -first_result)
        if first == "alice":
            return first_result, second_result
        return second_result, first_result


class WritableInode(InodeModel):
    """Forbidden variant: the first reader chooses the committed value."""

    name = "writable inode (first reader chooses the value)"

    def run_with_message(self, bits, a, b):
        bits = np.asarray(bits)
        A = np.where(bits == 1, 1, -1)                      # Alice writes her bit
        p_equal = math.sin((a - b) / 2) ** 2
        equal = self.rng.random(bits.size) < p_equal
        B = np.where(equal, A, -A)
        return A, B


# --------------------------------------------------------------------------
# Statistics
# --------------------------------------------------------------------------

def correlation(A, B):
    return float(np.mean(A * B))


# Standard CHSH angles for the singlet (maximal violation)
A0, A1 = 0.0, math.pi / 2
B0, B1 = math.pi / 4, 3 * math.pi / 4


def chsh(model, n, first="alice"):
    E = {}
    for (ka, a), (kb, b) in itertools.product((("a", A0), ("a'", A1)), (("b", B0), ("b'", B1))):
        A, B = model.run(a, b, n, first)
        E[(ka, kb)] = correlation(A, B)
    S = E[("a", "b")] - E[("a", "b'")] + E[("a'", "b")] + E[("a'", "b'")]
    return S, E


def best_deterministic_replica():
    """Try every deterministic answer table: Alice (A0, A1), Bob (B0, B1) in {+-1}."""
    best = -math.inf
    for a0, a1, b0, b1 in itertools.product((-1, 1), repeat=4):
        S = a0 * b0 - a0 * b1 + a1 * b0 + a1 * b1
        best = max(best, abs(S))
    return best                        # mixtures of tables can't beat the best table


def bob_marginal(model, n, alice_angle, b=B0):
    _, B = model.run(alice_angle, b, n)
    return float(np.mean(B == 1))


def standard_error_S(n):
    # each E has variance <= 1/n; S is a sum of four
    return 2 / math.sqrt(n)


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

@dataclass
class Report:
    S_replica: float
    S_inode_alice_first: float
    S_inode_bob_first: float
    best_table: float
    marginals: dict
    message_bits_ok: float
    n: int

    def text(self):
        se = standard_error_S(self.n)
        lines = [
            f"Trials per setting: {self.n:,}   (statistical error on S about +-{se:.3f})",
            "",
            "1. Bell / CHSH test        bound for any replica: |S| <= 2",
            f"   replica model          S = {self.S_replica:+.3f}",
            f"   shared inode model     S = {self.S_inode_alice_first:+.3f}"
            f"   (quantum prediction {-2*math.sqrt(2):+.3f})",
            "",
            f"2. Best possible deterministic replica table: |S| = {self.best_table:.0f}",
            "",
            "3. No-signalling: fraction of +1 results Bob sees, by Alice's angle",
        ]
        for name, vals in self.marginals.items():
            row = "  ".join(f"{k}: {v:.3f}" for k, v in vals.items())
            lines.append(f"   {name:<38} {row}")
        lines += [
            "",
            "4. Order symmetry of the shared inode",
            f"   Alice reads first      S = {self.S_inode_alice_first:+.3f}",
            f"   Bob reads first        S = {self.S_inode_bob_first:+.3f}",
            "",
            "5. If the first reader could CHOOSE the value (writable inode):",
            f"   Bob decodes Alice's message correctly {self.message_bits_ok*100:.1f}% of the time",
            "   -> faster-than-light messaging. Real entanglement never allows this,",
            "      so in the UDL model the commit must be random.",
        ]
        return "\n".join(lines)


def run_all(n=200_000, seed=0):
    rng = np.random.default_rng(seed)
    replica, inode, writable = ReplicaModel(rng), InodeModel(rng), WritableInode(rng)

    S_rep, _ = chsh(replica, n)
    S_ia, _ = chsh(inode, n, "alice")
    S_ib, _ = chsh(inode, n, "bob")

    marg = {}
    for m in (replica, inode):
        marg[m.name] = {f"{round(math.degrees(t))} deg": bob_marginal(m, n, t)
                        for t in (0.0, math.pi / 4, math.pi / 2)}

    bits = rng.integers(0, 2, n)
    A, B = writable.run_with_message(bits, 0.0, 0.0)       # same angle: B = -A
    decoded = (B == -1).astype(int)                        # Bob flips the sign
    ok = float(np.mean(decoded == bits))

    return Report(S_rep, S_ia, S_ib, best_deterministic_replica(), marg, ok, n)


def plot(path, n=50_000, seed=1):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rng = np.random.default_rng(seed)
    replica, inode = ReplicaModel(rng), InodeModel(rng)
    th = np.linspace(0, math.pi, 37)
    E_rep = [correlation(*replica.run(0.0, t, n)) for t in th]
    E_ino = [correlation(*inode.run(0.0, t, n)) for t in th]
    deg = np.degrees(th)

    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.axhline(0, color="#ccc", lw=0.8)
    ax.plot(deg, -np.cos(th), color="#1f4e79", lw=2, label="quantum theory (and experiments)")
    ax.plot(deg, E_ino, "o", ms=4, color="#1f4e79", mfc="white", label="shared inode model (simulated)")
    ax.plot(deg, E_rep, "s", ms=3.5, color="#c0504d", label="replica model (simulated)")
    for x in (45, 135):
        ax.axvline(x, color="#999", ls=":", lw=0.8)
    ax.set_xlabel("angle between Alice's and Bob's queries (degrees)")
    ax.set_ylabel("correlation  E = mean(A x B)")
    ax.set_xticks(range(0, 181, 45))
    ax.set_title("The models agree at 0, 90 and 180 degrees and differ in between:\n"
                 "the gap at 45 and 135 degrees is what a Bell test measures")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=140)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("-n", type=int, default=200_000, help="trials per setting")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--plot", help="save correlation-vs-angle figure to this file")
    args = p.parse_args()
    print(run_all(args.n, args.seed).text())
    if args.plot:
        plot(args.plot)
        print(f"\nFigure saved to {args.plot}")


if __name__ == "__main__":
    main()
