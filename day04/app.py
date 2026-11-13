# app.py
# Web interface for the Metropolis simulation (day04).
#
# This file handles only the web side:
#   1. it shows a form,
#   2. reads what the visitor typed and checks it,
#   3. calls the physics in metropolis.py,
#   4. asks plots.py to draw the plots,
#   5. and fills the page templates/index.html with the results.
# Python's built-in modules.
import math                # for math.exp(x), which is e^x
from pathlib import Path   # builds file paths that work on Windows, Mac and Linux

# Flask is the web framework we use. We import three things from it:
#   Flask           : the class that creates the web application
#   render_template : fills an HTML file from the "templates" folder with values
#   request         : holds what the browser sent, such as the form's contents
from flask import Flask, render_template, request

# my own files. This is where the day03 is reused.
from Metropolis import metropolis_trace, record_points, exact_energy, read_energies, make_start
from plots import plot_start, plot_whole_run, plot_theta

# Create the web application. __name__ is this file's name; Flask uses it to
# find the "templates" folder next to this file.
app = Flask(__name__)

# The path of the CSV file. __file__ is the path of this file (app.py);
# .parent is the folder it is in; "/" adds a file name to a path. This finds
# the CSV no matter which folder the program was started from.
CSV_FILE = Path(__file__).parent / "start_energies.csv"

# Read the day03 data: a list of 100 starting energies. This line runs once,
# when the server starts. The web app uses the data only for the form's
# default values (see below).
CSV_START = read_energies(CSV_FILE)

# Limits on what a visitor may ask for, so that a single request can't keep
# the server busy for minutes. Names in CAPITALS are, by habit, fixed values.
MAX_STEPS = 10**7     # most Metropolis steps (10 to the power 7)
MAX_N = 1000          # most particles
MAX_Q = 10000         # largest starting total energy
MAX_STARTS = 5        # most starting totals in one run (each is a simulation)


# The line starting with @ is a "decorator". It tells Flask: when a browser
# asks for the address "/" (the home page), call the function below.
#   GET  : the browser asks for the page (someone opened or reloaded it)
#   POST : the browser sends the form (someone pressed "Run")
@app.route("/", methods=["GET", "POST"])
def index():
    """Show the form (GET), or run the simulation and show the result (POST)."""
    # What the five boxes of the form contain. To begin with, the defaults.
    # Everything is text (in quotes), because a form only holds text.
    form = {
        "theta": "2.5",                             # temperature with no units
        "steps": "1000000",                         # 10^6 steps: answers in about a second
        "seed": "0",                                # seed for the random numbers
        "n": str(len(CSV_START)),                   # number of rows in the CSV (100), as text
        "q_totals": f"0, {sum(CSV_START)}, 1000",   # 0, the CSV's total (266), and 1000
    }

    # Nothing to show yet. None is Python's word for "no value".
    result = None    # will hold the results of a successful run
    error = None     # will hold a message if the input is wrong

    # Did the visitor press "Run"? (On a GET, this whole block is skipped,
    # and the page is shown with the default values and no result.)
    if request.method == "POST":

        # Replace each default with the text the visitor typed.
        # request.form is like a dictionary of the form's boxes, by their
        # "name". .get(name, "") gives "" if a box is missing.
        for name in form:
            form[name] = request.form.get(name, "")

        # Turn the text into numbers. If some text is not a number, float()
        # or int() fails with a ValueError. "try" lets us catch that instead
        # of crashing.
        try:
            theta = float(form["theta"])    # a decimal number, such as 2.5
            steps = int(form["steps"])      # a whole number
            seed = int(form["seed"])        # a whole number
            n = int(form["n"])              # a whole number

            # The starting totals arrive as one text, "0, 266, 1000".
            # .split(",") cuts it at the commas into ["0", " 266", " 1000"],
            # and int() turns each piece into a number (it ignores spaces).
            q_totals = [int(text) for text in form["q_totals"].split(",")]

        # This block runs only if one of the conversions above failed.
        except ValueError:
            error = "Theta must be a number. Everything else must be whole numbers."

        # This block runs only if all conversions worked. Now check that the
        # numbers are in a sensible range. Only the first failed check sets
        # the message (if / elif).
        else:
            # theta must be positive: the formulas divide by theta.
            if not 0.01 <= theta <= 1000:
                error = "Theta must be between 0.01 and 1000."

            # At least 2 steps, so the "second half" is not empty.
            # {MAX_STEPS:,} writes the number with commas: 10,000,000.
            elif not 2 <= steps <= MAX_STEPS:
                error = f"Steps must be between 2 and {MAX_STEPS:,}."

            # At least one particle.
            elif not 1 <= n <= MAX_N:
                error = f"Number of particles must be between 1 and {MAX_N:,}."

            # Not too many starting totals: each one is a whole simulation.
            elif len(q_totals) > MAX_STARTS:
                error = f"Give at most {MAX_STARTS} starting totals."

            # Every starting total must be in range (energy can't be negative).
            # all(...) is True only if the condition holds for every q.
            elif not all(0 <= q <= MAX_Q for q in q_totals):
                error = f"Each starting total must be between 0 and {MAX_Q:,}."

        # Still no error message? Then the input is fine: do the computation.
        if error is None:

            # --- 1. Build the starting states ---
            # For each starting total the visitor typed, build the macrostate
            # (n, q_total): a list of n energies that add up to q_total,
            # spread at random over the particles.
            starts = []
            for q_total in q_totals:
                starts.append(make_start(n, q_total, seed))

            # --- 2. The two formulas ---
            exact = exact_energy(n, theta)    # exact answer, for whole energy units
            classical = n * theta             # classical answer, for continuous energy

            # --- 3. Run one simulation per starting state ---
            # The step numbers at which the simulation should remember the
            # total energy, for the plots.
            record = record_points(steps)

            # One dictionary of results per starting state.
            runs = []
            for start in starts:

                # The day03 Metropolis loop. It returns:
                # the mean total energy and the trace (the remembered steps).
                # All runs use the same theta, steps and seed; only the
                # starting energies differ.
                simulated, trace = metropolis_trace(start, theta, steps, seed, record)

                # Store what the page needs to know about this run.
                runs.append({
                    "start_total": sum(start),          # total energy before the run
                    "simulated": simulated,             # mean total energy from the simulation
                    "difference": simulated - exact,    # simulated minus exact, in energy units
                    "trace": trace,                     # (steps done, total energy) pairs, for the plots
                })

            # --- 4. Find the step at which the runs become identical ---
            # All runs use the same seed, so they make the same random moves.
            # Once they have forgotten their different starts, they have
            # exactly the same total energy from then on. We look for the
            # step where that begins.
            merged_at = None             # stays None if it never happens
            if len(runs) > 1:            # with only one run there is nothing to compare

                # [run["trace"] for run in runs] is a list of the traces.
                # zip(*...) regroups them by time: first the pairs of all
                # runs at step 0, then the pairs of all runs at the next
                # remembered step, and so on. reversed(...) walks through
                # them backwards, from the end of the run toward the start.
                for points in reversed(list(zip(*[run["trace"] for run in runs]))):

                    # The energies of all runs at this moment, as a set.
                    # A set drops repeats, so if every run has the same
                    # energy the set has exactly one element.
                    energies = {energy for step, energy in points}

                    # More than one value: here the runs still differ.
                    # Stop walking back ("break" leaves the loop).
                    if len(energies) > 1:
                        break

                    # The runs agree here, so the merge happened at this
                    # step or earlier. points[0] is the first run's pair
                    # (step, energy), and [0] of that is the step.
                    merged_at = points[0][0]

            # --- 5. Collect everything the page will display ---
            result = {
                "n": n,                      # number of particles used
                "theta": theta,              # temperature used
                "steps": steps,              # number of steps used
                "runs": runs,                # the simulation results, one per starting q
                "exact": exact,              # exact answer
                "classical": classical,      # classical answer
                "merged_at": merged_at,      # step from which the runs are identical (or None)

                # The steps of the exact calculation, which the page shows
                # one by one:
                "inv_theta": 1 / theta,              # step 1: 1 / theta
                "exp_term": math.exp(1 / theta),     # step 2: e^(1/theta)
                "per_particle": exact / n,           # step 4: average units per particle
                "gap": classical - exact,            # how many units the classical answer is too high

                # The three plots. Each function returns a PNG picture packed
                # into text, which the page puts into an <img> tag.
                "plot_start": plot_start(runs, exact, merged_at),
                "plot_whole": plot_whole_run(runs, exact, classical, steps),
                "plot_theta": plot_theta(runs, n, theta),
            }

    # Fill templates/index.html with these values and send the finished page
    # to the browser. Each name=value makes the value available in the HTML
    # under that name. This line runs for GET and for POST: on a GET, and
    # after an error, `result` is None and the page shows no result section.
    return render_template("index.html", form=form, result=result, error=error,
                           max_steps=MAX_STEPS, max_n=MAX_N, max_q=MAX_Q, max_starts=MAX_STARTS)


# True only when this file is started directly with "python app.py".
if __name__ == "__main__":

    # Start Flask's built-in web server on this computer. It keeps running
    # and waits for browsers, until you press Ctrl+C. debug=True restarts
    # the server when you save a change to the code, and shows errors in the
    # browser. (It is meant for your own computer only, not for a public site.)
    app.run(debug=True)