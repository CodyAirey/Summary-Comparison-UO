import json
import pathlib
import sys
import csv
import pandas as pd

def calculate_most_used_source():
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
    
    f = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/fixed_chapter_summaries_all_final.jsonl"),
                encoding='utf-8')
    for line in f:
        summary = json.loads(line)
        number_of_matches[summary['source']] += 1

    for e in number_of_matches:
        print(e, number_of_matches[e])

    source = [i for i in number_of_matches if number_of_matches[i] == max(number_of_matches.values())][0]
    return source


def thingy():
    with open("../../evaluation/csv_results/booksum_summaries/line_by_line_section/chapter-comparison-results-all-rouge-1n-lbl.csv") as f:
        x = 0
        f2 = csv.reader(f, delimiter=',') #section title, ref source, hyp source, ref sent index, hyp sent index, rougescore, prec, recall
        for row in f2:
            if x > 5:
                break
            # print( ", ".join(row))
            print(row)
            x += 1


def yeapp(ref_source):
    df = pd.read_csv("../../evaluation/csv_results/booksum_summaries/line_by_line_section/chapter-comparison-results-all-rouge-1n-lbl.csv")

    for index, row in df.iterrows():

        print(row)
        print("done")
        sys.exit(1)

        if row['Reference Source'] == ref_source:

            print(row)
            sys.exit(1)

            

def main(argv):
    ref_source = calculate_most_used_source
    # thingy()
    yeapp(ref_source)

if __name__ == "__main__":
    main(sys.argv[:])