import sys
import pandas as pd
import numpy as np

def main(argv):
    
    mypath = argv[0]
    df = pd.read_csv(mypath, index_col=0)

    print(df)

    unique_sections = df['Section Title'].unique()
    metric = df.columns[5]

    meanscore = np.mean(df[metric])

    print(meanscore)

    filtered_df: pd.DataFrame = df[(df[metric]>=meanscore)]
    print(filtered_df)
    grouped_filtered_df = filtered_df.groupby(["Section Title", "Book Title", "Source"])
    grouped_filtered_df =  grouped_filtered_df.aggregate(np.mean).reset_index()

    print(grouped_filtered_df)

    print(meanscore)

if __name__ == "__main__":
    main(sys.argv[1:])