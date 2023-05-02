import json
import pathlib
import sys
import csv
import pandas as pd
import copy
import numpy as np
from disagree import metrics
import os
from pathlib import Path


book_files = []
section_files = []

def find__most_matched_source(dataset):
    number_of_matches = {
        "bookwolf"     : 0,
        "cliffnotes"   : 0,
        "gradesaver"   : 0,
        "novelguide"   : 0,
        "pinkmonkey"   : 0,
        "shmoop"       : 0,
        "sparknotes"   : 0,
        "thebestnotes" : 0
    }
    
    x = "chapter" if dataset == "section" else "book"

    f = open(pathlib.Path(f"../../alignments/{x}-level-summary-alignments/fixed_{dataset}_summaries_all.jsonl"), encoding='utf-8')

    for line in f:
        summary = json.loads(line)
        number_of_matches[summary['source']] += 1
    # for e in number_of_matches:
    #     print(e, number_of_matches[e])
    source = max(number_of_matches, key=number_of_matches.get)
    # print(source)
    return source


def find_related_lbl_files(dataset):
    csv_folder_path = f"../csv_results/booksum_summaries/fixed/line_by_line_{dataset}"
    for (dirpath, dirnames, filenames) in os.walk(csv_folder_path):
        # print(dirpath)
        for file in filenames:
            # print(file)
            if Path(file).suffix == ".csv":
                if dataset == "book":
                    book_files.append(file)
                elif dataset == "section":
                    section_files.append(file)
                    

def gather_sentence_ids(dataset, source):
    """Creates a list of sentences depending on dataset given (book or section) using the most correlated/matched source

    Args:
        dataset (str): 'book' or 'section'
        source (str): source used as reference in kripendoff alpha calculation

    Returns:
        list: list of sentence id's
    """
    df = "NA"
    if dataset == "book":
        title = "Book Title"
        df = pd.read_csv(f"../csv_results/booksum_summaries/fixed/line_by_line_{dataset}/{book_files[0]}")
    elif dataset == "section":
        title = "Section Title"
        df = pd.read_csv(f"../csv_results/booksum_summaries/fixed/line_by_line_{dataset}/{section_files[0]}")
    else:
        print("bad dataset/scope given!", file=sys.stderr)
        sys.exit(1)

    custom_ids = {}
    for index, row in df.iterrows():
        if row['Reference Source'] == source:
            custom_id = row[title] +" " + source + " sentence-" + str(row['Reference Sentence Index'])
            custom_ids[custom_id] = custom_id
        # if len(custom_ids) >= 10:
        #     break
        
    return list(custom_ids.keys())


def create_kappa_table(ids, source, infilename, dataset):
    """Creates a table of max f1scores for any unique sentence across all sourcesso that krippendorff scores can be calculated

    Args:
        ids (list): list of unique sentence ids
        source (str): main source to be compared against, will be most correlated source
        infilename (str): line-by-line file used to gather scores
        dataset (str): 'book' or 'section', denotes what scope is used
    """
    
    # print(ids) 
    #setup template for new df
    sources = ["bookwolf", "cliffnotes", "gradesaver", "novelguide", "pinkmonkey", "sparknotes", "thebestnotes", "shmoop"]
    
    for s in sources:
        if source == s:
            sources.remove(source)
    newdf = pd.DataFrame(columns=sources, index=ids)
    
    # print(newdf.head(20))

    filetitle = "AHHH"
    
    title = "Section Title" if dataset == "section" else "Book Title"
    
    #Grab title from lbl file to use in new krippendorff table name
    filename_split = infilename.split("-")
    # print(filename_split)
    for i, split in enumerate(filename_split):
        if split == "lbl.csv":
            filetitle = filename_split[i-1]

    #use lbl file as df
    filepath = f"../csv_results/booksum_summaries/fixed/line_by_line_{dataset}"
    df = pd.read_csv(f"{filepath}/{infilename}")
    f1_title = df.columns[6]

    #grab max f1 for any unique sentence for ref source
    for index, row in df.iterrows():
        if row['Reference Source'] == source:
            custom_id = row[title] + " " + source + " sentence-" + str(row['Reference Sentence Index'])
            if np.isnan(newdf.loc[custom_id, row["Hypothesis Source"]]):
                newdf.loc[custom_id, row["Hypothesis Source"]] = row[f1_title]
            newdf.loc[custom_id, row["Hypothesis Source"]] = max(newdf.loc[custom_id, row["Hypothesis Source"]], row[f1_title])

    #fill out values that have no scores
    newdf = newdf.fillna(value= np.nan)
    
    # Check if any column contains only NaN values
    
    try:
        cols_to_drop = []
        for col in newdf.columns:
            if newdf[col].isna().all():
                cols_to_drop.append(col)
    except:
        print(newdf.columns)

    # Drop the columns that contain only NaN values
    newdf = newdf.drop(cols_to_drop, axis=1)
    #note ^ This happens for a lot of book, as gradesaver is the most matched source, yet only matches with:
    # cliffnotes, sparknotes, and shmoop.
    
    #fix
    # newdf = newdf.fillna(value= np.nan)

    outfilename = f"{source}-{filetitle}-sentence-max-scores.csv"
    newdf.to_csv(f"../csv_results/krippendorff/{dataset}/{outfilename}", na_rep=np.nan)
    
    # print(newdf.head())


#Not actually sure this is good / works. uses set value of .2; doesn't work for all metrics 
# (pretty much only rouge). don't think it makes sense to use average and then ceil / floor based off of that.
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


def calculate_scores(dataset):
    """
    Reads CSV files from a directory specified by the `dataset` argument, calculates Krippendorff's alpha scores
    for each file, and saves the scores to a new CSV file in a subdirectory called "scores".
    
    Parameters:
    -----------
    dataset : str
        The name of the directory containing the CSV files.
    
    Returns:
    --------
    None
    """
    scores = {}
    for (dirpath, dirnames, filenames) in os.walk(f"../csv_results/krippendorff/{dataset}"):
        for file in filenames:
            df = pd.read_csv(f"{dirpath}/{file}", index_col=0)
            kripp = metrics.Krippendorff(df)
            alpha = kripp.alpha(data_type="ratio")
            scores[file] = alpha
    
    kripp_scores = pd.DataFrame(list(scores.items()), columns=["Source File", "Krippendorff Score"])
    filename = f"kripenndorff-alpha-scores-{dataset}.csv"
    kripp_scores.to_csv(f"../csv_results/krippendorff/scores/{filename}")
    
    
#why didin't I just use more global variables.
def main():
    
    # for dataset in ["section", "book"]:
    for dataset in ["book"]:
        source = find__most_matched_source(dataset)
        find_related_lbl_files(dataset)
        
        ids = gather_sentence_ids(dataset, source)

        files = section_files if dataset == "section" else book_files
        for file in files:
            create_kappa_table(ids, source, file, dataset)
            
            
        calculate_scores(dataset)

if __name__ == "__main__":
    main()