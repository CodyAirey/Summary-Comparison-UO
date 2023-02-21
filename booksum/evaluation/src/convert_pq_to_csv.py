import pandas as pd
import os
from pathlib import Path
import sys

"""
Converts all parquet files located in booksum_summaries folder to csvs. 
the Parquet versions remain. Only files with the .csv extension will be converted.
"""

def pq_to_csv(dirpath, file):
    df = pd.read_parquet((dirpath + "/" + file))
    newfilename = file.replace('.parquet', '.csv')
    df.to_csv((dirpath + "/" + newfilename))

def convert_files():
    pq_folder_path = "../csv_results/booksum_summaries"

    for (dirpath, dirnames, filenames) in os.walk(pq_folder_path):
        for file in filenames:
            if Path(file).suffix == '.parquet':
                pq_to_csv(dirpath, file)

                
def main(argv):
    convert_files()


if __name__ == "__main__":
    main(sys.argv)
