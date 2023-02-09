import pathlib
import json
import sys

f = open(pathlib.Path(f"../../alignments/book-level-summary-alignments/book_summaries_aligned_all.jsonl"),
        encoding='utf-8')

fixed = []

for line in f:
    content = json.loads(line)
    content['normalized_title'] = content['title']
    fixed.append(content)

with open(f"adjusted_book_summaries_all_final.jsonl", 'w') as n:
    for each in fixed:
        n.write(json.dumps(each))
        n.write('\n')




f = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/chapter_summary_aligned_all_split.jsonl"),
        encoding='utf-8')

fixed = []

for line in f:
    content = json.loads(line)
    content['corrected_section'] = content['book_id']
    content['normalized_title'] = content['bid']
    fixed.append(content)


with open(f"adjusted_chapter_summaries_all_final.jsonl", 'w') as n:
    for each in fixed:
        n.write(json.dumps(each))
        n.write('\n')