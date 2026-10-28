# The physics

## The idea in one paragraph

Imagine a fish that can swim at most 1 m/s in a river. Upstream, the river flows at 0.5 m/s, and the fish can swim against it. Downstream, the river narrows and speeds up to 2 m/s. A fish that drifts past the point where the river reaches 1 m/s can never swim back. That point is a horizon. Bill Unruh noticed in 1981 that sound or water waves in a flowing fluid obey the same equations as light near a black hole, with the flow playing the role of spacetime being "dragged" inward. This "river model" is not just a metaphor: the wave equation in a moving medium is mathematically a wave equation on a curved spacetime with an *acoustic metric*.

## This experiment

Here the fish are surface waves and the river is reversed in time: waves travel **upstream** and the current over the bump stops them. A region that waves cannot *enter* is the time-reverse of a black hole, called a **white hole**. Black and white hole horizons share the same physics of mode conversion.

## Why the horizon depends on frequency

Water waves are *dispersive*: their speed depends on wavelength. In a frame moving with the water, the frequency and wavenumber are related by

```
Ω(k)² = (g·k + σ·k³/ρ) · tanh(k·h)
```

where *g* is gravity, *σ* surface tension, *ρ* density and *h* depth. Against a current *U*, the frequency measured in the lab is shifted (the Doppler effect):

```
ω = Ω(k) − U·k
```

The lab frequency is fixed by the wave maker. As the wave moves into faster water, its wavenumber must change to keep ω constant. The wave can continue only while its **group velocity** dΩ/dk exceeds *U*. The highest lab frequency that still makes it upstream is the maximum of Ω(k) − U·k; `horizon.py` computes it at every point over the bump. Higher frequencies are blocked earlier, lower ones later or not at all, so each frequency has its own horizon.

Real gravitational horizons are believed to be sharp for all frequencies. The dispersive, frequency-dependent horizon is a known difference of fluid analogues. It is also an interesting one: it mimics what some quantum-gravity ideas suggest for spacetime at very short scales, where the "medium" would stop looking smooth.

## Blue-shift and mode conversion

Approaching the horizon, the wave's wavelength shrinks (blue-shift). At the blocking point it cannot continue, and its energy is converted into other waves allowed at the same lab frequency:

- **short capillary waves** (wavelengths of a few millimetres) with positive frequency in the water frame, which are swept back downstream;
- a **negative-norm wave**, whose frequency is negative in the water frame.

The second one is the important one. In Hawking's calculation, a black hole horizon converts vacuum fluctuations into pairs of positive- and negative-frequency modes, and the ratio of their amplitudes follows a thermal (Boltzmann) law. In a water tank the same mode conversion happens to classical waves sent in deliberately: *stimulated* rather than spontaneous emission. Weinfurtner et al. (2011) measured this ratio and found the thermal form. Euvé et al. (2016) went further and found correlations in the background noise matching Hawking's prediction.

## What this experiment shows, and what it doesn't

**It shows** that horizons, blue-shift and Hawking-type mode conversion are properties of *waves in a moving medium*. None of it needs gravity. The geometry the waves "feel" is created by the medium and its flow.

**It does not show** anything about real gravity, quantum gravity, or the Universal Data Lake idea. An analogue reproduces the equations, not the underlying reality. It also has no quantum fluctuations to amplify at room temperature: the spontaneous Hawking effect has been seen only in a Bose–Einstein condensate (Steinhauer 2016, 2019).

**Why it is relevant to the UDL idea anyway.** The UDL hypothesis proposes that gravity is a property of an underlying substrate, not a quantum field living on top of it. Analogue gravity is the strongest existing demonstration that spacetime-like geometry *can* emerge from a substrate. That makes it a natural first experiment: build a medium, watch geometry appear. Testing whether real gravity is quantum requires experiments of a different kind, such as the proposed gravitationally induced entanglement tests (Bose et al. 2017; Marletto & Vedral 2017).

## Assumptions in `horizon.py`

- 1D flow: speed uniform across the depth and width (no boundary layers).
- Energy conserved over the bump (no friction losses), on the subcritical branch.
- Linear waves of small amplitude.
- Dispersion relation of a flat bottom with the local depth, i.e. the bump changes slowly compared to the wavelength. This is the weakest assumption for the shorter waves.
- Clean-water surface tension 0.072 N/m by default.

Expect real horizons within a few centimetres of the prediction, not millimetres.

## References

- W. G. Unruh, *Experimental black-hole evaporation?*, Phys. Rev. Lett. **46**, 1351 (1981).
- R. Schützhold and W. G. Unruh, *Gravity wave analogues of black holes*, Phys. Rev. D **66**, 044019 (2002).
- C. Barceló, S. Liberati and M. Visser, *Analogue gravity*, Living Rev. Relativ. **8**, 12 (2005); updated 2011.
- G. Rousseaux, C. Mathis, P. Maïssa, T. G. Philbin and U. Leonhardt, *Observation of negative-frequency waves in a water tank: a classical analogue to the Hawking effect?*, New J. Phys. **10**, 053015 (2008).
- T. G. Philbin, C. Kuklewicz, S. Robertson, S. Hill, F. König and U. Leonhardt, *Fiber-optical analog of the event horizon*, Science **319**, 1367 (2008).
- S. Weinfurtner, E. W. Tedford, M. C. J. Penrice, W. G. Unruh and G. A. Lawrence, *Measurement of stimulated Hawking emission in an analogue system*, Phys. Rev. Lett. **106**, 021302 (2011).
- L.-P. Euvé, F. Michel, R. Parentani, T. G. Philbin and G. Rousseaux, *Observation of noise correlated by the Hawking effect in a water tank*, Phys. Rev. Lett. **117**, 121301 (2016).
- J. Steinhauer, *Observation of quantum Hawking radiation and its entanglement in an analogue black hole*, Nature Phys. **12**, 959 (2016).
- T. Jacobson, *Thermodynamics of spacetime: the Einstein equation of state*, Phys. Rev. Lett. **75**, 1260 (1995).
- S. Bose et al., *Spin entanglement witness for quantum gravity*, Phys. Rev. Lett. **119**, 240401 (2017); C. Marletto and V. Vedral, *Gravitationally induced entanglement between two massive particles is sufficient evidence of quantum effects in gravity*, Phys. Rev. Lett. **119**, 240402 (2017).
- J. Oppenheim, *A postquantum theory of classical gravity?*, Phys. Rev. X **13**, 041040 (2023).
