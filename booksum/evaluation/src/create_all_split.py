import pathlib
import json

all_book_summaries = []
all_section_summaries = []
splits = ['val', 'train', 'test']

def create_chapter_all_split():
    # read in the 3 splits
    for split in splits:
        f = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/chapter_summary_aligned_{split}_split.jsonl"), encoding='utf-8')
        for line in f:
            content = json.loads(line)
            all_section_summaries.append(content)

    #write the 'all' split
    with open(f"../../alignments/chapter-level-summary-alignments/chapter_summary_aligned_all_split.jsonl", 'w') as newf:
        for line in all_section_summaries:
            newf.write(json.dumps(line))
            newf.write('\n')



def create_book_all_split():
    # read in the 3 splits
    for split in splits:
        f = open(pathlib.Path(f"../../alignments/book-level-summary-alignments/book_summaries_aligned_{split}.jsonl"), encoding='utf-8')
        for line in f:
            content = json.loads(line)
            all_book_summaries.append(content)

    #write the 'all' split
    with open(f"../../alignments/book-level-summary-alignments/book_summaries_aligned_all.jsonl", 'w') as newf:
        for line in all_book_summaries:
            newf.write(json.dumps(line))
            newf.write('\n')

def main():
    create_chapter_all_split()
    create_book_all_split()

if __name__ == "__main__":
    main()