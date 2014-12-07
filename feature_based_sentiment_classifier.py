import simplejson
from process_reviews import INPUT_FILENAME
from process_reviews import BUSINESS_FILENAME
from process_reviews import CONCEPT_PARSER_COMMAND_LIST
from process_reviews import load_results
from process_reviews import compute_polarity
from svmutil import *
from urllib2 import HTTPError

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
    try:
        score = sn.polarity(word)
    except HTTPError:
        score = compute_polarity(word)

    return score

def setup(sample):
    sentence = sample["sentence"]
    y.append(sample["rating"])
    new_x = {
        # "polarity": sample["polarity"],
        # "adj_polarity": sample["adj_polarity"],
        # "dep_polarity": sample["dep_polarity"],
        # "adjective_score_distance_pair": []
    }

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

    for i, word_and_POS in enumerate(tagged):
        POS = word_and_POS[1]
        if POS == "JJ":
            score = compute_polarity_wrapper(word_and_POS[0])
            distance = abs(i - food_index)

            new_x[distance] = score
            # new_x["adjective_score_distance_pair"].append((score, distance))

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
    original_read_input()
    results = load_results(SAMPlE_DATA_PATH)
    gold_samples = filter(lambda x: x["type"] == "manual_label" and x["food"] == foodName, results)

    # for now, let's do the first 10 sentences
    gold_samples = gold_samples[0:200]
    for i in range(len(gold_samples)):
        print str(i) + '/' + str(len(gold_samples))
        gold_sample = gold_samples[i]
        setup(gold_sample)

    # y, x = svm_read_problem('/Users/sorathan/libsvm-3.20/heart_scale')
    m = svm_train(y[:150], x[:150], '-c 4')
    p_label, p_acc, p_val = svm_predict(y[150:], x[150:], m)

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