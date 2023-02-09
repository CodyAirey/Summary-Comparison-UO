#Write some lines to encode (sentences 0 and 2 are both ideltical):
sen = [
    "Three years later, the coffin was still full of Jello.",
    "The fish dreamed of escaping the fishbowl and into the toilet where he saw his friend go.",
    "The person box was packed with jelly many dozens of months later.",
    "He found a leprechaun in his walnut shell."
]
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('bert-base-nli-mean-tokens')
#Encoding:
sen_embeddings = model.encode(sen)
sen_embeddings.shape


from sklearn.metrics.pairwise import cosine_similarity
#let's calculate cosine similarity for sentence 0:
print(cosine_similarity(
    [sen_embeddings[0]],
    sen_embeddings[1:]
))

