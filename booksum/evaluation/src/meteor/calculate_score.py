from scipy import stats
import nltk
from nltk import tokenize

nltk.download('omw-1.4')

def compute_score(token, sent):
    a = tokenize.word_tokenize(token)
    b = tokenize.word_tokenize(sent)
    current_score = nltk.translate.meteor_score.single_meteor_score(a, b)
    return current_score