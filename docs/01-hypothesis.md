# The UDL hypothesis

Each claim is numbered so that critique can point at it. For each one: what it says, what it rests on, and its status.

---

### H1. Space is information

**Claim.** What we call space is a passive store of information, the *Universal Data Lake*. It does nothing by itself.

**Rests on.** Wheeler's "it from bit"; the holographic principle and black-hole thermodynamics, which tie the information content of a region to the area of its boundary.

**Status.** A shared starting point of several serious research programmes. Not new, but well motivated.

---

### H2. Reading creates structure (schema-on-read)

**Claim.** Data in the lake has no fixed form until it is read. A *read* is any interaction that records an outcome: a measurement, or a particle hitting a detector. What we observe is always the result of reads.

**Rests on.** Quantum measurement: properties such as spin along an axis are not defined before they are measured (see H4 and Bell's theorem).

**Status.** A metaphor for the standard measurement postulate. It adds a vocabulary, not new physics.

---

### H3. Superposition is one record with several weighted hard links

**Claim.** A particle "in two places" is not two copies. It is one record (an inode) with several directory entries (hard links), each carrying a complex weight (an *amplitude*). A read follows one link with probability |weight|² and removes the others.

**Why not copies.** The no-cloning theorem forbids copying an unknown quantum state, and interference (links cancelling each other) needs signed or complex weights, which copies don't have.

**Status.** A faithful picture of the state vector and the Born rule, once weights are complex. Details in [03](03-superposition-and-entanglement.md).

---

### H4. Entanglement is one inode linked from two places

**Claim.** An entangled pair is one record reachable through two links at distant locations. Neither link holds a value of its own: each local view is pure noise. The first read, from either side, commits a random value; the other link then resolves consistently with it.

**Constraints the model must respect** (all verified in [`simulations/bell`](../simulations/bell/)):
- values are not stored in advance, or Bell's bound |S| ≤ 2 would hold, and it is violated in experiments;
- the committed value is random, otherwise the commit could carry a message faster than light;
- the result must not depend on who reads first, since for distant readers relativity does not fix an order.

**Status.** Equivalent to the textbook "collapse" calculation. Openly non-local. An interpretation, not yet a theory.

---

### H5. Gravity is a property of the lake, not of the data

**Claim.** Quantum physics describes reads. Gravity describes the lake itself: its geometry, or how its capacity is used. It is not one more field to be read.

**Rests on.** Jacobson's derivation of Einstein's equations from thermodynamics; entropic and emergent gravity; analogue gravity, where horizons and curved-spacetime wave equations arise in ordinary fluids (see the [water experiment](../experiments/water-horizon/)).

**Status.** A minority but serious position. Its sharpest modern form is Oppenheim's postquantum classical gravity. Details in [04](04-gravity.md).

---

### H6. Unifying gravity with quantum theory may be the wrong goal

**Claim.** If H5 holds, gravity does not need to be quantized, and the search for quantum gravity in the usual sense asks the wrong question.

**Status.** The boldest claim, and a testable one: experiments looking for gravitationally induced entanglement could refute it within decades. See [06](06-how-to-refute-it.md).

---

## What UDL is not

- It is not a replacement for quantum mechanics or general relativity. Every number in this repository comes from standard physics.
- It does not say the universe is a computer running code. The lake is passive; nothing "executes".
- It is not finished. Open problems are listed in [05](05-open-problems.md).
