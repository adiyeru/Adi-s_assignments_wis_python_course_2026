# plots.py
# Draws the three plots for the web page (day04), using matplotlib.
#
# A web page shows pictures with an <img> tag. Normally the tag points to a
# picture file. Here we don't save any files: each function draws a plot in
# memory, turns the PNG picture into a long piece of text (called base64),
# and returns that text. The page puts the text straight into the <img> tag.

# Python's built-in modules.
import base64   
# turns raw bytes (the picture) into ordinary text characters
# A web page is text, but a PNG picture is binary data: 
# raw bytes, many of which aren’t letters at all. 
# To put the picture inside the page’s text, 
# it has to be written with ordinary characters first. 
# Base64 does that: it rewrites any bytes using only 64 safe 
# characters (A–Z, a–z, 0–9, + and /).
import io       # gives us a "file" that lives in memory instead of on disk
import math     # for math.exp(x), which is e^x

# matplotlib is the plotting library (install it with: pip install matplotlib).
# A Figure is one whole picture. We use Figure directly, and not the more
# common "pyplot", because pyplot keeps hidden state between calls, which
# causes trouble inside a web server.
from matplotlib.figure import Figure

# Colours, written as hex codes (#RRGGBB).
# One colour per starting q, always in this order: blue, orange, green,
# yellow, pink. The web app allows at most 5 starting totals, so 5 are enough.
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
INK = "#1a1a19"    # near-black: used for the exact answer
GREY = "#8a897f"   # grey: used for the classical answer and for markers


def new_figure(title, xlabel, ylabel):
    """Create an empty plot with a title and axis names.
    All three plots start here, so they look alike."""
    # One picture, 7.4 inches wide and 4.4 inches high.
    # layout="constrained" makes matplotlib arrange everything so that the
    # labels and the legend fit inside the picture without overlapping.
    fig = Figure(figsize=(7.4, 4.4), layout="constrained")

    # "Axes" (here: ax) is the rectangle in which the data is drawn,
    # together with its two axes. subplots() with no numbers creates one.
    ax = fig.subplots()

    # The title, at the top left, in bold.
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")

    # The names written along the horizontal (x) and vertical (y) axes.
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # Light grey grid lines, to make values easier to read off.
    ax.grid(color="#e4e3dd", linewidth=0.8)

    # Draw the grid behind the data, not on top of it.
    ax.set_axisbelow(True)

    # A plot normally has a box around it. Hide its top and right sides,
    # which carry no information.
    ax.spines[["top", "right"]].set_visible(False)

    # Give back both: the picture, and the drawing area inside it.
    return fig, ax


def add_legend(fig, columns=3):
    """Add the legend: the key that says what each line means."""
    # It collects every line that was given a label=... .
    # "outside lower center" puts it under the plot, where it can never cover
    # the data. ncols is the number of columns; frameon=False removes the box.
    fig.legend(loc="outside lower center", ncols=columns, frameon=False, fontsize=9)


def to_image(fig):
    """Turn a finished figure into text that an <img> tag can show."""
    # An empty in-memory "file" for bytes.
    buffer = io.BytesIO()

    # Draw the picture into it in PNG format. dpi (dots per inch) sets the
    # sharpness: 7.4 inches x 110 dpi = 814 pixels wide.
    fig.savefig(buffer, format="png", dpi=110)

    # buffer.getvalue()  -> the PNG picture as raw bytes
    # b64encode(...)     -> the same data written with text characters only
    # .decode()          -> from Python "bytes" to an ordinary string
    return base64.b64encode(buffer.getvalue()).decode()


# What the plot functions receive:
#   runs      : a list with one dictionary per starting q. Each has
#                 "start_total" : the starting total energy
#                 "simulated"   : the mean total energy from the simulation
#                 "trace"       : a list of (steps done, total energy) pairs
#   exact     : the exact answer,      N / (e^(1/theta) - 1)
#   classical : the classical answer,  N * theta


def plot_start(runs, exact, merged_at):
    """Plot 1: total energy against steps, with the steps on a log scale.

    On a log scale each tick is 10 times the one before (1, 10, 100, ...),
    so the first few steps get as much room as the last few million. That
    makes it possible to see how each start is forgotten."""
    # Empty plot with title, x-axis name and y-axis name.
    fig, ax = new_figure("How each start is forgotten",
                         "Steps done (log scale: each tick is 10 times the one before)",
                         "Total energy (units)")

    # zip pairs the runs with the colours: first run with blue, second with
    # orange, and so on. The loop draws one line per starting q.
    for run, color in zip(runs, COLORS):

        # Split the trace's pairs into two lists: x values (steps done) and
        # y values (total energy). The pair at step 0 is left out, because a
        # log scale cannot show 0.
        xs = [x for x, y in run["trace"] if x >= 1]
        ys = [y for x, y in run["trace"] if x >= 1]

        # Draw the line. `label` is the text for the legend.
        ax.plot(xs, ys, color=color, linewidth=1.5, label=f"start q = {run['start_total']}")

    # A horizontal line across the whole plot at the exact answer.
    # "--" means dashed. {exact:.1f} writes the number with 1 decimal.
    ax.axhline(exact, color=INK, linestyle="--", linewidth=1.2, label=f"exact = {exact:.1f}")

    # merged_at is the step from which all runs have the same energy, or
    # None if that never happened. "if merged_at:" is true only for a real,
    # non-zero step number.
    if merged_at:
        # A vertical dotted (":") line at that step.
        # {merged_at:,} writes the number with thousands commas: 23,174.
        ax.axvline(merged_at, color=GREY, linestyle=":", linewidth=1.5,
                   label=f"all starts identical from step {merged_at:,}")

    # Switch the horizontal axis to a log scale.
    ax.set_xscale("log")

    # Add the legend, and return the picture as text.
    add_legend(fig)
    return to_image(fig)


def plot_whole_run(runs, exact, classical, steps):
    """Plot 2: total energy over the whole run, on an ordinary step axis.
    This is the plot from the course exercise, with more on it."""
    fig, ax = new_figure("The whole run: fluctuating around the average",
                         "Steps done", "Total energy (units)")

    # A grey background from step 0 to the halfway step: the half of the run
    # that is NOT used for the average. alpha=0.15 makes it almost
    # see-through; linewidth=0 removes its border.
    ax.axvspan(0, steps / 2, color=GREY, alpha=0.15, linewidth=0,
               label="first half: not averaged")

    # Here we collect every energy value seen in the second half, from all
    # runs. They are used below to decide how far to zoom in.
    settled = []

    # One line per starting q.
    for run, color in zip(runs, COLORS):

        # x values (steps done) and y values (total energy). This time the
        # starting point at step 0 is included.
        xs = [x for x, y in run["trace"]]
        ys = [y for x, y in run["trace"]]

        # Draw a thin line. Its legend text also gives the run's mean.
        ax.plot(xs, ys, color=color, linewidth=0.9,
                label=f"start q = {run['start_total']}: mean {run['simulated']:.1f}")

        # Add this run's second-half energies to the collection.
        settled += [y for x, y in run["trace"] if x >= steps / 2]

    # Two horizontal dashed lines: the exact answer (black) and the
    # classical answer (grey).
    ax.axhline(exact, color=INK, linestyle="--", linewidth=1.2, label=f"exact = {exact:.1f}")
    ax.axhline(classical, color=GREY, linestyle="--", linewidth=1.2, label=f"classical = {classical:.1f}")

    # Choose the vertical range by hand. Left alone, matplotlib would make
    # room for a far-away start such as q = 1000, and the interesting
    # fluctuations would be squashed flat. Instead we zoom in on the settled
    # values, making sure both answer lines stay visible.
    low = min(settled + [exact, classical])    # lowest value that must be visible
    high = max(settled + [exact, classical])   # highest value that must be visible
    margin = 0.15 * (high - low) + 1           # some empty room above and below
    ax.set_ylim(low - margin, high + margin)   # set the range (far-away starts are cut off)

    # Write the step numbers in full, not as "1e6" ...
    ax.ticklabel_format(axis="x", style="plain")
    # ... and with thousands commas: 1,000,000. matplotlib calls this small
    # function for every tick, with the tick's value x (and its position,
    # which we don't use).
    ax.xaxis.set_major_formatter(lambda x, pos: f"{x:,.0f}")

    add_legend(fig)
    return to_image(fig)


def plot_theta(runs, n, theta):
    """Plot 3: mean total energy against temperature.
    Two curves from the formulas, plus this run's simulated results as dots."""
    fig, ax = new_figure(f"Mean total energy against temperature (N = {n})",
                         # The x-axis name, with theta's unit. Text between $...$ is drawn
                         # as a formula: \theta is the Greek letter, k_B is k with a small B,
                         # \varepsilon is epsilon. The r"..." keeps the backslashes as they are.
                         r"Temperature $\theta = k_BT/\varepsilon$ (energy units)",
                         "Mean total energy (units)")

    # How far the temperature axis goes: twice this run's theta, so that the
    # dots land in the middle, but at least up to 5.
    top = max(2 * theta, 5)

    # 200 temperatures, evenly spaced from top/200 up to top.
    # (They start just above 0, because the formula can't be computed at 0.)
    thetas = [top * k / 200 for k in range(1, 201)]

    # The exact curve: the formula computed at each of the 200 temperatures.
    ax.plot(thetas, [n / (math.exp(1 / t) - 1) for t in thetas], color=INK, linewidth=2,
            label="exact: N / (e^(1/theta) - 1)")

    # The classical answer, N * theta: a straight dashed line.
    ax.plot(thetas, [n * t for t in thetas], color=GREY, linewidth=2, linestyle="--",
            label="classical: N x theta")

    # One dot per starting q, at (this run's theta, its simulated mean).
    # "o" means: draw a round marker and no line. The white edge keeps dots
    # apart when they touch. When the starts agree, the dots lie exactly on
    # top of each other and only the last one is visible.
    for run, color in zip(runs, COLORS):
        ax.plot(theta, run["simulated"], "o", color=color, markersize=8, markeredgecolor="white",
                label=f"simulated, start q = {run['start_total']}: {run['simulated']:.1f}")

    # The labels here are long, so the legend gets 2 columns instead of 3.
    add_legend(fig, columns=2)
    return to_image(fig)