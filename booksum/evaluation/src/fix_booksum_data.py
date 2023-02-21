import pathlib
import json
import re
import sys
from dataclasses import dataclass

'''
Code to fix the "is_aggregate" column in the chapter-alignments, as it 
is based on the pre 'chapterized' fixes that the booksum repo performs.

also fix the titles to be uniform by removing roman numerals and changing aggregate chapters 
to have the same name format: chapters 3-4   ->   chapter 3 - chapter 4
'''

keywords = ['act', 'canto', 'epilogue', 'scene', 'finale', 'prologue', 'chapter', 'volume', 'part', 'book']
sources = ["bookwolf", "cliffnotes", "gradesaver", "novelguide", "pinkmonkey", "shmoop", "sparknotes", "thebestnotes"]
data_type = sys.argv[1]
library = {}

hardcoded_fixes = {
    "middlemarch-book-8-chapter-84-chapter-finale": 4,
    "coriolanus-act-4-5-scene-5-scene-1": 4,
    "the-winter's-tale-act-3-4-scene-3-3": 4,
}

@dataclass
class book_coverage_item:
    source: str
    book_name: str
    chapters_covered: int
    percentage: float

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


# yoinked from geeks for geeks | https://www.geeksforgeeks.org/python-program-for-converting-roman-numerals-to-decimal-lying-between-1-to-3999/
def romanToInt(s):
    """Given a string, return its number in roman numberals, -1 if not.
    Only takes uppercase strings

    Args:
        s (str): string to calculate roman numeral for

    Returns:
        int: roman numeral to decimal conversion, -1 if not applicable
    """
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


def extract_book_title_from_id(id):
    book_title = id.split(".")[0:1][0].replace(
        ",", "").replace("!", "")  # extracts book title as a string
    if id.split(".")[0:3] == ["Dr", " Jekyll and Mr", " Hyde"]:
        book_title = "Dr. Jekyll and Mr. Hyde"
    if id.split(".")[0:2] == ["Mrs", " Warren's Profession"]:
        book_title = "Mrs. Warren's Profession"
    return book_title

def fix_aggregates():
    """Function updates jsonl alignments to have a corrected 'is_aggregate' column, matching the data after being cleaned.
    running the 'chapterized' section of the booksum repo doesn't update the "is_aggregate" column, this function aims to fix that.
    if a pair of keywords, such as 'chapter' is found, then the section must be aggregate. eg. Dracula-chapter-3-chapter-4
    if keyword is plural, must cover multiple 'chapters'

    Returns:
        list: jsonl list with the adjusted aggregate column
    """
    f = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/chapter_summary_aligned_{data_type}_split.jsonl"),
             encoding='utf-8')

    fixed_file = []
    for line in f:
        summary = json.loads(line)

        #all possible keywords from booksum
        counter = {
            'act':      0,
            'canto':    0,
            'epilogue': 0,
            'scene':    0,
            'scenes':   0,
            'finale':   0,
            'prologue': 0,
            'chapter':  0,
            'volume':   0,
            'part':     0,
            'book':     0,
            'chapters': 0
        }

        # fix all options for false-negative, only 4 so just hardcode.
        if summary['source'] == "sparknotes" and summary['book_id'] == "Coriolanus.act ii-iii.scenes iii-i":
            summary['is_aggregate'] = True
            continue
        if summary['source'] == "sparknotes" and summary['book_id'] == "Coriolanus.act iii-iv.scenes ii-iv":
            summary['is_aggregate'] = True
            continue
        if summary['source'] == "sparknotes" and summary['book_id'] == "The Turn of the Screw.prologue":
            summary['is_aggregate'] = True
            continue
        if summary['source'] == "bookwolf" and summary['book_id'] == "Hamlet.act 4.scenes 2-3":
            summary['is_aggregate'] = True
            continue
        if summary['source'] == "sparknotes" and summary['book_id'] == "The New Testament.acts of the apostles":
            summary['is_aggregate'] = True

        # fix all options for false-positives, rougly 200.
        if summary['is_aggregate'] is True:

            book_title = extract_book_title_from_id(summary['book_id'])

            # cut off book title to just have a list of sections
            section_id = summary['book_id'].split(book_title)[1][1:]
            section_split = re.split("\.|_|-| ", section_id)

            #count for aggregates
            for section in section_split:
                if section in counter.keys():
                    counter[section] += 1

            #change aggregate based on counter.
            if not any(val >= 2 for val in counter.values()):
                summary['is_aggregate'] = False
            if counter['chapters'] >= 1 or counter['scenes'] >= 1:
                summary['is_aggregate'] = True

            # single hardcoded fix. (issue for 'books' that cover multiple acts from scenes other than the first.)
            if summary['book_id'] == "The Winter's Tale.act 3-4.scene 3-3":
                summary['is_aggregate'] = True

        fixed_file.append(summary)
    return fixed_file


def fix_romans(corrected_title):
    """Function to take a hypen-separated-title and fix any roman numerals it contains,

    Args:
        corrected_title (str): hypen-separated-tytle

    Returns:
        str: title with romans converted to ints
    """
    keywordsz = ['act', 'canto', 'epilogue', 'scene', 'finale', 'prologue',
                 'chapter', 'volume', 'part', 'book', 'chapters', 'scenes']
    id_split = corrected_title.split("-")
    for i, each in enumerate(id_split):
        if each == "Mill": #special case for book: "floss on the mill"
            continue
        if (romanToInt(each.upper()) >= 1):
            if id_split[i-1] in keywordsz:
                id_split[i] = str(romanToInt(each.upper()))
    corrected_title = "-".join(id_split)
    return corrected_title


def make_json(fixed_file):
    with open(f"../../alignments/chapter-level-summary-alignments/fixed_section_summaries_{data_type}.jsonl", 'w') as f:
        for each in fixed_file:
            f.write(json.dumps(each))
            f.write('\n')


def correct_section(summary):
    i = 0
    id_split = re.split("\.|_|-| ", summary['book_id'])
    temp_id = []

    # fix instances of "chapters_43-48" to "chapter-43-chapter-48" etc.
    while i < len(id_split):
        if id_split[i] == "chapters" and i+1 <= len(id_split) and summary['is_aggregate'] == True:
            temp_id.append("chapter")
            temp_id.append(id_split[i+1])
            temp_id.append("chapter")
            i += 2
        elif id_split[i] == "scenes" and i+1 <= len(id_split) and summary['is_aggregate'] == True:
            temp_id.append("scene")
            temp_id.append(id_split[i+1])
            temp_id.append("scene")
            i += 2
        elif i < len(id_split):
            temp_id.append(id_split[i])
            i += 1

    corrected_section = "-".join(temp_id).lower().replace(",", "").replace("!", "")

    #remove 'the' off the front of select titles to create more alignments between correlated titles
    # "The Merry Wives of Windsor | The Portrait of a Lady | The Two Gentlemen of Verona | The Invisible Man
    #note, could do a one size fix all solution, but it feels wrong to needlessly cut "the" off titles that should have it.
    if temp_id[0].lower() == "the" and temp_id[1].lower() in ["two", "merry", "portrait"]:
            corrected_section = "-".join(temp_id[1:])

    return corrected_section

def normalize_titles(inputfile):
    fixed_file = []

    for summary in inputfile:

        summary['book_id'] = summary['book_id'].replace("Around the World in 80 Days", "Around the World in Eighty Days")

        # fix instances of "chapters_43-48" to "chapter-43-chapter-48" etc.
        corrected_section = correct_section(summary)

        # Hardcode section fixes for few outliers
        corrected_section = corrected_section.replace("king-henry-iv-part-1", "henry-iv-part-1")
        corrected_section = corrected_section.replace("alice-in-wonderland", "alice's-adventures-in-wonderland")
        corrected_section = corrected_section.replace("looking-backward", "looking-backward:-2000-1887")
        corrected_section = corrected_section.replace("notes-from-the-underground", "notes-from-underground")
        corrected_section = corrected_section.replace("love's-labours-lost", "love's-labour's-lost")
        corrected_section = corrected_section.replace("maggie-a-girl-of-the-streets", "maggie:-a-girl-of-the-streets")
        corrected_section = corrected_section.replace("the-invisible-man", "invisible-man")

        corrected_section = fix_romans(corrected_section)

        corrected_section = corrected_section.replace("the-ramayana-book-1-chapter-canto-chapter-1-canto-77", "the-ramayana-book-1-canto-1-canto-77")
        corrected_section = corrected_section.replace("the-ramayana-book-2-chapter-canto-chapter-1-canto-119", "the-ramayana-book-2-canto-1-canto-119")
        corrected_section = corrected_section.replace("the-ramayana-book-3-chapter-canto-chapter-1-canto-76", "the-ramayana-book-3-canto-1-canto-76")
        corrected_section = corrected_section.replace("the-ramayana-book-4-chapter-canto-chapter-1-canto-67", "the-ramayana-book-4-canto-1-canto-67")
        corrected_section = corrected_section.replace("the-ramayana-book-5-chapter-canto-chapter-1-canto-66", "the-ramayana-book-5-canto-1-canto-66")
        corrected_section = corrected_section.replace("the-ramayana-book-6-chapter-canto-chapter-1-canto-130", "the-ramayana-book-6-canto-1-canto-130")


        summary["corrected_section"] = corrected_section

        # hardcoded fixes so that regular loops can work.
        book_title = summary['book_id'].split(".")[0:1][0].replace(",", "").replace("!", "")  # extracts book title as a string

        #Hardcoded title fixes here.

        book_id = summary['book_id']
        if book_id.startswith("Dr. Jekyll and Mr. Hyde"):
            book_title = "Dr. Jekyll and Mr. Hyde"
        elif book_id.startswith("Mrs. Warren's Profession"):
            book_title = "Mrs. Warren's Profession"

        hardcoded_title_fixes = {
            "King Henry IV Part 1": "Henry IV Part 1",
            "Alice in Wonderland": "Alice's Adventures In Wonderland",
            "Looking Backward": "Looking Backward: 2000-1887",
            "Notes from the Underground": "Notes From Underground",
            "Love's Labours Lost": "Love's Labour's Lost",
            "Maggie A Girl of the Streets": "Maggie: A Girl of the Streets"
        }

        book_title = hardcoded_title_fixes.get(book_title, book_title)

        title_temp = book_title.split(" ")
        if title_temp[0].lower() == "the" and title_temp[1].lower() in ["two", "merry", "portrait", "invisible"]:
            book_title = " ".join(title_temp[1:])

        summary['cleaned_title'] = book_title
        summary['normalized_title'] = book_title.lower()

        fixed_file.append(summary)

    return fixed_file


def setup_library(inputfile):
    for content in inputfile:
        book = content['normalized_title']

        library[book] = {
            'total_individual_chapters': 0,
            'coverage': []
        }

def create_number_of_chapters(inputfile):
    """ estimates the number of chapters in a book by counting the number of 
    individual chapters/the number of chapters covered in a section(aggregate), the 
    results are output to a jsonl located in the summary_correlation_data folder.

    Args:
        inputfile (list): jsonl data after being cleaned via fix_aggregates()

    Raises:
        ValueError: error when a section could not have its number of chapters calculated
    """
    setup_library(inputfile)
    for book in library:
        number_of_matches = {source: 0 for source in ["bookwolf", "cliffnotes", "gradesaver", "novelguide", "pinkmonkey", "shmoop", "sparknotes", "thebestnotes"]}

        for summary in inputfile:
            if summary['normalized_title'] == book:
                if summary['is_aggregate']:
                    chapter_coverage = calc_agg_chap_coverage(summary)
                    number_of_matches[summary['source']] += chapter_coverage
                else:
                    number_of_matches[summary['source']] += 1

        library[book]['total_individual_chapters'] = max(number_of_matches.values())

    with open(f"../summary_correlation_data/fixed/chapter_numbers/chapter_numbers_{data_type}.jsonl", 'w') as f:
        json.dump(library, f)


def calc_agg_chap_coverage(summary):
    """Function to calculate how many chapters/scenes/etc a summary/section tries to cover

    Args:
        summary (dict): summary to calculate coverage for

    Raises:
        ValueError: unable to calculate chapters covered based off section title

    Returns:
        int: number of chapters that the summary/section covers
    """
    chapter_coverage = None
    section_t_split = summary['corrected_section'].split("-")

    for word in keywords:
        if section_t_split.count(word) >= 2:
            first_chapter_number = section_t_split[section_t_split.index(word) + 1]
            section_t_split.reverse()
            second_chapter_number = section_t_split[section_t_split.index(word) - 1]
            if first_chapter_number.isnumeric() and second_chapter_number.isnumeric():
                chapter_coverage = int(second_chapter_number) - (int(first_chapter_number) - 1)

    if summary['corrected_section'] in hardcoded_fixes:
        chapter_coverage = hardcoded_fixes[summary['corrected_section']]

    if chapter_coverage is None:
        raise ValueError(f"ERROR with section: {summary['corrected_section']}")
    else:
        return chapter_coverage
    

def calculate_source_coverage(inputfile):
    """Function to calculate how much of a book each source covers.

    Args:
        inputfile (list): jsonl data after being cleaned via fix_aggregates()
    """

    # Define the sources to search for
    # Create an empty coverage item for each book/source combination in the library
    for book in library:
        for source in sources:
            library[book]['coverage'].append({
                'source': source,
                'book_name': book,
                'chapters_covered': 0,
                'percentage': 0.0,
            })

    # Loop through each summary in the input file and update the coverage information
    for summary in inputfile:
        for book in library:
            for source in sources:
                chapter_coverage = 0

                # If this is an aggregate summary for the current book and source,
                # calculate the number of chapters covered based on the section title
                if summary['is_aggregate'] and summary['source'] == source and summary['normalized_title'] == book:
                    chapter_coverage = calc_agg_chap_coverage(summary)

                # If non-agg summary for the current book and source,
                elif summary['source'] == source and summary['normalized_title'] == book:
                    chapter_coverage = 1
                # Update the coverage item for this book and source with the new chapter coverage
                for item in library[book]['coverage']:
                    if item['source'] == source:
                        item['chapters_covered'] += chapter_coverage

    # Calculate the percentage of individual chapters covered for each source/book combination
    for book in library:
        for coverage_item in library[book]['coverage']:
            if coverage_item['chapters_covered'] != 0:
                coverage_item['percentage'] = coverage_item['chapters_covered'] / library[book]['total_individual_chapters']

    # Write the coverage data to a JSON file
    with open(f"../summary_correlation_data/fixed/book_coverage/book_coverage_{data_type}.jsonl", 'w') as f:
        f.write(json.dumps(library, default=vars))


def fix_book_summaries():
    """
    Function to fix book titles that should align, as they cover the same book.
    """
    # Open the file containing the book summaries for the given data type.
    with open(pathlib.Path(f"../../alignments/book-level-summary-alignments/book_summaries_aligned_{data_type}.jsonl"), encoding='utf-8') as f:
        
        fixed_file = []
        
        # Iterate over each line (summary) in the input file.
        for line in f:
            # Parse the JSON summary data.
            summary = json.loads(line)
            # Get the lowercase version of the book title.
            title = summary['title'].lower()

            # Fix the normalized title for specific books that have title inconsistencies.
            normalized_titles = {
                "the merry wives of windsor": "merry wives of windsor",
                "the two gentlemen of verona": "two gentlemen of verona",
                "looking backward": "looking backward: 2000-1887",
                "alice in wonderland": "alice's adventure in wonderland",
                "notes from the underground": "notes from underground",
                "around the world in 80 days": "around the world in eighty days",
                "the invisible man": "invisible man"
            }
            title = normalized_titles.get(title, title)

            # Add the fixed normalized title to the summary data.
            summary['normalized_title'] = title
            fixed_file.append(summary)

    # Write the fixed summaries to a new file.
    with open(f"../../alignments/book-level-summary-alignments/fixed_book_summaries_{data_type}.jsonl", 'w') as n:
        for each in fixed_file:
            n.write(json.dumps(each))
            n.write('\n')

def main():
    # Fixing book aggregates
    file = fix_aggregates()

    finished_file = normalize_titles(file)
    
    create_number_of_chapters(finished_file)
    calculate_source_coverage(finished_file)

    # fix_book_summaries()


    make_json(finished_file)

    # givemetrue()
    # givemefalse()


if __name__ == "__main__":
    main()
