# to run: python -m pytest

from pathlib import Path     
# builds file paths that work on any system

import pytest                
# the testing library
#  How pytest works, in short:
#   - it finds every file whose name starts with test_ (like this one)
#   - inside it, it runs every function whose name starts with test_
#   - a test PASSES if the function finishes without an error
#   - a test FAILS if an `assert` line is false (or anything else goes wrong)
#
#   assert <condition>   means: "this must be true;
#                        If not, stop and report a failure"

# Import the functions from Metropolis.py that this test file checks.
from Metropolis import (exact_energy, make_start, metropolis, metropolis_trace,
                        read_energies, record_points)


# --- The exercise settings, shared by several tests ---

# 100 particles, as in the exercise.
N = 100

# The exercise uses theta = 2.5. theta is the temperature measured in energy
# units:  theta = k_B·T / ε.  It is the temperature written as an energy
# (k_B·T), counted in energy units ε. So theta = 2.5 means k_B·T = 2.5 energy
# units, and therefore 1/theta = ε / (k_B·T) is a plain number with no unit.
THETA = 2.5

# Number of Metropolis steps for the physics tests below.
# 10^6, not the exercise's 10^7: the system settles after about 20,000 steps,
# so 10^6 is plenty, and each run takes under half a second instead of ~3.
STEPS = 10**6

# How far the simulated mean may be from the exact answer, as a fraction (5%).
# The simulation is random, so it never hits the formula exactly.
# Measured, not guessed: over 20 seeds at 10^6 steps the error was 1.5% on
# average and 3.7% at most, so 5% is safe.
TOLERANCE = 0.05

# ------

# Formula check: 
# The simulation's mean energy should match the exact formula.
# Exact_energy(n, theta): the formula N / (e^(1/theta) - 1)
def test_exact_energy_for_the_exercise():
    # The value quoted in the README: 203.3 for N = 100 at theta = 2.5.
    # The real value is 203.32..., so an exact "==" with 203.3 would fail.
    # pytest.approx(203.3, abs=0.05) means "203.3, give or take 0.05".
    assert exact_energy(N, THETA) == pytest.approx(203.3, abs=0.05)


def test_exact_energy_is_proportional_to_n():
    # The particles are independent, so twice the particles should hold twice the energy.
    # pytest.approx with no extra argument allows only a tiny rounding difference,
    # lets a test compare numbers within a small tolerance instead of requiring an exact match. 
    # That’s useful because calculations and simulations can produce tiny rounding differences.
    # because decimal numbers in a computer are not always exact.
    assert exact_energy(200, THETA) == pytest.approx(2 * exact_energy(100, THETA))


def test_exact_energy_is_almost_zero_at_low_temperature():
    # When the bath is very cold, a whole unit of energy is almost never available,
    # so 100 particles together hold almost nothing.
    # 1e-6 is scientific notation for 0.000001.
    assert exact_energy(N, 0.05) < 1e-6


# make_start(n, q_total, seed): n particles sharing q_total units at random
# @pytest.mark.parametrize runs the test below once for each pair in the list.
# The first string names the test's arguments; 
# each pair gives their values.
# So this one test runs 4 times: 
# 
# (n, q_total) = (100, 266): exercise's starting state, 100 particles sharing 266 units.
# (n, q_total) = (100, 0): No energy at all. 
# The loop that hands out units never runs.
# The function must still return 100 zeros, 
# not an empty list or an error.
# (n, q_total) = (1, 7): only one particle with 7 units. 
# Every unit must go to that one particle, so the list must be exactly [7].
# (n, q_total) = (5, 1000): Far more units than particles, 
# about 200 each. Nothing should cap a particle’s energy (say at 5, like the CSV), 
# and the total must still come out to exactly 1000.

@pytest.mark.parametrize("n, q_total", [(100, 266), (100, 0), (1, 7), (5, 1000)])
def test_make_start_builds_the_requested_macrostate(n, q_total):
    q = make_start(n, q_total)             # build the starting energies
    assert len(q) == n                     # one energy per particle
    assert sum(q) == q_total               # the units add up to the total
    assert all(e >= 0 for e in q)          # no negative energies (all() is True only if every e >= 0)

# Every starting state must have the right N and total q.

def test_make_start_is_reproducible():
    # Same seed, same starting energies: needed so runs can be repeated.
    # Two separate calls with seed 3 must give exactly the same list.
    assert make_start(100, 266, seed=3) == make_start(100, 266, seed=3)

# seed=3 gives the random-number generator a fixed starting point. 
# That makes make_start(100, 266, seed=3) reproducible: 
# calling it again with the same inputs and seed produces 
# the same list of energies. 
# The 3 isn’t the number of particles or energy—it’s just
# a chosen value for initializing the random sequence.

def test_make_start_depends_on_the_seed():
    # A different seed spreads the units differently.
    # "!=" means "is not equal to".
    assert make_start(100, 266, seed=1) != make_start(100, 266, seed=2)


# record_points(steps): which steps to remember for the plots
def test_record_points_stay_within_the_run():
    # A run of 10^6 steps should only remember steps that 
    # exist in that run.
    points = record_points(10**6)           
    # the steps to remember in a run of 10^6 steps
    assert min(points) >= 1                 
    # nothing before the first step
    assert max(points) == 10**6             
    # the last step is included
    assert 1 in points                      
    # the very first step is included

# metropolis_trace and metropolis: the simulation itself
def test_metropolis_is_reproducible():
    # Same inputs and seed, same result, 
    # exactly (not just close).
    # This also checks that metropolis() works on a copy 
    # of the list: if it changed `start`, 
    # the second run would begin from a different state
    # and give a different result.
    start = make_start(N, 266)                                   # one fixed starting state
    first = metropolis(start, THETA, 10**4, seed=5)              # first run with seed 5
    second = metropolis(start, THETA, 10**4, seed=5)             # second run with seed 5
    assert first == second                                       # must be identical

# The rules of the loop: ±1 per step, never below 0.
def test_energy_changes_by_at_most_one_unit_per_step():
    # Each step adds, removes or keeps one unit, never more.
    # Record EVERY step and check the change between neighbours.
    steps = 5000   # a short run
    # range(1, steps + 1) is 1, 2, ..., 5000;
    # it remembers the energy after every step.
    # make_start(10, 20) is a small solid: 
    # 10 particles sharing 20 units.
    mean, trace = metropolis_trace(make_start(10, 20), THETA, steps, record=range(1, steps + 1))
    energies = [energy for step, energy in trace] # keep only the energies

    # zip(energies, energies[1:]) pairs each energy with the next one:
    # (e0, e1), (e1, e2), ... 
    # The difference within each pair is at most 1.
    assert all(abs(b - a) <= 1 for a, b in zip(energies, energies[1:]))

    assert all(e >= 0 for e in energies)               
    # the total never goes below zero


# This test runs 3 times, with start_total = 0, 266 and 1000.
@pytest.mark.parametrize("start_total", [0, 266, 1000])
def test_result_does_not_depend_on_the_start(start_total):
    # The main physics claim: from any starting total, 
    # the mean ends near the exact answer (203.3).
    start = make_start(N, start_total)                 
    # build the starting state
    result = metropolis(start, THETA, STEPS)           
    # run the simulation

    # rel=TOLERANCE means "within 5% of the exact answer".
    assert result == pytest.approx(exact_energy(N, THETA), rel=TOLERANCE)
# Result does not depend on the start is the main physics claim here.


# This test runs 3 times, with theta = 1.0, 2.5 and 5.0.
@pytest.mark.parametrize("theta", [1.0, 2.5, 5.0])
# tells pytest to run the test below it three times—once for each value in the list. 
# Each run receives that value in its theta parameter.
def test_result_follows_the_exact_formula_at_other_temperatures(theta):
    # Temperature does change the result, and the simulation follows the formula.
    result = metropolis(make_start(N, 0), theta, STEPS)                     
    # start from 0 and run
    assert result == pytest.approx(exact_energy(N, theta), rel=TOLERANCE)  
    # within 5% of the formula

def test_result_is_below_the_classical_answer():
    # With whole energy units the average is lower than the
    # classical answer N * theta (100 x 2.5 = 250 energy units).
    result = metropolis(make_start(N, 266), THETA, STEPS)   
    # run the exercise settings
    assert result < N * THETA                               
    # must be below 250
