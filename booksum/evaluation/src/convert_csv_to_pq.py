import pandas as pd
import os
from pathlib import Path
import sys

"""
Converts all csv files located in booksum_summaries folder to parquet's. 
the csv versions remain. Only files with the .parquet extension will be converted.
"""

def csv_to_pq(dirpath, file):
    df = pd.read_csv((dirpath + "/" + file))
    newfilename = file.replace('.csv', '.parquet')
    df.to_parquet((dirpath + "/" + newfilename))


def compress_csvs():
    csv_folder_path = "../csv_results/booksum_summaries"

    for (dirpath, dirnames, filenames) in os.walk(csv_folder_path):
        for file in filenames:
            if Path(file).suffix == '.csv':
                csv_to_pq(dirpath, file)


def main(argv):
    compress_csvs()


if __name__ == "__main__":
    main(sys.argv)
