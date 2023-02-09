from sacrerouge.metrics import QAEval

evaluator = None

def create_model():
    global evaluator
    evaluator = QAEval()

def compute_score(token, sentence):
    global evaluator
    current_score = evaluator.score(token, [sentence])['qa-eval']['f1']
    return current_score