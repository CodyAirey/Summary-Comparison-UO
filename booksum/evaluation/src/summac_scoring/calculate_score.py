from summac.model_summac import SummaCZS, SummaCConv
import numpy as np

evaluator = None

def compute_score(token, sentence):
    global evaluator
    current_score = evaluator.score(np.array([token]), np.array([sentence]))['scores'][0]
    return current_score

def create_model():
    global evaluator
    evaluator = SummaCConv(models=["vitc"], bins='percentile', granularity="sentence", nli_labels="e", device="cpu", start_file="default", agg="mean")