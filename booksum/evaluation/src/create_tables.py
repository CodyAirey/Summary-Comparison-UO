import pathlib
import json
import re
import sys
from dataclasses import dataclass
import pandas as pd
from nltk.tokenize import word_tokenize
import string

import numpy as np

data_type = sys.argv[1]

# @dataclass
# class Book:
#     title: str

# @dataclass
# class Original_Book_Variation:
#     book_title: str
#     book_path: str
#     book_word_count: int

#     def as_dict(self):
#         return {
#             'Book Title': self.book_title,
#             'Book Word Count': self.book_word_count,
#             'Book Path': self.book_path
#             }


# @dataclass
# class Section:
#     section_title: str

# @dataclass
# class Original_Section_Variation:
#     chapter_path: str
#     section_word_count: int

# @dataclass
# class Section_Summary:
#     summary_path: str
#     section_sum_word_count: int


books = pd.DataFrame(columns=["Book Title", "Number of Chapters"])
original_book_variations = pd.DataFrame(columns= ["Book Title", "Word Count", "Book Path"])
book_summaries = pd.DataFrame(columns=["Book Title", "Source", "Word Count", "Summary Path"])

sections = pd.DataFrame(columns=['Section Title', "Book Title"])
original_section_variations = pd.DataFrame(columns=['Book Title', "Section Title", "Word Count", "Section Path"])
section_summaries = pd.DataFrame(columns=['Book Title', "Section Title", "Source", "Word Count", "Summary Path"])

book_coverage_report = pd.DataFrame(columns=["Book Title", "Source", "Chapters in Book", "Chapters Covered", "Percentage Covered"])


#Create Books
book_file = open(pathlib.Path(f"../../alignments/book-level-summary-alignments/fixed_book_summaries_{data_type}_final.jsonl"),
            encoding='utf-8')
section_file = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/fixed_chapter_summaries_{data_type}_final.jsonl"),
            encoding='utf-8')

for line in book_file:
    summary = json.loads(line)

    if summary['normalized_title'] not in books['Book Title'].values:
        new_df = pd.DataFrame([[summary['normalized_title']]], columns=["Book Title"])
        books = pd.concat([books, new_df], ignore_index=True)
for line in section_file:
    summary = json.loads(line)

    if summary['normalized_title'] not in books['Book Title'].values:
        new_df = pd.DataFrame([[ summary['normalized_title'] ]], columns=["Book Title"])
        books = pd.concat([books, new_df], ignore_index=True)



#Create Original_Book_Variations
book_file = open(pathlib.Path(f"../../alignments/book-level-summary-alignments/fixed_book_summaries_{data_type}_final.jsonl"),
            encoding='utf-8')
x = 0
for line in book_file:
    summary = json.loads(line)
    if summary['book_path'] not in original_book_variations["Book Path"].values:
        #speed wise, wonder if there is better way to do this, could be worse though, only has to run once.
        with open("../../" + summary['book_path'], 'r') as f:
            data = f.read()
            tokens = word_tokenize(data)
            words = [''.join(letter for letter in word if letter not in string.punctuation) for word in tokens]
            words = list(filter(None, words))
            word_count = len(words)

        new_df = pd.DataFrame( [[summary['normalized_title'], word_count, summary['book_path']]], columns=['Book Title', 'Word Count', 'Book Path'])
        original_book_variations = pd.concat([original_book_variations, new_df], ignore_index=True)
    #     x += 1
    # if x >= 25:
    #     break




#Create Book_Summaries
book_file = open(pathlib.Path(f"../../alignments/book-level-summary-alignments/fixed_book_summaries_{data_type}_final.jsonl"),
            encoding='utf-8')
for line in book_file:
    summary = json.loads(line)
    if summary['summary_path'] not in book_summaries['Summary Path'].values:

        try:

            with open("../../scripts/" + summary['summary_path'], 'r') as f:
                f = json.load(f)#summaries come in json format
                data = f['summary']
                tokens = word_tokenize(data)
                words = [''.join(letter for letter in word if letter not in string.punctuation) for word in tokens]
                words = list(filter(None, words))
                word_count = len(words)

            new_df = pd.DataFrame( [[ summary['normalized_title'], summary['source'], word_count, summary['summary_path'] ]], columns=['Book Title', 'Source', "Word Count", "Summary Path"])
            book_summaries = pd.concat([book_summaries, new_df], ignore_index=True)
        except:
            print(f"Could not find summary for: {summary['normalized_title']} - {summary['source']}, path: {summary['summary_path']}")
            continue


#Create Sections
section_file = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/fixed_chapter_summaries_{data_type}_final.jsonl"),
            encoding='utf-8')
for line in section_file:
    summary = json.loads(line)

    if summary['corrected_section'] not in sections['Section Title'].values:
        new_df = pd.DataFrame([[summary['corrected_section'], summary['normalized_title']]], columns=["Section Title", "Book Title"])
        sections = pd.concat([sections, new_df], ignore_index=True)

    
#Create Original Section Variations
x = 0
section_file = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/fixed_chapter_summaries_{data_type}_final.jsonl"),
            encoding='utf-8')
for line in section_file:
    summary = json.loads(line)

    if summary['chapter_path'] not in original_section_variations['Section Path'].values:

        try:
            with open("../../" + summary['chapter_path'], 'r') as f:
                data=f.read()
                tokens = word_tokenize(data)
                words = [''.join(letter for letter in word if letter not in string.punctuation) for word in tokens]
                words = list(filter(None, words))
                word_count = len(words)

                new_df = pd.DataFrame([[summary['normalized_title'], summary['corrected_section'], word_count, summary['chapter_path'] ]], columns=['Book Title', "Section Title", "Word Count", "Section Path"])
                original_section_variations = pd.concat([original_section_variations, new_df], ignore_index=True)
        except:
            print(f"Could not find original section: {summary['chapter_path']}")
            continue
    #     x += 1
    # if x >= 25:
    #     break



#Create Section Summaries
x = 0
section_file = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/fixed_chapter_summaries_{data_type}_final.jsonl"),
            encoding='utf-8')
for line in section_file:
    summary = json.loads(line)
    if summary['summary_path'] not in section_summaries['Summary Path'].values:

        try:
            with open("../../scripts/" + summary['summary_path'], 'r') as f:
                f = json.load(f)#summaries come in json format
                data = f['summary']
                tokens = word_tokenize(data)
                words = [''.join(letter for letter in word if letter not in string.punctuation) for word in tokens]
                words = list(filter(None, words))
                word_count = len(words)
    
                new_df = pd.DataFrame([[summary['normalized_title'], summary['corrected_section'], summary['source'], word_count, summary['summary_path'] ]], columns=['Book Title', "Section Title", "Source", "Word Count", "Summary Path"])
                section_summaries = pd.concat([section_summaries, new_df], ignore_index=True)
        except:
            print(f"Could not find summary: {summary['summary_path']}")
            continue
    #     x += 1
    # if x >= 25:
    #     break


#Add number of chapters to Books
coverage_file = open(f"book_coverage_{data_type}.jsonl", 'r')
data = json.load(coverage_file)
for book in data:
    books.loc[books["Book Title"]==book, "Number of Chapters"] = data[book]['total_individual_chapters']


for book in data:
    # for coverage_item in data[book]:
        coverage_items = data[book]['coverage']
        for current in coverage_items:
        # print(current)
            new_df = pd.DataFrame([[book, current['source'], data[book]['total_individual_chapters'], current['chapters_covered'], current['percentage'] ]], columns=["Book Title", "Source", "Chapters in Book", "Chapters Covered", "Percentage Covered"])
            book_coverage_report = pd.concat([book_coverage_report, new_df], ignore_index=True)


print(books)
print(original_book_variations)
print(book_summaries)
print(sections)
print(original_section_variations)
print(section_summaries)
print(book_coverage_report)

books.to_csv("data/books.csv")
original_book_variations.to_csv("data/original_book_variations.csv")
book_summaries.to_csv("data/book_summaries.csv")
sections.to_csv("data/sections.csv")
original_section_variations.to_csv("data/original_section_variations.csv")
section_summaries.to_csv("data/section_summaries.csv")
book_coverage_report.to_csv("data/book_coverage.csv")