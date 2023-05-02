import bert_score

scorer = None

def create_model():
    global scorer
    scorer = bert_score.BERTScorer(lang="en", rescale_with_baseline=True)

def compute_score(token, sentence):
    global scorer
    
    if scorer is None:
        create_model()

    f1, precision, recall = bert_score.score([token], [sentence], lang="en", rescale_with_baseline=True, return_hash=False)
    
    f1 = f1[0].item()
    precision = precision[0].item()
    recall = recall[0].item()
    
    return f1, precision, recall
