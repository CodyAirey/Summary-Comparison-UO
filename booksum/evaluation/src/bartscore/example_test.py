from bart_score import BARTScorer
bart_scorer = BARTScorer(device='cuda:0', checkpoint='facebook/bart-large-cnn')

srcs = ["I'm super happy today.", "This is a good idea."]
tgts = [["I feel good today.", "I feel sad today."], ["Not bad.", "Sounds like a good idea."]] # List[List of references for each test sample]


x = bart_scorer.multi_ref_score(srcs, tgts, agg="max", batch_size=4) # agg means aggregation, can be mean or max
# [out]
# [-2.5008113384246826, -1.626236081123352]
print(x)

y = bart_scorer.score(['This is interesting.'], ['This is fun.'], batch_size=4) # generation scores from the first list of texts to the second list of texts.
# [out]
# [-2.510652780532837]
print(y)

bart_scorer.load(path='bart.pth')
z = bart_scorer.score(['This is interesting.'], ['This is fun.'], batch_size=4)
# [out]
# [-2.336203098297119]
print(z)
