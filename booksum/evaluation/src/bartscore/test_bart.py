import json
import os
import pathlib
import pandas as pd
import numpy as np
from glob import glob
import nltk
from nltk import tokenize
import matplotlib.pyplot as plt
from scipy import stats
import math
import statistics
from bart_score import BARTScorer

human_sums_bad = [
    ["The man went to the park.", "There were dogs there, they were chasing a rabbit.", "Lola did a backflip."],
    ["You think you've got it, oh, you think you've got it", "But 'got it' just don't get it till there's nothi ng at all (Ah!)",  "We get together, oh, we get together"],
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

ref_doc = tokenize.sent_tokenize("""Scientists are studying Mars to learn about the Red Planet and find landing sites for future missions.
One possible site, known as Arcadia Planitia, is covered instrange sinuous features.
The shapes could be signs that the area is actually made of glaciers, which are large masses of slow-moving ice.
Arcadia Planitia is in Mars' northern lowlands.""")

large_test_ref_exact = ["Chapter I is taken from the May 3rd and May 4th entries in Jonathan Harker's journal.", 'Harker is on a business trip in Eastern Europe, making his way across one of the most isolated regions of Europe.', 'He is going to meet with a noble of Transylvania, Count Dracula.', 'The heading to his journal entry tells us that Jonathan is writing in Bistritz, in what is now Romania.', 'Two days ago, he was in Munich.', 'One day ago, he was in Vienna.', 'As he has moved farther east, the country has become wilder and less modern.', 'Jonathan Harker records his observations of the people and the countryside, their costume and customs.', "He has been instructed to stay at an old fashioned hotel in Bistritz before setting out for the final leg of the journey to Dracula's castle.", 'At Bistritz, a letter from Dracula is waiting for him.', "Jonathan is to rest before setting out the next day for the Borgo Pass, where the Count's coach will be waiting for him.", "The landlord and his wife are visibly distressed by Jonathan's intentions to go to Dracula's castle.", "Although they cannot understand each other's languages and must communicate in German, the innkeeper passively tries to stop Jonathan by pretending not to understand his requests for a carriage to the Borgo Pass.", "The landlord's wife more aggressively tries to dissuade Jonathan, warning him that tomorrow is St. George's Day, and at midnight on St. George's Eve evil is at its strongest.", 'When he insists that he must go, she gives him a crucifixJonathan accepts the gift, even though, as an English Protestant, he considers crucifixes idolatrous.', 'Before Jonathan leaves, he notices that a number of the peasants are watching him with apprehension.', 'Although he cannot understand much of their language, he can make out the words for devil, Satan, werewolf, and vampire.', 'The peasants make motions at him to protect him from the evil eye.', 'On the carriage ride, his fellow passengers, on learning where he is going, treat him with the same kind of concerned sympathy, giving him gifts and protecting him with charms.', 'The ride is in wild and beautiful country.', "The carriage driver arrives at the Borgo Pass an hour early, and in bad German he then tries to convince Jonathan that Dracula's coachman might not come tonight, and Jonathan should come with the rest of them to Bukovina.", 'At that moment, a fearsome-looking coachman arrives on a vehicle pulled by coal-black horses.', 'One of the passengers whispers, "for He rebukes the carriage driver, and brings Jonathan onto the coach.', 'The final part of the trip is terrifying.', 'The moon is bright but is occasionally obscured by clouds, and strange blue fires and wolves appear along the way.', 'On several occasions, the driver leaves the coach, at which point the wolves come closer and closer to the vehicle.', "Whenever the driver returns, the wolves fleethe final time this phenomenon occurs, it seems that the wolves flee on the driver's command.", "The chapter ends with Dracula's castle coming into view, its crumbling battlements cutting a jagged line against the night sky."]
large_test_hyp_exact = [["Chapter I is taken from the May 3rd and May 4th entries in Jonathan Harker's journal.", 'Harker is on a business trip in Eastern Europe, making his way across one of the most isolated regions of Europe.', 'He is going to meet with a noble of Transylvania, Count Dracula.', 'The heading to his journal entry tells us that Jonathan is writing in Bistritz, in what is now Romania.', 'Two days ago, he was in Munich.', 'One day ago, he was in Vienna.', 'As he has moved farther east, the country has become wilder and less modern.', 'Jonathan Harker records his observations of the people and the countryside, their costume and customs.', "He has been instructed to stay at an old fashioned hotel in Bistritz before setting out for the final leg of the journey to Dracula's castle.", 'At Bistritz, a letter from Dracula is waiting for him.', "Jonathan is to rest before setting out the next day for the Borgo Pass, where the Count's coach will be waiting for him.", "The landlord and his wife are visibly distressed by Jonathan's intentions to go to Dracula's castle.", "Although they cannot understand each other's languages and must communicate in German, the innkeeper passively tries to stop Jonathan by pretending not to understand his requests for a carriage to the Borgo Pass.", "The landlord's wife more aggressively tries to dissuade Jonathan, warning him that tomorrow is St. George's Day, and at midnight on St. George's Eve evil is at its strongest.", 'When he insists that he must go, she gives him a crucifixJonathan accepts the gift, even though, as an English Protestant, he considers crucifixes idolatrous.', 'Before Jonathan leaves, he notices that a number of the peasants are watching him with apprehension.', 'Although he cannot understand much of their language, he can make out the words for devil, Satan, werewolf, and vampire.', 'The peasants make motions at him to protect him from the evil eye.', 'On the carriage ride, his fellow passengers, on learning where he is going, treat him with the same kind of concerned sympathy, giving him gifts and protecting him with charms.', 'The ride is in wild and beautiful country.', "The carriage driver arrives at the Borgo Pass an hour early, and in bad German he then tries to convince Jonathan that Dracula's coachman might not come tonight, and Jonathan should come with the rest of them to Bukovina.", 'At that moment, a fearsome-looking coachman arrives on a vehicle pulled by coal-black horses.', 'One of the passengers whispers, "for He rebukes the carriage driver, and brings Jonathan onto the coach.', 'The final part of the trip is terrifying.', 'The moon is bright but is occasionally obscured by clouds, and strange blue fires and wolves appear along the way.', 'On several occasions, the driver leaves the coach, at which point the wolves come closer and closer to the vehicle.', "Whenever the driver returns, the wolves fleethe final time this phenomenon occurs, it seems that the wolves flee on the driver's command.", "The chapter ends with Dracula's castle coming into view, its crumbling battlements cutting a jagged line against the night sky."]]


# for sent in ref_doc:
#     print(sent)



def process_summaries(ref_doc, summaries):

    max_scores = []
    for sentence_list in summaries:
        sentence_scores = []
        unique_sents = set()
        for i, token in enumerate(ref_doc):
            best_score = -math.inf
            best_score_i = -1;
            for j, sentence in enumerate(sentence_list):
                current_score = bart_scorer.score([token], [sentence])[0]
                
                print(current_score)
                #print("token:", token)
                #print("sentence:", sentence)
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


bart_scorer = BARTScorer(device='cuda:0', checkpoint='facebook/bart-large-cnn')
summary_scores = []

# process_summaries(ref_doc, human_sums_bad)
# process_summaries(ref_doc, human_sums_good)
# process_summaries(ref_doc, human_sums_exact)
process_summaries(large_test_ref_exact, large_test_hyp_exact)
