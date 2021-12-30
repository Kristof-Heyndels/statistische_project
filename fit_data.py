import os
import pandas
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#Data parameters
adh_prob = 1
thickness = 50
ensemble = 100
simulated_steps = 1000
bias_min = 0.12
bias_max = 0.50

def main():
    b = bias_min
    while b <= bias_max:
        bias = "{:#.2g}".format(b)
        df = load_data(bias)
        x = np.array(df['sample_width'])  
        y = np.array(df['norm_counts'])

        popt, pcov = curve_fit(func, x, y, bounds=([0.9999999,-1,0],[1,0,50]))        
        plt.plot(x, func(x, *popt), label=f"bias {bias}") 

        b += 0.02
        b = np.round(b, 2) 

    save_plot(init_plot())


def func(x, l, k, x_0):
    return l / (1 + np.exp(-k * (x - x_0)))


def load_data(b):
    # setting up file path
    dirname = os.path.dirname(__file__)
    #dirname = "/content/drive/MyDrive/statistische"
    filepath = os.path.join(
        dirname, f'sp_transfer_plots/adh_prob_{adh_prob}/bias_{b}/thickness_{thickness}/ensemble_{ensemble}/')

    with open(f'{filepath}steps_{simulated_steps}.csv', 'r') as file:
        return pandas.read_csv(file, delimiter = ';', names=['sample_width', 'counts', 'norm_counts'])
        

def init_plot():
    plt.gcf().set_size_inches(60, 30)
    plt.xlabel('Sample Thickness', fontsize='50')
    plt.ylabel('Transfer Probability', fontsize='50')    
    plt.xticks(fontsize=40)
    plt.yticks(fontsize=40)
    plt.legend(fontsize=40)

    return plt.gcf()


def save_plot(fig):
    dirname = os.path.dirname(__file__)
    #dirname = "/content/drive/MyDrive/statistische"
    filepath = os.path.join(
        dirname, f'sp_transfer_plots/adh_prob_{adh_prob}/')

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