import os
import numpy as np

sample_count = 10
concentration = 0.1
sample_width = 250
crystal_height = 400
grid = []

#sample_adh_probs = [1, 0.5, 0.1, 0.05, 0.02, 0.01]
sample_adh_probs = [1]


def main():
    for s in sample_adh_probs:
        phi = []
        lamda_max = []
        df = []
        for k in range(sample_count):
            load_crystal(k, s)
            curr_phi = calc_porosity()
            curr_lamda = calc_max_pore_diameter()
            curr_df = calc_fractial_dim(curr_phi, curr_lamda)

            phi.append(curr_phi)
            lamda_max.append(curr_lamda)
            df.append(curr_df)

        save_data(phi, lamda_max, df, sample_count, s)


def calc_porosity():
    ap = 0  # pore surface area
    at = sample_width * crystal_height  # total surface area
    for i in range(crystal_height):
        for j in range(sample_width):
            if grid[i][j] == 0:
                ap += 1
    return ap / at


def calc_max_pore_diameter():
    lamdas = []
    current_lambda = 0
    prev_cell = 0
    for i in range(len(grid)):
        for j in grid[i]:
            if j == 0:
                current_lambda += 1
            if j == 1 and prev_cell == 0:
                lamdas.append(current_lambda)
                current_lambda = 0
            prev_cell = j
    return max(lamdas)


def calc_fractial_dim(phi, l_max):
    return 2 - (np.log2(phi) / np.log2(1 / l_max))


def load_crystal(k, s):
    # setting up file path

    dirname = os.path.dirname(__file__)
    #dirname = "/content/drive/MyDrive/statistische"
    filepath = os.path.join(
        dirname, f'data/material_S={s}_f={concentration}/')

    grid.clear()
    with open(f'{filepath}mat_{k}.txt', 'r') as file:
        height = 2
        for line in file:
            row = []
            # shave off last 100 rows for consistent crystal structure
            if height > 1 and height < crystal_height - 100:
                for char in line:
                    if not char == '\n':
                        row.append(int(char))
            else:
                row = np.zeros(sample_width, dtype=int)
            grid.append(np.array(row))
            height += 1


def save_data(p, l, df, k, s):
    dirname = os.path.dirname(__file__)
    #dirname = ""
    filepath = os.path.join(
        dirname, f'data/material_S={s}_f={concentration}/')

    # creating dir
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(f'{filepath}porosity.csv', 'w') as file:
        file.write('sample;porosity;lambda_max;fractal_dimension\n')
        for i in range(len(p)):
            file.write(f'sample_{i};{p[i]};{l[i]};{df[i]};\n')
        file.write(f'avg;{sum(p) / k};{sum(l) / k};{sum(df) / k}')


if __name__ == "__main__":
    main()
