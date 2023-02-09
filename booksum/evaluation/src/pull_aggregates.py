import pathlib
import json
import re
import sys
from dataclasses import dataclass

'''
Method to fix the "is_aggregate" column in the chapter-alignments, as it 
is based on the pre 'chapterized' fixes that the booksum repo performs.

also fix the titles to be uniform by removing roman numerals and changing aggregate chapters 
to have the same name format: chapters 3-4   ->   chapter 3 - chapter 4
'''

#yoinked from geeks for geeks | https://www.geeksforgeeks.org/python-program-for-converting-roman-numerals-to-decimal-lying-between-1-to-3999/


data_type = sys.argv[1]

library = {}


# @dataclass
# class virtual_chapter:
#     book_name: str 
#     chapter_num = int

# @dataclass
# class summary_chapter:
#     summary_id: str  #Use summary_path?
#     virtual_chapter_number: int


@dataclass
class book_coverage_item:
    source: str
    book_name: str
    chapters_covered: int
    percentage: float

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)



def romanToInt(s):

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

        
def fix_aggregates():
    f = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/chapter_summary_aligned_{data_type}_split.jsonl"),
            encoding='utf-8')

    fixed_file = []
    for line in f:
        summary = json.loads(line)

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


        #fix all options for false-negative, only 4 so just hardcode.
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

        summary['book_id'] =  summary['book_id'].replace("Around the World in 80 Days", "Around the World in Eighty Days")
        

        #fix all options for false-positives, rougly 200.
        if summary['is_aggregate'] is True:

            book_title = summary['book_id'].split(".")[0:1][0].replace(",","").replace("!","") #extracts book title as a string
            if summary['book_id'].split(".")[0:3] == ["Dr"," Jekyll and Mr", " Hyde"]:
                book_title = "Dr. Jekyll and Mr. Hyde"
            if summary['book_id'].split(".")[0:2] == ["Mrs", " Warren's Profession"]:
                book_title = "Mrs. Warren's Profession"
            if book_title == "The New Testament": #acts of the apostles causes issues because "acts", only 1 book with no other copys from another source
                continue

            #cutt off book title to just have a list of sections
            section_id = summary['book_id'].split(book_title)[1][1:]
            section_split = re.split("\.|_|-| ", section_id)

            #replace roman numerals
            for i, each in enumerate(section_split):
                if each == "Mill":
                    continue
                if(romanToInt(each.upper()) >= 1):
                    section_split[i] = str(romanToInt(each.upper()))

            #increment counter for every section found
            for section in section_split:
                if section in counter.keys():
                    counter[section] += 1

            if not any(val >= 2 for val in counter.values()):
                summary['is_aggregate'] = False
            if counter['chapters'] >= 1 or counter['scenes'] >= 1:
                summary['is_aggregate'] = True
            #single hardcoded fix, ah well.
            if summary['book_id'] == "The Winter's Tale.act 3-4.scene 3-3":
                summary['is_aggregate'] = True

        fixed_file.append(summary)
    return fixed_file

def fix_romans(corrected_title):
    keywordsz = ['act', 'canto', 'epilogue', 'scene', 'finale', 'prologue', 'chapter', 'volume', 'part', 'book', 'chapters', 'scenes']
    id_split = corrected_title.split("-")
    for i, each in enumerate(id_split):
         if each == "Mill": 
            continue
         if(romanToInt(each.upper()) >= 1):
               if id_split[i-1] in keywordsz:
                id_split[i] = str(romanToInt(each.upper()))
    corrected_title = "-".join(id_split)
    return corrected_title



def make_json(fixed_file):
    with open(f"fixed_chapter_summaries_{data_type}_final.jsonl", 'w') as f:
        for each in fixed_file:
            f.write(json.dumps(each))
            f.write('\n')

def givemetrue():

    true_array = []

    f = open(pathlib.Path(f"test_fixed_chapter_summaries_{data_type}.jsonl"),
            encoding='utf-8')
    for line in f:
        content = json.loads(line)
        if content['is_aggregate'] == True:
            true_array.append(content)

    with open(f"test_fixed_chapter_summaries_{data_type}_true.jsonl", 'w') as f:
        for each in true_array:
            f.write(json.dumps(each))
            f.write('\n')

def givemefalse():

    false_array = []

    f = open(pathlib.Path(f"test_fixed_chapter_summaries_{data_type}.jsonl"),
            encoding='utf-8')
    for line in f:
        content = json.loads(line)
        if content['is_aggregate'] == False:
            false_array.append(content)

    with open(f"test_fixed_chapter_summaries_{data_type}_false.jsonl", 'w') as f:
        for each in false_array:
            f.write(json.dumps(each))
            f.write('\n')


def normalize_titles(inputfile):
    fixed_file = []

    for content in inputfile:
        # content = json.loads(line)

        # content['book_id'] = content['book_id'].replace("Around the World in Eighty Days", "Around the World in 80 Days")

        i = 0
        id_split = re.split("\.|_|-| ", content['book_id'])
        temp_id = []

        # fix instances of "chapters_43-48" to "chapter-43-chapter-48" etc.
        try :
            while i < len(id_split):
                if id_split[i] == "chapters" and i+1 <= len(id_split) and content['is_aggregate'] == True:
                    temp_id.append("chapter")
                    temp_id.append(id_split[i+1])
                    temp_id.append("chapter")
                    # i += 2
                    i += 2
                elif id_split[i] == "scenes" and i+1 <= len(id_split) and content['is_aggregate'] == True:
                    temp_id.append("scene")
                    temp_id.append(id_split[i+1])
                    temp_id.append("scene")
                    # i += 2
                    i += 2
                elif i < len(id_split):
                    temp_id.append(id_split[i])
                    i += 1
        except:
            temp_id.append(id_split[i])
            i += 1
            continue
        
        corrected_section = "-".join(temp_id).lower().replace(",","").replace("!","")

        if temp_id[0].lower() == "the" and temp_id[1].lower() in ["two", "merry", "portrait"]:
            corrected_section = "-".join(temp_id[1:])

        if "king-henry-iv-part-1" in corrected_section:
            corrected_section = corrected_section.replace("king-henry-iv-part-1", "henry-iv-part-1")
        if "alice-in-wonderland" in corrected_section:
            corrected_section = corrected_section.replace("alice-in-wonderland", "alice's-adventures-in-wonderland")
        if "looking-backward" in corrected_section:
            corrected_section = corrected_section.replace("looking-backward", "looking-backward:-2000-1887")
        if "notes-from-the-underground":
            corrected_section = corrected_section.replace("notes-from-the-underground", "notes-from-underground")
        if "love's-labours-lost" in corrected_section:
            corrected_section = corrected_section.replace("love's-labours-lost", "love's-labour's-lost")
        if "maggie-a-girl-of-the-streets" in corrected_section:
            corrected_section = corrected_section.replace("maggie-a-girl-of-the-streets", "maggie:-a-girl-of-the-streets")


        # if title_temp[0].lower() == "the" and title_temp[1].lower() in ["two", "merry", "portrait", "invisible"]:
            # book_title = " ".join(title_temp[1:])

        # "The Merry Wives of Windsor | The Portrait of a Lady | The Two Gentlemen of Verona | The Invisible Man

        if "the-merry-wives-of-windsor" in corrected_section:
            corrected_section = corrected_section.replace("the-merry-wives-of-windsor", "merry-wives-of-windsor")
        if "the-portrait-of-a-lady" in corrected_section:
            corrected_section = corrected_section.replace("the-portrait-of-a-lady", "portrait-of-a-lady")
        if "the-two-gentlemen-of-verona" in corrected_section:
            corrected_section = corrected_section.replace("the-two-gentlemen-of-verona", "two-gentlemen-of-verona")
        if "the-invisible-man" in corrected_section:
            corrected_section = corrected_section.replace("the-invisible-man", "invisible-man")
        
        corrected_section = fix_romans(corrected_section)

        #Hardcode section fixes for few outliers
        if corrected_section == "the-ramayana-book-1-chapter-canto-chapter-1-canto-77":
            corrected_section = "the-ramayana-book-1-canto-1-canto-77"
        if corrected_section == "the-ramayana-book-2-chapter-canto-chapter-1-canto-119":
            corrected_section = "the-ramayana-book-2-canto-1-canto-119"
        if corrected_section == "the-ramayana-book-3-chapter-canto-chapter-1-canto-76":
            corrected_section = "the-ramayana-book-3-canto-1-canto-76"
        if corrected_section == "the-ramayana-book-4-chapter-canto-chapter-1-canto-67":
            corrected_section = "the-ramayana-book-4-canto-1-canto-67"
        if corrected_section == "the-ramayana-book-5-chapter-canto-chapter-1-canto-66":
            corrected_section = "the-ramayana-book-6-canto-1-canto-130"
        if corrected_section == "the-ramayana-book-6-chapter-canto-chapter-1-canto-130":
            corrected_section = "the-ramayana-book-5-canto-1-canto-66"

        content["corrected_section"] =  corrected_section

        # if "book" in corrected_section.split("-"):
        #     new_t = re.split("act|canto|epilogue|scene|finale|prolouge|chapter|volume|part", corrected_section)[0]
        #     if(new_t[len(new_t)-1] == "-"):
        #         new_t = new_t[:-1]
        #     new_t = new_t.replace("-", " ")
        #     book_title = new_t

        #     if book_title.split(" ")[0].lower() == "the":
        #         book_title = " ".join(book_title.split(" ")[1:])
        #     # if book_title == "House of Mirth book 1":
        #     #     book_title = "The House of Mirth book 1"
        #     # if book_title == "House of Mirth book 2":
        #     #     book_title = "The House of Mirth book 2"

        # else:
        book_title = content['book_id'].split(".")[0:1][0].replace(",","").replace("!","") #extracts book title as a string
        #its honestly so much easier to just hardcode these.
        if content['book_id'].split(".")[0:3] == ["Dr"," Jekyll and Mr", " Hyde"]:
            book_title = "Dr. Jekyll and Mr. Hyde"
        if content['book_id'].split(".")[0:2] == ["Mrs", " Warren's Profession"]:
            book_title = "Mrs. Warren's Profession"
        if book_title == "The New Testament": #acts of the apostles causes issues because "acts", only 1 book with no other copys from another source
            continue
        if book_title == "King Henry IV Part 1":
            book_title = "Henry IV Part 1"
        if book_title == "Alice in Wonderland":
            book_title = "Alice's Adventures In Wonderland"
        if book_title == "Looking Backward":
            book_title = "Looking Backward: 2000-1887"
        if book_title == "Notes from the Underground":
            book_title = "Notes From Underground"
        if book_title == "Love's Labours Lost":
            book_title = "Love's Labour's Lost"
        if book_title == "Maggie A Girl of the Streets":
            book_title = "Maggie: A Girl of the Streets"

        
        title_temp = book_title.split(" ")

        if title_temp[0].lower() == "the" and title_temp[1].lower() in ["two", "merry", "portrait", "invisible"]:
            book_title = " ".join(title_temp[1:])

        content['cleaned_title'] = book_title
        content['normalized_title'] = book_title.lower()
        


        fixed_file.append(content)

    return fixed_file


def setup_library(inputfile):
    for content in inputfile:
        book = content['normalized_title']

        library[book] = {
            'total_individual_chapters': 0,
            'coverage': []
        }

def create_number_of_chapters(inputfile):
    setup_library(inputfile)

    keywords = ['act', 'canto', 'epilogue', 'scene', 'finale', 'prologue', 'chapter', 'volume', 'part', 'book']

    
    # issues
    #   middlemarch book 8 goes from chapters 72 - 86 +  a finale = 16 chapters covered(including finale)
    #   Coriolanus-act-4-5-scene-5-scene-1,  scenes span over multiple acts, really stupid, only 1 instance of issue, so just hardcode. (A4,s5-s7 + A5,s1 = 4 scenes)
    # The-Winter's-Tale-act-3-4-scene-3-3, covers a whole act from scene3 to scene 3. hardcode.
    # no issues for prologues, as none are aggregates, so can just += 1 for each like normal. also no issues for anything else that im aware of.


    for book in library:
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
        for summary in inputfile:

            if summary['normalized_title'] == book:

                if summary['is_aggregate']:

                    section_t_split = summary['corrected_section'].split("-")
                    chapter_coverage = None

                    for word in keywords:
                        if section_t_split.count(word) >= 2:

                            first_chapter_number = section_t_split[section_t_split.index(word)+1] #get numbers (3 & 4) from string: "Dracula-chapter-3-chapter-4"
                            section_t_split.reverse()
                            second_chapter_number = section_t_split[section_t_split.index(word)-1] # ^^

                            if first_chapter_number.isnumeric() and second_chapter_number.isnumeric(): #avoid things like: chapter-1-chapter-finale
                                chapter_coverage = int(second_chapter_number) - (int(first_chapter_number)-1) # chapter 1 - chapter 3 should = 3 covered chapters.
                    
                    #three hardcoded fixes
                    if summary['corrected_section'] == "middlemarch-book-8-chapter-84-chapter-finale":
                        chapter_coverage = 4
                    if summary['corrected_section'] == "coriolanus-act-4-5-scene-5-scene-1":
                        chapter_coverage = 4
                    if summary['corrected_section'] == "the-winter's-tale-act-3-4-scene-3-3":
                        chapter_coverage = 4 #act3-s3, act4-s1, s2 and, s3
                    

                    if chapter_coverage == None:
                        print(f"ERROR with section: {summary['corrected_section']}") #should never happen.
                    else:
                        number_of_matches[summary['source']] += chapter_coverage
                else: #not aggregate, thank god!
                    number_of_matches[summary['source']] += 1

        library[book]['total_individual_chapters'] = max(number_of_matches.values())

    with open(f"chapter_numbers/chapter_numbers_{data_type}.jsonl", 'w') as f:
        f.write(json.dumps(library))


def calculate_source_coverage(inputfile):
    keywords = ['act', 'canto', 'epilogue', 'scene', 'finale', 'prologue', 'chapter', 'volume', 'part', 'book']
    sources = ["bookwolf", "cliffnotes", "gradesaver", "novelguide", "pinkmonkey", "shmoop", "sparknotes", "thebestnotes"]


    for book in library:
        for source in sources:
            library[book]['coverage'].append( book_coverage_item(source=source, book_name=book, chapters_covered=0, percentage=0.0) )

    for summary in inputfile:
        for book in library:

            for source in sources:

            # print(type(library[book]['coverage']))

                


                chapter_coverage = 0
                # start_chapter = None
                # end_chapter = Nones

                if summary['is_aggregate'] and summary['source'] == source and summary['normalized_title'] == book:

                    section_t_split = summary['corrected_section'].split("-")

                    for word in keywords:
                        if section_t_split.count(word) >= 2:

                            first_chapter_number = section_t_split[section_t_split.index(word)+1] #get numbers (3 & 4) from string: "Dracula-chapter-3-chapter-4"
                            section_t_split.reverse()
                            second_chapter_number = section_t_split[section_t_split.index(word)-1] # ^^

                            if first_chapter_number.isnumeric() and second_chapter_number.isnumeric(): #avoid things like: chapter-1-chapter-finale
                                chapter_coverage = int(second_chapter_number) - (int(first_chapter_number)-1) # chapter 1 - chapter 3 should = 3 covered chapters.
                                # start_chapter = first_chapter_number
                                # end_chapter = second_chapter_number
                    
                    #three hardcoded fixes
                    if summary['corrected_section'] == "middlemarch-book-8-chapter-84-chapter-finale":
                        chapter_coverage = 4
                        # start_chapter = 84
                        # end_chapter = 87
                    if summary['corrected_section'] == "coriolanus-act-4-5-scene-5-scene-1":
                        chapter_coverage = 4
                        # start_chapter = 21s
                        # end_chapter = 24

                    if summary['corrected_section'] == "the-Winter's-Tale-act-3-4-scene-3-3":
                        chapter_coverage = 4 #act3-s3, act4-s1, s2 and, s3
                        # start_chapter = 8
                        # end_chapter = 11

                elif summary['source'] == source and summary['normalized_title'] == book: #not aggregate, thank god!
                    chapter_coverage += 1

                for item in library[book]['coverage']:
                        if item.source == source:
                            item.chapters_covered += chapter_coverage
            
    
    for book in library:
        for coverage_item in library[book]['coverage']:
            if coverage_item.chapters_covered != 0:
                coverage_item.percentage =  coverage_item.chapters_covered / library[book]['total_individual_chapters']

            

    with open(f"book_coverage/book_coverage_{data_type}.jsonl", 'w') as f:
        f.write(json.dumps(library, default=vars))


def fix_book_summaries():
    f = open(pathlib.Path(f"../../alignments/book-level-summary-alignments/book_summaries_aligned_{data_type}.jsonl"),
            encoding='utf-8')
    
    fixed_file = []
    
    for line in f:
        summary = json.loads(line)
        title = summary['title'].lower()

        if title == "the merry wives of windsor":
            title = "merry wives of windsor"
        if title == "the two gentlemen of verona":
            title = "two gentlemen of verona"
        if title == "looking backward":
            title = "looking backward: 2000-1887"
        if title == "alice in wonderland":
            title = "alice's adventure in wonderland"
        if title == "notes from the underground":
            title = "notes from underground"
        if title == "around the world in 80 days":
            title = "around the world in eighty days"
        if title == "the invisible man":
            title = "invisible man"

        summary['normalized_title'] = title

        fixed_file.append(summary)

    with open(f"fixed_book_summaries_{data_type}_final.jsonl", 'w') as n:
        for each in fixed_file:
            n.write(json.dumps(each))
            n.write('\n')


    
# def calculate_source_coverage_all():
#     f = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/fixed_chapter_summaries_all_final.jsonl"),
#             encoding='utf-8')
    
#     keywords = ['act', 'canto', 'epilogue', 'scene', 'finale', 'prologue', 'chapter', 'volume', 'part', 'book']
#     sources = ["bookwolf", "cliffnotes", "gradesaver", "novelguide", "pinkmonkey", "shmoop", "sparknotes", "thebestnotes"]

#     for book in library:
#         for source in sources:
#             library[book]['coverage'].append( book_coverage_item(source=source, book_name=book, chapters_covered=0, percentage=0.0) )

#     for line in f:
#         summary = json.loads(line)
#         for book in library:

#             for source in sources:

#             # print(type(library[book]['coverage']))

                


#                 chapter_coverage = 0
#                 # start_chapter = None
#                 # end_chapter = Nones

#                 if summary['is_aggregate'] and summary['source'] == source and summary['normalized_title']:

#                     section_t_split = summary['corrected_section'].split("-")

#                     for word in keywords:
#                         if section_t_split.count(word) >= 2:

#                             first_chapter_number = section_t_split[section_t_split.index(word)+1] #get numbers (3 & 4) from string: "Dracula-chapter-3-chapter-4"
#                             section_t_split.reverse()
#                             second_chapter_number = section_t_split[section_t_split.index(word)-1] # ^^

#                             if first_chapter_number.isnumeric() and second_chapter_number.isnumeric(): #avoid things like: chapter-1-chapter-finale
#                                 chapter_coverage = int(second_chapter_number) - (int(first_chapter_number)-1) # chapter 1 - chapter 3 should = 3 covered chapters.
#                                 # start_chapter = first_chapter_number
#                                 # end_chapter = second_chapter_number
                    
#                     #three hardcoded fixes
#                     if summary['corrected_section'] == "middlemarch-book-8-chapter-84-chapter-finale":
#                         chapter_coverage = 4
#                         # start_chapter = 84
#                         # end_chapter = 87
#                     if summary['corrected_section'] == "coriolanus-act-4-5-scene-5-scene-1":
#                         chapter_coverage = 4
#                         # start_chapter = 21s
#                         # end_chapter = 24

#                     if summary['corrected_section'] == "the-Winter's-Tale-act-3-4-scene-3-3":
#                         chapter_coverage = 4 #act3-s3, act4-s1, s2 and, s3
#                         # start_chapter = 8
#                         # end_chapter = 11

#                 elif summary['source'] == source and summary['normalized_title'] == book: #not aggregate, thank god!
#                     chapter_coverage += 1

#                 for item in library[book]['coverage']:
#                         if item.source == source:
#                             item.chapters_covered += chapter_coverage
            
    
#     for book in library:
#         for coverage_item in library[book]['coverage']:
#             if coverage_item.chapters_covered != 0:
#                 coverage_item.percentage =  coverage_item.chapters_covered / library[book]['total_individual_chapters']

            

#     with open(f"book_coverage_all.jsonl", 'w') as f:
#         f.write(json.dumps(library, default=vars))

# def create_number_of_chapters_all():
#     f = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/fixed_chapter_summaries_all_final.jsonl"),
#             encoding='utf-8')
    
#     inputfile = []
    
#     for line in f:
#         summary = json.loads(line)
#         inputfile.append(summary)
    
#     setup_library(inputfile)

#     keywords = ['act', 'canto', 'epilogue', 'scene', 'finale', 'prologue', 'chapter', 'volume', 'part', 'book']

    
#     # issues
#     #   middlemarch book 8 goes from chapters 72 - 86 +  a finale = 16 chapters covered(including finale)
#     #   Coriolanus-act-4-5-scene-5-scene-1,  scenes span over multiple acts, really stupid, only 1 instance of issue, so just hardcode. (A4,s5-s7 + A5,s1 = 4 scenes)
#     # The-Winter's-Tale-act-3-4-scene-3-3, covers a whole act from scene3 to scene 3. hardcode.
#     # no issues for prologues, as none are aggregates, so can just += 1 for each like normal. also no issues for anything else that im aware of.


#     for book in library:
#         number_of_matches = {
#             "bookwolf"     : 0,
#             "cliffnotes"   : 0,
#             "gradesaver"   : 0,
#             "novelguide"   : 0,
#             "pinkmonkey"   : 0,
#             "shmoop"       : 0,
#             "sparknotes"   : 0,
#             "thebestnotes" : 0
#         }
#         for summary in inputfile:

#             if summary['normalized_title'] == book:

#                 if summary['is_aggregate']:

#                     section_t_split = summary['corrected_section'].split("-")
#                     chapter_coverage = None

#                     for word in keywords:
#                         if section_t_split.count(word) >= 2:

#                             first_chapter_number = section_t_split[section_t_split.index(word)+1] #get numbers (3 & 4) from string: "Dracula-chapter-3-chapter-4"
#                             section_t_split.reverse()
#                             second_chapter_number = section_t_split[section_t_split.index(word)-1] # ^^

#                             if first_chapter_number.isnumeric() and second_chapter_number.isnumeric(): #avoid things like: chapter-1-chapter-finale
#                                 chapter_coverage = int(second_chapter_number) - (int(first_chapter_number)-1) # chapter 1 - chapter 3 should = 3 covered chapters.
                    
#                     #three hardcoded fixes
#                     if summary['corrected_section'] == "middlemarch-book-8-chapter-84-chapter-finale":
#                         chapter_coverage = 4
#                     if summary['corrected_section'] == "coriolanus-act-4-5-scene-5-scene-1":
#                         chapter_coverage = 4
#                     if summary['corrected_section'] == "the-winter's-tale-act-3-4-scene-3-3":
#                         chapter_coverage = 4 #act3-s3, act4-s1, s2 and, s3
                    

#                     if chapter_coverage == None:
#                         print(f"ERROR with section: {summary['corrected_section']}") #should never happen.
#                     else:
#                         number_of_matches[summary['source']] += chapter_coverage
#                 else: #not aggregate, thank god!
#                     number_of_matches[summary['source']] += 1

#         library[book]['total_individual_chapters'] = max(number_of_matches.values())

#     with open(f"chapter_numbers_all.jsonl", 'w') as f:
#         f.write(json.dumps(library, default=vars))

def main():
    #Fixing book aggregates
    file = fix_aggregates()
    finished_file = normalize_titles(file)
    create_number_of_chapters(finished_file)
    calculate_source_coverage(finished_file)
    
    fix_book_summaries()
    make_json(finished_file)

    # calculate_source_coverage_all()
    # create_number_of_chapters_all()
    # givemetrue()
    # givemefalse()

    
    
if __name__ == "__main__":
    main()


#TODO refactor into smaller functions, title adjustment and title normalization should be separated. 