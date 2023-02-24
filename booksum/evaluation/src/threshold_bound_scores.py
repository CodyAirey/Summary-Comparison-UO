import pandas as pd
import numpy as np
import os
import pathlib

# for gather_files()
fixed_files = []
adjusted_files = []
datasets = ("adjusted", "fixed")

#for gather_ids() 
adjusted_ids = {}
fixed_ids = {}


def gather_files():
    #collect all line_by_line files created
    for dataset in datasets:
        for root, dirs, files in os.walk(f"../csv_results/booksum_summaries/{dataset}/line_by_line_section_to_book"):
            for file in files:
                if Path(file).suffix == ".parquet":
                    if dataset == "fixed":
                        fixed_files.append(file)
                    else:
                        adjusted_files.append(file)

    print(f"Adjusted:\n{adjusted_files}")
    print(f"Fixed:\n{fixed_files}")



#Collect Unique ID's
def gather_ids():
    tempdf = pd.read_parquet(f"../csv_results/booksum_summaries/adjusted/line_by_line_section_to_book/{adjusted_files[0]}")
    for index, row in tempdf.iterrows():

        custom_id = row['Section Title'] + ", " + row['Reference Source'] + ", sentence: " + row['Reference Sentence Index']
        adjusted_ids[custom_id] = custom_id

    tempdf = pd.read_parquet(f"../csv_results/booksum_summaries/fixed/line_by_line_section_to_book/{fixed_files[0]}")
    for index, row in tempdf.iterrows():

        custom_id = row['Section Title'] + ", " + row['Reference Source'] + ", sentence: " + row['Reference Sentence Index']
        fixed_ids[custom_id] = custom_id 


def create_new_df_based_on_meanf1_threshold(df):
    #calculate threshold based on the meanf1 score for current metric
    f1_title = df.columns[5]
    threshold = np.mean(df[f1_title])

    # groupby reference sentence, source, and section title
    grouped = df.groupby(['Section Title', 'Reference Source', 'Hypothesis Source', 'Reference Sentence Index'])

    # initialize new dataframe
    new_df = pd.DataFrame(columns=['Section Title', 'Reference Source', 'Hypothesis Source', 'Reference Sentence Index', 'Threshold Based F1 Score'])

    # loop over groups
    for name, group in grouped:
        # get f1 scores above threshold
        f1_scores = group[group['f1score'] > threshold]['f1score']
        # calculate new f1 score as average of f1 scores above threshold
        new_f1 = f1_scores.mean()
        # add row to new dataframe
        new_df = new_df.append({'Section Title': name[0], 'Reference Source': name[1], 'Hypothesis Source': name[2], 'Reference Sentence Index': name[3], 'Threshold Based F1 Score': new_f1}, ignore_index=True)




def tester(df):
    #calculate threshold based on the meanf1 score for current metric
    f1_title = df.columns[5]
    threshold = np.mean(df[f1_title])
    avg_f1 = "NA"

    # Initialize new dataframe
    new_df = pd.DataFrame(columns=['Section Title', 'Source', 
                                'Reference Sentence Index', 'Hypothesis Sentence Indexes used', 'New F1 Score'])

    # Loop over unique combinations of columns and calculate average new F1 score
    for idx, group in df.groupby(['Section Title', 'Source', 
                                'Reference Sentence Index', 'Hypothesis Sentence Index']):
        avg_f1 = group.loc[group[avg_f1] > threshold][f1_title].mean()
        if pd.notnull(avg_f1):
            new_row = {'Section Title': idx[0],
                    'Source': idx[1],
                    'Reference Sentence Index': idx[2],
                    'Hypothesis Sentence Indexes used': idx[3],
                    'New F1 Score': avg_f1}
            new_df = new_df.append(new_row, ignore_index=True)

    # Save new dataframe to CSV file
    new_df.to_csv('new_df.csv', index=False)


# df = pd.read_parquet(pathlib.Path("../csv_results/fixed/booksum_summaries/fixed/line_by_line_section_to_book/fixed-section-to-book-comparison-results-all-rouge-1n-lbl.parquet"))
df = pd.read_csv("../csv_results/booksum_summaries/fixed/line_by_line_section_to_book/fixed-section-to-book-comparison-results-all-rouge-l-lbl.csv")
tester(df)


# custom_ids = {} #silly but it works, ordered + hashed
# for index, row in df.iterrows():
#     if row['Reference Source'] == source:
#         custom_id = row['Section Title'] + ", sentence-" + str(row['Reference Sentence Index'])
#         custom_ids[custom_id] = custom_id

# for e in custom_ids.keys():
#     print(e)booksum/evaluation/csv_results/booksum_summaries/fixed/line_by_line_section_to_book/fixed-section-to-book-comparison-results-all-rouge-l-lbl.parquet