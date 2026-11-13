# metropolis.py
# Metropolis simulation of an Einstein solid touching a heat bath.
#
# The solid has N particles. Each particle holds a whole number of energy
# units (0, 1, 2, ...). Energy moves between the solid and the heat bath one
# unit at a time. The heat bath has a fixed temperature, theta.
#
# This file is the "business logic": all the physics is here, and nothing
# about web pages. It can be used in two ways:
#   - python metropolis.py   -> runs the day03 exercise and prints the result
#   - import metropolis      -> app.py borrows the functions for the web page
#
# What changed since day03 (the loop itself is the same):
#   1. the loop lives in metropolis_trace(), which also remembers the total
#      energy at chosen steps, so it can be plotted.
#      metropolis() calls it and returns the same number as in day03.
#   2. record_points() chooses which steps to remember.
#   3. exact_energy() holds the exact formula.
#   4. make_start() builds starting energies from a macrostate (N, q_total).
#   5. read_energies() reads the CSV file.
#   6. the command-line part sits under  if __name__ == "__main__":

# Python's built-in modules. Nothing needs to be installed for this file.
import csv      # reads CSV files, giving each row by its column names
import math     # mathematical functions; we use math.exp(x), which is e^x
import random   # random numbers


def metropolis_trace(q, theta, steps, seed=0, record=()):
    """Run Metropolis on the energies q. Return two things:
    - the mean total energy over the second half of the run
    - a "trace": a list of (steps done, total energy) pairs, for plotting

    q      : list of starting energies, one per particle
    theta  : temperature of the heat bath, in energy units
    steps  : number of steps to run
    seed   : starting point for the random numbers, so runs can be repeated
    record : the step numbers at which to remember the total energy
             (empty by default, which means: remember only the start)
    """
    # Turn `record` into a set. Asking "is this number in the set?" is very
    # fast, and we will ask it once in every step.
    record = set(record)

    # Fix the seed: the same seed gives the same random numbers, and so
    # exactly the same simulation, every time.
    random.seed(seed)

    # Make a copy of the list. We are going to change the energies, and we
    # don't want to change the list that the caller gave us.
    q = list(q)

    # The chance of accepting a move that ADDS one unit of energy.
    # Metropolis rule: a move that raises the energy by dE is accepted with
    # probability e^(-dE/theta). Here dE = 1, so it is e^(-1/theta).
    # At theta = 2.5 this is 0.67. It never changes, so compute it once.
    p_up = math.exp(-1 / theta)

    # The total energy of the solid right now. We keep it up to date by
    # adding or subtracting 1, which is much faster than sum(q) in every step.
    q_tot = sum(q)

    # Running sum of q_tot over the second half of the run. At the end,
    # dividing it by the number of steps added gives the average.
    total = 0

    # The trace: a list of pairs (steps done so far, total energy).
    # It begins with the starting total, before any step was done.
    trace = [(0, q_tot)]

    # The main loop. `step` takes the values 0, 1, 2, ..., steps - 1.
    for step in range(steps):

        # Pick one particle at random. randrange(len(q)) gives a whole number
        # from 0 to N - 1, which is that particle's position in the list.
        i = random.randrange(len(q))

        # random.random() gives a decimal number between 0 and 1.
        # It is below 0.5 half of the time, so this is a fair coin toss:
        # half the time we try to add a unit, half the time to remove one.
        if random.random() < 0.5:

            # TRY TO ADD 1 unit. Adding energy raises the solid's energy, so
            # the move is accepted only with chance p_up. A second random
            # number between 0 and 1 is below p_up exactly that often.
            if random.random() < p_up:
                q[i] += 1        # accepted: the particle gains 1 unit
                q_tot += 1       # and so does the total
            # (if not accepted, nothing changes in this step)

        # Otherwise (the other half of the time): TRY TO REMOVE 1 unit.
        # Removing energy lowers the solid's energy, and Metropolis always
        # accepts such a move. The only condition is that the particle has
        # at least 1 unit, because its energy can't go below 0.
        elif q[i] >= 1:
            q[i] -= 1            # the particle loses 1 unit
            q_tot -= 1           # and so does the total

        # Add the current total to the running sum, but only in the second
        # half of the run. "//" is whole-number division, so steps // 2 is
        # the halfway step. During the first half the system is still
        # drifting from its starting energy toward its average, and
        # including that drift would spoil the average.
        if step >= steps // 2:
            total += q_tot

        # For the plots: if the number of steps done so far (step + 1,
        # because step starts at 0) is one of the chosen ones, remember the
        # pair (steps done, total energy).
        if step + 1 in record:
            trace.append((step + 1, q_tot))

    # The average: the running sum divided by how many steps were added.
    # That is the number of steps in the second half: steps - steps // 2.
    mean = total / (steps - steps // 2)

    # Give back both results. Python returns them together as a pair.
    return mean, trace


def metropolis(q, theta, steps, seed=0):
    """The day03 function: return only the mean total energy over the
    second half of the run."""
    # Run the simulation without asking it to remember any extra steps.
    # The result is a pair, which we split into two names.
    mean, trace = metropolis_trace(q, theta, steps, seed)

    # Return only the mean; the trace is not needed here.
    return mean


def record_points(steps, count=400):
    """Choose the step numbers to remember for the plots.

    Remembering all 10 million steps would be far too much to draw, so we
    pick about 800: `count` evenly spaced ones, plus `count` that are packed
    near the start, where the energy changes fastest."""
    # Evenly spaced: steps/400, 2*steps/400, ..., steps.
    # The {...} with "for" inside builds a set: a collection with no repeats.
    even = {steps * k // count for k in range(1, count + 1)}

    # Packed near the start: steps^(0/400), steps^(1/400), ..., steps^(400/400).
    # These go from 1 up to `steps`, each one a fixed factor larger than the
    # one before (for example 1, 10, 100, 1000, ... if the factor were 10).
    # "**" means "to the power of"; round() gives the nearest whole number.
    early = {round(steps ** (k / count)) for k in range(count + 1)}

    # "|" joins two sets into one. A step that is in both appears once.
    return even | early


def exact_energy(n, theta):
    """Exact mean total energy of n particles at temperature theta."""
    # For one particle the exact average is 1 / (e^(1/theta) - 1) units.
    # The particles are independent, so n particles have n times that.
    return n / (math.exp(1 / theta) - 1)


def make_start(n, q_total, seed=0):
    """Build starting energies for the macrostate (n, q_total):
    n particles that share q_total energy units, spread at random."""
    # A separate random-number generator with its own seed. Using a separate
    # one means this function does not disturb the random numbers of the
    # simulation, and the same inputs always give the same starting energies.
    rng = random.Random(seed)

    # A list of n zeros: every particle starts with no energy.
    q = [0] * n

    # Hand out the units one at a time: repeat q_total times.
    for unit in range(q_total):

        # Pick a random particle (position 0 to n - 1) and give it this unit.
        q[rng.randrange(n)] += 1

    # The list now has n energies that add up to q_total.
    return q


def read_energies(path):
    """Read the starting energies from a CSV file. Return them as a list."""
    # Open the file for reading. "with" closes it automatically afterwards.
    with open(path) as f:

        # DictReader reads the first line as column names, and then gives
        # each following line as a dictionary: {column name: text in that column}.
        rows = csv.DictReader(f)

        # Go through the rows. From each one take the text in the column
        # "starting_energy_units" and turn it into a whole number with int().
        # The [...] with "for" inside collects the results into a list.
        return [int(row["starting_energy_units"]) for row in rows]


# Python sets __name__ to "__main__" only in the file that was started
# directly. So the block below runs with "python metropolis.py", but NOT when
# app.py does "import metropolis". Without this line, opening the web app
# would first run the whole 10^7-step simulation.
if __name__ == "__main__":

    # Read the 100 starting energies from the CSV file.
    start = read_energies("start_energies.csv")

    # Settings
    theta = 2.5          # temperature of the heat bath
    steps = 10**7        # number of Metropolis steps (10 to the power 7)
    N = len(start)       # number of particles: the length of the list (100)

    # Run the simulation, and compute the exact formula to compare with.
    result = metropolis(start, theta, steps)
    exact = exact_energy(N, theta)

    # Print both, rounded to 1 decimal place.
    print("simulated <q_tot> =", round(result, 1))
    print("exact <q_tot>     =", round(exact, 1))

    # N * theta is the classical answer (energy as a continuous amount).
    # It is only close to the exact answer when theta is large.
    print("N * theta         =", N * theta)