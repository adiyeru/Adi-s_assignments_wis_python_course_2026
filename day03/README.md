# Metropolis simulation of an Einstein solid

This program simulates 100 particles that exchange energy with a heat bath,
using the Metropolis algorithm (statistical physics).

## Background

### The Einstein solid

The Einstein solid is a simple model of a crystal, proposed by Albert Einstein
in 1907. Each atom sits in the crystal and vibrates around its place, like a
ball on a spring. In the model, every spring is the same and vibrates
independently of the others.

The key idea comes from quantum mechanics: a vibrating spring can't hold any
amount of energy. Its energy can only go up or down in equal steps, called
energy units (or quanta). So each particle's energy is a whole number:
0, 1, 2, 3 and so on. In this exercise, each "particle" is one such spring.

Einstein used this model to explain why solids absorb less heat at low
temperatures. When there is little thermal energy around, a whole energy unit
is hard to get, so the springs mostly stay at 0.

### The heat bath and temperature

Here the solid touches a heat bath: a much larger object kept at a fixed
temperature. Energy can flow between them, so the solid's total energy isn't
fixed. Instead, it fluctuates around an average set by the temperature.

`theta` is that "temperature", measured in energy units. With theta = 2.5, the
bath's typical thermal energy is 2.5 units. At a fixed temperature, physics
says the chance that a particle has energy `q` is proportional to
`exp(-q/theta)`. This is the Boltzmann distribution: low energies are the most
common, and higher energies get less likely.

The Metropolis algorithm

The Metropolis algorithm, published by Metropolis and colleagues in 1953, is a way to make random samples that follow the Boltzmann distribution. It doesn't follow how real atoms move. Instead, it repeats a simple loop:

Suggest a small random change.
If the change lowers the energy, accept it.
If the change raises the energy by dE, accept it with probability exp(-dE/theta). Otherwise, keep things as they were.

This creates two opposite pulls:

Losing energy is always accepted. On its own, this would drain every particle down to 0.
Gaining energy is only sometimes accepted. The chance is higher when the bath is hotter. For adding 1 unit, it's 0.14 at theta = 0.5, 0.67 at theta = 2.5 and 0.90 at theta = 10.

When the total energy is high, many particles have energy to lose, so the total drops. When it's low, many particles are stuck at 0 and can't lose any, so gains win and the total rises. The system settles where gains and losses balance on average, and at that point the energies follow the Boltzmann distribution.

That balance point doesn't depend on where the system starts. Starting from the CSV (total 266), the total fell to 203.2. Starting with every particle at 0, it rose to 202.6. Both runs end in the same place.

## The computation

Each particle starts with the energy given in `start_energies.csv`. The
program runs 10^7 steps with theta = 2.5. At each step:

1. Pick one particle at random.
2. With probability 1/2, try to add 1 unit. This raises the energy by 1, so it
   is accepted with probability `exp(-1/theta)`, which is 0.67 here.
3. Otherwise, try to remove 1 unit. This lowers the energy, so it is always
   accepted, as long as the particle has at least 1 unit (energy can't go
   below 0).

The function `metropolis(q, theta, steps, seed=0)` returns the average total
energy over the second half of the run, after the system has settled.

## Files

| File | What it is |
|---|---|
| `metropolis.py` | The program, with the `metropolis()` function |
| `make_data.py` | Generates the input data |
| `start_energies.csv` | Starting energy of each of the 100 particles, with columns `particle_number` and `starting_energy_units` |

The data is generated: each starting energy is a random whole number from 0 to 5 (seed 1).

## Understanding the results

### Why only the second half is averaged

The data starts with a total energy of 266, which is not the equilibrium value.
At first the system drifts toward equilibrium, and only after that does it
fluctuate around its average. Averaging the second half of the run (5 million
steps) leaves out that drift.

### Why the answer is 203 and not 250

**The exact answer.** In the Boltzmann distribution, each extra unit of energy
is `exp(-1/theta)` = 0.67 times as likely as the one before. So for one
particle at theta = 2.5:

| Energy | Chance |
|---|---|
| 0 | 0.33 |
| 1 | 0.22 |
| 2 | 0.15 |
| 3 | 0.10 |
| ... | each 0.67 times the one before |

Averaging over all these energies gives exactly `1 / (exp(1/theta) - 1)`,
which is 2.033 units per particle. Times 100 particles, that's 203.3. The
simulation gives 203.2, so it matches within 0.05%.

**Where 250 comes from.** `N * theta` is the classical answer. Classical
physics treats energy as continuous, so a particle can hold any amount, such
as 0.3 or 1.7 units. In that case, each particle's average energy is exactly
theta, which gives 100 × 2.5 = 250.

**Why whole units give less.** With whole units, a particle can't hold a small
amount of energy: it has either 0 or at least 1 full unit. Getting that first
unit is relatively costly, so a third of the particles sit at 0. That pulls
the average down by about half a unit per particle compared with the classical
answer (2.03 instead of 2.5).

**When 250 would be right.** The gap matters less as the temperature rises,
because a half unit becomes small next to the average energy:

| theta | Exact, per particle | Classical, per particle | Classical is too high by |
|---|---|---|---|
| 0.5 | 0.157 | 0.5 | 69% |
| 2.5 | 2.033 | 2.5 | 19% |
| 10 | 9.508 | 10 | 5% |
| 100 | 99.501 | 100 | 0.5% |

At theta = 2.5, energy units are still large compared with the thermal energy,
so the classical answer isn't accurate.

An earlier chat said to compare the result with `N * theta`. That instruction
came from a garbled translation of the original Hebrew exercise, so it should
be checked against the original.

### Why repeated runs differ slightly

The moves are random, so each seed gives a slightly different average. The five
extra seeds varied by about 0.8, or 0.4%. That's the statistical error of a
single run, and the gap from the exact value is well within it.

## Prompt

```text
Write a simple Python program that simulates an Einstein solid exchanging energy with a heat bath using the Metropolis algorithm.

Setup:
- 100 particles
- Temperature theta = 2.5
- 10^7 steps

At each step:
1. Pick a random particle.
2. With probability 1/2, try adding 1 unit of energy and accept with probability exp(-1/theta); otherwise, try removing 1 unit.
3. A particle's energy can't go below 0.

Please:
- Put the computation in one function, called metropolis, that takes the starting energies, theta, the number of steps and a random seed, and returns the mean total energy over the second half of the run.
- Generate the input data with a small separate script, using a fixed random seed, and save it to start_energies.csv. The main program should read its data from that file.
- Compare the result with N / (exp(1/theta) - 1). If they disagree, tell me why.
- Use as few packages as possible, and keep the code short and easy to read.
- Write a README.md describing the computation, the files, and the results.
```