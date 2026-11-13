# make_data.py
# Creates the input data file, start_energies.csv: a starting energy for each
# of 100 particles. Run it once with:   python make_data.py
# (The file already exists in this folder, so you only need to run this
# if you want to create the data again.)

# "random" is Python's built-in module for random numbers.
import random

# Fix the "seed" of the random numbers. A seed is the starting point of the
# random sequence. With the same seed, the script produces exactly the same
# "random" numbers every time, so everyone gets the same CSV file.
# The number 1 has no special meaning; any whole number would do.
random.seed(1)

# Open (create) the file for writing ("w"). "with" closes the file
# automatically when the indented block ends. "f" is our name for the open file.
with open("start_energies.csv", "w") as f:

    # First line of a CSV file: the column names, separated by a comma.
    # "\n" means "end of line".
    f.write("particle_number,starting_energy_units\n")

    # Repeat for i = 1, 2, ..., 100 (range stops BEFORE 101).
    for i in range(1, 101):

        # Write one line: the particle's number, a comma, and a random whole
        # number from 0 to 5 (both ends included) as its starting energy.
        # The f"..." form puts the values of the {...} parts into the text.
        f.write(f"{i},{random.randint(0, 5)}\n")