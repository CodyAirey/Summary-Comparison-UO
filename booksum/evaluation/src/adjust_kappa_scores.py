import pandas as pd
import numpy as np
import os

def adjust_kappa_tables_floor_ceil(dataset):
    for (dirpath, dirnames, filenames) in os.walk(f"../csv_results/krippendorff/{dataset}"):
        for file in filenames:
            dfin = pd.read_csv(f"{dirpath}/{file}")
            
            for row_index, row in dfin.iterrows():
                for col_index, value in row.items():
                    if isinstance(value, float):
                        if np.isnan(value):
                            continue
                        if value < .2:
                            value = 0.0
                        else:
                            value = 1.0
                        dfin.loc[row_index, col_index] = value
            
            dfin.to_csv(f"{dirpath}/adjusted_results/{file}")
            
