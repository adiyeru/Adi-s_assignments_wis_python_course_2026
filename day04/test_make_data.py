# # to run: python -m pytest
# test_make_data.py
# A test for make_data.py, the script that creates start_energies.csv.

# make_data.py is a script, not a function. When it runs, it writes the file
# start_energies.csv into the CURRENT folder (the folder the program is
# working in). If we simply ran it in the day04 folder, it would overwrite
# the real data file. 
# So the test:
#   1. moves into an empty temporary folder,
#   2. runs the script there, so the new file is written there,
#   3. compares the new file with the real one, and checks its contents,
#   4. moves back to day04 (pytest does this step for us).
# The real start_energies.csv is only read, never changed.

# runpy is a built-in module that runs a Python file, exactly as if you had
# typed "python make_data.py" in a terminal.
import runpy

# Path is a built-in tool for file paths. 
# It joins folder and file names with
# "/", and works the same on Windows, Mac and Linux (system indepentant).
from pathlib import Path

# the function from metropolis.py that reads the energies from a CSV file.
# Reusing it means the test reads the file the same way the app does.
from Metropolis import read_energies

# __file__ is the path of this test file. .parent is the folder it is in,
# which is the day04 folder. make_data.py and the real start_energies.csv are
# in that same folder.
HERE = Path(__file__).parent

# The test:
# pytest runs every function whose name starts with test_.
#
# The two arguments are pytest "fixtures": ready-made helpers. 
# pytest sees their names, 
# prepares them before the test starts, 
# and passes them in.
#   tmp_path    : the path of a brand-new, empty folder, 
#                  made just for this test. Each test gets its 
#                  own, so tests can't disturb each other. 
#                  pytest keeps only the folders of its last few runs
#                  and deletes older ones by itself.
#   monkeypatch : a helper for making temporary changes. 
#                 It remembers every change made through it 
#                 and undoes them all when the test ends, 
#                 even if the test fails halfway.
def test_make_data(tmp_path, monkeypatch):
    # STEP 1: move into the empty temporary folder.
    # chdir means "change directory": 
    # it changes the current folder, which is
    # where a program puts a file when it is given only a 
    # file name.
    # monkeypatch remembers that we were in day04, 
    # and moves back there by itself when the test ends 
    # (STEP 4), whether the test passed or failed.
    # (Plain os.chdir would leave us stuck in the 
    # temporary folder, and every test after this one would 
    # run from the wrong place.)

    monkeypatch.chdir(tmp_path)
    # STEP 2: run make_data.py.
    # HERE / "make_data.py" is the full path of the script in day04, 
    # so it is found even though we are now in the temporary folder.
    # str(...) turns the Path into ordinary text, which run_path expects.
    # Inside the script, open("start_energies.csv", "w") 
    # has no folder in the file name, 
    # so the file is written into the CURRENT folder: the
    # temporary one. The real file in day04 is not touched.
    runpy.run_path(str(HERE / "make data.py"))

    # The path of the file the script just wrote, in the temporary folder.
    new_file = tmp_path / "start_energies.csv"

    # The path of the real data file in day04, the one the web app reads.
    real_file = HERE / "start_energies.csv"

    # STEP 3a: 
    # the new file must be identical to the real one.
    # read_text() reads a whole file as one piece of text, 
    # so == compares the two files character for character.
    # This works because make_data.py fixes the seed 
    # (random.seed(1)): the same seed gives the same "random" 
    # numbers, so the same file every time.
    # If someone changes the script
    # (another seed, another range, another
    # number of particles), the new file differs and this 
    # line fails.
    assert new_file.read_text() == real_file.read_text()

    # STEP 3b: check the contents, 
    # to show what the file is used for.
    # read_energies gives a list of whole numbers: 
    # one energy per particle.
    q = read_energies(new_file)

    # 100 particles. 
    # The app uses this number as the default 
    # N on the page
    # (app.py: len(CSV_START)).
    assert len(q) == 100

    # The energies add up to 266. 
    # The app uses this as one of the default
    # starting totals, "0, 266, 1000" (app.py: sum(CSV_START)).
    assert sum(q) == 266

    # Each energy is between 0 and 5, 
    # because make_data.py draws every one
    # with random.randint(0, 5). 
    # all(...) is True only if every energy passes.
    assert all(0 <= e <= 5 for e in q)
