import pandas as pd
import numpy as np
import os
import pathlib

"""
File to create scores for the full summary, using the line-by-line scores calculated with calculate_all_f1s.sh (which runs the compare_{scope})

final scores for summary are either calculated using a threshold, which is found by finding the average score and taking all sentences above that.
or using the max sentence score for any one summary.

"""

# for gather_files()
fixed_files = {
    "line_by_line_book": [], 
    "line_by_line_section": [], 
    "line_by_line_section_to_book": []
}
adjusted_files = {
    "line_by_line_book": [], 
    "line_by_line_section": [], 
    "line_by_line_section_to_book": []
}

datasets = ("adjusted", "fixed")
threshold_scopes = ("full_summary_book_threshold", "full_summary_section_threshold", "full_summary_section_to_book_threshold")
max_scopes = ("full_summary_book_max", "full_summary_section_max", "full_summary_section_to_book_max")
lbl_scopes = ("line_by_line_book", "line_by_line_section", "line_by_line_section_to_book")

def gather_files(dataset):
    #collect all lbl csv files created
    for dataset in datasets:
        for scope in lbl_scopes:
            for root, dirs, files in os.walk(f"../csv_results/booksum_summaries/{dataset}/{scope}"):
                for file in files:
                    if pathlib.Path(file).suffix == ".csv":
                        if dataset == "fixed":
                            fixed_files[scope].append(file)
                        else:
                            adjusted_files[scope].append(file)

    for e in adjusted_files:
        print(f"Key:{e} - Adjusted,\n {adjusted_files[e]}\n")
    for e in fixed_files:
        print(f"Key:{e} - Fixed,\n {fixed_files[e]}\n")


def create_fullsum_threshold_s2b(df):
    """ Calculates the fullsummary threshold based scores for section to book files.

    Args:
        df (_type_): dataframe containing f1 scores for each line-by-line comparison

    Returns:
        _type_: _description_
    """
    #calculate threshold based on the meanf1 score for current metric
    f1_title = df.columns[5]
    threshold = np.mean(df[f1_title])
    avg_f1 = "NA"

    # Initialize new dataframe
    new_df = pd.DataFrame(columns=['Section Title', 'Source', 'Reference Sentence Index', 'Hypothesis Sentence Indexes used', 'Threshold F1 Score'])
    # Loop over unique combinations of columns and calculate average new F1 score
    for idx, group in df.groupby(['Section Title', 'Source', 'Reference Sentence Index']):
        avg_f1 = group.loc[group[f1_title] > threshold][f1_title].mean()
        hyp_indexes_used = list(group['Hypothesis Sentence Index'][group[f1_title] > threshold])
        
        if pd.notnull(avg_f1):
            new_row = {'Section Title': idx[0],
                    'Source': idx[1],
                    'Reference Sentence Index': idx[2],
                    'Hypothesis Sentence Indexes used': hyp_indexes_used,
                    'Threshold F1 Score': avg_f1}
            new_df = new_df.append(new_row, ignore_index=True)

    return new_df
    

def create_fullsum_max_s2b(df):
    """ Calculates the fullsummary max based scores for section to book files.

    Args:
        df (_type_): dataframe containing f1 scores for each line-by-line comparison

    Returns:
        new_df: dataframe containing the max scores for a each sentence usning given
    """
    
    #use customer user-made title for f1 score
    f1_title = df.columns[5]
    
    #setup new df for the max scores
    new_df = pd.DataFrame(columns=['Section Title', 'Book Title', 'Source', 'Reference Sentence Index', 'Hypothesis Sentence Index', 'Max F1 Score', 'Max Precision', 'Max Recall'])
    
    #group each sentence's scores and take the max
    for idx, group in df.groupby(['Section Title', 'Source', 'Reference Sentence Index']):
        highest_f1_row = group.loc[group[f1_title].idxmax()]
        # Create new row with only the columns we want and append to new_df (renamed)
        new_row = {
            'Section Title':  highest_f1_row['Section Title'], 
            'Book Title': highest_f1_row['Book Title'], 
            'Source':  highest_f1_row['Source'], 
            'Reference Sentence Index': highest_f1_row['Reference Sentence Index'], 
            'Hypothesis Sentence Index': highest_f1_row['Hypothesis Sentence Index'], 
            'Max F1 Score': highest_f1_row[f1_title], 
            'Max Precision': highest_f1_row['Precision'], 
            'Max Recall': highest_f1_row['Recall']
        }
        new_df = new_df.append(new_row, ignore_index=True)
    return new_df


def create_fullsum_threshold_section(df):
    """ Calculates the fullsummary threshold based scores for section files.

    Args:
        df (_type_): dataframe containing f1 scores for each line-by-line comparison

    Returns:
        _type_: _description_
    """
    #calculate threshold based on the meanf1 score for current metric
    f1_title = df.columns[5]
    threshold = np.mean(df[f1_title])
    avg_f1 = "NA"

    new_df = pd.DataFrame(columns=['Section Title', 'Reference Source', 'Hypothesis Source', 'Reference Sentence Index', 'Threshold F1 Score', 'Hypothesis Sentence Indexes Used']) 

    for idx, group in df.groupby(['Section Title', 'Reference Source', 'Hypothesis Source', 'Reference Sentence Index']):
        #group all rows with f1 score above
        avg_f1 = group.loc[group[f1_title] > threshold][f1_title].mean()
        hyp_indexes_used = list(group['Hypothesis Sentence Index'][group[f1_title] > threshold])
        
        if pd.notnull(avg_f1):
            new_row = {'Section Title': idx[0],
                    'Reference Source': idx[1],
                    'Hypothesis Source': idx[2],
                    'Reference Sentence Index': idx[3],
                    'Hypothesis Sentence Indexes Used': hyp_indexes_used,
                    'Threshold F1 Score': avg_f1}
            new_df = new_df.append(new_row, ignore_index=True)
    return new_df

def create_fullsum_max_section(df):
    """ Calculates the fullsummary max based scores for section files.

    Args:
        df (_type_): dataframe containing f1 scores for each line-by-line comparison

    Returns:
        _type_: _description_
    """
    f1_title = df.columns[5]
    print(f1_title)
    new_df = pd.DataFrame(columns=['Section Title', 'Reference Source', 'Hypothesis Source', 'Reference Sentence Index', 'Hypothesis Sentence Index', 'Max F1 Score']) 
    for idx, group in df.groupby(['Section Title', 'Reference Source', 'Hypothesis Source', 'Reference Sentence Index']):
        highest_f1_row = group.loc[group[f1_title].idxmax()]
        new_row = {
            'Section Title': highest_f1_row['Section Title'],
            'Reference Source': highest_f1_row['Reference Source'],
            'Hypothesis Source': highest_f1_row['Hypothesis Source'],
            'Reference Sentence Index': highest_f1_row['Reference Sentence Index'],
            'Hypothesis Sentence Index': highest_f1_row['Hypothesis Sentence Index'],
            'Max F1 Score': highest_f1_row[f1_title]
            }
        new_df = new_df.append(new_row, ignore_index=True)
    return new_df


def create_fullsum_max_book(df):
    """ Calculates the fullsummary max f1 score based scores for book files.

    Args:
        df (_type_): dataframe containing f1 scores for each line-by-line comparison

    Returns:
        _type_: _description_
    """
    f1_title = df.columns[5]
    new_df = pd.DataFrame(columns=["Book Title", "Reference Source", "Hypothesis Source", "Reference Sentence Index", "Hypothesis Sentence Index", "Max F1 Score"])
    for idx, group in df.groupby(["Book Title", "Reference Source", "Hypothesis Source", "Reference Sentence Index"]):
        highest_f1_row = group.loc[group[f1_title].idxmax()]
        new_row = {
            'Book Title': highest_f1_row['Book Title'],
            'Reference Source': highest_f1_row['Reference Source'],
            'Hypothesis Source': highest_f1_row['Hypothesis Source'],
            'Reference Sentence Index': highest_f1_row['Reference Sentence Index'],
            'Hypothesis Sentence Index': highest_f1_row['Hypothesis Sentence Index'],
            'Max F1 Score': highest_f1_row[f1_title]
        }
        new_df = new_df.append(new_row, ignore_index=True)
    return new_df


#note this code is the essentially the same as section version, but i kept them separate incase specific changes need/want to be made.
def create_fullsum_threshold_book(df):
    """ Calculates the fullsummary threshold based scores for book files.

    Args:
        df (_type_): dataframe containing f1 scores for each line-by-line comparison

    Returns:
        _type_: _description_
    """
    #calculate threshold based on the meanf1 score for current metric
    f1_title = df.columns[5]
    threshold = np.mean(df[f1_title])
    avg_f1 = "NA"

    new_df = pd.DataFrame(columns=['Book Title', 'Reference Source', 'Hypothesis Source', 'Reference Sentence Index', 'Threshold F1 Score', 'Hypothesis Sentence Indexes Used']) 

    for idx, group in df.groupby(['Book Title', 'Reference Source', 'Hypothesis Source', 'Reference Sentence Index']):
        avg_f1 = group.loc[group[f1_title] > threshold][f1_title].mean()
        hyp_indexes_used = list(group['Hypothesis Sentence Index'][group[f1_title] > threshold])
        
        if pd.notnull(avg_f1):
            new_row = {'Book Title': idx[0],
                    'Reference Source': idx[1],
                    'Hypothesis Source': idx[2],
                    'Reference Sentence Index': idx[3],
                    'Hypothesis Sentence Indexes Used': hyp_indexes_used,
                    'Threshold F1 Score': avg_f1}
            new_df = new_df.append(new_row, ignore_index=True)
    return new_df


def to_csv(df, filename, scope, dataset):
    # Save new dataframe to CSV file
    df.to_csv(f'../csv_results/booksum_summaries/{dataset}/{scope}/{filename}', index=False)

def main():

    gather_files(datasets)

    for dataset in datasets:
        if dataset == "adjusted":
            x = adjusted_files
        else:
            x = fixed_files
        for scope in x:
            for file in x[scope]:
                lbl_df = pd.read_csv(f"../csv_results/booksum_summaries/{dataset}/{scope}/{file}", index_col=0)
                
                if scope == lbl_scopes[0]: #book
                    max_df = create_fullsum_max_book(lbl_df)
                    threshold_df = create_fullsum_threshold_book(lbl_df)
                    to_csv(max_df, file, threshold_scopes[0], dataset)
                    to_csv(threshold_df, file, max_scopes[0], dataset)
                elif scope == lbl_scopes[1]: #section
                    max_df = create_fullsum_max_section(lbl_df)
                    threshold_df = create_fullsum_threshold_section(lbl_df)
                    to_csv(max_df, file, threshold_scopes[1], dataset)
                    to_csv(threshold_df, file, max_scopes[1], dataset)
                elif scope == lbl_scopes[2]: #S2B
                    max_df = create_fullsum_max_s2b(lbl_df)
                    threshold_df = create_fullsum_threshold_s2b(lbl_df)
                    to_csv(max_df, file, threshold_scopes[2], dataset)
                    to_csv(threshold_df, file, max_scopes[2], dataset)
                else:
                    NameError


if __name__ == "__main__":
    main()


# S2B
# df = pd.read_csv("../csv_results/booksum_summaries/fixed/line_by_line_section_to_book/fixed-section-to-book-comparison-results-all-rouge-l-lbl.csv", index_col=0)
# df = pd.read_csv("../csv_results/booksum_summaries/fixed/line_by_line_section_to_book/snippet.csv", index_col=0)
# new_df = create_fullsum_threshold_s2b(df)
# new_df = create_fullsum_max_s2b(df)


#SECTION
# df = pd.read_csv("../csv_results/booksum_summaries/fixed/line_by_line_section/fixed-section-comparison-results-all-rouge-1nsmall-lbl.csv", index_col=0)
# df = pd.read_csv("../csv_results/booksum_summaries/fixed/line_by_line_section/snippet.csv", index_col=0)
# new_df = create_fullsum_max_section(df)
# new_df = create_fullsum_threshold_section(df)

#BOOK
# df = pd.read_csv("../csv_results/booksum_summaries/fixed/line_by_line_book/fixed-book-comparison-results-all-rouge-1nsmall-lbl.csv", index_col=0)
# df = pd.read_csv("../csv_results/booksum_summaries/fixed/line_by_line_book/snippet.csv", index_col=0)
# new_df = create_fullsum_max_book(df)
# new_df = create_fullsum_threshold_book(df)

