import json
import os
import pathlib
import pandas as pd
from glob import glob
import numpy as np
import nltk
import math
import matplotlib.pyplot as plt
from scipy import stats
from nltk import tokenize
import sys

import rouge_scoring
from rouge_scoring import rouge_n
from rouge_scoring import rouge_l_sentence_level



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

ref_doc = tokenize.sent_tokenize("""Scientists are studying Mars to learn about the Red Planet and find landing sites for future missions.
One possible site, known as Arcadia Planitia, is covered instrange sinuous features.
The shapes could be signs that the area is actually made of glaciers, which are large masses of slow-moving ice.
Arcadia Planitia is in Mars' northern lowlands.""")

large_test_ref_exact = ["Chapter I is taken from the May 3rd and May 4th entries in Jonathan Harker's journal.", 'Harker is on a business trip in Eastern Europe, making his way across one of the most isolated regions of Europe.', 'He is going to meet with a noble of Transylvania, Count Dracula.', 'The heading to his journal entry tells us that Jonathan is writing in Bistritz, in what is now Romania.', 'Two days ago, he was in Munich.', 'One day ago, he was in Vienna.', 'As he has moved farther east, the country has become wilder and less modern.', 'Jonathan Harker records his observations of the people and the countryside, their costume and customs.', "He has been instructed to stay at an old fashioned hotel in Bistritz before setting out for the final leg of the journey to Dracula's castle.", 'At Bistritz, a letter from Dracula is waiting for him.', "Jonathan is to rest before setting out the next day for the Borgo Pass, where the Count's coach will be waiting for him.", "The landlord and his wife are visibly distressed by Jonathan's intentions to go to Dracula's castle.", "Although they cannot understand each other's languages and must communicate in German, the innkeeper passively tries to stop Jonathan by pretending not to understand his requests for a carriage to the Borgo Pass.", "The landlord's wife more aggressively tries to dissuade Jonathan, warning him that tomorrow is St. George's Day, and at midnight on St. George's Eve evil is at its strongest.", 'When he insists that he must go, she gives him a crucifixJonathan accepts the gift, even though, as an English Protestant, he considers crucifixes idolatrous.', 'Before Jonathan leaves, he notices that a number of the peasants are watching him with apprehension.', 'Although he cannot understand much of their language, he can make out the words for devil, Satan, werewolf, and vampire.', 'The peasants make motions at him to protect him from the evil eye.', 'On the carriage ride, his fellow passengers, on learning where he is going, treat him with the same kind of concerned sympathy, giving him gifts and protecting him with charms.', 'The ride is in wild and beautiful country.', "The carriage driver arrives at the Borgo Pass an hour early, and in bad German he then tries to convince Jonathan that Dracula's coachman might not come tonight, and Jonathan should come with the rest of them to Bukovina.", 'At that moment, a fearsome-looking coachman arrives on a vehicle pulled by coal-black horses.', 'One of the passengers whispers, "for He rebukes the carriage driver, and brings Jonathan onto the coach.', 'The final part of the trip is terrifying.', 'The moon is bright but is occasionally obscured by clouds, and strange blue fires and wolves appear along the way.', 'On several occasions, the driver leaves the coach, at which point the wolves come closer and closer to the vehicle.', "Whenever the driver returns, the wolves fleethe final time this phenomenon occurs, it seems that the wolves flee on the driver's command.", "The chapter ends with Dracula's castle coming into view, its crumbling battlements cutting a jagged line against the night sky."]
large_test_hyp_exact = [["Chapter I is taken from the May 3rd and May 4th entries in Jonathan Harker's journal.", 'Harker is on a business trip in Eastern Europe, making his way across one of the most isolated regions of Europe.', 'He is going to meet with a noble of Transylvania, Count Dracula.', 'The heading to his journal entry tells us that Jonathan is writing in Bistritz, in what is now Romania.', 'Two days ago, he was in Munich.', 'One day ago, he was in Vienna.', 'As he has moved farther east, the country has become wilder and less modern.', 'Jonathan Harker records his observations of the people and the countryside, their costume and customs.', "He has been instructed to stay at an old fashioned hotel in Bistritz before setting out for the final leg of the journey to Dracula's castle.", 'At Bistritz, a letter from Dracula is waiting for him.', "Jonathan is to rest before setting out the next day for the Borgo Pass, where the Count's coach will be waiting for him.", "The landlord and his wife are visibly distressed by Jonathan's intentions to go to Dracula's castle.", "Although they cannot understand each other's languages and must communicate in German, the innkeeper passively tries to stop Jonathan by pretending not to understand his requests for a carriage to the Borgo Pass.", "The landlord's wife more aggressively tries to dissuade Jonathan, warning him that tomorrow is St. George's Day, and at midnight on St. George's Eve evil is at its strongest.", 'When he insists that he must go, she gives him a crucifixJonathan accepts the gift, even though, as an English Protestant, he considers crucifixes idolatrous.', 'Before Jonathan leaves, he notices that a number of the peasants are watching him with apprehension.', 'Although he cannot understand much of their language, he can make out the words for devil, Satan, werewolf, and vampire.', 'The peasants make motions at him to protect him from the evil eye.', 'On the carriage ride, his fellow passengers, on learning where he is going, treat him with the same kind of concerned sympathy, giving him gifts and protecting him with charms.', 'The ride is in wild and beautiful country.', "The carriage driver arrives at the Borgo Pass an hour early, and in bad German he then tries to convince Jonathan that Dracula's coachman might not come tonight, and Jonathan should come with the rest of them to Bukovina.", 'At that moment, a fearsome-looking coachman arrives on a vehicle pulled by coal-black horses.', 'One of the passengers whispers, "for He rebukes the carriage driver, and brings Jonathan onto the coach.', 'The final part of the trip is terrifying.', 'The moon is bright but is occasionally obscured by clouds, and strange blue fires and wolves appear along the way.', 'On several occasions, the driver leaves the coach, at which point the wolves come closer and closer to the vehicle.', "Whenever the driver returns, the wolves fleethe final time this phenomenon occurs, it seems that the wolves flee on the driver's command.", "The chapter ends with Dracula's castle coming into view, its crumbling battlements cutting a jagged line against the night sky."]]


deez= """the narrator explains how people can conquer new monarchies. He uses examples from the Roman Empire to illustrate his point that there are two kinds of governments: Republics and Monarchies. New monarchies are either completely new or kind of new. The idea is that when you conquer a new monarchy, it'll be easier for you to get rid of old monarchies than it is for someone else to take over. If you have an army that can't manage the new territory by themselves, people will rebel at first because they don't know how to deal with the new rulers. This means that even if your new land doesn't speak the same language like the other kingdoms, people won't hate you. You can move to another part of the world and make colonies, which are cheaper and more secure than armies. That way, no foreigners will come in and ruin your new country. Next, you should become "the guardian Angel" for the weak countries around your new territory. This is a good strategy because it makes sure that foreign powers do not try to invade and cramp your style. When Louis was trying to take Milan, he didn't help his neighbors. He helped two stronger states into the neighborhood; he helped the Pope Alexander invade Romegna and carry the King of Spaniards into Naples. Now, we're back to the topic of how difficult it would be to hold onto new lands. There are only two types of government: kings and non-elective barons. The king has real power, so Turkey is pretty easy to conquer. On the plus side though, once you take over, ruling is something of a cake since there's no baron who wants to challenge you after the king dies. Another example of this type of government is France, where Barons often go back long enough to find out what's going on. So now we've got three options: burn down all of these places and live there, pay taxes, create a tiny government, or destroy them altogether.
	we're introduced to a number of different types of rulers. Some are lucky, some are just lucky, and some are not so lucky at all. The first example is Hiero, who was made a dude because people needed a new leader. But after that, he got rid of his old army, broke off the other ones, and stayed in his new kingdom. For those who got their land by sheer luck or buying it, here's the good news: you now have some territory. The second example is Cesare Bjoria, whom he lost because his father tricked him into getting it for him when he died. This guy killed all of his enemies and set up a "court of locals" to punish anyone who tried to challenge him. Now we've got two more examples of how regular Joes can become rulers through crime and being made King by everybody else. First, we get an example of a bad guy named Agatcholes. He became the president of the army but then decided to become king. Everyone was too afraid of this crazy man to even try to mess with him. Next, we move to modern times with a guy named oliverotto. His uncle gave him fancy food, clothes, and works, so he went back to Fermemo and told his uncle to put a big party for him. When he arrived, if everyone knew he was there, they would kill him. After this bloody event, figured out that he had been chosen as the new king offermo.
	The narrator tells us that the new king has three options to choose from: monarchy, republic, or anarchy--the first is where the nobles get power and the second is where people get power. If the people want to become absolute ruler, then they need to give direct command to other people who have power over them. The problem with this situation is that the people don't always trust the most trustworthy person, so everything is going in flames before you know it. So make sure your kingdom needs all the help you can get, because no one will ever be able to defend it. The next topic is church states--popes are becoming more and more powerful as the church grows stronger. This means that popes now rule for ten years instead of just a few. It turns out that Pope Julius VI's dad got his son Cesare Bjoria some land when he was kidnapped by Pope Leo. Since the pope didn't really care what happened to the land, he gave it to Julius II, who took control of it.
	the narrator explains how important it is to become a king or queen. If you're not ready for war, then you'll just be pathetic. He tells us to stop thinking about war and start getting ready for it. This is all about "cold hard reality," which means that princes don't really want to be good in the first place. Princes have to fight and get real. They can do awesome things, but they won't make great rulers because they aren't willing to wage war. The only way to make a good ruler is to act like a Disney prince while doing all the other stuff that needs to be done in order to form a government. So, here's what we mean by "don't be generosity." It's more important to be generous than nice so that people hate you. And compassion doesn't work very well with the kind of warlike emperor who wants to destroy a country. We also learn that there's no reason why an insanely cruel guy named Hannibar was super awesome when he was murdered by a conspirator. You should always be careful not to go too wild. Just like our animal side and our human side, we need to figure out when we've got to change our strategies. As long as your kingdom prospers, people will think that you were one of the best guys ever. But if you try to rule without being hated, you might end up being a hypocrite.
	the narrator explains some of the most important ideas in the book. First, he tells us that rulers should not get too angry by the people because they're more powerful than we are. Second, a ruler should take away guns and divide town into factions. Third, if there's a war between two neighboring kingdoms, it's best to win it. If you lose, then you can plot revenge together. This is one of the first things he talks about in this chapter. He says that if you choose the right minister, everyone will think how smart you want to be for choosing such an awesome minister. The second thing he says is to make sure that your ministers know that you're the decider when you ask them for advice. Finally, his last point is to remember that good advice doesn't always work out as well as bad advice does. So here's what he ends with: "When in doubt...be impulsive."
	Lorenzo pleads with Pedringano to take up arms against Italy, but Petrarch has already done so. He leaves with a patriot's letter saying that he would like to rule Italy for as long as possible."""


nutty= """How to be a prince, by Niccolo Machiavelli to his BFF Lorenzo de' Medici: Step 1: get yourself a kingdom, and preferably have your own army while doing it since mercenaries are bad news. Be careful when choosing a place to take over. Even though it will be harder to conquer at first, choose the land of a king with no powerful barons or ministers, because it will be easiest to maintain in the long run. Make sure you kill anyone who might oppose you before continuing. And choose a role model. Step 2: keep your kingdom secure by not allowing people as strong as you are into the neighborhood. Also, make friends with your neighbors. Don't let people hate you, but don't worry too much if they grumble a bit. Maintain a reputation for awesomeness. When in doubt, think of Cesare Borgia. P.S. Pleasie weasie come rule Italy using the steps Machiavelli showed you. You can do it! Okay, okay, we'll break it down a little more: Chapters 1-4: States can be republics or kingdoms, old or new. The easiest to rule are old hereditary kingdoms, lands that are passed down from father to son . Basically, instead of passing along their 2001 Toyota Camry, your parents give you a kingdom. You'd have to be an idiot to have problems ruling one of these. Because they're so easy to rule, they are hard to take. The opposite is true of states that are easy to take: they tend to be hard to rule. The best way to take old hereditary kingdoms is by killing the old monarchy. Every last one. Chapters 5-7: You also need violence to take self-governed republics, because they will rebel if you don't crush them. Just remember not to keep being violent. Get it over with so you can start being nice and people won't hate you. Never let your people hate you. Lie, cheat, steal--just don't become hated. And make sure you have your own army. Chapters 10-14: Mercenaries and auxiliaries are a waste of time and dangerous, to boot. If you have a strong army, and your people love you, no one can touch you. They won't even think about it. On that topic, you need to run your army, so war needs to be on your mind all day every day. You need to be on the cutting edge of war techniques and technology. By the way, a word on fortresses: they look cool and everything, but they can also make people resent you. They're really only useful if you are afraid of your people. Chapters 16-23: Throw parties for your people. Listen to your ministers but avoid brown-noses. Chapters 24-26: Finally, Italy is not doing so great right now because its rulers didn't follow Machiavelli's rules. They blame bad luck, but you can always prepare for luck, and they didn't. Don't be like them. Be awesome."""


d2 = tokenize.sent_tokenize(deez)
n2 = [tokenize.sent_tokenize(nutty)]



def process_summaries(ref_doc, summaries):
    max_scores = []

    for sentence_list in summaries:
        sentence_scores = []
        unique_sents = set()

        for i, token in enumerate(ref_doc):
            best_score = -math.inf
            best_score_i = -1;

            for j, sentence in enumerate(sentence_list):

                # current_score, precision, recall = rouge_n([token], [sentence], n=1)
                current_score, precision, recall = rouge_n([token], [sentence], n=2)
                # current_score, precision, recall = rouge_l_sentence_level([token], [sentence])
                
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

# process_summaries(ref_doc, human_sums_bad)
# process_summaries(ref_doc, human_sums_good)
# process_summaries(large_test_ref_exact, large_test_hyp_exact)


process_summaries(d2, n2)

print(len(n2))