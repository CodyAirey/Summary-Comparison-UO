from nltk import tokenize
# from nltk.translate.bleu_score import sentence_bleu
from bleu import bleu_


def compute_score(token, sentence):
    token_split = tokenize.word_tokenize(token)
    sent_split = tokenize.word_tokenize(sentence)
    # current_score = sentence_bleu([token_split], sent_split, weights=(1,.0,0,0))
    current_score, precisions, bp, ratio, translation_length, reference_length = bleu_.compute_bleu(token_split, sent_split, max_order=1)
    return current_score, precisions[0]