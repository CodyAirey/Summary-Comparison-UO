import pandas as pd
import numpy as np
from IPython.display import display

metdf = pd.read_csv("../csv_results/kappa_results/shmoop-section-rouge1n-sentence-max-scores.csv", index_col=0)

display(metdf.describe())
x = 0
for row_index, row in metdf.iterrows():
    for col_index, value in row.items():
        if isinstance(value, float):
            if np.isnan(value):
                continue
            if value < .2:
                value = 0.0
            else:
                value = 1.0
            metdf.loc[row_index, col_index] = value
            x += 1

print(metdf)


metdf.to_parquet("../csv_results/kappa_results/shmoop-section-rouge1n-sentence-max-scores-threshold-adjusted.parquet")
# metdf.to_csv("../csv_results/kappa_results/shmoop-section-rouge1n-sentence-max-scores-threshold-adjusted.csv")