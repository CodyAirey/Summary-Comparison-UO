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

human_summaries = dict()
summaries_count = 0
data = []
used_files = []
unique_books = set()
unique_used_books = set()
unique_chapters = set()
unique_used_chapters = set()


def preprocessing_summary_setup(split):
   f = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/chapter_summary_aligned_{split}_split.jsonl"),
            encoding='utf-8')

   for line in f: #for each source ->  book -> chapter
      content = json.loads(line)
      if content['source'] == 'pinkmonkey': #skip pinkmonkey, causes issues
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


def result_printout(function):
   print("Unique chapters covered: {}".format(len(unique_chapters)))
   print("Unique chapters used: {}".format(len(unique_used_chapters)))
   FUNC_list = [data_item[0] for data_item in data]
   FUNC_mean = sum(FUNC_list) / len(FUNC_list)
   print(f"Mean {function}: {FUNC_mean}")
   print()


def get_human_summary(summary_path): #returns summaries located in scripts/finished_summaries
   try:
      with open("../../scripts/" + summary_path, encoding='utf-8') as f:
         summary_json = json.load(f)
         return summary_json["summary"]
   except Exception as e:
      print("Failed to read summary file: {}".format(e))
      return None


def setup_model(function): #there has got to be a better way to do this.
   if function == "bleu":
      return # no model reqiured
   elif function == "bert":
      from bert import calculate_score
      calculate_score.create_model()
   elif function == "bertscore":
      from bert import calculate_bertscore
      calculate_bertscore.create_model()
   elif function == "rouge-1n" or function == "rouge-2n" or function == "rouge-l":
      return # no model required
   elif function == "moverscore":
      return #no model required
   elif function == "qaeval":
      from qaeval_scoring import calculate_score
      calculate_score.create_model()
   elif function == "meteor":
      return #no model required
   elif function == "summac":
      from summac_scoring import calculate_score
      calculate_score.create_model()
      return
   elif function == "bartscore":
      from bartscore import calculate_score
      calculate_score.create_model()
   elif function == "chrf":
      return #no model required


def calculate_F1(function):
   start_time = time.time()
   summaries_count = 0

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
         print("No related summary documents were found for {}.".format(summary['chapter_title']))
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


                  #current_score = bart_scorer.score([token], [sentence])[0]
                  # ["bart", "bleu", "bert", "bertscore", "rouge", "moverscore", "qaeval", "meteor", "sumac", "bartscore", "chrf"]
                  #why did switch statements not exist till 3.10? surely there is a better way to do this. Why can't i think of it.

                  current_score = "!"

                  if function == "bleu":
                     from bleu import calculate_score
                     current_score = calculate_score.compute_score(token, sentence)
                  elif function == "bert":
                     from bert import calculate_score
                     current_score = calculate_score.compute_score(token, sentence)
                  elif function == "bertscore":
                     from bert import calculate_bertscore
                     current_score = calculate_bertscore.compute_score(token, sentence)
                  elif function == "rouge-1n":
                     from rouge_scoring import calculate_score
                     current_score = calculate_score.compute_score_1n(token, sentence)
                  elif function == "rouge-2n":
                     from rouge_scoring import calculate_score
                     current_score = calculate_score.compute_score_2n(token, sentence)
                  elif function == "rouge-l":
                     from rouge_scoring import calculate_score
                     current_score = calculate_score.compute_score_l(token, sentence)
                  elif function == "moverscore":
                     from moverscore import calculate_score
                     current_score = calculate_score.compute_score(token, sentence)
                  elif function == "qaeval":
                     from qaeval_scoring import calculate_score
                     current_score = calculate_score.compute_score(token, sentence)
                  elif function == "meteor":
                     from meteor import calculate_score
                     current_score = calculate_score.compute_score(token, sentence)
                  elif function == "summac":
                     from summac_scoring import calculate_score
                     current_score = calculate_score.compute_score(token, sentence)
                  elif function == "bartscore":
                     from bartscore import calculate_score
                     current_score = calculate_score.compute_score(token, sentence)
                  elif function == "chrf":
                     from chrf import calculate_score
                     current_score = calculate_score.compute_score(token, sentence)

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

      # if summaries_count >= 10:
      #    break

   total_time = (time.time() - start_time)

   print("time total:", round(total_time, 1), "seconds.", "Average:", (total_time / summaries_count))

   return data, summaries_count, unique_books, unique_used_books

def write_to_csv(function, split,filename):
   print(filename)
   df = pd.DataFrame(data, columns=[function, "number of Unique sentences", "chapter-title", "source"])
   # Save file.
   df.to_csv(f"../csv_results/booksum_summaries/chapter-comparison-results-{split}-{filename}.csv")


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
      opts, args = getopt.getopt(argv,"hf:o:s:",["help","function=", "ofile=","split="])
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
   data, summaries_count, unique_books, unique_used_books = calculate_F1(function)
   result_printout(function)
   write_to_csv(function, split, outputfile)




if __name__ == "__main__":
   # print(sys.argv[1:])
   # sys.exit(1)
   main(sys.argv[1:])