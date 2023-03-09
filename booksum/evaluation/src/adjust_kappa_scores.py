import pandas as pd
import numpy as np
import os

# metdf = pd.read_csv("../csv_results/kappa_results/shmoop-section-rouge1n-sentence-max-scores.csv", index_col=0)

# display(metdf.describe())
# x = 0
# for row_index, row in metdf.iterrows():
#     for col_index, value in row.items():
#         if isinstance(value, float):
#             if np.isnan(value):
#                 continue
#             if value < .2:
#                 value = 0.0
#             else:
#                 value = 1.0
#             metdf.loc[row_index, col_index] = value
#             x += 1

# print(metdf)


# metdf.to_parquet("../csv_results/kappa_results/shmoop-section-rouge1n-sentence-max-scores-threshold-adjusted.parquet")
# # metdf.to_csv("../csv_results/kappa_results/shmoop-section-rouge1n-sentence-max-scores-threshold-adjusted.csv")


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
            
