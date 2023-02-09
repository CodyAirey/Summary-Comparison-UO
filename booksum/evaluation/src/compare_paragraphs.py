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
data = []
used_files = []
unique_paragraphs = set()
unique_used_books = set()

count = 0

#yoinked from geeks for geeks | https://www.geeksforgeeks.org/python-program-for-converting-roman-numerals-to-decimal-lying-between-1-to-3999/
def romanToInt(s):

    try:

        translations = {
            "I": 1,
            "V": 5,
            "X": 10,
            "L": 50,
            "C": 100,
            "D": 500,
            "M": 1000
        }
        number = 0
        s = s.replace("IV", "IIII").replace("IX", "VIIII")
        s = s.replace("XL", "XXXX").replace("XC", "LXXXX")
        s = s.replace("CD", "CCCC").replace("CM", "DCCCC")
        for char in s:
            number += translations[char]
        return number
    except:
        return -1


def preprocessing_summary_setup(split):
    f = open(pathlib.Path(f"../../alignments/paragraph-level-summary-alignments/chapter_summary_aligned_{split}_split.jsonl.gathered.stable"),
             encoding='utf-8')

    global count

    source_list = ["bookwolf", "cliffnotes", "gradesaver", "novelguide",
                   "pinkmonkey", "shmoop", "sparknotes", "thebestnotes"]

    for line in f:  # for each paragraph, summary, and title
        content = json.loads(line)

        source = None
        for source_candidate in source_list:
            if source_candidate in content['title']:
                source = source_candidate
        if source == "pinkmoney":  # skip pinkmonkey, causes issues
            # JK's old hardcoded stuff... not worth refactoring / fixing. PM shouldn't even be in the json.
            continue

        title = content['title']
        if "around_the_world_in_eighty_days" in title:  # another JK fix
            title.replace("around_the_world_in_eighty_days",
                          "around_the_world_in_80_days")
        # title eg: "around_the_world_in_80_days.chapter_8.novelguide-stable-7"


        #preamble stuff to fix different naming schemes for the same content by different sources.
        p_title = title.replace(source, "source")
        new_title = p_title
        res = re.split('\.|_|-', new_title)
        final_t = []

        #replace romans to ints, e.g. ACT_II to ACT_2
        for i, each in enumerate(res):
            if(romanToInt(each.upper()) >= 1):
                res[i] = str(romanToInt(each.upper()))

        # fix instances of "chapter_43-48" to "chapter-43-chapter-48" etc.
        i = 0
        while i < len(res):
            if res[i] == "chapters":
                final_t.append("chapter")
                final_t.append(res[i+1])
                final_t.append("chapter")
                # i += 2
                i += 2
            if res[i] == "scenes":
                final_t.append("scene")
                final_t.append(res[i+1])
                final_t.append("scene")
                # i += 2
                i += 2
            if i < len(res):
                final_t.append(res[i])
                i += 1
        p_title = "-".join(final_t)

        text = content['summary']
        if text is not None:
            try:
                human_summaries[title] = {  # use full title
                    # example: "the_last_of_the_mohicans-p9"
                    "paragraph_title": p_title,
                    "source": source,
                    "summary_text": text
                }
            except:
                continue

    print("Evaluating {} summary documents...".format(len(human_summaries)))


def result_printout(function):
    print("Unique Books covered: {}".format(len(unique_paragraphs)))
    print("Unique Books used: {}".format(len(unique_used_books)))
    FUNC_list = [data_item[0] for data_item in data]
    FUNC_mean = sum(FUNC_list) / len(FUNC_list)
    print(f"Mean {function}: {FUNC_mean}")
    print()

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

# key is title: dracula.chapter_1.bookwolf-stable-0

# values:
#   source: bookwolf
#   text: [sent1, sent2, sent3]
#   paragraph_title: dracula.chapter_1.source-stable-0


def calculate_F1(function):
    start_time = time.time()
    summaries_count = 0

    for title, summary in human_summaries.items():
        # Get all related summary documents.
        unique_paragraphs.add(summary['paragraph_title'])

        related_summaries = list(filter(lambda curr_summary: curr_summary['paragraph_title'] == summary[
            'paragraph_title'] and curr_summary['source'] != summary['source'], human_summaries.values()))

        # Remember which files have been used.
        used_files.extend(related_summaries)

        # if there are no related summary documents, then just print.
        if len(related_summaries) == 0:
            print("No related summary documents were found for {}.".format(
                  summary['paragraph_title']))
            continue
        related_summary_texts = [curr_summary['summary_text']
                                 for curr_summary in related_summaries]

        # if  len(related_summaries) != 0:
        #     print(summary)

        #     for each in related_summaries:
        #         print(each)

        ref_doc = summary['summary_text']
        tokenized_sums = []
        for cursum in related_summary_texts:
            tokenized_sums.append(cursum)

        temp_time = time.time()

        max_scores = []
        for sentence_list in tokenized_sums:
            sentence_scores = []
            unique_sents = set()
            for i, token in enumerate(ref_doc):
                best_score = -math.inf
                best_score_i = -1
                for j, sentence in enumerate(sentence_list):

                    #current_score = bart_scorer.score([token], [sentence])[0]
                    # ["bart", "bleu", "bert", "bertscore", "rouge", "moverscore", "qaeval", "meteor", "sumac", "bartscore", "chrf"]
                    # why did switch statements not exist till 3.10? surely there is a better way to do this. Why can't i think of it.

                    current_score = "!"

                    if function == "bleu":
                        from bleu import calculate_score
                        current_score = calculate_score.compute_score(
                            token, sentence)
                    elif function == "bert":
                        from bert import calculate_score
                        current_score = calculate_score.compute_score(
                            token, sentence)
                    elif function == "bertscore":
                        from bert import calculate_bertscore
                        current_score = calculate_bertscore.compute_score(
                            token, sentence)
                    elif function == "rouge-1n":
                        from rouge_scoring import calculate_score
                        current_score = calculate_score.compute_score_1n(
                            token, sentence)
                    elif function == "rouge-2n":
                        from rouge_scoring import calculate_score
                        current_score = calculate_score.compute_score_2n(
                            token, sentence)
                    elif function == "rouge-l":
                        from rouge_scoring import calculate_score
                        current_score = calculate_score.compute_score_l(
                            token, sentence)
                    elif function == "moverscore":
                        from moverscore import calculate_score
                        current_score = calculate_score.compute_score(
                            token, sentence)
                    elif function == "qaeval":
                        from qaeval_scoring import calculate_score
                        current_score = calculate_score.compute_score(
                            token, sentence)
                    elif function == "meteor":
                        from meteor import calculate_score
                        current_score = calculate_score.compute_score(
                            token, sentence)
                    elif function == "summac":
                        from summac_scoring import calculate_score
                        current_score = calculate_score.compute_score(
                            token, sentence)
                    elif function == "bartscore":
                        from bartscore import calculate_score
                        current_score = calculate_score.compute_score(
                            token, sentence)
                    elif function == "chrf":
                        from chrf import calculate_score
                        current_score = calculate_score.compute_score(
                            token, sentence)

                    # print("token:", token)
                    # print("sentence: ", sentence)
                    # print("score:", current_score)
                    # print("---")
                    if current_score > best_score:
                        best_score = current_score
                        best_score_i = j
                sentence_scores.append(best_score)
                unique_sents.add(best_score_i)
                # print("NEXT TOKEN")
            max_scores.append(np.mean(sentence_scores))
            print(f"{sentence_scores} => {np.mean(sentence_scores)}")
            print("Unique sentences:", len(unique_sents), "out of",
                  len(ref_doc), "ref sents. :", unique_sents)
            mean_sent_score = np.mean(sentence_scores)
        print(f"{np.mean(max_scores)}")
        mean_max_score = np.mean(max_scores)

        print(summary['paragraph_title'], "-", summary['source'],
              "- time:", round((time.time() - temp_time), 3), "seconds.")

        data.append([mean_max_score, len(unique_sents),
                    summary['paragraph_title'], summary['source']])

        unique_used_books.add(summary['paragraph_title'])
        summaries_count += 1

        # if summaries_count >= 50:
        #     break

    total_time = (time.time() - start_time)

    print("time total:", round(total_time, 1), "seconds.",
          "Average:", (total_time / summaries_count))

    return data, summaries_count, unique_paragraphs, unique_used_books


def write_to_csv(function, split, filename):
    print(filename)
    df = pd.DataFrame(
        data, columns=[function, "number of Unique sentences", "title", "source"])
    # Save file.
    df.to_csv(
        f"../csv_results/booksum_summaries/paragraph-comparison-results-{split}-{filename}.csv")


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
    split_list = ["test", "train", "val"]

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
    data, summaries_count, unique_paragraphs, unique_used_books = calculate_F1(
        function)
    result_printout(function)
    write_to_csv(function, split, outputfile)


if __name__ == "__main__":
    # print(sys.argv[1:])
    # sys.exit(1)
    main(sys.argv[1:])
