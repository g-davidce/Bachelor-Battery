from datetime import datetime
from logging import fatal

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import Celldata
import time
import multiprocessing as mp

from os import listdir
from os.path import isfile, join
from pathlib import Path
from constants import LITHIATION, VOLTAGE, SOC, RMSE, FULLCELL, HANODE, HCATH, SOL
from helper import interpolate_cell_data
from scipy import optimize
from parser import read_halfcell_data_csv, read_cell_data_csv
from sklearn.metrics import root_mean_squared_error as rmse
from sklearn.metrics import mean_squared_error as mse
"""
Data Section
"""
anodes_dir = r"../halfCellAnodes"
cathodes_dir = r"../halfCellCathodes"
ocv_dir = r"../iOCVData"
results_dir=r"../results"
cwd = Path.cwd()

# define delta for steps
deltaSteps = 1
num_data_points = int(100 / deltaSteps)

def objective(initial_guess, full_cell: Celldata, half_cell_anode: Celldata, half_cell_cathode: Celldata,
              plot: bool = False):
    if initial_guess is None:
        initial_guess = [0.0, 0.95, 0.01, 0.99]

    orig_full = full_cell.get_data().copy(deep=True)
    interpolate_cell_data([full_cell], num_data_points)
    full_cell_df = full_cell.get_data()

    orig_half_anode = half_cell_anode.get_data().copy(deep=True)
    interpolate_cell_data([half_cell_anode], num_data_points, bounds=initial_guess[:2])
    half_cell_anode_df = half_cell_anode.get_data()

    orig_half_neg = half_cell_cathode.get_data().copy(deep=True)
    interpolate_cell_data([half_cell_cathode], num_data_points, bounds=initial_guess[-2:])
    half_cell_cathode_df = half_cell_cathode.get_data()

    error = rmse(full_cell_df[VOLTAGE], (half_cell_cathode_df[VOLTAGE] - half_cell_anode_df[VOLTAGE]))
    if plot :
        ax = full_cell_df.plot(x=SOC, y=VOLTAGE, label='iOCV')
        ax.set_title(
            f"{full_cell.get_composition()} \n{half_cell_anode.get_composition()} \n{half_cell_cathode.get_composition()}")
        half_cell_cathode_df.plot(ax=ax, x=LITHIATION, y=VOLTAGE, label="neg-fitted")
        half_cell_anode_df.plot(ax=ax, x=LITHIATION, y=VOLTAGE, label="post-fitted")
        simulated_df=pd.DataFrame(
            {
                SOC:(full_cell_df[SOC]),
                VOLTAGE:(half_cell_cathode_df[VOLTAGE]- half_cell_anode_df[VOLTAGE])
            }
        )
        simulated_df.plot(ax=ax, x=SOC, y=VOLTAGE, label="simulated")
        plt.show()
        plt.close()

    # restore data
    full_cell.set_data(orig_full)
    half_cell_anode.set_data(orig_half_anode)
    half_cell_cathode.set_data(orig_half_neg)
    return error


def worker(cell_i_ocv, cell_anode, cell_cathode):
    result = optimize.minimize(objective, x0=np.array([0.1, 0.99, 0.01, 0.99]),
                               args=(cell_i_ocv, cell_anode, cell_cathode),
                               bounds=[(0, 0.2), (0.95, 1), (0, 0.05), (0.95, 1)], method='Nelder-Mead')
    result_df=pd.DataFrame(
        {
            RMSE:[result.fun*1000],
            FULLCELL:[cell_i_ocv.get_composition()],
            HANODE:[cell_anode.get_composition()],
            HCATH:[cell_cathode.get_composition()],
            SOL:[result.x]
        })

    if result.success:
        #objective(result.x, cell_i_ocv, cell_anode, cell_cathode, True)
        return result_df
    else:
        return pd.DataFrame()


def calc_composition(delta: float = 0.1, order: int = 5, parameter_guess: [float] = [0.1, 0.99, 0.99, 0.01]):
    path_anodes = (cwd / anodes_dir).resolve()
    path_cathodes = (cwd / cathodes_dir).resolve()
    path_iocv = (cwd / ocv_dir).resolve()
    path_results = (cwd / results_dir).resolve()

    halfcell_anodes = read_cell_data_csv(path_anodes, True, True)
    halfcell_cathodes = read_cell_data_csv(path_cathodes, True, False)

    i_ocv_data = read_cell_data_csv(path_iocv, False, delimiter=" ")

    errors = pd.DataFrame(
        {
            RMSE: [],
            FULLCELL: [],
            HANODE: [],
            HCATH: []
        }
    )

    tasks = [(cell_i_ocv, cell_anode, cell_cathode) for cell_i_ocv in i_ocv_data for cell_anode in halfcell_anodes for
             cell_cathode in halfcell_cathodes]

    pool = mp.Pool(mp.cpu_count())
    for result in pool.starmap(worker, tasks):
        errors=pd.concat([errors, result], ignore_index=True)
    pool.close()
    pool.join()
    fname=datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    errors.to_csv(join(path_results,fname+".csv"))
    idx = errors.groupby(FULLCELL)[RMSE].idxmin()
    #plot best result
    best_fit:pd.DataFrame = errors.loc[idx].reset_index()
    best_fit.reset_index(inplace=True)
    cnt:int = 0
    for cell_i_ocv in i_ocv_data:
        for cell_anode in halfcell_anodes:
            for cell_cathode in halfcell_cathodes:
                if cnt > len(best_fit):
                    break
                if cell_i_ocv.get_composition() == best_fit.at[cnt,FULLCELL]:
                    if cell_anode.get_composition() == best_fit.at[cnt,HANODE]:
                        if cell_cathode.get_composition() == best_fit.at[cnt,HCATH]:
                            objective(best_fit.at[0,SOL],cell_i_ocv, cell_anode, cell_cathode, True)
                            cnt+=1

if __name__ == "__main__":
    start_time = time.time()
    calc_composition(order=5)
    end_time = time.time()
    print(end_time - start_time)
