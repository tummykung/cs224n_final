import simplejson
from process_reviews import INPUT_FILENAME
from process_reviews import BUSINESS_FILENAME
from process_reviews import load_results
from sentence import CONCEPT_PARSER_COMMAND_LIST
from sklearn import svm
from sklearn import cross_validation
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn import preprocessing
from sklearn.svm import SVC
from urllib2 import HTTPError
import math
import polarity

import ipdb
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
BAD_WORDS = "bad_words"

# initialization
inputs = []
businesses = []
results = []
NUM_SAMPLE = 10000
NUM_DATA = 280
NUM_FEATURES = 6
VERBOSE = True
x = np.zeros(shape=(NUM_DATA, NUM_FEATURES))
y = np.zeros(shape=(NUM_DATA)) 
sn = Senticnet()
bad_words = set()

def original_read_input():
    with open(BAD_WORDS, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            bad_words.add(line.rstrip('\n'))
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

def setup(sample, datapoint):
    sentence = sample["sentence"]
    rating = sample["rating"]
    # collapse 2 and -2 to 1 and -1, respectively
    if rating == 2:
        rating = 1
    if rating == -2:
        rating = -1

    y[datapoint] = rating

    x[datapoint][0] = 1
    x[datapoint][1] = sample["concept_polarity"]
    x[datapoint][2] = sample["adj_polarity"]
    x[datapoint][3] = sample["dep_polarity"]

    for bad_word in bad_words:
        if bad_word in sample["sentence"]:
            x[datapoint][5] += 1


    # ----- first, do language processing on this sentence -----
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

    total = 0
    count = 0
    scores = []
    for i, word_and_POS in enumerate(tagged):
        POS = word_and_POS[1]
        if POS in ("JJ", "JJS", "JJR"):
            score = compute_polarity_wrapper(word_and_POS[0])
            scores.append(score)
            distance = abs(i - food_index)
            if distance != 0:
                total += score / distance
                count += 1

    if count > 0:
        x[datapoint][4] = total / count
                # new_x["adjective_score_distance_pair"].append((score, distance))
        # if len(scores) > 0:
        #     new_x[0] = float(sum(scores))/len(scores)


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
        setup(gold_sample, i)

    cArray = []
    for i in range(-15,15):
        cArray.append(math.pow(2,i))

    gammaArray = []
    for i in range(-5,0):
        gammaArray.append(math.pow(10,i))

    coeffArray = []
    for i in range(-5,0):
        coeffArray.append(math.pow(10,i))

    # Set the parameters by cross-validation
    tuned_parameters = [{'kernel': ['rbf'], 'gamma': gammaArray,
                         'C': cArray},
                         {'kernel': ['poly'], 'gamma' : gammaArray, 
                             'C': cArray, 'coef0': coeffArray},
                        {'kernel': ['linear'], 'C': cArray}]

    global x
    #x = preprocessing.scale(x)
    x[:,0] = 1

    negativeWeight = len(y) / float(len(filter(lambda x : x == -1, y)))
    zeroWeight = len(y) / float(len(filter(lambda x : x == 0, y)))
    positiveWeight = len(y) / float(len(filter(lambda x : x == 1, y)))
    print negativeWeight
    print zeroWeight
    print positiveWeight
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(x, y, test_size=0.5, random_state=0)
    clf = GridSearchCV(SVC(class_weight={-1: negativeWeight, 0: zeroWeight, 1:
        positiveWeight}), tuned_parameters,
            cv=5, scoring='f1',
            n_jobs=16 ) 
    clf.fit(X_train, y_train)
    print("Best parameters set found on development set:")
    print()
    print(clf.best_estimator_)
    print()
   # print("Grid scores on development set:")
   # print()
   # for params, mean_score, scores in clf.grid_scores_:
   #     print("%0.3f (+/-%0.03f) for %r"
   #           % (mean_score, scores.std() / 2, params))
   # print()

    print("Detailed classification report:")
    print()
    print("The model is trained on the full development set.")
    print("The scores are computed on the full evaluation set.")
    print()
    y_true, y_pred = y_test, clf.predict(X_test)
    print(classification_report(y_true, y_pred))
    print()
    ipdb.set_trace()



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
