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

human_summaries = dict()
summaries_count = 0
summary_comparison_data = []
line_by_line_data = []
used_files = []
unique_books = set()
unique_used_books = set()
unique_chapters = set()
unique_used_chapters = set()


def preprocessing_summary_setup(split):
    f = open(pathlib.Path(f"../../alignments/book-level-summary-alignments/fixed_book_summaries_{split}_final.jsonl"),
             encoding='utf-8')

    for line in f:
        content = json.loads(line)

        text = get_human_summary(content['summary_path'])

        if text is not None:
            try:
                human_summaries[content['summary_path']] = {
                    "title": content['normalized_title'],
                    "source": content['source'],  # source from jsonl
                    # actual summary from different text file.
                    "summary_text": text,
                }
            except:
                continue

    print("Evaluating {} summary documents...".format(len(human_summaries)))


def result_printout(function):
    print("Unique Books covered: {}".format(len(unique_books)))
    print("Unique Books used: {}".format(len(unique_used_books)))
    FUNC_list = [data_item[0] for data_item in summary_comparison_data]
    FUNC_mean = sum(FUNC_list) / len(FUNC_list)
    print(f"Mean {function}: {FUNC_mean}")
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


def setup_model(function):
    if function == "bleu":
        return  # no model reqiured
    elif function == "bert":
        from bert import calculate_score
        calculate_score.create_model()
    elif function == "bertscore":
        from bert import calculate_bertscore
        calculate_bertscore.create_model()
    elif function == "rouge-1n" or function == "rouge-2n" or function == "rouge-l":
        return  # no model required
    elif function == "moverscore":
        return  # no model required
    elif function == "qaeval":
        from qaeval_scoring import calculate_score
        calculate_score.create_model()
    elif function == "meteor":
        return  # no model required
    elif function == "summac":
        from summac_scoring import calculate_score
        calculate_score.create_model()
        return
    elif function == "bartscore":
        from bartscore import calculate_score
        calculate_score.create_model()
    elif function == "chrf":
        return  # no model required


def calculate_F1(metric):
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

                    #current_score = bart_scorer.score([token], [sentence])[0]
                    # ["bart", "bleu", "bert", "bertscore", "rouge", "moverscore", "qaeval", "meteor", "sumac", "bartscore", "chrf"]
                    # why did switch statements not exist till 3.10? surely there is a better way to do this. Why can't i think of it.

                    current_score, precision, recall = compute_single_score(metric, ref_sent, hyp_sent)

                    # print("token:", token)
                    # print("sentence: ", sentence)
                    # print("score:", current_score)
                    # print("---")
                    if current_score > best_score:
                        best_score = current_score
                        best_score_index = hyp_sent_index
                    
                    line_by_line_data.append([summary['title'], summary['source'], hyp_summary['source'], ref_sent_index, hyp_sent_index, current_score, precision, recall])
                sentence_scores.append(best_score)
                if hyp_summary['source'] in unique_sents.keys():
                    unique_sents[hyp_summary['source']].add(best_score_index)
                else:
                    unique_sents[hyp_summary['source']] = {best_score_index}
                # print("NEXT TOKEN")
            max_scores.append(np.mean(sentence_scores))
            # print(f"{sentence_scores} => {np.mean(sentence_scores)}")
            # print("Unique sentences:", len(unique_sents), "out of", len(ref_doc), "ref sents. :", unique_sents)
            mean_sent_score = np.mean(sentence_scores)
        # print(f"{np.mean(max_scores)}")
        mean_max_score = np.mean(max_scores)

        print(summary['title'], "-", summary['source'], "- time:", round((time.time() - temp_time), 3), "seconds.")

        summary_comparison_data.append([mean_max_score, summary['title'], summary['source'], unique_sents])

        unique_used_books.add(summary['title'])
        summaries_count += 1

        # if summaries_count >= 10:
        #     break

    total_time = (time.time() - start_time)

    print("time total:", round(total_time, 1), "seconds.",
          "Average:", (total_time / summaries_count))

    return summary_comparison_data, summaries_count, unique_books, unique_used_books

def compute_single_score(metric, ref_sent, hyp_sent):


    """Calculates an f1 score between two sentences depending on the metric used 

    Args:
        metric (str): metric to denote how the calculation is performed
        ref_sent (str): reference sentence
        hyp_sent (str): hypothesis sentence

    Returns:
        float: f1 score based on how similar the ref_sent and hyp_sent are
    """
    current_score = "NA"
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

def write_to_csv(function, split, filename):
    print(filename)
    df = pd.DataFrame(
        summary_comparison_data, columns=[function + " score", "title", "source", "unique Sentences used"])
    # Save file.
    df.to_csv(
        f"../csv_results/booksum_summaries/book/book-comparison-results-{split}-{filename}.csv")
    
    df = pd.DataFrame(line_by_line_data, columns=["Section Title", "Reference Source", "Hypothesis Source", "Reference Sentence Index", "Hypothesis Sentence Index", (function + "score"), "Precision", "Recall"])
    df.to_csv(
        f"../csv_results/booksum_summaries/line_by_line_book/book-comparison-results-{split}-{filename}-lbl.csv")

def helper(function_list):
    print('Usage: compare_chapters.py -f <function> -o <output-csv-filename> -s <split>')
    print('----')
    print("Functions:", function_list)
    print("Possible Splits: test, train, val    (default is train)")
    print("Example Filename: bart-24-12-2022")


def main(argv):
    function = None
    outputfile = None
    split = None
    function_list = ["bleu", "bert", "bertscore", "rouge-1n", "rouge-2n", "rouge-l",
                     "moverscore", "qaeval", "meteor", "summac", "bartscore", "chrf"]
    split_list = ["test", "train", "val", "all"]

    if (len(argv) <= 4):
        helper(function_list)
        sys.exit(2)

    try:
        opts, args = getopt.getopt(
            argv, "hf:o:s:", ["help", "function=", "ofile=", "split="])
    except getopt.GetoptError:
        helper(function_list)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            helper(function_list)
            sys.exit()
        elif opt in ("-f", "--function"):
            function = arg
            if function not in function_list or function == '' or function == None:
                print("Function not acceptable, please use one of:", function_list)
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

    print('Function is:', function)
    print('Output file is:', outputfile)
    print('Split is:', split)

    preprocessing_summary_setup(split)
    setup_model(function)
    data, summaries_count, unique_books, unique_used_books = calculate_F1(
        function)
    result_printout(function)
    write_to_csv(function, split, outputfile)


if __name__ == "__main__":
    # print(sys.argv[1:])
    # sys.exit(1)
    main(sys.argv[1:])
