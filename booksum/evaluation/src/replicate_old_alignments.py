import pathlib
import json
import sys

def replicate_book_summaries(split):
    """function to take the title of a book and also make it the 'normalized_title' 
    (note: this data has never been normalized, and is only for testing against ACTUAL 
    normalized summaries, created through the fix_booksum_data.py file)
    """
    f = open(pathlib.Path(f"../../alignments/book-level-summary-alignments/book_summaries_aligned_{split}.jsonl"),
            encoding='utf-8')
    adjusted = []

    for line in f:
        content = json.loads(line)
        content['normalized_title'] = content['title']
        adjusted.append(content)
    
    with open(f"adjusted_book_summaries_{split}.jsonl", 'w') as n:
        for line in adjusted:
            n.write(json.dumps(line))
            n.write('\n')


def replicate_section_summaries(split):
    """function to take the title of a chapter summary and also make it the 'normalized_title' 
    (note: this data has never been normalized, and is only for testing against ACTUAL 
    normalized summaries, created through the fix_booksum_data.py file)
    """
    f = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/chapter_summary_aligned_{split}_split.jsonl"),
            encoding='utf-8')

    fixed = []

    for line in f:
        content = json.loads(line)
        content['corrected_section'] = content['book_id']
        content['normalized_title'] = content['bid']
        fixed.append(content)


    with open(f"adjusted_chapter_summaries_{split}.jsonl", 'w') as n:
        for each in fixed:
            n.write(json.dumps(each))
            n.write('\n')


def main(argv):
    """code to take original booksum data, and replicate the new information so that
    compare_sections / book_overviews / section_to_book can be used with both the original data, and the new.

    files produced with this code will not have information added, only duplicated to work with the compare_x.py files.
    these output files should be used to test the difference between the original booksum data, and the new cleaned & normalized data.
    
    this file should be used in conjuction with fix_booksum_data.py

    Args:
        argv (str): arguments
    """
    replicate_book_summaries()
    replicate_section_summaries()


if __name__ == "__main__":
    main(sys.argv[:])
