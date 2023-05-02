from typing import List, Union, Iterable
import numpy as np
import nltk
import math
from collections import defaultdict
from nltk import tokenize
from itertools import zip_longest
import json
import sys
import getopt
import pathlib
import time
import pandas as pd
import re

sys.path.append('source_modules')

human_summaries = dict()
summaries_count = 0
summary_comparison_data = []
line_by_line_data = []
used_files = []
unique_books = set()
unique_used_books = set()
unique_chapters = set()
unique_used_chapters = set()


def preprocessing_summary_setup(split, dataset):
    """
    Reads the jsonl containing summary information, and creates a dictionary 
    holding the relevant information

    Args:
        split (str): split to be used (all, test, val, train)
        dataset (str): dataset to be used (fixed or adjusted)
    """
    f = open(pathlib.Path(f"../../alignments/book-level-summary-alignments/{dataset}_book_summaries_{split}.jsonl"),
             encoding='utf-8')

    for line in f:
        content = json.loads(line)

        text = get_human_summary(content['summary_path'])

        if text is not None:
            try:
                human_summaries[content['summary_path']] = {
                    "title": content['normalized_title'],
                    "source": content['source'],
                    "summary_text": text,
                }
            except:
                continue

    print("Evaluating {} summary documents...".format(len(human_summaries)))


def result_printout(metric):
    print("Unique Books covered: {}".format(len(unique_books)))
    print("Unique Books used: {}".format(len(unique_used_books)))
    print()


# returns summaries located in scripts/finished_summaries
def get_human_summary(summary_path):
    try:
        with open("../../scripts/" + summary_path, encoding='utf-8') as f:
            summary_json = json.load(f)
            return summary_json["summary"]
    except Exception as e:
        print("Failed to read summary file: {}".format(e))
        return None


def setup_model(metric):
    """
    Setups models for neccessary metrics

    Args:
        metric (str): metric used
    """
    if metric == "bert":
        from bert import calculate_score
        calculate_score.create_model()
    elif metric == "bertscore":
        from bert import calculate_bertscore
        calculate_bertscore.create_model()
    elif metric == "bartscore":
        from bartscore import calculate_score
        calculate_score.create_model()


def calculate_F1(metric):
    """
    Scores each book summary (reference document) against its corresponding 
    (hypothesis document) book summaries from a different source(s). Each reference 
    sentence is scores against all hypothesis sentences indiviually, taking the 
    max F1 score from the lot (a single sentence to sentence pair with the greatest 
    similarity).

    The final score for the two summaries is calculated by averaging each of 
    the max-sentence-f1 scores.

    Starts by looping over all summaries, and scoring the similarity between 
    reviews from different sources for the same book. 
    E.G. Dracula.sparknotes vs Dracula.bookwolf, Dracula.gradesaver

    Args:
        metric (str): the metric to be used for the f1 calculation
    """
    start_time = time.time()
    summaries_count = 0

    for summary_path, summary in human_summaries.items():
        # Get all related summary documents.
        unique_books.add(summary['title'])

        related_summaries = list(filter(lambda curr_summary:
                                        curr_summary['title'] == summary['title']
                                        and curr_summary['source'] != summary['source'], human_summaries.values()))
        # Remember which files have been used.
        used_files.extend(related_summaries)

        # if there are no related summary documents, then just print.
        if len(related_summaries) == 0:
            print("No related summary documents were found for {}.".format(
                  summary['title']))
            continue
        related_summary_texts = [curr_summary['summary_text']
                                 for curr_summary in related_summaries]

        ref_doc = tokenize.sent_tokenize(summary['summary_text'])
        tokenized_sums = []
        for cursum in related_summary_texts:
            tokenized_sums.append(tokenize.sent_tokenize(cursum))

        temp_time = time.time()
        unique_sents = dict()
        max_scores = []
        for hyp_summary in related_summaries:
            hyp_doc = tokenize.sent_tokenize(hyp_summary['summary_text'])
            sentence_scores = []
            
            for ref_sent_index, ref_sent in enumerate(ref_doc):
                best_score = -math.inf
                best_score_index = -1
                for hyp_sent_index, hyp_sent in enumerate(hyp_doc):


                    current_score, precision, recall = compute_single_score(metric, ref_sent, hyp_sent)

                    # # print("token:", token)
                    # # print("sentence: ", sentence)
                    # # print("score:", current_score)
                    # # print("---")
                    # if current_score > best_score:
                    #     best_score = current_score
                    #     best_score_index = hyp_sent_index
                    
                    line_by_line_data.append([summary['title'], summary['source'], hyp_summary['source'], ref_sent_index, hyp_sent_index, current_score, precision, recall])
                # sentence_scores.append(best_score)
                # if hyp_summary['source'] in unique_sents.keys():
                #     unique_sents[hyp_summary['source']].add(best_score_index)
                # else:
                #     unique_sents[hyp_summary['source']] = {best_score_index}
                # print("NEXT TOKEN")
            # max_scores.append(np.mean(sentence_scores))
            # print(f"{sentence_scores} => {np.mean(sentence_scores)}")
            # print("Unique sentences:", len(unique_sents), "out of", len(ref_doc), "ref sents. :", unique_sents)
            # mean_sent_score = np.mean(sentence_scores)
        # print(f"{np.mean(max_scores)}")
        # mean_max_score = np.mean(max_scores)

        print(summary['title'], "-", summary['source'], "- time:", round((time.time() - temp_time), 3), "seconds.")

        # summary_comparison_data.append([mean_max_score, summary['title'], summary['source'], unique_sents])

        unique_used_books.add(summary['title'])
        summaries_count += 1

        # if summaries_count >= 10:
        #     break

    total_time = (time.time() - start_time)

    print("time total:", round(total_time, 1), "seconds.",
          "Average:", (total_time / summaries_count))

    return

def compute_single_score(metric, ref_sent, hyp_sent):
    """
    Calculates an f1 score between two sentences depending on the metric used 

    Args:
        metric (str): metric to denote how the calculation is performed
        ref_sent (str): reference sentence
        hyp_sent (str): hypothesis sentence

    Returns:
        float: f1 score based on how similar the ref_sent and hyp_sent are
    """
    current_score, precision, recall = "NA", "NA", "NA"

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
    elif metric == "meteor":
        from meteor import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "bartscore":
        from bartscore import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "chrf":
        from chrf import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)

    return current_score, precision, recall

def write_to_csv(metric, split, filename, dataset):
    """
    Writes F1 score data to CSV and Paruqet, one csv/pq for line-by-line sentence comparison scores and another csv/pq for full book scores

    Args:
        metric (str): metric used
        split (str): split used
        filename (str): output string to be added to file outputname
        dataset (str): dataset used
    """

    print("Writing to CSV...")

    # df = pd.DataFrame(summary_comparison_data, columns=[metric + " score", "title", "source", "unique Sentences used"])
    # df.to_csv(f"../csv_results/booksum_summaries/{dataset}/full_summary_book/{dataset}-book-comparison-results-{split}-{filename}.csv")
    # df.to_parquet(f"../csv_results/booksum_summaries/{dataset}/full_summary_book/{dataset}-book-comparison-results-{split}-{filename}.parquet")

    df = pd.DataFrame(line_by_line_data, columns=["Book Title", "Reference Source", "Hypothesis Source", "Reference Sentence Index", "Hypothesis Sentence Index", (metric + "score"), "Precision", "Recall"])
    df.to_csv(f"../csv_results/booksum_summaries/{dataset}/line_by_line_book/{dataset}-book-comparison-results-{split}-{filename}-lbl.csv")
    df.to_parquet(f"../csv_results/booksum_summaries/{dataset}/line_by_line_book/{dataset}-book-comparison-results-{split}-{filename}-lbl.parquet")

    print("Writes finished.")


def arg_print_help(metric_list, split_list, dataset_list):
    """
    Prints useful help commands when user uses file with incorrect arguments

    Args:
        metrics_list (list): list of possible metrics (currently supported)
        split_list (list): list of possible splits supported
        dataset_list (list): list of possible data file types supported
    """
    print(f"""
        Usage: compare_sections.py -m <metric> -o <output-csv-filename> -s <split> -d <dataset> \n
        ---- \n
        Metrics: {metric_list}\n
        Possible Splits: {split_list}\n
        Possible Data Sets: {dataset_list}\n
        Example filename: bartscore-postfix
        """)


def arg_handler(argv):
    """
    handles arguments given in command line

    Metric: the metric to use for the f1 calculation
    Outputfile: name of the file to be output
    Split: The input data you want from booksum alignment
    dataset: fixed or adjusted summary data
    """
    metric = None
    outputfile = None
    split = None
    dataset = None
    metric_list = ["bleu", "bert", "bertscore", "rouge-1n", "rouge-2n", "rouge-l",
                     "moverscore", "meteor", "bartscore", "chrf"]
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

    outputfile.replace("-", "")
    
    print('Metric is:', metric)
    print('Output file is:', outputfile)
    print('Split is:', split)
    print("Data set is:", dataset)
    return metric, outputfile, split, dataset

def main(argv):
    metric, outputfile, split, dataset = arg_handler(argv)

    preprocessing_summary_setup(split, dataset)
    setup_model(metric)

    calculate_F1(metric)

    result_printout(metric)
    write_to_csv(metric, split, outputfile, dataset)


if __name__ == "__main__":
    main(sys.argv[1:])
