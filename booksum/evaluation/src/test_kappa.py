import json
import pathlib
import sys
import csv
import pandas as pd
import copy
import numpy as np
from disagree import metrics
from IPython.display import display
# from disagree.metrics import Krippendorff
# from disagree.metrics import Metrics

# metdf = pd.read_csv("../csv_results/kappa_results/shmoop-section-rouge1n-sentence-max-scores-threshold-adjusted.csv")
# metdf2 = pd.read_csv("../csv_results/kappa_results/mini_test_prefix.csv", index_col=0)
# bigdf = pd.read_parquet("../csv_results/kappa_results/shmoop-section-rouge1n-sentence-max-scores-threshold-adjusted.parquet")



test_annotations = {"a": [None, None, None, None, None, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, None, 1.0],
                    "b": [0.0, None, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, None, None, None, None, None, None, None],
                    "c": [None, None, 1.0, 0.0, 1.0, 0.0, 0.0, None, 1.0, 0.0, 0.0, 1.0, 1.0, None, 0.0]}
df = pd.DataFrame(test_annotations)

print(df)
mets = metrics.Metrics(df)
fleiss = mets.fleiss_kappa()
print("Fleiss kappa: {:.2f}".format(fleiss))




metdf = pd.read_csv("../csv_results/kappa_results/mini_test.csv", index_col=0)
# metdf = metdf.replace(np.nan, None)

print(metdf)
kripp = metrics.Krippendorff(metdf)
alpha = kripp.alpha(data_type="ratio")
print("Krippendorff's alpha: {:.2f}".format(alpha))


# print(metdf2)
# mets = metrics.Metrics(metdf2)
# fleiss = mets.fleiss_kappa()
# print("Fleiss kappa: {:.2f}".format(fleiss))




# test = {"a": [None, None, None, None, None, 2, 3, 0, 1, 0, 0, 2, 2, None, 2],
#                     "b": [0, None, 1, 0, 2, 2, 3, 2, None, None, None, None, None, None, None],
#                     "c": [None, None, 1, 0, 2, 3, 3, None, 1, 0, 0, 2, 2, None, 3]}

# df_test = pd.DataFrame(test)

# mets = metrics.Metrics(df_test)
# fleiss = mets.fleiss_kappa()
# fleiss = float("{:.3f}".format(fleiss))

# print(fleiss)