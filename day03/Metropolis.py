# Metropolis simulation of an Einstein solid touching a heat bath.
# Each of the 100 particles holds a whole number of energy units (0, 1, 2, ...).
# Energy moves in and out of the heat bath one unit at a time. The program
# finds the average total energy and compares it with the exact formula.

import csv      # reads the CSV file by column name
import math     # for exp()
import random   # for random choices


def metropolis(q, theta, steps, seed=0):
    """Run Metropolis on the energies q. Return the mean total energy
    over the second half of the run, after the system has settled.

    q      : list of starting energies, one per particle
    theta  : temperature of the heat bath, in energy units
    steps  : number of steps to run
    seed   : starting point for the random numbers, so runs can be repeated
    """
    random.seed(seed)
    q = list(q)                      # copy, so the original list isn't changed
    p_up = math.exp(-1 / theta)      # chance of accepting +1 unit (0.67 here)
    q_tot = sum(q)                   # current total energy
    total = 0                        # running sum of q_tot, for the average

    for step in range(steps):
        i = random.randrange(len(q))             # pick a random particle

        if random.random() < 0.5:                # half the time: try to add 1
            # Adding energy costs energy, so accept only with chance p_up
            if random.random() < p_up:
                q[i] += 1
                q_tot += 1
        elif q[i] >= 1:                          # otherwise: try to remove 1
            # Removing energy is always accepted, unless the particle is at 0
            # (energy can't go below 0)
            q[i] -= 1
            q_tot -= 1

        # Skip the first half, while the system drifts toward its average.
        # Only the second half is added up.
        if step >= steps // 2:
            total += q_tot

    # Divide by the number of steps in the second half
    return total / (steps - steps // 2)


# Read the starting energies, using the column name
with open("start_energies.csv") as f:
    rows = csv.DictReader(f)
    start = [int(row["starting_energy_units"]) for row in rows]

# Settings from the exercise
theta = 2.5          # temperature of the heat bath
steps = 10**7        # number of Metropolis steps
N = len(start)       # number of particles (100)

result = metropolis(start, theta, steps)

# Exact answer for whole energy units: N / (e^(1/theta) - 1)
exact = N / (math.exp(1 / theta) - 1)

print("simulated <q_tot> =", round(result, 1))
print("exact <q_tot>     =", round(exact, 1))
# N * theta is the classical answer (continuous energy). It is only
# close to the exact answer when theta is large.
print("N * theta         =", N * theta)