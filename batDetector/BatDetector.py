from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

from Celldata import Celldata
import time
import multiprocessing as mp
import statistics

from os.path import join
from pathlib import Path
from constants import *
from helper import interpolate_cell_data, interpolate_halfcell, interpolate, normalize
from scipy import optimize
from parser import read_cell_data_csv
from sklearn.metrics import root_mean_squared_error as rmse
from scipy.interpolate import CubicSpline as CSP

"""
Data Section
"""
anodes_dir = r"../halfCellAnodes"
cathodes_dir = r"../halfCellCathodes"
ocv_dir = r"../iOCVData"
results_dir = r"../results"
cwd = Path.cwd()

num_data_points = 100
use_thread = 12

def objective(initial_guess, full_cell: Celldata, half_cell_anode: Celldata, half_cell_cathode: Celldata,
              plot: bool = False):
    """
    Calculates the root mean squared error (RMSE) between the full-cell iOCV data
    and a simulated curve generated from the provided half-cell anode and cathode data.

    Args:
        initial_guess (list): A list of four floats representing the initial guess
                            for the optimization parameters. These parameters
                            control the scaling of the half-cell anode and cathode data
                            to best fit the full-cell iOCV data.
        full_cell (Celldata): A Celldata object representing the full-cell iOCV data.
        half_cell_anode (Celldata): A Celldata object representing the half-cell anode data.
        half_cell_cathode (Celldata): A Celldata object representing the half-cell cathode data.
        plot (bool, optional): If True, the function will plot the full-cell iOCV
                              data, the fitted anode and cathode curves, and the simulated
                              full-cell curve. Defaults to False.

    Returns:
        float: The RMSE between the full-cell iOCV data and the simulated curve.
    """


    bounds_delta = 0.1
    # Set initial guess if not provided
    if initial_guess is None:
        initial_guess = [0.0, 0.95, 0.01, 0.99]

    # Check if the anode and cathode bounds are large enough.
    if (initial_guess[1] - initial_guess[0]) < bounds_delta:
        return -1
    if (initial_guess[3] - initial_guess[2]) < bounds_delta:
        return -1

    # Make copies of the original data to avoid modifying the input data
    orig_full = full_cell.get_data().copy(deep=True)
    interpolate_cell_data([full_cell], num_data_points)
    full_cell_df = full_cell.get_data()

    orig_half_anode = half_cell_anode.get_data().copy(deep=True)
    interpolate_cell_data([half_cell_anode], num_data_points, bounds=initial_guess[:2])
    half_cell_anode_df = half_cell_anode.get_data()

    orig_half_neg = half_cell_cathode.get_data().copy(deep=True)
    interpolate_cell_data([half_cell_cathode], num_data_points, bounds=initial_guess[-2:])
    half_cell_cathode_df = half_cell_cathode.get_data()

    # Calculate the RMSE between the full-cell iOCV data and the simulated curve
    error = rmse(full_cell_df[VOLTAGE], (half_cell_cathode_df[VOLTAGE] - half_cell_anode_df[VOLTAGE]))

    # Plotting if desired
    if plot:
        ax = full_cell_df.plot(x=SOC, y=VOLTAGE, label='iOCV')
        ax.set_title(
            f"{full_cell.get_composition()} \n{half_cell_anode.get_composition()} \n{half_cell_cathode.get_composition()}")
        half_cell_cathode_df.plot(ax=ax, x=LITHIATION, y=VOLTAGE, label="neg-fitted")
        half_cell_anode_df.plot(ax=ax, x=LITHIATION, y=VOLTAGE, label="post-fitted")
        simulated_df = pd.DataFrame(
            {
                SOC: (full_cell_df[SOC]),
                VOLTAGE: (half_cell_cathode_df[VOLTAGE] - half_cell_anode_df[VOLTAGE])
            }
        )
        simulated_df.plot(ax=ax, x=SOC, y=VOLTAGE, label="simulated")
        plt.show()
        plt.close()

    # Restoring original data for reusability
    full_cell.set_data(orig_full)
    half_cell_anode.set_data(orig_half_anode)
    half_cell_cathode.set_data(orig_half_neg)

    return error


def worker(cell_i_ocv, cell_anode, cell_cathode, methode):
    # Performs optimization to fit half-cell data to full-cell iOCV data.
    # Minimizes the root mean squared error (RMSE) using the specified optimization method.
    result = optimize.minimize(objective,
                               x0=np.array([0.01, 0.99, 0.01, 0.99]),
                               args=(cell_i_ocv, cell_anode, cell_cathode),
                               bounds=[(0, 0.2), (0.7, 1), (0, 0.4), (0.7, 1)],
                               method=methode)

    # Creates a DataFrame to store results.
    result_df = pd.DataFrame(
        {
            RMSE: [result.fun * 1000],  # RMSE value scaled to mV
            FULLCELL: [cell_i_ocv.get_composition()],
            HANODE: [cell_anode.get_composition()],
            HCATH: [cell_cathode.get_composition()],
            SOL: [result.x]
        })

    # Checks if the optimization was successful.
    if result.success:
        # TODO: Consider uncommenting the plotting commented code if needed
        # objective(result.x, cell_i_ocv, cell_anode, cell_cathode, True)
        return result_df
    else:
        return pd.DataFrame()


def get_material(tot_full_cap,df_user_ocv: [pd.DataFrame], cell_name: [str], methode: str, plot_title:bool):
    """
    This function performs a multi-threaded calculation to fit half-cell data
    to full-cell iOCV data, minimizing the root mean squared error (RMSE).

    Args:
        df_user_ocv (pd.DataFrame): iOCV data for full cells
        cell_name (list): List of names corresponding to each full-cell.
        methode (str):  Name of the optimization algorithm to use.
        delta (float, optional): A value representing the step size used in
                                interpolation. Defaults to 0.1 (Not Used)
        parameter_guess (list, optional): Initial guess for the optimization
                                          parameters. Defaults to [0.1, 0.99, 0.99, 0.01].

    Returns:
        pd.DataFrame: dataframe containing the optimised parameters and corresponding RMSE values.
    """

    # Construct file paths for anode, cathode, and results directories
    path_anodes = (cwd / anodes_dir).resolve()
    path_cathodes = (cwd / cathodes_dir).resolve()
    path_results = (cwd / results_dir).resolve()

    # Load the half-cell anode and cathode data
    halfcell_anodes = read_cell_data_csv(path_anodes, True, True)
    halfcell_cathodes = read_cell_data_csv(path_cathodes, True, False)

    # Check if the number of full-cell iOCV datasets and cell names matches
    if len(df_user_ocv) != len(cell_name):
        raise Exception("name count does not match dataframe count, check input arrays\n"
                        f"dataframe count was:{len(df_user_ocv)}, cell name array count was:{len(cell_name)}")

    # Create Celldata objects for each full-cell iOCV dataset
    ocv_cells = [Celldata(name, df, False, False) for df in df_user_ocv for name in cell_name]

    # Initialize an empty dataframe to store the results
    result_df = pd.DataFrame(
        {
            RMSE: [],
            FULLCELL: [],
            HANODE: [],
            HCATH: []
        }
    )

    # Generate a list of tuples, each tuple representing a task for multiprocessing
    tasks = [(ocv_cell, cell_anode, cell_cathode, methode)
             for ocv_cell in ocv_cells
             for cell_anode in halfcell_anodes
             for cell_cathode in halfcell_cathodes]

    # Create a multiprocessing pool with the number of workers defined in 'use_thread'
    pool = mp.Pool(use_thread)

    # Apply the 'worker' function to each task in parallel
    for result in pool.starmap(worker, tasks):
        result_df = pd.concat([result_df, result], ignore_index=True)

    # Close the pool and wait for all tasks to complete
    pool.close()
    pool.join()

    # Save the results to a CSV file with a timestamp in the filename
    fname = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    result_df.to_csv(join(path_results, fname + methode + ".csv"))

    #  Find the index of the row with the minimum RMSE for each full-cell
    idx = result_df.groupby(FULLCELL)[RMSE].idxmin()


    best_fit: pd.DataFrame = result_df.loc[idx].reset_index()
    best_fit.reset_index(inplace=True)

    #print Match, Cell Information
    print(f"RMSE: {str(np.round(best_fit[RMSE].loc[0], decimals=4))} mV")
    print(f"Match: Anode:{best_fit[HANODE].loc[0]} Cathode:{best_fit[HCATH].loc[0]}")
    print(f"Solution: {[str(np.round(elem, decimals=4)) for elem in best_fit[SOL].loc[0]]}")




    def get_fitted(data_anode,data_cathode, sol):
        anode_interp=interpolate(data_anode,colm=LITHIATION, voltage_col=VOLTAGE,steps=100,bounds=sol[:2])
        cathode_interp = interpolate(data_cathode,colm=LITHIATION, voltage_col=VOLTAGE, steps=100, bounds=sol[-2:])
        return anode_interp,cathode_interp

    def get_norm_halfcell(data_anode: pd.DataFrame,data_cathode: pd.DataFrame):
        return ((data_anode[LITHIATION] - data_anode[LITHIATION].min()) / (data_anode[LITHIATION].max() - data_anode[LITHIATION].min())
                ,(data_cathode[LITHIATION] - data_cathode[LITHIATION].min()) / (data_cathode[LITHIATION].max() - data_cathode[LITHIATION].min()))

    def get_scaling_offset(sol, full_cap):
        sol_1 = sol[:2]  # anode, negEl
        sol_2 = sol[-2:]  # cathode, posEl

        a_1 = np.array([[sol_1[0], 1], [sol_1[1], 1]])
        b_1 = np.array([0, 1])
        x_1 = np.linalg.solve(a_1, b_1)  # alpha_an,beta_an

        a_2 = np.array([[sol_2[0], 1], [sol_2[1], 1]])
        b_2 = np.array([0, 1])
        x_2 = np.linalg.solve(a_2, b_2)  # alpha_cat,beta_cat

        an_cap = full_cap / (sol_1[1] - sol_1[0])
        cat_cap = full_cap / (sol_2[1] - sol_2[0])

        print(f"Anode alpha_an,beta_an = {x_1}")
        print(f"Cathode alpha_cat,beta_cat = {x_2}")
        print(f"an_cap={an_cap} mAh, cat_cap={cat_cap} mAh")
        return x_1, x_2

    def plot_data(user_ocv,anode_ocp,cathode_ocp,x_an,x_cat):

        ax = user_ocv.plot(x=SOC,y=VOLTAGE, label="iOCV",figsize=(8, 6))
        ax.grid()
        anode_ocp[LITHIATION], cathode_ocp[LITHIATION] = get_norm_halfcell(anode_ocp, cathode_ocp)

        cat_x_new=np.linspace(cathode_ocp[LITHIATION].min(),cathode_ocp[LITHIATION].max(),num_data_points)
        cat_spl=CSP(cathode_ocp[LITHIATION],cathode_ocp[VOLTAGE])
        cathode_ocp=pd.DataFrame({
            LITHIATION:cat_x_new,
            VOLTAGE:cat_spl(cat_x_new)
        })

        cathode_ocp[LITHIATION] = cathode_ocp[LITHIATION].apply(lambda x: x_cat[0]*x+x_cat[1])
        cathode_ocp.plot(ax=ax, x=LITHIATION, y=VOLTAGE, label="Cathode")

        an_x_new = np.linspace(anode_ocp[LITHIATION].min(), anode_ocp[LITHIATION].max(), num_data_points)
        an_spl = CSP(anode_ocp[LITHIATION], anode_ocp[VOLTAGE])
        anode_ocp = pd.DataFrame({
            LITHIATION: an_x_new,
            VOLTAGE: an_spl(an_x_new)
        })

        anode_ocp[LITHIATION] = anode_ocp[LITHIATION].apply(lambda x: x_an[0] * x + x_an[1])
        anode_ocp.plot(ax=ax, x=LITHIATION, y=VOLTAGE, label="Anode")

        anode_sol, cathode_sol = get_fitted(anode_data, cath_data, best_fit[SOL].loc[0])
        simulated_df = pd.DataFrame(
            {
                SOC: (np.linspace(0,1,num_data_points)),
                VOLTAGE: (cathode_sol[VOLTAGE] - anode_sol[VOLTAGE])
            }
        )
        simulated_df.plot(ax=ax, x=SOC, y=VOLTAGE, label="simulated",linestyle = 'dashed')
        ax.set_xlabel("SOC in %")
        ax.set_ylabel("Voltage in v")
        if plot_title:
            plt.title(f"iOCV Reconstruction\nAnode:{best_fit[HANODE].loc[0]} \nCathode:{best_fit[HCATH].loc[0]}")
        plt.grid()

        #plt.show()
        plt.savefig(f"Match_{best_fit[FULLCELL].loc[0]}.png")
        print(f"LLI:  {round(anode_ocp[LITHIATION].loc[0],4)}")

    anode_idx=[idx for idx,obj in enumerate(halfcell_anodes) if obj.get_composition()==best_fit[HANODE].loc[0]]
    cathode_idx = [idx for idx,obj in enumerate(halfcell_cathodes) if obj.get_composition()==best_fit[HCATH].loc[0]]

    anode_data=halfcell_anodes[anode_idx[0]].get_data()
    cath_data=halfcell_cathodes[cathode_idx[0]].get_data()

    x_anode,x_cathode=get_scaling_offset(best_fit[SOL].loc[0],tot_full_cap)

    #plot the best-fitting result
    plot_data(df_user_ocv[0],anode_data,cath_data,x_anode, x_cathode)


def benchmark():
    runs = 15
    global use_thread
    threads = [8]
    use_thread = mp.cpu_count()
    #possible optimizers
    #["COBYLA", "COBYQA", "Nelder-Mead", "Powell", "TNC"]
    optimizers = ["COBYLA", "COBYQA", "Nelder-Mead", "Powell", "TNC"]
    time_vals = []

    df_lfp = pd.read_csv(r"G:\GitHub\Bachelor-Battery\iOCVData\TC23LFP01_CU_25deg.txt", sep=" ")
    df_nmc = pd.read_csv(r"G:\GitHub\Bachelor-Battery\iOCVData\TC23NMC01_CU_25deg.txt", sep=" ")
    # Open a file to store the benchmark results
    with open("times.txt", "a") as f:
        for thread_cnt in threads:
            f.flush()
            use_thread=thread_cnt
            f.write(f"CPU Count: {use_thread}\n")
            for optimizer in optimizers:
                print(f"Starting benchmark with {optimizer} and thread count {use_thread}")
                for i in range(runs):
                    start_time = time.time()
                    get_material([df_lfp], ["LFP"], optimizer)
                    end_time = time.time()

                    # Calculate the execution time and append it to the list
                    time_vals.append(end_time - start_time)
                    print(f"Run #{i}/{runs}")
                print(f"{optimizer}: {statistics.fmean(time_vals)}")

                # Write the benchmark result to the file

                f.write(f"{optimizer}: time:{statistics.fmean(time_vals)}\n")

                # Clear the list of execution times for the next run
                time_vals.clear()
            f.flush()

def calc_max_cpu():
    #this function limit cpu thread usage if cpu has less than 12 threads to prevent slowdown
    global use_thread
    if mp.cpu_count()<12:
        use_thread=mp.cpu_count()-3

if __name__ == "__main__":
    # possible optimizers
    # ["COBYLA", "COBYQA", "Nelder-Mead", "Powell", "TNC"]
    cell_cap=2000 #mAh
    calc_max_cpu()
    df_nmc= pd.read_csv(r"G:\GitHub\Bachelor-Battery\iOCVData\TC23LFP01_CU_25deg.txt", sep=" ")
    get_material(cell_cap,[df_nmc], ["LFP-HighV"], "COBYLA",False)