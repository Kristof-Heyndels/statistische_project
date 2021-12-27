import numpy as np
import os
import time
import matplotlib.pyplot as plt
from matplotlib import colors

grid = []
row_size = 800
col_size = 250
allowed_zone_height = row_size * 0.05
concentration = 0.4
adhesion_prob = 0.01
dentric_height = 1
working_volume = dentric_height + allowed_zone_height * col_size
desired_crystal_size = 400
desired_samples = 50

free_particles = []
growth = {(0, 0)}


def main():
    times = []
    for k in range(desired_samples):
        t_0 = time.time()
        init_grid()

        N = int(concentration * working_volume)
        for i in range(N):
            fill_random_square()

        while dentric_height < desired_crystal_size:
            move_particles()

        print_grid_to_file(k)
        print(f"Finished material sample: {k}")

        # guesstimating eta
        times.append(time.time() - t_0)
        avg = sum(times) / (k+1)
        projected_total_duration = avg * desired_samples
        estimated_eta = projected_total_duration - (k * avg)
        print(f"Simulation finish eta: {round(estimated_eta / 60)} minutes")


def init_grid():
    # resetting for new simulation
    grid.clear()
    free_particles.clear()
    growth.clear()

    global dentric_height
    dentric_height = 1

    grid.append(np.ones(col_size, dtype=int))
    for j in range(col_size):
        growth.add((0, j))

    for i in range(row_size - 1):
        grid.append(np.zeros(col_size, dtype=int))


def fill_random_square():
    b = True
    i = 0
    while b:
        i += 1
        upper_bound = min(dentric_height + allowed_zone_height, row_size)
        if dentric_height + 1 >= row_size:
            return
        row = np.random.randint(dentric_height + 10, upper_bound, dtype=int)
        col = np.random.randint(0, col_size, dtype=int)
        b = grid[row][col]
    grid[row][col] = 1
    free_particles.append([row, col])


def move_particles():
    for p in range(len(free_particles)):
        if p < len(free_particles):
            r = free_particles[p][0]
            c = free_particles[p][1]

            dr = np.random.randint(-1, 2, dtype=int)
            dc = np.random.randint(-1, 2, dtype=int)

            new_pos = update_position_after_step(r, dr, c, dc)
            if not has_grown(new_pos):
                free_particles[p] = [new_pos[0], new_pos[1]]
            else:
                free_particles[p] = free_particles[len(free_particles) - 1]
                free_particles.pop()
                growth.add((new_pos[0], new_pos[1]))
        else:
            break


def update_position_after_step(r, dr, c, dc):
    # do nothing if colliding with border
    if r+dr < 0 \
        or c+dc < 0 \
        or r+dr >= row_size \
            or c+dc >= col_size:
        return [r, c]

    # particles are not allowed to interact with each other
    if not grid[r+dr][c+dc] == 1:
        grid[r][c] = 0
        grid[r+dr][c+dc] = 1
        return [r+dr, c+dc]
    else:
        return [r, c]


def has_grown(pos):
    r = pos[0]
    c = pos[1]

    # checking if particle attaches to growth
    if (r+1, c) in growth \
            or (r-1, c) in growth \
            or (r, c+1) in growth \
            or (r, c-1) in growth:
        if np.random.uniform(0, 1) < adhesion_prob:
            growth.add((r, c))

        # updating height of dentric growth
        global dentric_height
        if r > dentric_height:
            dentric_height = r

        # adjusting concentration
        if len(free_particles) / working_volume < concentration:
            fill_random_square()
        return True
    return False


def print_grid():
    # cleaning free particles
    for p in free_particles:
        grid[p[0]][p[1]] = 0

    for i in range(len(grid)):
        print(grid[i])


def print_grid_to_file(k, clean_file=True):
    global adhesion_prob
    global concentration

    #dirname = os.path.dirname(__file__)
    dirname = ""
    filepath = os.path.join(
        dirname, f'material_S={adhesion_prob}_f={concentration}/')

    # cleaning free particles
    if clean_file:
        for p in free_particles:
            grid[p[0]][p[1]] = 0

    # creating dir
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(f'{filepath}mat_{k}_cleaned.txt', 'w') as file:
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if grid[i][j] == 1:
                    file.write(str(grid[i][j]))
                else:
                    file.write(" ")
            file.write("\n")

    with open(f'{filepath}mat_{k}.txt', 'w') as file:
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                file.write(str(grid[i][j]))
            file.write("\n")

    plot(k, filepath)


def plot(k, path):
    image_path = os.path.join(path, 'img/')

    # creating dir
    if not os.path.exists(os.path.dirname(image_path)):
        try:
            os.makedirs(os.path.dirname(image_path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    cmap_growth = colors.ListedColormap(['white', 'black'])
    bounds = [0, .5, 1]
    norm = colors.BoundaryNorm(bounds, cmap_growth.N)

    # Plot crystal
    plt.figure(figsize=(200, 200))
    plt.imsave(f'{image_path}mat_{k}.png', grid, cmap=cmap_growth)
    plt.show()


if __name__ == "__main__":
    main()
