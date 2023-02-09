import json
import os
import pathlib
from glob import glob
import math
import nltk
#from scipy import stats
import numpy as np
from nltk import tokenize
import time
from typing import List, Union, Iterable
import numpy as np
import nltk
import math
from collections import defaultdict
from nltk import tokenize
from itertools import zip_longest
import sys
import unicodedata
import argparse
import time
import string
import pandas as pd


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
    
    #human_summaries = /scripts/finished_summaries/source/book/chapter
    # tuple, containing, 

    print("Evaluating {} summary documents...".format(len(human_summaries)))

    start_time = time.time()

    for i, sum in enumerate(human_summaries.items()):
        print(sum)
        print(type(sum))


        print(sum[1])
        print(type(sum[1]))
        if i == 2:
            break

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
        related_summary_texts = [curr_summary['summary_text'] for curr_summary in related_summaries]


                                

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


                    totalF, averageTotalF, totalPrec, totalRec = computeChrF(token, sentence, 1, 1, 2)
                    #token, sentence, word ngram, c ngram, beta

                    current_score = averageTotalF
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
            #print(f"{sentence_scores} => {np.mean(sentence_scores)}")
            print(np.mean(sentence_scores))
            print("Unique sentences:", len(unique_sents), "out of", len(ref_doc), "ref sents. :", unique_sents)
            mean_sent_score = np.mean(sentence_scores)
        print(f"{np.mean(max_scores)}")
        mean_max_score = np.mean(max_scores)

        print(summary['chapter_title'], "-", summary['source'], "- time:", round((time.time() - temp_time), 3), "seconds.")

        data.append([mean_max_score, len(unique_sents), summary['chapter_title'], summary['source']])

        unique_used_books.add(summary['chapter_title'])
        summaries_count += 1

        # if summaries_count >= 10:
            # break


    total_time = (time.time() - start_time)

    print("time total:", round(total_time, 1), "seconds.", "Average:", (total_time / summaries_count))

    return data, summaries_count, unique_books, unique_used_books


def separate_characters(line):
    return list(line.strip().replace(" ", ""))

def separate_punctuation(line):
    words = line.strip().split()
    tokenized = []
    for w in words:
        if len(w) == 1:
            tokenized.append(w)
        else:
            lastChar = w[-1] 
            firstChar = w[0]
            if lastChar in string.punctuation:
                tokenized += [w[:-1], lastChar]
            elif firstChar in string.punctuation:
                tokenized += [firstChar, w[1:]]
            else:
                tokenized.append(w)
    
    return tokenized
    
def ngram_counts(wordList, order):
    counts = defaultdict(lambda: defaultdict(float))
    nWords = len(wordList)
    for i in range(nWords):
        for j in range(1, order+1):
            if i+j <= nWords:
                ngram = tuple(wordList[i:i+j])
                counts[j-1][ngram]+=1
   
    return counts

def ngram_matches(ref_ngrams, hyp_ngrams):
    matchingNgramCount = defaultdict(float)
    totalRefNgramCount = defaultdict(float)
    totalHypNgramCount = defaultdict(float)
 
    for order in ref_ngrams:
        for ngram in hyp_ngrams[order]:
            totalHypNgramCount[order] += hyp_ngrams[order][ngram]
        for ngram in ref_ngrams[order]:
            totalRefNgramCount[order] += ref_ngrams[order][ngram]
            if ngram in hyp_ngrams[order]:
                matchingNgramCount[order] += min(ref_ngrams[order][ngram], hyp_ngrams[order][ngram])


    return matchingNgramCount, totalRefNgramCount, totalHypNgramCount


def ngram_precrecf(matching, reflen, hyplen, beta):
    ngramPrec = defaultdict(float)
    ngramRec = defaultdict(float)
    ngramF = defaultdict(float)
    
    factor = beta**2
    
    for order in matching:
        if hyplen[order] > 0:
            ngramPrec[order] = matching[order]/hyplen[order]
        else:
            ngramPrec[order] = 1e-16
        if reflen[order] > 0:
            ngramRec[order] = matching[order]/reflen[order]
        else:
            ngramRec[order] = 1e-16
        denom = factor*ngramPrec[order] + ngramRec[order]
        if denom > 0:
            ngramF[order] = (1+factor)*ngramPrec[order]*ngramRec[order] / denom
        else:
            ngramF[order] = 1e-16
            
    return ngramF, ngramRec, ngramPrec

def computeChrF(fpRef, fpHyp, nworder, ncorder, beta, sentence_level_scores = None):
    norder = float(nworder + ncorder)

    # initialisation of document level scores
    totalMatchingCount = defaultdict(float)
    totalRefCount = defaultdict(float)
    totalHypCount = defaultdict(float)
    totalChrMatchingCount = defaultdict(float)
    totalChrRefCount = defaultdict(float)
    totalChrHypCount = defaultdict(float)
    averageTotalF = 0.0

    nsent = 0
    for hline, rline in zip(fpHyp, fpRef):
        nsent += 1
        
        # preparation for multiple references
        maxF = 0.0
        bestWordMatchingCount = None
        bestCharMatchingCount = None

        bestMatchingCount = defaultdict(float)
        bestRefCount = defaultdict(float)
        bestHypCount = defaultdict(float)
        bestChrMatchingCount = defaultdict(float)
        bestChrRefCount = defaultdict(float)
        bestChrHypCount = defaultdict(float)
        
        hypNgramCounts = ngram_counts(separate_punctuation(hline), nworder)
        hypChrNgramCounts = ngram_counts(separate_characters(hline), ncorder)

        # going through multiple references

        refs = rline.split("*#")

        for ref in refs:
            refNgramCounts = ngram_counts(separate_punctuation(ref), nworder)
            refChrNgramCounts = ngram_counts(separate_characters(ref), ncorder)

            # number of overlapping n-grams, total number of ref n-grams, total number of hyp n-grams
            matchingNgramCounts, totalRefNgramCount, totalHypNgramCount = ngram_matches(refNgramCounts, hypNgramCounts)
            matchingChrNgramCounts, totalChrRefNgramCount, totalChrHypNgramCount = ngram_matches(refChrNgramCounts, hypChrNgramCounts)
                    
            # n-gram f-scores, recalls and precisions
            ngramF, ngramRec, ngramPrec = ngram_precrecf(matchingNgramCounts, totalRefNgramCount, totalHypNgramCount, beta)
            chrNgramF, chrNgramRec, chrNgramPrec = ngram_precrecf(matchingChrNgramCounts, totalChrRefNgramCount, totalChrHypNgramCount, beta)

            sentRec  = (sum(chrNgramRec.values())  + sum(ngramRec.values()))  / norder
            sentPrec = (sum(chrNgramPrec.values()) + sum(ngramPrec.values())) / norder
            sentF    = (sum(chrNgramF.values())    + sum(ngramF.values()))    / norder

            if sentF > maxF:
                maxF = sentF
                bestMatchingCount = matchingNgramCounts
                bestRefCount = totalRefNgramCount
                bestHypCount = totalHypNgramCount
                bestChrMatchingCount = matchingChrNgramCounts
                bestChrRefCount = totalChrRefNgramCount
                bestChrHypCount = totalChrHypNgramCount
        # all the references are done


        # write sentence level scores
        if sentence_level_scores:
            sentence_level_scores.write("%i::c%i+w%i-F%i\t%.4f\n"  % (nsent, ncorder, nworder, beta, 100*maxF))


        # collect document level ngram counts
        for order in range(nworder):
            totalMatchingCount[order] += bestMatchingCount[order]
            totalRefCount[order] += bestRefCount[order]
            totalHypCount[order] += bestHypCount[order]
        for order in range(ncorder):
            totalChrMatchingCount[order] += bestChrMatchingCount[order]
            totalChrRefCount[order] += bestChrRefCount[order]
            totalChrHypCount[order] += bestChrHypCount[order]

        averageTotalF += maxF

    # all sentences are done
     
    # total precision, recall and F (aritmetic mean of all ngrams)
    totalNgramF, totalNgramRec, totalNgramPrec = ngram_precrecf(totalMatchingCount, totalRefCount, totalHypCount, beta)
    totalChrNgramF, totalChrNgramRec, totalChrNgramPrec = ngram_precrecf(totalChrMatchingCount, totalChrRefCount, totalChrHypCount, beta)

    totalF    = (sum(totalChrNgramF.values())    + sum(totalNgramF.values()))    / norder
    averageTotalF = averageTotalF / nsent
    totalRec  = (sum(totalChrNgramRec.values())  + sum(totalNgramRec.values()))  / norder
    totalPrec = (sum(totalChrNgramPrec.values()) + sum(totalNgramPrec.values())) / norder

    return totalF, averageTotalF, totalPrec, totalRec

sentence_level_scores = None
summary_scores = []

data, summaries_count, unique_chapters, unique_used_chapters = calculate_F1()

print("Unique chapters covered: {}".format(len(unique_chapters)))
print("Unique chapters used: {}".format(len(unique_used_chapters)))
CHRF_list = [data_item[0] for data_item in data]
CHRF_mean = sum(CHRF_list) / len(CHRF_list)
print("Mean CHRF score: {}".format(CHRF_mean))
print()

# # Comment these out to avoid saving the csv files.
df = pd.DataFrame(data, columns=["Chrf score", "number of Unique sentences", "chapter-title", "source"])
# Save file.
df.to_csv("../../csv_results/booksum_summaries/chapter-level-sum-comparison-results-train-chrf.csv")