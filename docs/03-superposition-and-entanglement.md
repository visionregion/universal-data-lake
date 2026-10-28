# Superposition and entanglement in the lake

This note follows how the metaphor was refined, because each failed version shows a real physical constraint.

## Attempt 1: superposition as copies — fails

*"A copy of the information can sit in several places in the lake."*

Three things break it:

1. **No-cloning theorem.** An unknown quantum state cannot be copied. If nature kept copies, we could read them.
2. **Interference.** Copies just add up. Branches of a superposition can *cancel*: in the double-slit experiment there are places the particle never lands precisely because both slits are open. That needs each branch to carry a phase, not just data.
3. **Bell tests** rule out copies that each hold their own value (see below).

## Attempt 2: superposition as hard links — works, with weights

*"Not a copy: a hard link."*

One inode, several directory entries. Nothing is duplicated, so no-cloning is respected. Two additions make it match quantum mechanics:

- **Each link carries a complex weight** (amplitude). A read follows a link with probability |weight|². Weights with opposite phases cancel, which gives interference.
- **A read unlinks the other entries.** Afterwards one path remains: that is collapse, or state update.

```
inode #7    (one particle)
├── /slit1/p  →  #7   weight  1/√2
└── /slit2/p  →  #7   weight  1/√2 · e^{iφ}

read(/screen)  →  probability depends on |w1 + w2|² at that point:
                  bright where phases agree, dark where they cancel
```

## Attempt 3: entanglement as a replica — fails

*"Entanglement is a replica: on measurement one side is write, the other read."*

The read/write split matches the textbook calculation: the first measurement updates the joint state, and the second one sees the update. But a *replica* in the database sense stores values, and stored values are exactly what Bell tests exclude.

Three properties the replica would need, which no real database has:

1. **The write is random.** Alice chooses *which field* to read (the measurement angle), not the value. If she could choose the value, she could message Bob instantly. Bob sees 50/50 noise whatever Alice does.
2. **No value exists before the query.** Correlations follow cos²(Δθ/2), stronger than any table of pre-written answers can produce. The simulation in [`simulations/bell`](../simulations/bell/) checks all 16 possible answer tables; the best gets |S| = 2, while experiments get 2.83.
3. **No real primary.** For distant, nearly simultaneous measurements, different observers disagree on who measured first. The model must give the same statistics either way, and it does.

## Synthesis: one inode, two hard links, local views

*"Physicists explain entanglement as one object spread across space."*

That is the right reading. An entangled pair has one state that cannot be split into "Alice's state" plus "Bob's state" (it is *non-factorizable*). In UDL terms:

```
inode #42          state of the pair: fully defined
├── /alice/q  →  #42   local view: random, 50/50
└── /bob/q    →  #42   local view: random, 50/50

read(/alice/q, field = θ)
  → random result r
  → inode commits; alternatives are dropped
  → /bob/q now resolves to a consistent value
    (Bob cannot tell anything happened: his local view
     still looks exactly as random as before)
```

- From the **hard link** comes "one object, several addresses": nothing travels through space, because there is only one thing.
- From the **replica** comes the "local view": each address has its own way of being read, but **holds no data of its own**. The information is in the relation between the links, not at their ends.

A useful classical comparison is **XOR secret sharing**: each share alone is random bits, together they give the secret. The quantum version is stronger: the inode stores not an answer but *a rule for answering* consistently any question, even one chosen at the last moment. That is why it beats every classical sharing scheme in a Bell test.

## What the model must never do

| Rule | Physics behind it | Checked in simulation |
|---|---|---|
| No copies of content | No-cloning theorem | (by construction) |
| No values stored in advance | Bell's theorem, loophole-free tests (2015) | Test 1–2 |
| Commit is random | No-signalling theorem | Test 3, 5 |
| Order of reads doesn't matter | Relativity of simultaneity | Test 4 |
