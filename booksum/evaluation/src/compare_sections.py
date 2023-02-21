import numpy as np
import math
from nltk import tokenize
import json
import sys
import getopt
import pathlib
import time
import pandas as pd

sys.path.append('source_modules')

human_summaries = dict()
summaries_count = 0
summary_comparison_data = []
line_by_line_data = []
used_files = []
unique_books = set()
unique_used_books = set()
unique_chapters = set()
unique_used_chapters = set()
library = {}
allignment_tables = {}
chapter_numbers = {}
average_books = {}
number_of_matches = {
    "bookwolf": dict(),
    "cliffnotes": dict(),
    "gradesaver": dict(),
    "novelguide": dict(),
    "pinkmonkey": dict(),
    "shmoop": dict(),
    "sparknotes": dict(),
    "thebestnotes": dict()
}
# source1 ----------book1 -------total_aggreagte_sections = 0
#           \              \---- total_agg_sections_used = 0
#            \              \ ---total_sections = 0
#             \              \---used_sections = 0
#              \              \-- { section_name_1 { sources : [s1, s2,s3], word_count : 123 },
#                                 , section_name_2 { sources : [s2, s4,s7], word_count : 213 }
#                                  , ...etc.etc  { sources : [s1, s2,s3], word_count : 123 }
#               \              \-
#                \
#                 \-book2 ----- etc ^
# souce2 ---- etc.


def setup_matches_datastructure(split, dataset):
    f = open(pathlib.Path(f"../../alignments/chapter-level-summary-alignments/{dataset}_chapter_summaries_{split}_final.jsonl"),
             encoding='utf-8')

    for line in f:
        content = json.loads(line)

        library[content['normalized_title']] = {
            'total_sections_used': 0, # that are found elsewhere / compared with.
            'total_aggregate_sections': 0,
            'total_aggregate_sections_compared': 0, #that are found elsewhere / compared with.
            'total_non-aggregate_sections': 0,
            'total_non-aggregate_sections_compared': 0, # that are found elsewhere / compared with.
            'non-aggregate_sections_compared': dict(),
            'aggregate_sections_compared': dict(), #that are found elsewhere / compared with.
            'non-aggregate_sections_not_compared': dict(),
            'aggregate_sections_not_compared': dict()
        }

        text = get_human_summary(content['summary_path'])
        
        if text is not None:
            try:
                human_summaries[content['summary_path']] = {
                    "book": content['normalized_title'],
                    "section_title": content['corrected_section'],
                    "source": content['source'],
                    "summary_text": text,
                    'is_aggregate': content['is_aggregate'],
                    'chapter_path': content['chapter_path']
                }

                print(f"Found {content['c_title']}")
            except:
                continue
    print("Evaluating {} summary documents...".format(len(human_summaries)))


def result_printout(metric):
    """Prints out the results for summary comparison

    Args:
        function (str): the function used in the test
    """
    print("Unique chapters covered: {}".format(len(unique_chapters)))
    print("Unique chapters used: {}".format(len(unique_used_chapters)))
    FUNC_list = [data_item[0] for data_item in summary_comparison_data]
    FUNC_mean = sum(FUNC_list) / len(FUNC_list)
    print(f"Mean {metric}: {FUNC_mean}")
    print()


# returns summaries located in scripts/finished_summaries
def get_human_summary(summary_path):
    """ Retrieves the summary text from the given path

    Args:
        summary_path (str): filepath to summary

    Returns:
        str: summary text
    """
    try:
        with open("../../scripts/" + summary_path, encoding='utf-8') as f:
            summary_json = json.load(f)
            return summary_json["summary"]
    except Exception as e:
        print("Failed to read summary file: {}".format(e))
        return None

def setup_model(metric):  # there has got to be a better way to do this.
    """Sets up a model if required, using given function

    Args:
        function (str): function used for test

    Returns:
        _type_: _description_
    """
    if metric == "bert":
        from bert import calculate_score
        calculate_score.create_model()
    elif metric == "bertscore":
        from bert import calculate_bertscore
        calculate_bertscore.create_model()
        from qaeval_scoring import calculate_score
        calculate_score.create_model()
    elif metric == "summac":
        from summac_scoring import calculate_score
        calculate_score.create_model()
    elif metric == "bartscore":
        from bartscore import calculate_score
        calculate_score.create_model()


def calculate_F1(metric):
    """Scores each section summary (reference document) against its corresponding (hypothesis document),
    summaries (if any) from different source(s). Each reference sentence is scored against all hypothesis
    sentences individually, taking the max F1 score from the lot (a single sentence to sentence pair 
    with the greatest similarity).

    The final score for the two summaries is calculated by averaging each of the max-sentence-f1 scores.

    Starts by looping over all summaries, and scoring the similarity between reviews from different sources for the same book. 
    E.G. Dracula.chapter1.sparknotes vs Dracula.chapter1.bookwolf, Dracula.chapter1.gradesaver

    chapter is compared one sentence at a time to ensure uniform comparing methods for each function
    (some can't handle multiple at once)

    Args:
        metric (str): the metric to use to calculate score

    Returns:
    """
    start_time = time.time()
    summaries_count = 0

    #Loop over each Reference Summary
    for summary_path, ref_summary in human_summaries.items():

        ref_sum_book = ref_summary['book']
        section_title = ref_summary['section_title']
        source = ref_summary['source']
        summary_text = ref_summary['summary_text']
        is_aggregate = ref_summary['is_aggregate']
        

        unique_books.add(section_title) #add to set.

        #grab all summaries with same title but different source (matching sections to compare with one another) aka related.
        related_summaries = list(filter(lambda curr_summary: curr_summary['section_title'] == ref_summary['section_title'] and curr_summary['source'] != ref_summary['source'], human_summaries.values()))


        if ref_summary['is_aggregate'] == True:
            library[ref_summary['book']]['total_aggregate_sections'] += 1
        else:
            library[ref_summary['book']]['total_non-aggregate_sections'] += 1

        # if there are no related summary documents, then just print.
        if len(related_summaries) == 0:
            print(f"No related summary documents were found for {section_title}.")
            if(is_aggregate):
                library[ref_summary['book']]['aggregate_sections_not_compared'][section_title] = [source]
            else:
                library[ref_summary['book']]['non-aggregate_sections_not_compared'][section_title] = [source]
            continue #no need to perform calculation


        if is_aggregate:
            library[ref_summary['book']]['aggregate_sections_compared'][section_title] = [source]
        else:
            library[ref_summary['book']]['non-aggregate_sections_compared'][section_title] = [source]

        related_summary_texts = []
        for summary2 in related_summaries: #same title, diff source.
            related_summary_texts.append(summary2['summary_text'])
            if is_aggregate:
                library[ref_summary['book']]['aggregate_sections_compared'][section_title].append(summary2['source'])
                library[ref_summary['book']]['total_aggregate_sections_compared'] += 1
                library[ref_summary['book']]['total_sections_used'] += 1
            else: #not aggregate
                library[ref_summary['book']]['non-aggregate_sections_compared'][section_title].append(summary2['source'])
                library[ref_summary['book']]['total_non-aggregate_sections_compared'] += 1
                library[ref_summary['book']]['total_sections_used'] += 1
            
        # prep text by tokenizing it into sentencesgi
        ref_doc = tokenize.sent_tokenize(summary_text)
        tokenized_sums = []
        for cursum in related_summary_texts:
            tokenized_sums.append(tokenize.sent_tokenize(cursum))

        temp_time = time.time()
        unique_sents = dict()
        max_scores = []

        for hyp_summary in related_summaries:
            hyp_doc = tokenize.sent_tokenize(hyp_summary['summary_text'])
            sentence_scores = []
            

            for ref_sent_index, ref_sent in enumerate(ref_doc):
                best_score = -math.inf
                best_score_index = -1
                for hyp_sent_index, hyp_sent in enumerate(hyp_doc):
                    current_score = "!"
                    precision = "NA"
                    recall = "NA"

                    current_score, precision, recall = compute_single_score(metric, ref_sent, hyp_sent)

                    if current_score > best_score:
                        best_score = current_score
                        best_score_index = hyp_sent_index

                    line_by_line_data.append([ref_summary['section_title'], ref_summary['source'], hyp_summary['source'], ref_sent_index, hyp_sent_index, current_score, precision, recall])
                sentence_scores.append(best_score)

                if hyp_summary['source'] in unique_sents.keys():
                    unique_sents[hyp_summary['source']].add(best_score_index)
                else:
                    unique_sents[hyp_summary['source']] = {best_score_index}
            max_scores.append(np.mean(sentence_scores))
            # print(f"{sentence_scores} => {np.mean(sentence_scores)}")
            # print("Unique sentences:", len(unique_sents), "out of", len(ref_doc), "ref sents. :", unique_sents)
            mean_sent_score = np.mean(sentence_scores)

        # print(f"{np.mean(max_scores)}")
        mean_max_score = np.mean(max_scores)
        summary_comparison_data.append([mean_max_score, section_title, ref_summary['source'], unique_sents])
        unique_used_books.add(section_title)
        summaries_count += 1

        print(section_title, "-", ref_summary['source'], "- time:", round((time.time() - temp_time), 3), "seconds.")

        # if summaries_count >= 10:
        #     break

    total_time = (time.time() - start_time)
    print(summaries_count)
    print("time total:", round(total_time, 1), "seconds.", "Average:", (total_time / summaries_count))

    return

def compute_single_score(metric, ref_sent, hyp_sent):
    """Calculates an f1 score between two sentences depending on the metric used 
    Args:
        metric (str): metric to denote how the calculation is performed
        ref_sent (str): reference sentence
        hyp_sent (str): hypothesis sentence

    Returns:
        float: f1 score based on how similar the ref_sent and hyp_sent are
    """

    current_score, precision, recall = "NA", "NA", "NA" #initilze value to something error worthy if not changed.

    # calculate score based on metric, p.s. surely there is a better way to do this.
    if metric == "bleu":
        from bleu import calculate_score
        current_score, precision = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "bert":
        from bert import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "bertscore":
        from bert import calculate_bertscore
        current_score, precision, recall = calculate_bertscore.compute_score(ref_sent, hyp_sent)
    elif metric == "rouge-1n":
        from source_modules.rouge_scoring import calculate_score
        current_score, precision, recall = calculate_score.compute_score_1n(ref_sent, hyp_sent)
    elif metric == "rouge-2n":
        from rouge_scoring import calculate_score
        current_score, precision, recall = calculate_score.compute_score_2n(ref_sent, hyp_sent)
    elif metric == "rouge-l":
        from rouge_scoring import calculate_score
        current_score, precision, recall = calculate_score.compute_score_l(ref_sent, hyp_sent)
    elif metric == "moverscore":
        from moverscore import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "qaeval":
        from qaeval_scoring import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "meteor":
        from meteor import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "summac":
        from summac_scoring import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "bartscore":
        from bartscore import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)
    elif metric == "chrf":
        from chrf import calculate_score
        current_score = calculate_score.compute_score(ref_sent, hyp_sent)

    return current_score, precision, recall

def write_summary_count_to_json(split, filename, dataset):
    with open(f"../summary_count/{dataset}-section-comparison-counts-postfix-{split}-{filename}.json", 'w') as f:
        f.write(json.dumps(library))
            

def write_to_csv(metric, split, filename, dataset):
    df = pd.DataFrame(summary_comparison_data, columns=[ metric, "Section Title", "Source", "Unique sentences used"])
    df.to_csv(
        f"../csv_results/booksum_summaries/section/{dataset}-section-comparison-results-{split}-{filename}.csv")
    
    df = pd.DataFrame(line_by_line_data, columns=["Section Title", "Reference Source", "Hypothesis Source", "Reference Sentence Index", "Hypothesis Sentence Index", (metric + "score"), "Precision", "Recall"])
    df.to_csv(
        f"../csv_results/booksum_summaries/line_by_line_section/{dataset}section-comparison-results-{split}-{filename}-lbl.csv")


def arg_print_help(metric_list, split_list, dataset_list):
    """Prints useful help commands when user uses file with incorrect arguments

    Args:
        metrics_list (list): list of possible metrics (currently supported)
        split_list (list): list of possible splits supported
        dataset_list (list): list of possible data file types supported
    """
    print(f"""Usage: compare_sections.py -m <metric> -o <output-csv-filename> -s <split> -d <dataset> \n
          ---- \n
          Metrics: {metric_list}\n
          Possible Splits: {split_list}\n
          Possible Data Sets: {dataset_list}\n
          Example filename: bartscore-postfix""")


def arg_handler(argv):
    """Function that handles arguments given in command line
    Metric: the metric to use for the f1 calculation
    Outputfile: name of the file to be output
    Split: The input data you want from booksum alignment
    dataset: fixed or adjusted summary data"""
    metric = None
    outputfile = None
    split = None
    dataset = None
    metric_list = ["bleu", "bert", "bertscore", "rouge-1n", "rouge-2n", "rouge-l",
                     "moverscore", "qaeval", "meteor", "summac", "bartscore", "chrf"]
    split_list = ["test", "train", "val", "all"]

    dataset_list = ["fixed", "adjusted"]

    if (len(argv) <= 5):
        arg_print_help(metric_list, split_list, dataset_list)
        sys.exit(2)

    # used getopt for first time to handle arguments, works well but feels messy. Will try another solution next time
    try:
        opts, args = getopt.getopt(
            argv, "hm:o:s:d:", ["help", "metric=", "ofile=", "split=", "data="])
    except getopt.GetoptError:
        arg_print_help(metric_list)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            arg_print_help(metric_list)
            sys.exit()
        elif opt in ("-m", "--metric"):
            metric = arg
            if metric not in metric_list or metric == '' or metric == None:
                print("Metric not acceptable, please use one of:", metric_list)
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
        elif opt in ("-d", "--data"):
            dataset = arg
            if dataset not in dataset_list:
                print("Data set not acceptable, please use on of:", dataset_list)
                sys.exit(2)

    print('Metric is:', metric)
    print('Output file is:', outputfile)
    print('Split is:', split)
    print("Data set is:", dataset)
    return metric, outputfile, split, dataset


def main(argv):
    """Main method takes arguments for Function, OutputFilename, and Split to use.
    Afterwhich, it calculates the score for all booksum sections and writes the output to a file.

    Args:
        argv (list): filename, metric, split, dataset
    """
    metric, outputfile, split, dataset = arg_handler(argv)

    #preamble methods
    setup_matches_datastructure(split, dataset)
    setup_model(metric)
    
    calculate_F1(metric)
    
    result_printout(metric)
    write_to_csv(metric, split, outputfile, dataset)
 
    write_summary_count_to_json(split, outputfile, dataset)


if __name__ == "__main__":
    main(sys.argv[1:])
