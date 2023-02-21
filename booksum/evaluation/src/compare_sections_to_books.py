import numpy as np
import nltk
import math
from nltk import tokenize
import json
import sys
import getopt
import pathlib
import pandas as pd
import time

sys.path.append('source_modules')

chapter_summaries = dict()
book_summaries = dict()
threshold = .2 #threshold used as a cut-off when taking f1 scores
summary_comparison_data = [] #holds relevant information for each summary to summary calculation
line_by_line_data = [] #holds relevant information for each individual sentence to sentence calculation


# returns summaries located in scripts/finished_summaries
def get_human_summary(summary_path):
    """ Retrieves the summary text from the given path

    Args:
        summary_path (str): filepath to summary

    Returns:
        str: summary text
    """
    try:
        with open("../../scripts/" + summary_path, encoding='utf-8') as f:
            summary_json = json.load(f)
            return summary_json["summary"]
    except Exception as e:
        print("Failed to read summary file: {}".format(e))
        return None


def scan_chapter_summaries(split, dataset):
    """Gets each chapter summary and places all relevant info into a dictionary
    """
    f = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/{dataset}_chapter_summaries_{split}.jsonl"),
             encoding='utf-8')
    for line in f:
        summary = json.loads(line)
        summary_text = get_human_summary(summary['summary_path'])
        if summary_text is not None:
            try:
                chapter_summaries[summary['summary_path']] = {
                    "section_title": summary['corrected_section'],
                    "source": summary['source'],
                    "book_title": summary['normalized_title'],
                    "summary_text": summary_text
                }
            except:
                continue
    print("Evaluating {} chapter summary documents...".format(len(chapter_summaries)))


def scan_book_summaries(split, dataset):
    """Gets each book summary and places all relevant info into a dictionary
    """
    f = open(pathlib.Path(f"../../alignments/book-level-summary-alignments/{dataset}_book_summaries_{split}.jsonl"),
             encoding='utf-8')
    for line in f:
        summary = json.loads(line)
        summary_text = get_human_summary(summary['summary_path'])
        if summary_text is not None:
            try:
                book_summaries[summary['summary_path']] = {
                    "book_title": summary['normalized_title'],
                    "source": summary['source'],
                    "summary_text": summary_text
                }
            except:
                continue
    print("Evaluating {} book summary documents...".format(len(book_summaries)))


def setup_model(metric):  # there has got to be a better way to do this.
    """Sets up a model if required, using given metric

    Args:
        metric (str): metric used for test

    Returns:
        _type_: _description_
    """
    if metric == "bleu":
        return  # no model reqiured
    elif metric == "bert":
        from bert import calculate_score
        calculate_score.create_model()
    elif metric == "bertscore":
        from bert import calculate_bertscore
        calculate_bertscore.create_model()
    elif metric == "rouge-1n" or metric == "rouge-2n" or metric == "rouge-l":
        return  # no model required
    elif metric == "moverscore":
        return  # no model required
    elif metric == "qaeval":
        from qaeval_scoring import calculate_score
        calculate_score.create_model()
    elif metric == "meteor":
        return  # no model required
    elif metric == "summac":
        from summac_scoring import calculate_score
        calculate_score.create_model()
        return
    elif metric == "bartscore":
        from bartscore import calculate_score
        calculate_score.create_model()
    elif metric == "chrf":
        return  # no model required
    

def calculate_score(metric, threshold):
    """Scores each chapter summary (reference document) against its corresponding book summary
    (hypothesis document) from the same source. Each ref-sentence i is scored against all hyp sentences 0..n
    individually, taking the all scores above the threshold for each ref-sentence i, then using the average 
    of each ref-sentence score(s) as the final scoring.

    metric used depends on the metric given.

    Args:
        metric (_type_): _description_
    """
    calculated_scores_count = 0
    for chap_summary in chapter_summaries.values():
        for book_summary in book_summaries.values():
            if chap_summary['source'] == book_summary['source'] and chap_summary['book_title'] == book_summary['book_title']:
                ref_doc = tokenize.sent_tokenize(chap_summary['summary_text'])
                hyp_doc = tokenize.sent_tokenize(book_summary['summary_text'])
                ref_sentence_scores = [] # contains the max scores from each singular ref-sentence i, against all possible hyp-sentences 0..n 
                temp_time = time.time()
                for ref_sent_index, ref_sent in enumerate(ref_doc):

                    for hyp_sent_index, hyp_sent in enumerate(hyp_doc):

                        current_score, precision, recall = compute_single_score(metric, ref_sent, hyp_sent)
                        
                        if current_score > threshold:
                            ref_sentence_scores.append(current_score)

                        line_by_line_data.append([chap_summary['section_title'], book_summary['book_title'], book_summary['source'], ref_sent_index, hyp_sent_index, current_score, precision, recall])
                        
                    #end hyp-sent forloop
                #end ref-sent forloop
                score = np.mean(ref_sentence_scores)
                summary_comparison_data.append([score, chap_summary['section_title'], book_summary['book_title'], book_summary['source']])
                calculated_scores_count += 1
                print(f"{book_summary['book_title']}, {chap_summary['section_title']}, {book_summary['source']} - Time: {round(time.time() - temp_time, 3)}, seconds.")

                if calculated_scores_count >= 20:
                    return
                

def compute_single_score(metric, ref_sent, hyp_sent):
    """Calculates an f1 score between two sentences depending on the metric used 
    Args:
        metric (str): metric to denote how the calculation is performed
        ref_sent (str): reference sentence
        hyp_sent (str): hypothesis sentence

    Returns:
        float: f1 score based on how similar the ref_sent and hyp_sent are
    """

    current_score = "NA" #initilze value to something error worthy if not changed.
    precision = "NA"
    recall = "NA"

    # calculate score based on metric, p.s. surely there is a better way to do this.
    if metric == "bleu":
        from bleu import calculate_score
        current_score, precision = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "bert":
        from bert import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "bertscore":
        from bert import calculate_bertscore
        current_score, precision, recall = calculate_bertscore.compute_score(ref_sent, hyp_sent)
    elif metric == "rouge-1n":
        from rouge_scoring import calculate_score
        current_score, precision, recall = calculate_score.compute_score_1n(ref_sent, hyp_sent)
    elif metric == "rouge-2n":
        from rouge_scoring import calculate_score
        current_score, precision, recall = calculate_score.compute_score_2n(ref_sent, hyp_sent)
    elif metric == "rouge-l":
        from rouge_scoring import calculate_score
        current_score, precision, recall = calculate_score.compute_score_l(ref_sent, hyp_sent)
    elif metric == "moverscore":
        from moverscore import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "qaeval":
        from qaeval_scoring import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "meteor":
        from meteor import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "summac":
        from summac_scoring import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "bartscore":
        from bartscore import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "chrf":
        from chrf import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)

    return current_score, precision, recall

def write_results_to_csv(metric, split, filename, dataset):
    """Writes results from calculate score to csv files located in csv_results directory

    Args:
        metric (str): metric that was used for calculation
        split (str): split that was used for calculation
        filename (str): name of csv file located in ../csv_results
    """

    print("Writing to CSV...")
    df = pd.DataFrame(summary_comparison_data, columns=[metric + "score", "Section Title", "Book Title", "Source"])
    df.to_csv(f"../csv_results/booksum_summaries/{dataset}/full_summary/full_summary_section_to_book/{dataset}-section-to-book-comparison-results-{split}-{filename}.csv")
    df.to_parquet(f"../csv_results/booksum_summaries/{dataset}/full_summary/full_summary_section_to_book/{dataset}-section-to-book-comparison-results-{split}-{filename}.parquet")

    df = pd.DataFrame(line_by_line_data, columns=["Section Title", "Book Title", "Source", "Reference Sentence Index", "Hypothesis Sentence Index", metric + " score", "Precision", "Recall"])
    df.to_csv(f"../csv_results/booksum_summaries/{dataset}/line_by_line/line_by_line_section_to_book/{dataset}-section-to-book-comparison-results-{split}-{filename}.csv")
    df.to_parquet(f"../csv_results/booksum_summaries/{dataset}/line_by_line/line_by_line_section_to_book/{dataset}-section-to-book-comparison-results-{split}-{filename}.parquet")
    print("Writes finished.")

def arg_print_help(metric_list):
    """Prints useful help commands when user uses file with incorrect arguments

    Args:
        metrics_list (list): list of possible metrics (currently supported)
    """
    print('Usage: compare_adjusted_book_overviews.py -m <metric> -o <output-csv-filename> -s <split>')
    print('----')
    print("Metrics:", metric_list)
    print("Possible Splits: test, train, val    (default is train)")
    print("Example Filename: bartscore-postfix")

def arg_handler(argv):
    """Function that handles arguments given in command line
    Metric: the metric to use for the f1 calculation
    Outputfile: name of the file to be output
    Split: The input data you want from booksum alignment
    dataset: fixed or adjusted summary data"""
    metric = None
    outputfile = None
    split = None
    dataset = None
    metric_list = ["bleu", "bert", "bertscore", "rouge-1n", "rouge-2n", "rouge-l",
                     "moverscore", "qaeval", "meteor", "summac", "bartscore", "chrf"]
    split_list = ["test", "train", "val", "all"]

    dataset_list = ["fixed", "adjusted"]

    if (len(argv) <= 5):
        arg_print_help(metric_list, split_list, dataset_list)
        sys.exit(2)

    # used getopt for first time to handle arguments, works well but feels messy. Will try another solution next time
    try:
        opts, args = getopt.getopt(
            argv, "hm:o:s:d:", ["help", "metric=", "ofile=", "split=", "data="])
    except getopt.GetoptError:
        arg_print_help(metric_list)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            arg_print_help(metric_list)
            sys.exit()
        elif opt in ("-m", "--metric"):
            metric = arg
            if metric not in metric_list or metric == '' or metric == None:
                print("Metric not acceptable, please use one of:", metric_list)
                sys.exit(2)
        elif opt in ("-o", "--ofile"):
            outputfile = arg
            if outputfile == '' or outputfile == None:
                print("Please provide a output filename")
                sys.exit(2)
        elif opt in ("-s", "--split"):
            split = arg
            if split not in split_list:
                print("Split not acceptable, please use one of:", split_list)
                sys.exit(2)
        elif opt in ("-d", "--data"):
            dataset = arg
            if dataset not in dataset_list:
                print("Data set not acceptable, please use on of:", dataset_list)
                sys.exit(2)

    print('Metric is:', metric)
    print('Output file is:', outputfile)
    print('Split is:', split)
    print("Data set is:", dataset)
    return metric, outputfile, split, dataset

def main(argv):
    
    metric, outputfile, split, dataset = arg_handler(argv)

    #preamble methods
    scan_chapter_summaries(split, dataset)
    scan_book_summaries(split, dataset)
    setup_model(metric)

    score_start_time = time.time()
    calculate_score(metric, threshold)
    print(f"Total time: {round(time.time() - score_start_time, 3)} Seconds.")

    write_results_to_csv(metric, split, outputfile, dataset)


if __name__ == "__main__":
    main(sys.argv[1:])