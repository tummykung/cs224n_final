import simplejson
from process_reviews import INPUT_FILENAME
from process_reviews import BUSINESS_FILENAME
from process_reviews import load_results
from sentence import CONCEPT_PARSER_COMMAND_LIST
from svmutil import *
from urllib2 import HTTPError
import polarity

import nltk
from nltk.stem import WordNetLemmatizer
from senticnet.senticnet import Senticnet
import subprocess
import ipdb
import numpy as np
import os
import sys
import matplotlib.pyplot as plt

# ==== CONFIGURATION ====
SAMPlE_DATA_PATH = "static/test_data/sample_data.json"

# initialization
inputs = []
businesses = []
results = []
NUM_SAMPLE = 10000
VERBOSE = True
x = []
y = []
sn = Senticnet()

def original_read_input():
    with open(INPUT_FILENAME, 'r') as f:
        for i in range(NUM_SAMPLE):
            inputs.append(simplejson.loads(f.readline()))

    with open(BUSINESS_FILENAME, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            businesses.append(simplejson.loads(line))



def compute_polarity_wrapper(word):
    score = 0.0
    raw_score = polarity._compute_polarity_from_cache(word)
    if raw_score != None:
        return raw_score

    try:
        score = sn.polarity(word)
    except HTTPError:
        score = polarity._compute_polarity(word)

    return score

def setup(sample):
    sentence = sample["sentence"]
    rating = sample["rating"]
    # collapse 2 and -2 to 1 and -1, respectively
    if rating == 2:
        rating = 1
    if rating == -2:
        rating = -1

    y.append(rating)
    new_x = {
        0: 1,
        1: sample["concept_polarity"],
        2: sample["adj_polarity"],
        3: sample["adj_polarity"],
    }

    offset = len(new_x) - 1

    # the remaining is for computing other features

    # ----- first, do langauge processing on this sentence -----
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    # if VERBOSE:
        # print "POS: " + repr(tagged)

    food_index = -1
    actual_word = ""
    for i, word_and_POS in enumerate(tagged):
        if foodName in word_and_POS[0]:
            food_index = i
            actual_word = word_and_POS[0]

    scores = []
    for i, word_and_POS in enumerate(tagged):
        POS = word_and_POS[1]
        if POS in ("JJ", "JJS", "JJR"):
            score = compute_polarity_wrapper(word_and_POS[0])
            scores.append(score)
            distance = abs(i - food_index)

            new_x[distance + offset] = score
            # new_x["adjective_score_distance_pair"].append((score, distance))
    # if len(scores) > 0:
    #     new_x[0] = float(sum(scores))/len(scores)
    business = filter(lambda x:x["business_id"] == sample["business_id"], businesses)[0]


    x.append(new_x)

    # results.append({
    #     "rating": dep_polarity, # for now, we'll use the dep_polarity as the main rating
    #     "type": "dep_polarity",
    #     "polarity": average_polarity,
    #     "adj_polarity": adj_polarity,
    #     "dep_polarity": dep_polarity,
    #     "id": i,
    #     "sentence": sentence,
    #     "sentence_key": sentence_key,
    #     "subsentence_key": subsentence_key,
    #     "business_id": inputs[sentence_key]["business_id"],
    #     "user_id": inputs[sentence_key]["user_id"],
    #     "votes": inputs[sentence_key]["votes"],
    #     "stars": inputs[sentence_key]["stars"],
    #     "lng": business["longitude"],
    #     "lat": business["latitude"],
    #     "full_address": business["full_address"],
    #     "name": business["name"],
    #     "food": foodName,
    #     "concepts": sample_dict['full_concept'],
    #     "filtered_concepts": sample_dict['filtered_concept']
    # })

def write():
    to_write = []
    for currKey in filtered_sentences:
        for subsentence_key in filtered_sentences[currKey]:
            to_write.append(filtered_sentences[currKey][subsentence_key])

    with open(TARGET_FILENAME, 'w') as f:
        f.write(simplejson.dumps(to_write))


def main():
    polarity.load_cached_polarity()
    original_read_input()
    results = load_results(SAMPlE_DATA_PATH)
    gold_samples = filter(lambda x: x["type"] == "manual_label" and x["food"] == foodName, results)

    # for now, let's do the first 10 sentences
    gold_samples = gold_samples[0:280]
    for i in range(len(gold_samples)):
        print str(i) + '/' + str(len(gold_samples))
        gold_sample = gold_samples[i]
        setup(gold_sample)

    # y, x = svm_read_problem('/Users/sorathan/libsvm-3.20/heart_scale')
    m = svm_train(y[:210], x[:210], '-c 1000000 -w1 0 -w-1 5 -w0 1')
    p_label, p_acc, p_val = svm_predict(y[210:], x[210:], m)
    import ipdb; ipdb.set_trace()

    # train(train_data)
    # test(test_data)
    # original_read_input()
    # write()

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print "Invalid number of arguments, need: python feature_based_sentiment_classifier.py foodName"
        exit(0)
    try:
        foodName = args[0]
    except ValueError:
        print "Bad input arguments!"
        exit(0)
    main()