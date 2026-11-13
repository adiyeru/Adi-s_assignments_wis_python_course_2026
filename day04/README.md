# Day 04: web interface for the Metropolis simulation

This is a small Flask web application for the day03 project, a Metropolis
simulation of an Einstein solid. The physics ("business logic") is the same
`metropolis()` function as in day03. Day04 only adds a web page in front of it.

For the physics background (the Einstein solid, the heat bath, the Metropolis
algorithm and why the answer is 203 and not 250), see the day03 README.

## How to run

```text
pip install flask matplotlib
python app.py
```

Then open http://127.0.0.1:5000 in a browser. Stop the server with Ctrl+C.

The command-line version from day03 still works: `python metropolis.py`.

## How to use

A macrostate of an Einstein solid is defined by two numbers: the number of
particles N and the total number of energy units q. On the page, the visitor
chooses the starting macrostates and the heat bath:

| Input | Meaning | Default | Allowed |
|---|---|---|---|
| Number of particles N | How many particles the solid has | 100 | 1 to 1,000 |
| Starting total energies q | One or more starting totals, separated by commas | 0, 266, 1000 | up to 5 values, each 0 to 10,000 |
| Temperature theta | Temperature of the heat bath, in energy units | 2.5 | 0.01 to 1000 |
| Steps | Number of Metropolis steps | 1,000,000 | 2 to 10,000,000 |
| Random seed | Starting point for the random numbers | 0 | any whole number |

Press **Run**. For each starting total q, the program spreads q energy units
at random over the N particles and runs a separate simulation from there, all
with the same theta, steps and seed.

`start_energies.csv` is not simulated directly. It supplies the form's default
values: N = 100 particles, and 266 as one of the starting totals.

The page then shows:

- **The calculation.** The exact answer, `N / (exp(1/theta) - 1)`, worked out
  step by step with the numbers of this run, and the classical answer,
  `N * theta`, each with a short explanation.
- **The simulation table.** One row per starting total q: its simulated mean
  total energy, and simulated minus exact in energy units.
- **Three plots**, each with a short explanation (see "The plots" below).

For the default N = 100 and theta = 2.5, the calculation reads:

| Step | Calculation | Result |
|---|---|---|
| 1 | 1 / theta = 1 / 2.5 | 0.4 |
| 2 | e^0.4 | 1.492 |
| 3 | 1.492 - 1 | 0.4918 |
| 4 | 1 / 0.4918 | 2.033 units per particle |
| 5 | 100 particles x 2.033 | 203.3 |

The classical answer is 100 x 2.5 = 250.0, which is 46.7 units too high.

If an input is not a number, or is out of range, the page shows an error
message instead of a result.

With the default settings a run takes about a second. Each simulation of 10^7
steps takes a few seconds, so the default three rows take about 8 seconds.

## The plots

Every run draws three plots, with one coloured line (or dot) per starting q.

1. **How each start is forgotten.** Total energy against steps, with the steps
   on a log scale, so the first few steps get as much room as the last few
   million. The lines begin at their different starting totals and are pulled
   toward the exact answer. A dotted vertical line marks the step from which
   all starts have exactly the same total energy (about step 23,000 with the
   default settings). With 1,000 steps the lines never meet, which shows why
   the number of steps matters.
2. **The whole run.** The same data on an ordinary step axis, zoomed in on the
   settled part, like the figure in the course exercise. The total energy
   keeps fluctuating around the exact answer (dashed black line), below the
   classical answer (dashed grey line). The first half has a grey background,
   because it is not averaged. The legend gives each run's mean.
3. **Mean total energy against temperature.** The exact curve and the
   classical line for the chosen N, with this run's simulated means as dots.
   The dots should sit on the exact curve. Running again with another theta
   moves them along it.

The plots are drawn with matplotlib in `plots.py` and sent inside the page
itself, so no picture files are saved.

## What the page demonstrates

All numbers below are for N = 100 and seed 0, with starting totals 0, 266 and
1000 spread at random.

**The starting energies don't change the result**, once there are enough
steps. **The number of steps does**: with too few, each run still remembers
where it started, and more steps also mean less noise (theta = 2.5):

| Steps | q = 0 | q = 266 | q = 1000 | Exact |
|---|---|---|---|---|
| 1,000 | 116.5 | 245.9 | 912.7 | 203.3 |
| 1,000,000 | 204.0 | 204.0 | 204.0 | 203.3 |
| 10,000,000 | 203.2 | 203.2 | 203.2 | 203.3 |

**Temperature changes the result.** All rows move together and follow the
exact answer (10^6 steps):

| theta | q = 0 | q = 266 | q = 1000 | Exact |
|---|---|---|---|---|
| 0.5 | 15.6 | 15.6 | 15.6 | 15.7 |
| 2.5 | 204.0 | 204.0 | 204.0 | 203.3 |
| 10 | 982.5 | 982.5 | 982.5 | 950.8 |

**N changes the result too.** With N = 500, theta = 2.5 and 10^6 steps, the
starts q = 0 and q = 5000 both give 1039.1 (exact 1016.6).

With enough steps the rows are exactly equal, and not only close, because all
of them use the same seed and so the same random moves: once each has
forgotten its start, they follow the same path.

At theta = 10, and at N = 500, the result is 2 to 3% off after 10^6 steps. A
hotter or larger system settles more slowly, so it needs more steps.

## Files

| File | What it is |
|---|---|
| `app.py` | The Flask web application: reads the form, checks the input, calls `metropolis()` |
| `templates/index.html` | The web page: the form, the calculation, the result table and the plots |
| `plots.py` | Draws the three plots with matplotlib |
| `metropolis.py` | The business logic from day03: `metropolis()`, plus `metropolis_trace()`, `record_points()` and `make_start()` |
| `make_data.py` | Generates the input data (unchanged from day03) |
| `start_energies.csv` | The day03 data (unchanged); supplies the form's default N and one default q |

## How it works

1. The browser asks for the page (a GET request). `app.py` sends back
   `index.html` with the form and its default values.
2. The user presses Run. The browser sends the three values back to `app.py`
   (a POST request).
3. `app.py` turns the text into numbers and checks them.
4. For each starting total q, `app.py` calls `make_start(n, q, seed)` to build
   the starting energies, and then `metropolis_trace(start, theta, steps, seed,
   record)`, which returns the mean and the energy at the recorded steps.
   Both are imported from `metropolis.py`. The web code contains no physics of
   its own.
5. `app.py` passes the results to `plots.py`, which draws the three plots.
6. `app.py` fills `index.html` with the results and sends it to the browser.

## What changed in `metropolis.py` since day03

`metropolis()` takes the same inputs and returns the same numbers as in day03
(203.2 for the exercise's settings). Five things changed for the web app:

- **The script part is under `if __name__ == "__main__":`.** In day03, the
  file ran the full 10^7-step simulation as soon as it was loaded. Now that
  only happens with `python metropolis.py`, and not on `import metropolis`.
- **Reading the CSV is a function, `read_energies(path)`**, so both the
  command-line program and the web app use the same code.
- **The exact formula is a function, `exact_energy(n, theta)`**, for the same
  reason.
- **New function `make_start(n, q_total, seed)`.** It builds a starting state
  for the macrostate (N, q): N particles that share q energy units, spread at
  random.
- **The loop moved into `metropolis_trace(q, theta, steps, seed, record)`.**
  It is the same loop, with one addition: at the step numbers listed in
  `record`, it remembers the total energy. It returns the mean and that list.
  `metropolis()` now just calls it and returns the mean. `record_points(steps)`
  chooses which steps to record: 400 evenly spaced, plus 400 packed near the
  start.

The file is also named `metropolis.py` in lower case (it was uploaded as
`Metropolis.py`), to match the import in `app.py` and the day03 README.

## Prompt

```text
here is my day03 project. pls give code to: Write a web application (e.g. using Flask) that will use the "business logic" from the previous implementation and provide a web interface to it.
explain every row pls in comments in code and in here. update a day04 readme file.
```

```text
ok but i want people to see how insert diffrent steps and temperature changes results while starting energies dont
```

```text
no i mean like in the last line here: [Hebrew lecture summary: a macrostate of an Einstein solid is defined by two numbers, the number of particles and the total number of energy units]
```

```text
1+ let visitor define the fixed starts values
```

```text
[quoting "The CSV row: when N is 100, the page also runs your day03 data from start_energies.csv as an extra row"] dont
```

```text
[quoting "It calculates the exact answer, N / (e^(1/theta) - 1), and the classical answer, N x theta."] add the calculation and explain.
```

```text
[quoting the "What the visitor learns from it" list and the description of the result table, with two pages of the course exercise attached: a plot of total energy against steps with the simulated and theoretical means] add it and show plot, not precent of all those comparisons similarly but more detailed than this
```