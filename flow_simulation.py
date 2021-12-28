### FLOW ###

import numpy as np
import os
import time
import matplotlib.pyplot as plt

sample_count = 50
ensemble_size = 1
min_slice_height = 5
max_slice_height = 5
simulated_steps = pow(10, 3)

grid = []
concentration = 0.4
adhesion_prob = 1
sample_width = 250
sample_height = 800
starting_row = 1
incoming_flow = 5

a_up = 0.2  # prob to move upwards, for a = 0.2 we have a_up = 2*a_remaining
# defining all steps
step_no_step = [0, 0]
step_ldiag_up = [-1, -1]
step_rdiag_up = [-1, 1]
step_down = [1, 0]
step_ldiag_down = [1, -1]
step_rdiag_down = [1, 1]
step_left = [0, -1]
step_right = [0, 1]
remaining_steps = (step_no_step, step_down, step_left, step_right,
                   step_ldiag_up, step_ldiag_down, step_rdiag_up, step_rdiag_down)


def main():
    times = []
    results = init_results(max_slice_height)
    for k in range(sample_count):
        t_0 = time.time()
        for d in range(min_slice_height, max_slice_height + 1):
            load_crystal(k, d)
            # init for t=0
            particles = []
            outgoing_particles = 0

            for t in range(simulated_steps):
                # each time step, n amount of particles enter the experiment
                for n in range(incoming_flow):
                    particles.append(create_particle(d+5))

                # iterate over each particle, allowing it to take a single step
                for i in range(len(particles)):
                    if i < len(particles):
                        p = particles[i]
                        grid[p[0]][p[1]] = 0
                        #print(f"====== \nmoving particle: {p} ... ")
                        p = step(p)
                        grid[p[0]][p[1]] = 9
                        #print(f"moved to {p} \n======")
                        if p[0] == 0:
                            grid[p[0]][p[1]] = 0    
                            outgoing_particles += 1
                            particles[i] = particles[len(particles) - 1]
                            particles.pop()

                    else:
                        break
            outgoing_flow = outgoing_particles / simulated_steps
            print(
                f"{outgoing_particles} Particles passed the filter. The outgoing flow is {outgoing_flow}.")

            #print_grid_to_file(k, d)

        # guesstimating eta
        times.append(time.time() - t_0)
        avg = sum(times) / (k+1)
        projected_total_duration = avg * sample_count
        estimated_eta = projected_total_duration - (k * avg)
        print(
            f"{k}: Using a_up = {a_up}, simulation finish eta: {round(estimated_eta / 60)} minutes")

        keys = list(results.keys())
        norm_vals = [x / (sample_count * ensemble_size)
                     for x in list(results.values())]

        #save_plot(init_plot(keys, norm_vals))
        # plt.show()
        #save_plot_data(results, norm_vals)


def create_particle(srow):
    return [srow, np.random.randint(0, sample_width, dtype=int)]


def step(p):
    #print(f"initial p: {p}")
    if np.random.uniform(0, 1) < a_up:
        step = [-1, 0]
    else:
        step = remaining_steps[np.random.randint(0, 8, dtype=int)]

    #print(f"has_collision = {has_collision}")
    if not check_collision_in_path(p, step):
        p[0] += step[0]
        p[1] += step[1]
    #print(f"final_p {p} \n")
    return p


def check_collision_in_path(p, step):
    nrow = p[0]+step[0]
    ncol = p[1]+step[1]

    #print(f"stepping from {p} using step {step} to {[nrow,ncol]}")
    if nrow >= 0 and nrow < sample_height - 1 \
            and ncol >= 0 and ncol < sample_width - 1 \
            and grid[nrow][ncol] == 0:
        return False
    return True


def load_crystal(k, h):
    # setting up file path

    dirname = os.path.dirname(__file__)
    #dirname = "/content/drive/MyDrive/statistische"
    filepath = os.path.join(
        dirname, f'data/material_S={adhesion_prob}_f={concentration}/')

    grid.clear()
    with open(f'{filepath}mat_{k}.txt', 'r') as file:
        height = 1
        for line in file:
            row = []
            if height > 1 and height < h:
                for char in line:
                    if not char == '\n':
                        row.append(int(char))
            else:
                row = np.zeros(sample_width, dtype=int)
            grid.append(np.array(row))
            height += 1


def init_results(d):
    res = {}
    for i in range(min_slice_height, d + 1):
        res[i] = 0
    return res


def init_plot(keys, norms):
    plt.figure(figsize=(60, 30))
    plt.xlabel('Sample Thickness', fontsize=50)
    plt.xticks(fontsize=40)
    plt.yticks(fontsize=40)
    plt.ylabel('Transfer probablity', fontsize=50)
    plt.xlim(-0.5, len(keys)-.5)

    plt.bar(range(len(keys)), norms, tick_label=keys, width=0.9)
    return plt.gcf()


def print_grid():
    for i in range(len(grid)):
        print(grid[i])


def print_grid_to_file(k, d, clean_file=True):
    global adhesion_prob
    global concentration

    dirname = os.path.dirname(__file__)
    #dirname = ""
    filepath = os.path.join(
        dirname, f'test_flow_material_S={adhesion_prob}_f={concentration}/sample_{k}/')

    # creating dir
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(f'{filepath}flow_cleaned.txt', 'w') as file:
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if not grid[i][j] == 0:
                    file.write(str(grid[i][j]))
                else:
                    file.write(" ")
            file.write("\n")

    with open(f'{filepath}flow.txt', 'w') as file:
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                file.write(str(grid[i][j]))
            file.write("\n")


def save_plot(fig):
    #dirname = os.path.dirname(__file__)
    dirname = ""
    filepath = os.path.join(
        dirname, f'/content/drive/MyDrive/statistische/sp_transfer_plots/adh_prob_{adhesion_prob}/bias_{a_up}/thickness_{max_slice_height}/ensemble_{ensemble_size}/')

    # creating dir
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    fig.savefig(f'{filepath}steps_{simulated_steps}.png', dpi='figure')


def save_plot_data(res, norm):
    #dirname = os.path.dirname(__file__)
    dirname = ""
    filepath = os.path.join(
        dirname, f'/content/drive/MyDrive/statistische/sp_transfer_plots/adh_prob_{adhesion_prob}/bias_{a_up}/thickness_{max_slice_height}/ensemble_{ensemble_size}/')
    keys = list(res.keys())
    vals = list(res.values())

    # creating dir
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(f'{filepath}steps_{simulated_steps}.csv', 'w') as file:
        for i in range(len(keys)):
            file.write(f'{keys[i]};{vals[i]};{norm[i]}\n')


if __name__ == "__main__":
    main()
