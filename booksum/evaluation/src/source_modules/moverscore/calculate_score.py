from moverscore.moverscore_v2 import word_mover_score
from typing import List, Union, Iterable
from collections import defaultdict
import numpy as np



def compute_score(token, sentence):
    current_score = sentence_score(token, [sentence])
    return current_score

def sentence_score(hypothesis: str, references: List[str], trace=0):
    idf_dict_hyp = defaultdict(lambda: 1.)
    idf_dict_ref = defaultdict(lambda: 1.)
    
    hypothesis = [hypothesis] * len(references)
    
    sentence_score = 0 

    scores = word_mover_score(references, hypothesis, idf_dict_ref, idf_dict_hyp, stop_words=[], n_gram=1, remove_subwords=False)
    
    sentence_score = np.mean(scores)
    
    if trace > 0:
        print(hypothesis, references, sentence_score)
            
    return sentence_score