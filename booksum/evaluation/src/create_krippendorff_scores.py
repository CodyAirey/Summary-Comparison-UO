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

    f = open(pathlib.Path(f"../../alignments/{dataset}-level-summary-alignments/fixed_{dataset}_summaries_all_final.jsonl"), encoding='utf-8')

    for line in f:
        summary = json.loads(line)
        number_of_matches[summary['source']] += 1
    for e in number_of_matches:
        print(e, number_of_matches[e])
    source = [i for i in number_of_matches if number_of_matches[i] == max(number_of_matches.values())][0]
    return source


def find_related_lbl_files(dataset):
    csv_folder_path = "../csv_results/booksum_summaries/fixed/line_by_line_{dataset}"
    for (dirpath, dirnames, filenames) in os.walk(csv_folder_path):
        for file in filenames:
            if Path(file.suffix) == ".csv":
                if dataset == "book":
                    book_files.append(file)
                elif dataset == "section":
                    section_files.append(file)

def gather_book_summary_sentences(dataset, source):
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
        df = pd.read_csv(f"../csv_results/booksum_summaries/fixed/line_by_line{dataset}/{book_files[0]}")
    elif dataset == "section":
        title = "Section Title"
        df = pd.read_csv(f"../csv_results/booksum_summaries/fixed/line_by_line{dataset}/{section_files[0]}")
    else:
        print("bad dataset/scope given!", file=sys.stderr)
        sys.exit(1)

    custom_ids = {} #silly but it works, ordered + hashed
    for index, row in df.iterrows():
        if row['Reference Source'] == source:
            custom_id = row[title] + ", sentence-" + str(row['Reference Sentence Index'])
            custom_ids[custom_id] = custom_id
        # if len(custom_ids) >= 10:
        #     break

    # print("Doneish")

    return custom_ids.keys()


def create_kappa_table(sentence_ids, df, source):
    
    sources = ["bookwolf", "cliffnotes", "gradesaver", "novelguide", "pinkmonkey", "sparknotes", "thebestnotes"]

    newdf = pd.DataFrame(index = sentence_ids, columns=sources)

    print(newdf.head)

    for index, row in df.iterrows():
        if row['Reference Source'] == source:
            custom_id = row['Section Title'] + ", sentence-" + str(row['Reference Sentence Index'])
            if np.isnan(newdf.loc[custom_id, row["Hypothesis Source"]]):
                newdf.loc[custom_id, row["Hypothesis Source"]] = row['rouge-1nscore']
            newdf.loc[custom_id, row["Hypothesis Source"]] = max(newdf.loc[custom_id, row["Hypothesis Source"]], row['rouge-1nscore'])

    ###TODO Figure out how / where to throw these tables (what information is required? base source, filename, scope/dataset, location to store, what to name file?)
    newdf = newdf.fillna(value= np.nan)
    newdf.to_csv("../csv_results/kappa_results/shmoop-section-rouge1n-sentence-max-scores.csv", na_rep=np.nan, index=False)


#TODO use these tables to make some results/scores.. figure out the best way to store these scores (all 1 file? or take too long to gather all?)