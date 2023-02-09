from bart_score import BARTScorer
import json
import os
import time
import math

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"

os.environ["CUDA_VISIBLE_DEVICES"] = "0"


bart_scorer = BARTScorer(device='cpu', checkpoint='facebook/bart-large-cnn')

summaries_directory = '../nlp/finished_summaries'

book1dir = '../nlp/finished_summaries/bookwolf/A Tale of Two Cities/overview.json'
book2dir = '../nlp/finished_summaries/cliffnotes/A Tale of Two Cities/overview.txt'

bookwolf_dir = '../nlp/finished_summaries/bookwolf/'



books = [book1dir, book2dir]
transcripts = []


for book_dir in books:
    with open(book_dir, 'r') as f:
        transcripts.append(json.load(f))


# print("Loading Books")
# books = os.listdir(bookwolf_dir)
# print(books)


# for index, book in enumerate(books):
#     if(index >= 2):
#         break
#     with open(bookwolf_dir + "{}/overview.json".format(book), 'r') as f:
#         transcripts.append(json.load(f))


# for transcript in transcripts:
#     print(transcript["summary"])
#     print("---")





book1_scentences = transcripts[0]["summary"].split(". ")
book2_scentences = transcripts[1]["summary"].split(". ")

book1_scentences.pop()
book2_scentences.pop()

for i, scetence in enumerate(book1_scentences):
    book1_scentences[i] = scetence.strip()

for i, scetence in enumerate(book2_scentences):
    book2_scentences[i] = scetence.strip()

print("-- Summary 1: Bookwolf --")
print(book1_scentences)

print("-- Summary 2: Cliffnotes --")
print(book2_scentences)


min_total_len = min(len(book1_scentences), len(book2_scentences))-1


scores = []
for i in range(min_total_len):
    scores.append(bart_scorer.score([book1_scentences[i]],[book2_scentences[i]], batch_size=4))

print("----")
print(scores)
print("----")

print("length of smallest paragraph length:", min_total_len, "scentences.")

print("number of bart scores:", len(scores))
print("----")


min_score_i = -1
max_score_i = -1

min_score = math.inf
max_score = -math.inf


for i, num in enumerate(scores):
    if num[0] > max_score:
        max_score_i = i
        max_score = num[0]
    if num[0] < min_score:
        min_score_i = i
        min_score = num[0]


print("Most similar scentences")
print("Bookwolf: " + book1_scentences[max_score_i])
print("Cliffnotes: " + book2_scentences[max_score_i])

print("----")

print("Least similar scentences")
print("Bookwolf: " + book1_scentences[min_score_i])
print("Cliffnotes: " + book2_scentences[min_score_i])
