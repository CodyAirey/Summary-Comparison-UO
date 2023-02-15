import bert_score
bert_score.__version__
from bert_score import score
from bert_score import BERTScorer

scorer = None

def create_model():
    global scorer
    scorer = BERTScorer(lang="en", rescale_with_baseline=True)

def compute_score(token, sentence):
    global scorer
    p, r, f1 = scorer.score([token], [sentence])
    current_score = float(f1.mean())
    return current_score, p, r