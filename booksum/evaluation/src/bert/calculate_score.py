from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

model = None

def create_model():
    global model
    model = SentenceTransformer('bert-base-nli-mean-tokens')

def compute_score(token, sentence):
    global model

    current_pair = list()
    current_pair.append(token)
    current_pair.append(sentence)
    embedded_pair = model.encode(current_pair)
    embedded_pair.shape

    current_score = cosine_similarity([embedded_pair[0]], [embedded_pair[1]])[0][0]

    return current_score