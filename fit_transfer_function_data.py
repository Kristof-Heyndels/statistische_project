import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Data parameters
adh_prob = 1
concentration = 0.4
thickness = 50
ensemble = 100
simulated_steps = 1000
bias_min = 0.12
bias_max = 0.2


def main():
    b = bias_min
    k = (0, 50, 0)
    while b <= bias_max:
        bias = "{:#.2g}".format(b)
        df = load_data(bias)
        x = np.array(df['sample_width'])
        y = np.array(df['norm_counts'])

        popt, pcov = curve_fit(func_logistic, x, y, bounds=(
            [0.9999999, -1, 0], [1, 0, thickness]))
        save_fit_params(popt, bias)

        if popt[1] <= k[1]:
            k = (b, popt[1], popt[2])

        x = [x for x in range(500)]
        plt.plot(x, func_logistic(x, *popt), label=f"bias {bias}")

        b += 0.02
        b = np.round(b, 2)

    print(k)
    save_plot(init_plot())


def func_logistic(x, l, k, x_0):
    return l / (1 + np.exp(-k * (x - x_0)))


def load_data(b):
    # setting up file path
    dirname = os.path.dirname(__file__)
    #dirname = "/content/drive/MyDrive/statistische"
    filepath = os.path.join(
        
        dirname, f'sp_transfer_plots/adh_prob_{adh_prob}_concentration_{concentration}/bias_{b}/thickness_{thickness}/ensemble_{ensemble}/')

    with open(f'{filepath}steps_{simulated_steps}.csv', 'r') as file:
        return pd.read_csv(file, delimiter=';', names=['sample_width', 'counts', 'norm_counts'])


def save_fit_params(popt, b):
    dirname = os.path.dirname(__file__)
    #dirname = "/content/drive/MyDrive/statistische"
    filepath = os.path.join(
        dirname, f'sp_transfer_plots/adh_prob_{adh_prob}_concentration_{concentration}/bias_{b}/thickness_{thickness}/ensemble_{ensemble}/')

    # creating dir
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(f'{filepath}fit_for_steps_{simulated_steps}.csv', 'w') as file:
        file.write('l;k;x_0\n')
        file.write(f'{popt[0]};{popt[1]};{popt[2]}\n')


def init_plot():
    plt.gcf().set_size_inches(60, 30)
    plt.xlabel('Sample Thickness', fontsize='100')
    plt.ylabel('Transfer Probability', fontsize='100')
    plt.xticks(fontsize=80)
    plt.yticks(fontsize=80)
    plt.legend(fontsize=100)
    plt.gca().set_xlim(left=1, right=200)
    plt.gca().set_ylim(bottom=0)
    return plt.gcf()


def save_plot(fig):
    dirname = os.path.dirname(__file__)
    #dirname = "/content/drive/MyDrive/statistische"
    filepath = os.path.join(
        dirname, f'sp_transfer_plots/adh_prob_{adh_prob}_concentration_{concentration}/')

    # creating dir
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    fig.savefig(f'{filepath}fitted_curves.png', dpi='figure')


if __name__ == "__main__":
    main()
