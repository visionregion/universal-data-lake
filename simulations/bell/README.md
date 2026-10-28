# Bell test: replica vs. shared inode

Two storage models of an entangled pair, checked against what experiments see.

| Model | Idea | CHSH score \|S\| |
|---|---|---|
| **Replica** | The source writes answers to every possible query into both copies in advance. | ≤ 2 (Bell's theorem) |
| **Shared inode** | One record, two links. The first read, from either side, commits a random value; the other side resolves against it. | 2√2 ≈ 2.83 |
| Experiments, quantum theory | | 2.83 |

```bash
python udl_bell.py                     # report
python udl_bell.py --plot bell.png     # plus correlation-vs-angle figure
pytest -q                              # checks
```

Sample output (200,000 trials per setting):

```
1. Bell / CHSH test        bound for any replica: |S| <= 2
   replica model          S = -1.997
   shared inode model     S = -2.830   (quantum prediction -2.828)

2. Best possible deterministic replica table: |S| = 2

3. No-signalling: fraction of +1 results Bob sees, by Alice's angle
   replica (values written in advance)    0 deg: 0.500  45 deg: 0.503  90 deg: 0.501
   shared inode (commit on first read)    0 deg: 0.500  45 deg: 0.500  90 deg: 0.499

4. Order symmetry of the shared inode
   Alice reads first      S = -2.830
   Bob reads first        S = -2.833

5. If the first reader could CHOOSE the value (writable inode):
   Bob decodes Alice's message correctly 100.0% of the time
```

The sign of S only reflects that the pair is anticorrelated; what matters is its size.

## What this does and doesn't show

It shows that the *replica* picture of entanglement cannot be right, and that the *shared inode with random commit* picture is consistent with experiment.

It does not show that the inode picture is how nature works. The inode model is built to reproduce quantum statistics. It is the textbook collapse calculation written in storage terms, so its agreement with quantum theory is by construction. Its value is in making the constraints visible: remove randomness, or store values in advance, and it breaks.

The model is a sampler of outcome statistics, not a simulation of physical particles: it uses the joint probabilities directly. A real Bell experiment measures them.
