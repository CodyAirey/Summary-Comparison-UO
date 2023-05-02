import bert_score

r1 = ["The cat sat on the mat"]
r2 = ["The dog slept on the couch"],


c1 = ["The cat is on the mat"]
c2 = ["The dog is sleeping on the sofa"]


f1, precision, recall = bert_score.score(r1, c1, lang="en", rescale_with_baseline=True, return_hash=False)

# f1 = score_hash['f1']
# precision = score_hash['precision']
# recall = score_hash['recall']
# return f1, precision, recall


print(f1, precision, recall)