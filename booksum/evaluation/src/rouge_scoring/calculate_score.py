import rouge_scoring
from rouge_scoring.rouge_scoring import rouge_n
from rouge_scoring.rouge_scoring import rouge_l_sentence_level



def compute_score_1n(token, sentence):
    current_score, precision, recall = rouge_n([token], [sentence], n=1)
    return current_score, precision, recall


def compute_score_2n(token, sentence):
    current_score, precision, recall = rouge_n([token], [sentence], n=2)
    return current_score, precision, recall


def compute_score_l(token, sentence):
    current_score, precision, recall = rouge_l_sentence_level([token], [sentence])
    return current_score, precision, recall