import random

random.seed(1)
with open("start_energies.csv", "w") as f:
    f.write("particle_number,starting_energy_units\n")
    for i in range(1, 101):
        f.write(f"{i},{random.randint(0, 5)}\n")