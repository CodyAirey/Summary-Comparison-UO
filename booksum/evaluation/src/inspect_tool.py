import json
from nltk import tokenize

b = open("../../alignments/book-level-summary-alignments/fixed_book_summaries_all_final.jsonl")
c = open("../../alignments/chapter-level-summary-alignments/fixed_chapter_summaries_all_final.jsonl")


section_title = "siddhartha-part-2-chapter-5-chapter-12"
source = "gradesaver"
book = "siddhartha"

sect_line_number = 19
book_line_number = 35

b_summ = ""
c_summ = ""


# returns summaries located in scripts/finished_summaries
def get_human_summary(summary_path):

    try:
        with open("../../scripts/" + summary_path, encoding='utf-8') as f:
            summary_json = json.load(f)
            return summary_json["summary"]
    except Exception as e:
        print("Failed to read summary file: {}".format(e))
        return None
    

for line in b:
    content = json.loads(line)

    if content['source'] == source and content['normalized_title'] == book:
        b_summ = get_human_summary(content['summary_path'])


for line in c:
    content = json.loads(line)

    if content['source'] == source and content['corrected_section'] == section_title:
        c_summ = get_human_summary(content['summary_path'])

b_summ = tokenize.sent_tokenize(b_summ)

c_summ = tokenize.sent_tokenize(c_summ)


print(c_summ[sect_line_number])

print("==")

print(b_summ[book_line_number])


print("===")

from bert import calculate_bertscore
calculate_bertscore.create_model()
current_score, precision, recall = calculate_bertscore.compute_score(c_summ[sect_line_number], b_summ[book_line_number])

print(current_score)