# Metropolis simulation of an Einstein solid: web app (day04) and tests (day05)

This project builds on the day03 Metropolis simulation of an Einstein solid.

- **Day 04** adds a small Flask web application in front of the day03
  "business logic": a page where a visitor chooses the starting energies and
  the heat bath, runs the simulation and sees the results and three plots.
- **Day 05** adds pytest tests for that business logic and for the data
  script.

The physics is the same `metropolis()` function as in day03. For the physics
background (the Einstein solid, the heat bath, the Metropolis algorithm and why
the answer is 203 and not 250), see the day03 README.

## How to run

Install the packages once:

```text
pip install flask matplotlib pytest
```

**The web app (day04).** From the project folder:

```text
python app.py
```

Then open http://127.0.0.1:5000 in a browser. Stop the server with Ctrl+C.

**The tests (day05).** From the project folder:

```text
python -m pytest
```
**The command-line version from day03** still works: `python Metropolis.py`.

---

## Day 04: the web app

### How to use

A macrostate of an Einstein solid is defined by two numbers: the number of
particles N and the total number of energy units q. On the page, the visitor
chooses the starting macrostates and the heat bath:

| Input | Meaning | Default | Allowed |
|---|---|---|---|
| Number of particles N | How many particles the solid has | 100 | 1 to 1,000 |
| Starting total energies q | One or more starting totals, separated by commas | 0, 266, 1000 | up to 5 values, each 0 to 10,000 |
| Temperature theta | Temperature of the heat bath, in energy units (see below) | 2.5 | 0.01 to 1000 |
| Steps | Number of Metropolis steps | 1,000,000 | 2 to 10,000,000 |
| Random seed | Starting point for the random numbers | 0 | any whole number |

**The unit of theta.** theta = k_B·T / ε. It is the temperature written as an
energy (k_B·T, where k_B is Boltzmann's constant), counted in energy units (ε is
the size of one unit). So theta = 2.5 means k_B·T = 2.5 energy units: the bath's
typical thermal energy is two and a half units. Because theta and the energies
use the same unit, 1/theta in the formulas has no unit, and N × theta is an
energy.

Press **Run**. For each starting total q, the program spreads q energy units
at random over the N particles and runs a separate simulation from there, all
with the same theta, steps and seed.

`start_energies.csv` is not simulated directly. It supplies the form's default
values: N = 100 particles, and 266 (the sum of its energies) as one of the
starting totals. 0 and 1000 are a very low and a very high start, on either
side of the equilibrium value of about 203.

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
| 1 | 1 / theta = 1 / 2.5 | 0.4 (no unit) |
| 2 | e^0.4 | 1.492 |
| 3 | 1.492 - 1 | 0.4918 |
| 4 | 1 / 0.4918 | 2.033 energy units per particle |
| 5 | 100 particles x 2.033 | 203.3 energy units |

The classical answer is 100 x 2.5 = 250.0 energy units, which is 46.7 units
too high.

If an input is not a number, or is out of range, the page shows an error
message instead of a result.

With the default settings a run takes about a second. Each simulation of 10^7
steps takes a few seconds, so the default three rows take about 8 seconds.

### The plots

Every run draws three plots. They are drawn with matplotlib in `plots.py`.

**How they are made**

- **One colour per starting q,** always in the same order: blue, orange,
  green, yellow, pink (the page allows at most 5 starts). The exact answer is
  a near-black dashed line, and the classical answer a grey dashed line.
- **The legend is under each plot,** so it can never cover the data.
- **No picture files are saved.** Each plot is drawn in memory, turned into
  text (base64) and put straight into the page's `<img>` tag.
- **matplotlib's `Figure` is used directly, not `pyplot`.** `pyplot` keeps
  hidden state between calls, which causes trouble inside a web server.
- **About 800 points per run are plotted, not every step.** Drawing all 10
  million steps would be far too slow, using `record_points()` .

The examples below come from a default run: N = 100, theta = 2.5, 10^6 steps,
seed 0, starting totals 0, 266 and 1000. All three starts end at a mean of
204.0, against the exact 203.3.

**1. How each start is forgotten**

Total energy against steps on a log scale, one line per starting q, converging on the exact answer:

Total energy against steps, with the steps on a **log scale**: each tick is 10
times the one before, so the first few steps get as much room as the last few
million. On an ordinary axis the start would be forgotten in an invisible
sliver at the left edge. The lines begin at their different starting totals
(0, 266 and 1000) and are pulled onto the exact answer: starts that are too
high lose energy, and starts that are too low gain it.

A **dotted vertical line** marks the step from which all starts have exactly
the same total energy: step 23,174 here. They become exactly equal, not just
close, because all runs use the same seed and so make the same random moves.
After that, only the last colour drawn (green) is visible. With 1,000 steps
the lines never meet, which shows why the number of steps matters. The text on
the page changes to match: whether the starts merged, never merged, or merged
too late for the means to agree.

**2. The whole run**

Total energy against steps for the whole run, fluctuating around the exact answer, below the classical answer:

The same runs on an ordinary step axis, like the figure in the course
exercise, with more on it. The total energy keeps fluctuating around the exact
answer (dashed black), below the classical answer (dashed grey). The **first
half has a grey background**, because it is not used for the mean. Each line's
legend entry gives its mean.

The vertical axis is **zoomed in on the settled part**, so the fluctuations
are not squashed flat. A far-away start such as q = 1000 therefore runs off
the top at the left edge; plot 1 shows that part in full. The step numbers are
written in full with commas (1,000,000, not 1e6).

**3. Mean total energy against temperature**

Mean total energy against temperature: the exact curve, the classical line, and this run's simulated mean as a dot on the exact curve:

The exact curve, N / (e^(1/theta) − 1), and the classical line, N × theta, for
the chosen N, drawn at 200 temperatures from just above 0 up to twice this
run's theta (at least up to 5). The horizontal axis is labelled with theta's
unit: **Temperature θ = k_BT/ε (energy units)**.

This run's simulated means are the dots. They sit on the exact curve, below
the classical line. When the starts agree, the dots lie on top of each other.
Running again with another theta moves them along the curve. The gap between
the curve and the line is largest at low temperature and stays at about half a
unit per particle at high temperature.

### What the page demonstrates

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

| theta (energy units) | q = 0 | q = 266 | q = 1000 | Exact |
|---|---|---|---|---|
| 0.5 | 15.6 | 15.6 | 15.6 | 15.7 |
| 2.5 | 204.0 | 204.0 | 204.0 | 203.3 |
| 10 | 982.5 | 982.5 | 982.5 | 950.8 |

**N changes the result too.** With N = 500, theta = 2.5 and 10^6 steps, the
starts q = 0 and q = 5000 both give 1039.1 (exact 1016.6).

At theta = 10, and at N = 500, the result is 2 to 3% off after 10^6 steps. A
hotter or larger system settles more slowly, so it needs more steps.

### How it works

1. The browser asks for the page (a GET request). `app.py` sends back
   `index.html` with the form and its default values.
2. The user presses Run. The browser sends the five values back to `app.py`
   (a POST request).
3. `app.py` turns the text into numbers and checks them.
4. For each starting total q, `app.py` calls `make_start(n, q, seed)` to build
   the starting energies, and then `metropolis_trace(start, theta, steps, seed,
   record)`, which returns the mean and the energy at the recorded steps.
   Both come from `Metropolis.py`. The web code contains no physics of its own.
5. `app.py` passes the results to `plots.py`, which draws the three plots.
6. `app.py` fills `index.html` with the results and sends it to the browser.

#### The Flask route: `@app.route`

The decorator in `app.py` connects a web address to a Python function:

```python
@app.route("/", methods=["GET", "POST"])
def index():
```

A **decorator** is Python syntax that adds behavior to a function. It starts
with `@` and is written directly above the function. Conceptually,
`@app.route(...)` is like calling:

```python
index = app.route("/", methods=["GET", "POST"])(index)
```

Python first creates the `index()` function and then passes that function to
`app.route()`. Flask uses the decorator to register `index()` as the function
that handles the home page. Later, when Flask receives a matching request, it
calls `index()` and sends its returned HTML to the browser.

`"/"` is the address of the home page. `methods=["GET", "POST"]` allows the
page to handle both kinds of HTTP request. The decorator tells Flask to call
`index()` whenever the browser requests `/`.

#### GET

GET requests the page. It is the request used when the browser opens
`http://127.0.0.1:5000/` or refreshes the page. It does not contain form
values, so `request.method == "POST"` is false:

```python
if request.method == "POST":
```

The result is therefore `None`, and `index.html` displays the form with the
default values but no simulation results.

#### POST

POST sends data to the server. In `templates/index.html`, the form uses
`method="post"`:

```html
<form method="post">
```

Pressing the Run button sends the five input values back to `/` as a POST
request. Flask places those values in `request.form`, where each input is
available by the name written in its HTML `name` attribute:

```python
form[name] = request.form.get(name, "")
```

For example, `<input name="n">` gives `request.form.get("n")`. Every form value
starts as text, so `app.py` converts it to a number with `float()` or `int()`.
The program then checks that the values are in the allowed ranges. If they are
valid, it runs the simulation, creates the plots and sends the page with the
results.

Both GET and POST reach the same route and call the same `index()` function.
The main difference is that GET asks only to display the page, while POST
submits form values and asks the server to perform the simulation.

Flask prints one line in the terminal for each request, for example
`"GET / HTTP/1.1" 200` when the page is opened and `"POST / HTTP/1.1" 200`
when Run is pressed. 200 means the page was sent successfully.

### What changed in `Metropolis.py` since day03

`metropolis()` takes the same inputs and returns the same numbers as in day03
(203.2 for the exercise's settings). Five things changed for the web app:

- **The script part is under `if __name__ == "__main__":`.** In day03, the
  file ran the full 10^7-step simulation as soon as it was loaded. Now that
  only happens when the file is run directly, not when it is imported.
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
  chooses which steps to record.

---

## Day 05: tests

The tests use **pytest**. pytest finds every file whose name starts with
`test_` and runs every function in it whose name starts with `test_`. A test
passes if it finishes without an error, and fails if an `assert` line is
false.

There are two test files, with 20 tests in total. All pass in about 3 seconds.

| File | Tests | What it tests |
|---|---|---|
| `test_metropolis.py` | 19 | the business logic in `Metropolis.py` |
| `test_make_data.py` | 1 | the data script `make data.py` |

Only the business logic is tested. `app.py` and `plots.py` contain no physics:
they read the form and display results, so they are left out.

### How the checks work

Two kinds of checks are used:

- **Exact checks,** for things that must always hold: the length of a list, a
  total, a value from a formula. For example, `assert sum(q) == q_total`.
- **Checks with a tolerance,** for the simulation, which is random and only
  comes close to the exact answer. For example,
  `assert result == pytest.approx(exact, rel=0.05)`, which means "within 5%".

**Why 5%.** The tolerance was measured, not guessed: over 20 seeds with N =
100, theta = 2.5 and 10^6 steps, the simulated mean was 1.5% from the exact
answer on average and 3.7% at most.

**Why 10^6 steps, not 10^7.** The system forgets its start after about 20,000
steps, so 10^6 is plenty, and each run takes under half a second.

**Why the random tests never fail by chance.** Every simulation in the tests
uses a fixed seed, so it gives exactly the same result on every run.

Two pytest tools keep the tests short:

- `@pytest.mark.parametrize` runs one test several times with different
  inputs, instead of copying it.
- `pytest.approx` compares numbers with a tolerance instead of exactly.

### `test_metropolis.py`: the business logic

| Test | What it checks | Why |
|---|---|---|
| `exact_energy_for_the_exercise` | gives 203.3 for N = 100, theta = 2.5 | the formula the simulation is compared with must be right |
| `exact_energy_is_proportional_to_n` | 200 particles hold twice the energy of 100 | the particles are independent |
| `exact_energy_is_almost_zero_at_low_temperature` | below 0.000001 at theta = 0.05 | in a cold bath a whole unit is almost never available |
| `make_start_builds_the_requested_macrostate` (4 runs) | N energies, adding up to q, none negative | every start must be the macrostate (N, q) asked for |
| `make_start_is_reproducible` | the same seed gives the same start | runs must be repeatable |
| `make_start_depends_on_the_seed` | different seeds give different starts | the seed must actually be used |
| `record_points_stay_within_the_run` | recorded steps run from 1 to the last step | the plots must not ask for steps that don't exist |
| `metropolis_is_reproducible` | the same seed gives exactly the same mean | runs must be repeatable; this also fails if the input list is changed instead of copied |
| `energy_changes_by_at_most_one_unit_per_step` | records every step: changes of at most 1, never below 0 | the rules of the Metropolis loop |
| `result_does_not_depend_on_the_start` (3 runs) | from q = 0, 266 and 1000, within 5% of 203.3 | the main physics claim |
| `result_follows_the_exact_formula_at_other_temperatures` (3 runs) | at theta = 1, 2.5 and 5, within 5% of the formula | temperature changes the result as the formula says |
| `result_is_below_the_classical_answer` | below N × theta = 250 | whole energy units give less than the classical answer |

The four `make_start` cases are chosen to cover the extremes, not only the
typical case:

| (N, q) | Case | What could go wrong |
|---|---|---|
| (100, 266) | the exercise's starting state | the basic job |
| (100, 0) | no energy at all | must still return 100 zeros, not an empty list |
| (1, 7) | a single particle | every unit must go to it: exactly `[7]` |
| (5, 1000) | far more units than particles | nothing may cap a particle's energy (for example at 5, like the CSV), or the total 1000 can't be reached |

### `test_make_data.py`: the data script

`make data.py` is a script, not a function: when it runs, it writes
`start_energies.csv` into the current folder. Running it in the project folder
would overwrite the real data file. So the test:

1. moves into an empty temporary folder (pytest's `tmp_path` and
   `monkeypatch.chdir`),
2. runs the script there with `runpy.run_path`, as `python "make data.py"`
   would,
3. checks the file it wrote,
4. moves back to the project folder (`monkeypatch` does this by itself, even
   if the test fails).

The real `start_energies.csv` is only read, never changed.

The test checks that:

- **the new file is identical to the real `start_energies.csv`.** The script
  fixes the seed (`random.seed(1)`), so it must reproduce the data exactly.
  This is the strongest check: any change to the script breaks it.
- **it has 100 energies totalling 266.** These are the app's default N and
  one of its default starting totals.
- **every energy is from 0 to 5,** as `random.randint(0, 5)` promises.

Checking only the existing CSV would not test the script. If someone changed
the script without rerunning it, the old file would still pass.

### Checking that the tests catch bugs

A test suite is only useful if it fails when the code is wrong. To check this,
typical bugs were planted one at a time in a copy of the code, and the tests
were run against each.

| Planted bug | Tests that failed |
|---|---|
| Acceptance chance `e^(-theta)` instead of `e^(-1/theta)` | 5 |
| Energy allowed to go below zero | 7 |
| Working on the caller's list instead of a copy | 1 |
| `make data.py`: seed 2 instead of 1 | 1 |
| `make data.py`: energies up to 6 | 1 |
| `make data.py`: only 99 particles | 1 |
| Averaging the whole run instead of the second half | **0** |

**Known gap.** No test notices if the mean is taken over the whole run
instead of the second half. The difference is too small for the 5% tolerance.
A test that would catch it: run 10,000 steps from 50 units at theta = 0.01 (a
very cold bath). All the energy drains away early, so the second half is all
zeros and the mean must be exactly 0. Averaging the whole run would include
the start and give more than 0.

---

## Files

| File | What it is |
|---|---|
| `app.py` | The Flask web application: reads the form, checks the input, calls the business logic (day04) |
| `templates/index.html` | The web page: the form, the calculation, the result table and the plots (day04) |
| `plots.py` | Draws the three plots with matplotlib (day04) |
| `Metropolis.py` | The business logic: `metropolis()`, `metropolis_trace()`, `record_points()`, `exact_energy()`, `make_start()`, `read_energies()` |
| `make data.py` | Generates the input data (unchanged from day03) |
| `start_energies.csv` | The day03 data (unchanged); supplies the form's default N and one default q |
| `test_metropolis.py` | pytest tests for the business logic (day05) |
| `test_make_data.py` | pytest test for `make data.py` (day05) |
| `images/` | The three example plots shown in this README |

## Prompts

**Day 04**

```text
here is my day03 project. pls give code to: Write a web application (e.g. using Flask)
explain every row pls in comments in code and in here. update a day04 readme file.
```

**Day 05**

```text
pls write some tests for the "business logic" of these. keep thing simple and good practice coding. explain why and how you check. use pytest.
```

