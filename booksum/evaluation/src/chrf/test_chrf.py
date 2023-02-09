# Copyright 2017 Maja Popovic

# The program is distributed under the terms 
# of the GNU General Public Licence (GPL)

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Publications of results obtained through the use of original or
# modified versions of the software have to cite the authors by refering
# to the following publication:

# Maja Popović (2015).
# "chrF: character n-gram F-score for automatic MT evaluation".
# In Proceedings of the Tenth Workshop on Statistical Machine Translation (WMT15), pages 392–395
# Lisbon, Portugal, September 2015.

# ~~~~~~~~~
from typing import List, Union, Iterable
import numpy as np
import nltk
import math
from collections import defaultdict
from nltk import tokenize
from itertools import zip_longest
import sys
import unicodedata
import argparse
import time
import string

human_sums_bad = [
    ["The man went to the park.", "There were dogs there, they were chasing a rabbit.", "Lola did a backflip."],
    ["You think you've got it, oh, you think you've got it", "But 'got it' just don't get it till there's nothing at all (Ah!)",  "We get together, oh, we get together"],
    ["Windmill, windmill for the land", "Turn forever, hand in hand", "Take it all in on your stride"]]

human_sums_good = [
    ["There are strange shape patterns on Arcadia Planitia.", "The shapes could indicate the area might be made of glaciers.", "This makes Arcadia Planitia ideal for future missions."],
    ["There are strange shape patterns on Arcadia Planitia.", "The shapes could indicate the area might be made of glaciers."],
    ["Scientists are studying Mars to check for the for it to be the landing site for future missions.", """They believe that the planet contains many glaciers that make up an area they are naming "Arcadia Planitia"."""]]

human_sums_exact = [[
    "Scientists are studying Mars to learn about the Red Planet and find landing sites for future missions.",
    "One possible site, known as Arcadia Planitia, is covered instrange sinuous features.",
    "The shapes could be signs that the area is actually made of glaciers, which are large masses of slow-moving ice.",
    "Arcadia Planitia is in Mars' northern lowlands."]]


human_sums_similar = [[
    "Scientists are studying Mars to learn about the Red Planet and find landing sites for future missions.",
    "One possible site, known as Arcadia Planitia, is covered instrange sinuous features.",
    "The shapes could be signs that the area is actually made of glaciers, which are large masses of slow-moving ice.",
    "Arcadia Planitia is in Mars' northern lowlands."]]

    
ref_doc = tokenize.sent_tokenize("""Scientists are studying Mars to learn about the Red Planet and find landing sites for future missions.
One possible site, known as Arcadia Planitia, is covered instrange sinuous features.
The shapes could be signs that the area is actually made of glaciers, which are large masses of slow-moving ice.
Arcadia Planitia is in Mars' northern lowlands.""")

large_test_ref_exact = ["Chapter I is taken from the May 3rd and May 4th entries in Jonathan Harker's journal.", 'Harker is on a business trip in Eastern Europe, making his way across one of the most isolated regions of Europe.', 'He is going to meet with a noble of Transylvania, Count Dracula.', 'The heading to his journal entry tells us that Jonathan is writing in Bistritz, in what is now Romania.', 'Two days ago, he was in Munich.', 'One day ago, he was in Vienna.', 'As he has moved farther east, the country has become wilder and less modern.', 'Jonathan Harker records his observations of the people and the countryside, their costume and customs.', "He has been instructed to stay at an old fashioned hotel in Bistritz before setting out for the final leg of the journey to Dracula's castle.", 'At Bistritz, a letter from Dracula is waiting for him.', "Jonathan is to rest before setting out the next day for the Borgo Pass, where the Count's coach will be waiting for him.", "The landlord and his wife are visibly distressed by Jonathan's intentions to go to Dracula's castle.", "Although they cannot understand each other's languages and must communicate in German, the innkeeper passively tries to stop Jonathan by pretending not to understand his requests for a carriage to the Borgo Pass.", "The landlord's wife more aggressively tries to dissuade Jonathan, warning him that tomorrow is St. George's Day, and at midnight on St. George's Eve evil is at its strongest.", 'When he insists that he must go, she gives him a crucifixJonathan accepts the gift, even though, as an English Protestant, he considers crucifixes idolatrous.', 'Before Jonathan leaves, he notices that a number of the peasants are watching him with apprehension.', 'Although he cannot understand much of their language, he can make out the words for devil, Satan, werewolf, and vampire.', 'The peasants make motions at him to protect him from the evil eye.', 'On the carriage ride, his fellow passengers, on learning where he is going, treat him with the same kind of concerned sympathy, giving him gifts and protecting him with charms.', 'The ride is in wild and beautiful country.', "The carriage driver arrives at the Borgo Pass an hour early, and in bad German he then tries to convince Jonathan that Dracula's coachman might not come tonight, and Jonathan should come with the rest of them to Bukovina.", 'At that moment, a fearsome-looking coachman arrives on a vehicle pulled by coal-black horses.', 'One of the passengers whispers, "for He rebukes the carriage driver, and brings Jonathan onto the coach.', 'The final part of the trip is terrifying.', 'The moon is bright but is occasionally obscured by clouds, and strange blue fires and wolves appear along the way.', 'On several occasions, the driver leaves the coach, at which point the wolves come closer and closer to the vehicle.', "Whenever the driver returns, the wolves fleethe final time this phenomenon occurs, it seems that the wolves flee on the driver's command.", "The chapter ends with Dracula's castle coming into view, its crumbling battlements cutting a jagged line against the night sky."]
large_test_hyp_exact = [["Chapter I is taken from the May 3rd and May 4th entries in Jonathan Harker's journal.", 'Harker is on a business trip in Eastern Europe, making his way across one of the most isolated regions of Europe.', 'He is going to meet with a noble of Transylvania, Count Dracula.', 'The heading to his journal entry tells us that Jonathan is writing in Bistritz, in what is now Romania.', 'Two days ago, he was in Munich.', 'One day ago, he was in Vienna.', 'As he has moved farther east, the country has become wilder and less modern.', 'Jonathan Harker records his observations of the people and the countryside, their costume and customs.', "He has been instructed to stay at an old fashioned hotel in Bistritz before setting out for the final leg of the journey to Dracula's castle.", 'At Bistritz, a letter from Dracula is waiting for him.', "Jonathan is to rest before setting out the next day for the Borgo Pass, where the Count's coach will be waiting for him.", "The landlord and his wife are visibly distressed by Jonathan's intentions to go to Dracula's castle.", "Although they cannot understand each other's languages and must communicate in German, the innkeeper passively tries to stop Jonathan by pretending not to understand his requests for a carriage to the Borgo Pass.", "The landlord's wife more aggressively tries to dissuade Jonathan, warning him that tomorrow is St. George's Day, and at midnight on St. George's Eve evil is at its strongest.", 'When he insists that he must go, she gives him a crucifixJonathan accepts the gift, even though, as an English Protestant, he considers crucifixes idolatrous.', 'Before Jonathan leaves, he notices that a number of the peasants are watching him with apprehension.', 'Although he cannot understand much of their language, he can make out the words for devil, Satan, werewolf, and vampire.', 'The peasants make motions at him to protect him from the evil eye.', 'On the carriage ride, his fellow passengers, on learning where he is going, treat him with the same kind of concerned sympathy, giving him gifts and protecting him with charms.', 'The ride is in wild and beautiful country.', "The carriage driver arrives at the Borgo Pass an hour early, and in bad German he then tries to convince Jonathan that Dracula's coachman might not come tonight, and Jonathan should come with the rest of them to Bukovina.", 'At that moment, a fearsome-looking coachman arrives on a vehicle pulled by coal-black horses.', 'One of the passengers whispers, "for He rebukes the carriage driver, and brings Jonathan onto the coach.', 'The final part of the trip is terrifying.', 'The moon is bright but is occasionally obscured by clouds, and strange blue fires and wolves appear along the way.', 'On several occasions, the driver leaves the coach, at which point the wolves come closer and closer to the vehicle.', "Whenever the driver returns, the wolves fleethe final time this phenomenon occurs, it seems that the wolves flee on the driver's command.", "The chapter ends with Dracula's castle coming into view, its crumbling battlements cutting a jagged line against the night sky."]]



def separate_characters(line):
    return list(line.strip().replace(" ", ""))

def separate_punctuation(line):
    words = line.strip().split()
    tokenized = []
    for w in words:
        if len(w) == 1:
            tokenized.append(w)
        else:
            lastChar = w[-1] 
            firstChar = w[0]
            if lastChar in string.punctuation:
                tokenized += [w[:-1], lastChar]
            elif firstChar in string.punctuation:
                tokenized += [firstChar, w[1:]]
            else:
                tokenized.append(w)
    
    return tokenized
    
def ngram_counts(wordList, order):
    counts = defaultdict(lambda: defaultdict(float))
    nWords = len(wordList)
    for i in range(nWords):
        for j in range(1, order+1):
            if i+j <= nWords:
                ngram = tuple(wordList[i:i+j])
                counts[j-1][ngram]+=1
   
    return counts

def ngram_matches(ref_ngrams, hyp_ngrams):
    matchingNgramCount = defaultdict(float)
    totalRefNgramCount = defaultdict(float)
    totalHypNgramCount = defaultdict(float)
 
    for order in ref_ngrams:
        for ngram in hyp_ngrams[order]:
            totalHypNgramCount[order] += hyp_ngrams[order][ngram]
        for ngram in ref_ngrams[order]:
            totalRefNgramCount[order] += ref_ngrams[order][ngram]
            if ngram in hyp_ngrams[order]:
                matchingNgramCount[order] += min(ref_ngrams[order][ngram], hyp_ngrams[order][ngram])


    return matchingNgramCount, totalRefNgramCount, totalHypNgramCount


def ngram_precrecf(matching, reflen, hyplen, beta):
    ngramPrec = defaultdict(float)
    ngramRec = defaultdict(float)
    ngramF = defaultdict(float)
    
    factor = beta**2
    
    for order in matching:
        if hyplen[order] > 0:
            ngramPrec[order] = matching[order]/hyplen[order]
        else:
            ngramPrec[order] = 1e-16
        if reflen[order] > 0:
            ngramRec[order] = matching[order]/reflen[order]
        else:
            ngramRec[order] = 1e-16
        denom = factor*ngramPrec[order] + ngramRec[order]
        if denom > 0:
            ngramF[order] = (1+factor)*ngramPrec[order]*ngramRec[order] / denom
        else:
            ngramF[order] = 1e-16
            
    return ngramF, ngramRec, ngramPrec

def computeChrF(fpRef, fpHyp, nworder, ncorder, beta, sentence_level_scores = None):
    norder = float(nworder + ncorder)

    # initialisation of document level scores
    totalMatchingCount = defaultdict(float)
    totalRefCount = defaultdict(float)
    totalHypCount = defaultdict(float)
    totalChrMatchingCount = defaultdict(float)
    totalChrRefCount = defaultdict(float)
    totalChrHypCount = defaultdict(float)
    averageTotalF = 0.0

    nsent = 0
    for hline, rline in zip(fpHyp, fpRef):
        nsent += 1
        
        # preparation for multiple references
        maxF = 0.0
        bestWordMatchingCount = None
        bestCharMatchingCount = None

        bestMatchingCount = defaultdict(float)
        bestRefCount = defaultdict(float)
        bestHypCount = defaultdict(float)
        bestChrMatchingCount = defaultdict(float)
        bestChrRefCount = defaultdict(float)
        bestChrHypCount = defaultdict(float)
        
        hypNgramCounts = ngram_counts(separate_punctuation(hline), nworder)
        hypChrNgramCounts = ngram_counts(separate_characters(hline), ncorder)

        # going through multiple references

        refs = rline.split("*#")

        for ref in refs:
            refNgramCounts = ngram_counts(separate_punctuation(ref), nworder)
            refChrNgramCounts = ngram_counts(separate_characters(ref), ncorder)

            # number of overlapping n-grams, total number of ref n-grams, total number of hyp n-grams
            matchingNgramCounts, totalRefNgramCount, totalHypNgramCount = ngram_matches(refNgramCounts, hypNgramCounts)
            matchingChrNgramCounts, totalChrRefNgramCount, totalChrHypNgramCount = ngram_matches(refChrNgramCounts, hypChrNgramCounts)
                    
            # n-gram f-scores, recalls and precisions
            ngramF, ngramRec, ngramPrec = ngram_precrecf(matchingNgramCounts, totalRefNgramCount, totalHypNgramCount, beta)
            chrNgramF, chrNgramRec, chrNgramPrec = ngram_precrecf(matchingChrNgramCounts, totalChrRefNgramCount, totalChrHypNgramCount, beta)

            sentRec  = (sum(chrNgramRec.values())  + sum(ngramRec.values()))  / norder
            sentPrec = (sum(chrNgramPrec.values()) + sum(ngramPrec.values())) / norder
            sentF    = (sum(chrNgramF.values())    + sum(ngramF.values()))    / norder

            if sentF > maxF:
                maxF = sentF
                bestMatchingCount = matchingNgramCounts
                bestRefCount = totalRefNgramCount
                bestHypCount = totalHypNgramCount
                bestChrMatchingCount = matchingChrNgramCounts
                bestChrRefCount = totalChrRefNgramCount
                bestChrHypCount = totalChrHypNgramCount
        # all the references are done


        # write sentence level scores
        if sentence_level_scores:
            sentence_level_scores.write("%i::c%i+w%i-F%i\t%.4f\n"  % (nsent, ncorder, nworder, beta, 100*maxF))


        # collect document level ngram counts
        for order in range(nworder):
            totalMatchingCount[order] += bestMatchingCount[order]
            totalRefCount[order] += bestRefCount[order]
            totalHypCount[order] += bestHypCount[order]
        for order in range(ncorder):
            totalChrMatchingCount[order] += bestChrMatchingCount[order]
            totalChrRefCount[order] += bestChrRefCount[order]
            totalChrHypCount[order] += bestChrHypCount[order]

        averageTotalF += maxF

    # all sentences are done
     
    # total precision, recall and F (aritmetic mean of all ngrams)
    totalNgramF, totalNgramRec, totalNgramPrec = ngram_precrecf(totalMatchingCount, totalRefCount, totalHypCount, beta)
    totalChrNgramF, totalChrNgramRec, totalChrNgramPrec = ngram_precrecf(totalChrMatchingCount, totalChrRefCount, totalChrHypCount, beta)

    totalF    = (sum(totalChrNgramF.values())    + sum(totalNgramF.values()))    / norder
    averageTotalF = averageTotalF / nsent
    totalRec  = (sum(totalChrNgramRec.values())  + sum(totalNgramRec.values()))  / norder
    totalPrec = (sum(totalChrNgramPrec.values()) + sum(totalNgramPrec.values())) / norder

    return totalF, averageTotalF, totalPrec, totalRec


def process_summaries(ref_doc, summaries):

    max_scores = []
    for sentence_list in summaries:
        sentence_scores = []
        unique_sents = set()
        for i, token in enumerate(ref_doc):
            best_score = -math.inf
            best_score_i = -1
            for j, sentence in enumerate(sentence_list):

                totalF, averageTotalF, totalPrec, totalRec = computeChrF(token, sentence, 1, 1, 2)
                #token, sentence, word ngram, c ngram, beta

                current_score = averageTotalF

                #print("token:", token)
                #print("sentence: ", sentence)
                #print("score:", current_score)
                #print("---")
                if current_score > best_score:
                    best_score = current_score
                    best_score_i = j
            sentence_scores.append(best_score)
            unique_sents.add(best_score_i)
            #print("NEXT TOKEN")
        max_scores.append(np.mean(sentence_scores))
        print(f"{sentence_scores} => {np.mean(sentence_scores)}")
        print("Unique sentences:", len(unique_sents), ", out of", len(ref_doc), "ref sents. :", unique_sents)
    print(f"{np.mean(max_scores)}")

summary_scores = []

sentence_level_scores = None

# process_summaries(ref_doc, human_sums_bad)
# process_summaries(ref_doc, human_sums_good)
# process_summaries(ref_doc, human_sums_exact)
process_summaries(large_test_ref_exact, large_test_hyp_exact)