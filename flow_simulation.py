### FLOW ###

import numpy as np
import os
import time
import matplotlib.pyplot as plt

sample_count = 1
min_slice_height = 10
max_slice_height = 10
a_up_min = 0.12  # prob to move upwards, for a = 0.2 we have a_up = 2*a_remaining
a_up_max = 0.12
incoming_flow = 10
simulated_steps = 5 * pow(10, 3)

grid = []
concentration = 0.4
adhesion_prob = 1
sample_width = 250
sample_height = 15
starting_row = 1

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
    for k in range(sample_count):
        t_0 = time.time()
        for d in range(min_slice_height, max_slice_height + 1):
            global a_up_min
            a_up = a_up_min
            while a_up <= a_up_max:
                # init for t=0
                load_crystal(k, d)
                particles = []
                flux = []
                flow = []
                flux.append(incoming_flow / sample_width)
                flow.append(0)

                outgoing_particles = 0
                incoming_particles = incoming_flow

                for t in range(simulated_steps):
                    if (t % 100 == 0):
                        print(f"time: {t}")

                    outgoing_flow = outgoing_particles / (t + 1)
                    incoming_flow_adjusted = incoming_particles / (t + 1)

                    incoming_flux = incoming_flow_adjusted / sample_width
                    outgoing_flux = outgoing_flow / sample_width

                    flux.append(incoming_flux - outgoing_flux)
                    flow.append(outgoing_flow)

                    # each time step, n amount of particles enter the experiment
                    for n in range(incoming_flow):
                        particle, c = create_particle(sample_height - 1)
                        if c:
                            particles.append(particle)
                            incoming_particles += 1

                    # iterate over each particle, allowing it to take a single step
                    for i in range(len(particles)):
                        if i < len(particles):
                            p = particles[i]
                            grid[p[0]][p[1]] = 0
                            #print(f"====== \nmoving particle: {p} ... ")
                            p = step(p, a_up)
                            grid[p[0]][p[1]] = 9
                            #print(f"moved to {p} \n======")
                            if p[0] == 0:
                                grid[p[0]][p[1]] = 0
                                outgoing_particles += 1
                                particles[i] = particles[len(particles) - 1]
                                particles.pop()
                        else:
                            break

                save_data(flow, flux, "{:#.2g}".format(a_up), d)
                save_plot(init_plot(flow, flux), "{:#.2g}".format(a_up), d)
                a_up += 0.02
                a_up_min = np.round(a_up_min, 2)

            #print_grid_to_file(k, d)

        # guesstimating eta
        times.append(time.time() - t_0)
        avg = sum(times) / (k+1)
        projected_total_duration = avg * sample_count
        estimated_eta = projected_total_duration - (k * avg)
        #print(f"{k}: Using a_up = {a_up}, simulation finish eta: {round(estimated_eta / 60)} minutes")


def create_particle(srow):
    scol = np.random.randint(0, sample_width, dtype=int)
    p = [srow, scol]
    if grid[srow][scol] == 0:
        return [p, True]
    return [[-1, -1], False]


def step(p, a_up):
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
    if nrow >= 0 and nrow < sample_height \
            and ncol >= 0 and ncol < sample_width \
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
            elif height > sample_height:
                break

            else:
                row = np.zeros(sample_width, dtype=int)
            grid.append(np.array(row))
            height += 1


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


def save_data(flow, flux, b, d):
    t = range(simulated_steps + 1)

    dirname = os.path.dirname(__file__)
    #dirname = "/content/drive/MyDrive/statistische"
    filepath = os.path.join(
        dirname, f'flow_plots/bias_{b}/sample_thickness_{d}/')

    # creating dir
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(f'{filepath}flow_flux.csv', 'w') as file:
        file.write('t;flow;flux\n')
        for i in t:
            file.write(f'{t[i]};{flow[i]};{flux[i]}\n')

# dummy function to hold example code


def init_plot(flow, flux):
    col1 = 'steelblue'
    col2 = 'red'

    fig, ax = plt.subplots()
    fig.set_size_inches(60, 30)

    ax.scatter(range(simulated_steps + 1), flow, s=80,
               facecolors='none', edgecolors='b')
    ax2 = ax.twinx()
    ax2.scatter(range(simulated_steps + 1), flux, s=80,
                facecolors='none', edgecolors='r')

    ax.set_xlabel('Time', fontsize=70)
    ax.set_ylabel('Flow', color=col1, fontsize=70)
    ax2.set_ylabel('Flux', color=col2, fontsize=70)

    ax.tick_params(axis='x', labelsize=40)
    ax.tick_params(axis='y', labelsize=40)
    ax2.tick_params(axis='y', labelsize=40)

    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)

    return fig


def save_plot(fig, b, d):
    dirname = os.path.dirname(__file__)
    #dirname = "/content/drive/MyDrive/statistische"
    filepath = os.path.join(
        dirname, f'flow_plots/bias_{b}/sample_thickness_{d}/')
    # creating dir
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    fig.savefig(f'{filepath}flow_flux_scatter.png', dpi='figure')


if __name__ == "__main__":
    main()
