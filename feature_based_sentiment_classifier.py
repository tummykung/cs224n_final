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
NUM_FEATURES = 9
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
    x[datapoint][4] = sample["pleasantness"]
    x[datapoint][5] = sample["aptitude"]
    x[datapoint][6] = sample["attention"]
    x[datapoint][7] = sample["sensitivity"]

    # for bad_word in bad_words:
    #     if bad_word in sample["sentence"]:
    #         x[datapoint][5] += 1


    # # ----- first, do language processing on this sentence -----
    # tokens = nltk.word_tokenize(sentence)
    # tagged = nltk.pos_tag(tokens)
    # # if VERBOSE:
    #     # print "POS: " + repr(tagged)
    # food_index = -1
    # actual_word = ""
    # for i, word_and_POS in enumerate(tagged):
    #     if foodName in word_and_POS[0]:
    #         food_index = i
    #         actual_word = word_and_POS[0]

    # total = 0
    # count = 0
    # scores = []
    # for i, word_and_POS in enumerate(tagged):
    #     POS = word_and_POS[1]
    #     if POS in ("JJ", "JJS", "JJR"):
    #         score = compute_polarity_wrapper(word_and_POS[0])
    #         scores.append(score)
    #         distance = abs(i - food_index)
    #         if distance != 0:
    #             total += score / distance
    #             count += 1

    # if count > 0:
    #     x[datapoint][4] = total / count
                # new_x["adjective_score_distance_pair"].append((score, distance))
        # if len(scores) > 0:
        #     new_x[0] = float(sum(scores))/len(scores)


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

    positve_examples = filter(lambda x: x["rating"] in (1, 2) , gold_samples)
    negative_examples = filter(lambda x: x["rating"] in (-1, -2), gold_samples)
    neutral_examples = filter(lambda x: x["rating"] == 0, gold_samples)

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

    # negativeWeight = len(y) / float(len(filter(lambda x : x == -1, y)))
    # zeroWeight = len(y) / float(len(filter(lambda x : x == 0, y)))
    # positiveWeight = len(y) / float(len(filter(lambda x : x == 1, y)))
    negativeWeight = 1
    zeroWeight = 1
    positiveWeight = 1
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

    # pair = zip(x, y)

    # train = pair[0:210]
    # test = pair[210:]

    # pos = filter(lambda x:x[1]==1, train)
    # zero  = filter(lambda x:x[1]==0, train)
    # neg  = filter(lambda x:x[1]==-1, train)

    # posTest = filter(lambda x:x[1]==1, test)
    # zeroTest  = filter(lambda x:x[1]==0, test)
    # negTest  = filter(lambda x:x[1]==-1, test)


    # mean1 = sum(map(lambda x:sum(x[0][2:])/2, neg))/len(neg)
    # mean2 = sum(map(lambda x:sum(x[0][2:])/2, zero))/len(zero)
    # mean3 = sum(map(lambda x:sum(x[0][2:])/2, pos))/len(pos)


    # best_error = 1.0
    # bestI = -1
    # bestJ = -1
    # for i in range(-20, 20):
    #     for j in range(-20, 20):
    #         thingI = float(i)/4
    #         thingJ = float(j)/4
    #         m, n = evaluate_dumb_predictor(train, i, j, mean1, mean2, mean3)
    #         if n < best_error:
    #             best_error = n
    #             bestI = thingI
    #             bestJ = thingJ

    # print evaluate_dumb_predictor(test, bestI, bestJ, mean1, mean2, mean3)
    ipdb.set_trace()

def dumb_predictor(thing, a, b, mean1, mean2, mean3):
    mean_neg = mean1
    mean_zero = mean2
    mean_pos = mean3

    lower_threshold = (mean_neg + mean_zero)/2 + a
    higher_threshold = (mean_pos + mean_zero)/2 + b

    mean_thing = sum(thing)/2

    if mean_thing < lower_threshold:
        return -1
    if mean_thing > higher_threshold:
        return 1
    else:
        return 0

def evaluate_dumb_predictor(data, i, j, mean1, mean2, mean3):
    predictions = []
    answers = []
    for dataX, dataY in data:
        predictions.append(dumb_predictor(dataX, i, j, mean1, mean2, mean3))
        answers.append(dataY)

    m, n = evaluate_error(zip(predictions, answers))
    # print i,j, m, n
    return m, n


def evaluate_error(to_evaluate):
    error = 0
    total = len(to_evaluate)
    for prediction, answer in to_evaluate:
        if prediction != answer:
            error += 1

    return error, float(error)/len(to_evaluate)


def num(the_set, threshold):
    a = len(filter(lambda x: sum(x[0])/4 >= threshold, the_set))
    b = len(the_set) - a
    c = len(the_set)
    return a,b,c



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
