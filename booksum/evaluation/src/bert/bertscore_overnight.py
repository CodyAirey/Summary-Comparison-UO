import json
import os
import pathlib
import pandas as pd
from glob import glob
import math
import nltk
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
from nltk import tokenize
import time


import bert_score
bert_score.__version__
from bert_score import score
from bert_score import BERTScorer



def get_human_summary(summary_path):
    try:
        with open("../../../scripts/" + summary_path, encoding='utf-8') as f:
            summary_json = json.load(f)
            return summary_json["summary"]
    except Exception as e:
        print("Failed to read summary file: {}".format(e))
        return None


def calculate_F1():
    summaries_count = 0
    data = []
    used_files = []
    unique_books = set()
    unique_used_books = set()
    scorer = BERTScorer(lang="en", rescale_with_baseline=True)

    human_summaries = dict()
    #f = open(pathlib.Path("../../booksum/alignments/chapter-level-summary-alignments/chapter_summary_aligned_all_split.jsonl"),

    #do train
    
    f = open(pathlib.Path("../../../alignments/chapter-level-summary-alignments/chapter_summary_aligned_train_split.jsonl"),
             encoding='utf-8')

    for line in f:
        content = json.loads(line)
        if content['source'] == 'pinkmonkey':
            continue
        text = get_human_summary(content['summary_path'])
        if text is not None:
            try:
                human_summaries[content['summary_path']] = {
                    "chapter_title": content['book_id'],
                    "source": content['source'],
                    "summary_text": text,
                }
            except:
                continue


    print("Evaluating {} summary documents...".format(len(human_summaries)))

    start_time = time.time()

    for summary_path, summary in human_summaries.items():
        # Get all related summary documents.
        unique_books.add(summary['chapter_title'])
        # Special case for Around the World in Eighty (80) Days
        if summary['chapter_title'] == "Around the World in Eighty Days":
            related_summaries = list(filter(
                lambda curr_summary: curr_summary['chapter_title'] == 'Around the World in 80 Days', human_summaries.values()))
        elif summary['chapter_title'] == "Around the World in 80 Days":
            related_summaries = list(filter(
                lambda curr_summary: curr_summary['chapter_title'] == 'Around the World in Eighty Days', human_summaries.values()))
        else:
            related_summaries = list(filter(lambda curr_summary: curr_summary['chapter_title'] == summary[
                                     'chapter_title'] and curr_summary['source'] != summary['source'], human_summaries.values()))
        # Remember which files have been used.
        used_files.extend(related_summaries)

        # if there are no related summary documents, then just print.
        if len(related_summaries) == 0:
            print("No related summary documents were found for {}.".format(
                summary['chapter_title']))
            continue
        related_summary_texts = [curr_summary['summary_text']
                                 for curr_summary in related_summaries]


        ref_doc = tokenize.sent_tokenize(summary['summary_text'])
        tokenized_sums = []
        for cursum in related_summary_texts:
            tokenized_sums.append(tokenize.sent_tokenize(cursum))

        temp_time = time.time()

        max_scores = []
        for sentence_list in tokenized_sums:
            sentence_scores = []
            unique_sents = set()
            for i, token in enumerate(ref_doc):
                best_score = -math.inf
                best_score_i = -1;
                for j, sentence in enumerate(sentence_list):


                    p, r, f1 = scorer.score([ref_doc[i]], [sentence_list[j]])
                    current_score = float(f1.mean())
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
            print("Unique sentences:", len(unique_sents), "out of", len(ref_doc), "ref sents. :", unique_sents)
            mean_sent_score = np.mean(sentence_scores)
        print(f"{np.mean(max_scores)}")
        mean_max_score = np.mean(max_scores)

        print(summary['chapter_title'], "-", summary['source'], "- time:", round((time.time() - temp_time), 3), "seconds.")

        data.append([mean_max_score, len(unique_sents), summary['chapter_title'], summary['source']])

        unique_used_books.add(summary['chapter_title'])
        summaries_count += 1

        if summaries_count >= 3:
            break


    total_time = (time.time() - start_time)

    print("time total:", round(total_time, 1), "seconds.", "Average:", (total_time / summaries_count))

    return data, summaries_count, unique_books, unique_used_books



data, summaries_count, unique_chapters, unique_used_chapters = calculate_F1()

print("Unique chapters covered: {}".format(len(unique_chapters)))
print("Unique chapters used: {}".format(len(unique_used_chapters)))
BERT_list = [data_item[0] for data_item in data]
BERT_mean = sum(BERT_list) / len(BERT_list)
print("Mean bertscore: {}".format(BERT_mean))
print()

# # Comment these out to avoid saving the csv files.
df = pd.DataFrame(data, columns=["Bertscore", "number of Unique sentences", "chapter-title", "source"])
# Save file.
df.to_csv("../../csv_results/booksum_summaries/chapter-level-sum-comparison-results-train-bertscore.csv")