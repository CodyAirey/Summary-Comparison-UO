# import json
# import os
# import pathlib
# import pandas as pd
# import numpy as np
# from glob import glob
# import nltk
# from nltk import tokenize
# import matplotlib.pyplot as plt
# from scipy import stats
# import math
# import statistics
from bartscore.bart_score import BARTScorer

model = None

def compute_score(token, sentence):
    global model
    current_score = model.score([token], [sentence])[0]
    return current_score

def create_model():
    global model
    model = BARTScorer(device='cuda:0', checkpoint='facebook/bart-large-cnn')